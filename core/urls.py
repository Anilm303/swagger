from django.contrib import admin
from django.urls import path, re_path
from django.http import JsonResponse, HttpResponse

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Home route (prevents 500 on "/")
def home(request):
    return JsonResponse({
        "message": "Django API Running 🚀",
        "swagger": "/swagger/",
        "redoc": "/redoc/"
    })

# Favicon fix
def favicon(request):
    return HttpResponse(status=204)

schema_view = get_schema_view(
    openapi.Info(
        title="API",
        default_version='v1',
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("", home),
    path("favicon.ico", favicon),

    path("admin/", admin.site.urls),

    re_path(r"^swagger/$", schema_view.with_ui("swagger", cache_timeout=0)),
    re_path(r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0)),
]