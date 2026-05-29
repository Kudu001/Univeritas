from django.urls import path
from .views import SystemSettingListView, SystemSettingDetailView

urlpatterns = [
    path('settings/', SystemSettingListView.as_view(), name='settings-list'),
    path('settings/<str:key>/', SystemSettingDetailView.as_view(), name='settings-detail'),
]
