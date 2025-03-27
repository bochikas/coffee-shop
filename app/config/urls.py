from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
]

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls  # noqa WPS433

    urlpatterns += debug_toolbar_urls()
