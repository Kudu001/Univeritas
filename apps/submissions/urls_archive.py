from django.urls import path
from .views.archive import ArchiveListView, ArchiveDetailView, ArchiveDownloadView, ArchiveSearchView

urlpatterns = [
    path('', ArchiveListView.as_view(), name='archive-list'),
    path('search/', ArchiveSearchView.as_view(), name='archive-search'),
    path('<slug:slug>/', ArchiveDetailView.as_view(), name='archive-detail'),
    path('<slug:slug>/download/', ArchiveDownloadView.as_view(), name='archive-download'),
]
