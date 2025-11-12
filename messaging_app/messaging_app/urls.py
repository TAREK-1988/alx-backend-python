from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),

    # Main API for our messaging app
    path("api/", include("chats.urls")),

    # DRF login/logout views for the browsable API
    path("api-auth/", include("rest_framework.urls")),
]
