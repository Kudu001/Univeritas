"""
Plagiarism detection pipeline.

Steps:
  1. Fetch version, create/update PlagiarismReport → PROCESSING
  2. Extract text (and code if has_code)
  3. Chunk text and code
  4. Generate embeddings (text: 384-dim MiniLM, code: 768-dim CodeBERT)
  5. Save DissertationChunk rows
  6. Query pgvector for similar chunks from DEAN_APPROVED/PUBLISHED archive
  7. Aggregate PlagiarismMatch rows (one per matched dissertation)
  8. Save PlagiarismChunkMatch rows
  9. Compute overall_score
 10. Flag if score exceeds threshold
 11. Set report → COMPLETED, version → PENDING_SUPERVISOR
 12. Notify supervisor
"""

from django.utils import timezone
from django.db import transaction

from apps.plagiarism.enums import ReportStatus, ChunkType
from apps.plagiarism.models import DissertationChunk, PlagiarismReport, PlagiarismMatch, PlagiarismChunkMatch
from apps.submissions.enums import SubmissionStatus
from apps.audit.services import log
from apps.audit.enums import AuditAction

SIMILARITY_THRESHOLD = 0.70  # chunk-level threshold — overridden by SystemSetting at runtime


def _get_flag_threshold():
    from apps.core.models import SystemSetting
    try:
        setting = SystemSetting.objects.get(key='PLAGIARISM_FLAG_THRESHOLD')
        return float(setting.value)
    except (SystemSetting.DoesNotExist, ValueError):
        return 0.40


def run_pipeline(version_id):
    from apps.submissions.models import SubmissionVersion

    try:
        version = SubmissionVersion.objects.select_related('submission__group').get(id=version_id)
    except SubmissionVersion.DoesNotExist:
        return

    report, _ = PlagiarismReport.objects.get_or_create(
        version=version,
        defaults={'status': ReportStatus.PENDING},
    )

    try:
        _execute(version, report)
    except Exception as exc:
        report.status = ReportStatus.FAILED
        report.save(update_fields=['status'])
        version.status = SubmissionStatus.PROCESSING_FAILED
        version.save(update_fields=['status'])
        log(actor=None, action=AuditAction.PLAGIARISM_FAILED, obj=version,
            changes={'error': str(exc)})
        raise


def _execute(version, report):
    from apps.plagiarism.services.extraction import extract_text_from_pdf, extract_code_from_zip
    from apps.plagiarism.services.chunking import chunk_text, chunk_code
    from apps.plagiarism.services.embedding import generate_text_embedding, generate_code_embedding
    from apps.plagiarism.services.similarity import find_similar_text_chunks, find_similar_code_chunks, cosine_similarity

    # Step 1 — mark as processing
    report.status = ReportStatus.PROCESSING
    report.save(update_fields=['status'])
    version.status = SubmissionStatus.PROCESSING
    version.save(update_fields=['status'])
    log(actor=None, action=AuditAction.PLAGIARISM_STARTED, obj=version)

    # Step 2 — extract text
    version.file.seek(0)
    pages = extract_text_from_pdf(version.file)
    full_text = ' '.join(text for _, text in pages)
    version.extracted_text = full_text
    version.save(update_fields=['extracted_text'])

    code_files = []
    if version.has_code and version.code_file:
        version.code_file.seek(0)
        code_files = extract_code_from_zip(version.code_file)

    # Steps 3-5 — chunk, embed, save
    text_chunks = chunk_text(pages)
    text_chunk_objs = []
    for chunk in text_chunks:
        emb = generate_text_embedding(chunk['content'])
        obj = DissertationChunk.objects.create(
            version=version,
            chunk_type=ChunkType.TEXT,
            chunk_index=chunk['chunk_index'],
            page_number=chunk['page_number'],
            content=chunk['content'],
            embedding=emb,
        )
        text_chunk_objs.append((obj, emb))

    code_chunk_objs = []
    if code_files:
        code_chunks = chunk_code(code_files)
        for chunk in code_chunks:
            emb = generate_code_embedding(chunk['content'])
            obj = DissertationChunk.objects.create(
                version=version,
                chunk_type=ChunkType.CODE,
                chunk_index=chunk['chunk_index'],
                source_file=chunk['source_file'],
                language=chunk['language'],
                content=chunk['content'],
                code_embedding=emb,
            )
            code_chunk_objs.append((obj, emb))

    # Steps 6-8 — similarity search and match aggregation
    match_map = {}  # matched_version_id → {'score': float, 'chunk_matches': list}

    for source_obj, emb in text_chunk_objs:
        similar = find_similar_text_chunks(emb, exclude_version_id=version.id)
        for archive_chunk in similar:
            sim = cosine_similarity(emb, archive_chunk.embedding)
            if sim < SIMILARITY_THRESHOLD:
                continue
            vid = str(archive_chunk.version_id)
            if vid not in match_map:
                match_map[vid] = {'score': 0.0, 'chunk_matches': [], 'version': archive_chunk.version}
            if sim > match_map[vid]['score']:
                match_map[vid]['score'] = sim
            match_map[vid]['chunk_matches'].append((source_obj, archive_chunk, sim))

    for source_obj, emb in code_chunk_objs:
        similar = find_similar_code_chunks(emb, exclude_version_id=version.id)
        for archive_chunk in similar:
            sim = cosine_similarity(emb, archive_chunk.code_embedding)
            if sim < SIMILARITY_THRESHOLD:
                continue
            vid = str(archive_chunk.version_id)
            if vid not in match_map:
                match_map[vid] = {'score': 0.0, 'chunk_matches': [], 'version': archive_chunk.version}
            if sim > match_map[vid]['score']:
                match_map[vid]['score'] = sim
            match_map[vid]['chunk_matches'].append((source_obj, archive_chunk, sim))

    overall_score = 0.0
    with transaction.atomic():
        for vid, data in match_map.items():
            pm = PlagiarismMatch.objects.create(
                report=report,
                matched_version=data['version'],
                similarity_score=data['score'],
                total_chunks_matched=len(data['chunk_matches']),
            )
            for source_chunk, archive_chunk, sim in data['chunk_matches']:
                PlagiarismChunkMatch.objects.create(
                    match=pm,
                    source_chunk=source_chunk,
                    matched_chunk=archive_chunk,
                    similarity_score=sim,
                )
            if data['score'] > overall_score:
                overall_score = data['score']

    # Steps 9-10 — finalise report
    threshold = _get_flag_threshold()
    report.overall_score = overall_score
    report.flagged = overall_score >= threshold
    report.status = ReportStatus.COMPLETED
    report.completed_at = timezone.now()
    report.save(update_fields=['overall_score', 'flagged', 'status', 'completed_at'])

    # Step 11 — advance version status
    version.status = SubmissionStatus.PENDING_SUPERVISOR
    version.save(update_fields=['status'])

    # Step 12 — notify supervisor
    from apps.notifications.services import notify
    from apps.notifications.enums import NotificationType
    notify(
        recipient=version.submission.group.supervisor,
        notification_type=NotificationType.PLAGIARISM_REPORT_READY,
        title='Plagiarism report ready',
        body=f'The plagiarism report for {version.submission.title} (v{version.version_number}) is ready. '
             f'Overall similarity score: {overall_score:.0%}.',
    )

    action = AuditAction.PLAGIARISM_FLAGGED if report.flagged else AuditAction.PLAGIARISM_COMPLETED
    log(actor=None, action=action, obj=version,
        changes={'overall_score': overall_score, 'flagged': report.flagged})
