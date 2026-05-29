from django.urls import path
from .views import (
    FacultyListCreateView, FacultyDetailView,
    DepartmentListView, DepartmentCreateView, DepartmentDetailView,
)

urlpatterns = [
    path('faculties/', FacultyListCreateView.as_view(), name='faculty-list'),
    path('faculties/<uuid:pk>/', FacultyDetailView.as_view(), name='faculty-detail'),
    path('faculties/<uuid:faculty_pk>/departments/', DepartmentListView.as_view(), name='department-list'),
    path('departments/', DepartmentCreateView.as_view(), name='department-create'),
    path('departments/<uuid:pk>/', DepartmentDetailView.as_view(), name='department-detail'),
]
