from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.accounts.urls.auth')),
    path('api/v1/accounts/', include('apps.accounts.urls.users')),
    path('api/v1/institutions/', include('apps.institutions.urls')),
    path('api/v1/groups/', include('apps.groups.urls')),
    path('api/v1/submissions/', include('apps.submissions.urls')),
    path('api/v1/plagiarism/', include('apps.plagiarism.urls')),
    path('api/v1/archive/', include('apps.submissions.urls_archive')),
    path('api/v1/audit/', include('apps.audit.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/config/', include('apps.core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    try:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass
