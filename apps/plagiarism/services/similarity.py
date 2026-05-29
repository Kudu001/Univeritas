from apps.plagiarism.models import DissertationChunk
from apps.plagiarism.enums import ChunkType
from apps.submissions.enums import SubmissionStatus


def _get_archive_version_ids():
    """Return IDs of versions that are in scope for similarity comparison."""
    from apps.submissions.models import SubmissionVersion
    return list(
        SubmissionVersion.objects.filter(
            status__in=[SubmissionStatus.DEAN_APPROVED, SubmissionStatus.PUBLISHED]
        ).values_list('id', flat=True)
    )


def find_similar_text_chunks(embedding, exclude_version_id, top_k=20):
    """
    Find the most similar TEXT chunks in the archive using cosine distance.
    Returns queryset of DissertationChunk ordered by similarity (closest first).
    """
    archive_ids = _get_archive_version_ids()
    if not archive_ids:
        return DissertationChunk.objects.none()

    return (
        DissertationChunk.objects
        .filter(chunk_type=ChunkType.TEXT, version__id__in=archive_ids)
        .exclude(version__id=exclude_version_id)
        .order_by(DissertationChunk.embedding.l2_distance(embedding))[:top_k]
    )


def find_similar_code_chunks(code_embedding, exclude_version_id, top_k=20):
    """
    Find the most similar CODE chunks in the archive using cosine distance.
    Returns queryset of DissertationChunk ordered by similarity (closest first).
    """
    archive_ids = _get_archive_version_ids()
    if not archive_ids:
        return DissertationChunk.objects.none()

    return (
        DissertationChunk.objects
        .filter(chunk_type=ChunkType.CODE, version__id__in=archive_ids)
        .exclude(version__id=exclude_version_id)
        .order_by(DissertationChunk.code_embedding.l2_distance(code_embedding))[:top_k]
    )


def cosine_similarity(vec_a, vec_b):
    """Compute cosine similarity between two vectors."""
    import numpy as np
    a = np.array(vec_a)
    b = np.array(vec_b)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)
