from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from apps.common.mixins import SuccessResponseMixin
from apps.common.pagination import StandardPagination
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(SuccessResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Notification.objects.filter(recipient=request.user)
        read_param = request.query_params.get('read')
        if read_param == 'false':
            qs = qs.filter(read=False)
        paginator = StandardPagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(NotificationSerializer(page, many=True).data)


class NotificationMarkReadView(SuccessResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.read = True
        notification.save(update_fields=['read'])
        return self.success(message='Notification marked as read.')


class NotificationMarkAllReadView(SuccessResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        count = Notification.objects.filter(recipient=request.user, read=False).update(read=True)
        return self.success(data={'updated': count}, message=f'{count} notifications marked as read.')


class NotificationUnreadCountView(SuccessResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(recipient=request.user, read=False).count()
        return self.success(data={'unread_count': count})
