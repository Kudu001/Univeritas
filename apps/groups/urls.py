from django.urls import path
from .views import (
    ProjectGroupListCreateView, ProjectGroupDetailView, ProjectGroupDeactivateView,
    GroupMemberCreateView, GroupMemberDeleteView, MyGroupView,
)

urlpatterns = [
    path('', ProjectGroupListCreateView.as_view(), name='group-list'),
    path('mine/', MyGroupView.as_view(), name='group-mine'),
    path('<uuid:pk>/', ProjectGroupDetailView.as_view(), name='group-detail'),
    path('<uuid:pk>/deactivate/', ProjectGroupDeactivateView.as_view(), name='group-deactivate'),
    path('<uuid:pk>/members/', GroupMemberCreateView.as_view(), name='group-member-add'),
    path('<uuid:pk>/members/<uuid:student_id>/', GroupMemberDeleteView.as_view(), name='group-member-remove'),
]
