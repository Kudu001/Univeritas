from django.urls import path
from .views import AuditLogListView, AuditLogDetailView

urlpatterns = [
    path('logs/', AuditLogListView.as_view(), name='audit-list'),
    path('logs/<uuid:pk>/', AuditLogDetailView.as_view(), name='audit-detail'),
]
