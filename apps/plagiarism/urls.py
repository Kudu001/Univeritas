from django.urls import path
from .views.report import PlagiarismReportView
from .views.match import PlagiarismMatchListView, ChunkMatchDetailView

urlpatterns = [
    path('reports/<uuid:version_id>/', PlagiarismReportView.as_view(), name='plagiarism-report'),
    path('reports/<uuid:version_id>/matches/', PlagiarismMatchListView.as_view(), name='plagiarism-matches'),
    path('matches/<uuid:match_id>/chunks/', ChunkMatchDetailView.as_view(), name='plagiarism-chunk-matches'),
]
