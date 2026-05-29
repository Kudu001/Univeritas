from django.urls import path
from ..views.users import (
    ProfileView,
    DeanListCreateView, DeanDetailView, DeanActivateView, DeanDeactivateView,
    SupervisorListCreateView, SupervisorDetailView, SupervisorActivateView, SupervisorDeactivateView,
)

urlpatterns = [
    path('me/', ProfileView.as_view(), name='profile'),
    path('deans/', DeanListCreateView.as_view(), name='dean-list'),
    path('deans/<uuid:pk>/', DeanDetailView.as_view(), name='dean-detail'),
    path('deans/<uuid:pk>/activate/', DeanActivateView.as_view(), name='dean-activate'),
    path('deans/<uuid:pk>/deactivate/', DeanDeactivateView.as_view(), name='dean-deactivate'),
    path('supervisors/', SupervisorListCreateView.as_view(), name='supervisor-list'),
    path('supervisors/<uuid:pk>/', SupervisorDetailView.as_view(), name='supervisor-detail'),
    path('supervisors/<uuid:pk>/activate/', SupervisorActivateView.as_view(), name='supervisor-activate'),
    path('supervisors/<uuid:pk>/deactivate/', SupervisorDeactivateView.as_view(), name='supervisor-deactivate'),
]
