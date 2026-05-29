from django.urls import path
from .views.submission import SubmissionListCreateView, SubmissionDetailView, SubmissionVersionListView
from .views.workflow import (
    ResubmitView, ApproveView, RejectView, DeanApproveView,
    PublishView, PublishBulkView, RevokeView, ReprocessView,
    CommentListCreateView, CommentResolveView,
)

urlpatterns = [
    path('', SubmissionListCreateView.as_view(), name='submission-list'),
    path('publish-bulk/', PublishBulkView.as_view(), name='submission-publish-bulk'),
    path('<uuid:pk>/', SubmissionDetailView.as_view(), name='submission-detail'),
    path('<uuid:pk>/versions/', SubmissionVersionListView.as_view(), name='submission-versions'),
    path('<uuid:pk>/resubmit/', ResubmitView.as_view(), name='submission-resubmit'),
    path('<uuid:pk>/approve/', ApproveView.as_view(), name='submission-approve'),
    path('<uuid:pk>/reject/', RejectView.as_view(), name='submission-reject'),
    path('<uuid:pk>/dean-approve/', DeanApproveView.as_view(), name='submission-dean-approve'),
    path('<uuid:pk>/publish/', PublishView.as_view(), name='submission-publish'),
    path('<uuid:pk>/revoke/', RevokeView.as_view(), name='submission-revoke'),
    path('<uuid:pk>/reprocess/', ReprocessView.as_view(), name='submission-reprocess'),
    path('<uuid:pk>/comments/', CommentListCreateView.as_view(), name='submission-comments'),
    path('<uuid:pk>/comments/<uuid:comment_id>/resolve/', CommentResolveView.as_view(), name='comment-resolve'),
]
