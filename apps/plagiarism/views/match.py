from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from apps.common.mixins import SuccessResponseMixin
from apps.submissions.models import SubmissionVersion
from ..models import PlagiarismReport, PlagiarismMatch
from ..serializers.match import PlagiarismMatchSerializer, ChunkMatchSerializer
from .report import PlagiarismReportView


class PlagiarismMatchListView(SuccessResponseMixin, APIView):

    def get(self, request, version_id):
        version = get_object_or_404(SubmissionVersion, pk=version_id)
        PlagiarismReportView()._check_access(request.user, version)
        report = get_object_or_404(PlagiarismReport, version=version)
        matches = report.matches.select_related('matched_version__submission__group__department__faculty').all()
        return self.success(data=PlagiarismMatchSerializer(matches, many=True).data)


class ChunkMatchDetailView(SuccessResponseMixin, APIView):

    def get(self, request, match_id):
        match = get_object_or_404(PlagiarismMatch, pk=match_id)
        PlagiarismReportView()._check_access(request.user, match.report.version)
        chunk_matches = match.chunk_matches.select_related('source_chunk', 'matched_chunk').all()
        return self.success(data=ChunkMatchSerializer(chunk_matches, many=True).data)
