from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import FileResponse

from apps.common.mixins import SuccessResponseMixin
from apps.common.pagination import StandardPagination
from ..models import Submission
from ..enums import SubmissionStatus


class ArchiveListView(SuccessResponseMixin, APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = Submission.objects.filter(
            versions__status=SubmissionStatus.PUBLISHED,
            versions__is_current=True,
        ).select_related('group__department__faculty', 'group__supervisor').distinct()

        faculty = request.query_params.get('faculty')
        department = request.query_params.get('department')
        year = request.query_params.get('year')
        q = request.query_params.get('q', '').strip()

        if faculty:
            qs = qs.filter(group__department__faculty__id=faculty)
        if department:
            qs = qs.filter(group__department__id=department)
        if year:
            qs = qs.filter(group__academic_year=year)
        if q:
            if request.user.is_authenticated:
                qs = qs.filter(Q(title__icontains=q) | Q(abstract__icontains=q) | Q(keywords__icontains=q))
            else:
                qs = qs.filter(title__icontains=q)

        paginator = StandardPagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(_serialize_public(page))


class ArchiveDetailView(SuccessResponseMixin, APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        submission = get_object_or_404(
            Submission,
            slug=slug,
            versions__status=SubmissionStatus.PUBLISHED,
            versions__is_current=True,
        )
        return self.success(data=_serialize_public([submission])[0])


class ArchiveDownloadView(SuccessResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        from ..models import SubmissionVersion
        submission = get_object_or_404(
            Submission,
            slug=slug,
            versions__status=SubmissionStatus.PUBLISHED,
            versions__is_current=True,
        )
        version = SubmissionVersion.objects.filter(
            submission=submission, is_current=True
        ).first()
        if not version:
            return self.error(message='File not available.', status_code=404)
        return FileResponse(version.file.open('rb'), as_attachment=True, filename=version.file.name.split('/')[-1])


class ArchiveSearchView(ArchiveListView):
    pass  # Reuses ArchiveListView — search logic is in the q param handler above


def _serialize_public(submissions):
    results = []
    for s in submissions:
        results.append({
            'slug': s.slug,
            'title': s.title,
            'abstract': s.abstract,
            'keywords': s.keywords,
            'academic_year': s.academic_year,
            'faculty': s.group.department.faculty.name,
            'department': s.group.department.name,
            'supervisor': s.group.supervisor.full_name,
            'authors': s.authors,
        })
    return results
