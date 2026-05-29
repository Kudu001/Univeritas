from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.common.mixins import SuccessResponseMixin
from apps.common.pagination import StandardPagination
from apps.accounts.permissions import IsAdmin
from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogListView(SuccessResponseMixin, APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        qs = AuditLog.objects.select_related('actor').order_by('-timestamp')

        actor = request.query_params.get('actor')
        action = request.query_params.get('action')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        if actor:
            qs = qs.filter(actor__id=actor)
        if action:
            qs = qs.filter(action=action)
        if date_from:
            qs = qs.filter(timestamp__date__gte=date_from)
        if date_to:
            qs = qs.filter(timestamp__date__lte=date_to)

        paginator = StandardPagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(AuditLogSerializer(page, many=True).data)


class AuditLogDetailView(SuccessResponseMixin, APIView):
    permission_classes = [IsAdmin]

    def get(self, request, pk):
        from django.shortcuts import get_object_or_404
        log = get_object_or_404(AuditLog, pk=pk)
        return self.success(data=AuditLogSerializer(log).data)
