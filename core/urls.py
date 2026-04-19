from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="🔐 Django Auth API",
        default_version="v1",
        description="""
## Django REST Framework — JWT Authentication API

A complete authentication system built with Django + DRF, with interactive Swagger docs.

---

### 🚀 Quick Start

**Step 1 — Register** a new account using `POST /api/auth/register/`

**Step 2 — Login** via `POST /api/auth/login/` — copy the `token` from the response

**Step 3 — Authorize** — click the 🔒 **Authorize** button above and enter:
```
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Step 4 — Use protected endpoints** like `GET /api/auth/profile/`

---

### 🔑 Token Info
- Format: `Authorization: Bearer <token>`
- Algorithm: HS256
- Expiry: 24 hours
        """,
        contact=openapi.Contact(email="admin@example.com"),
        license=openapi.License(name="MIT"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Redirect root → Swagger
    path("", RedirectView.as_view(url="/swagger/", permanent=False)),

    path("admin/", admin.site.urls),
    path("api/auth/", include("auth_app.urls")),

    # Swagger UI
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger-ui"),
    path("redoc/",   schema_view.with_ui("redoc",   cache_timeout=0), name="redoc-ui"),
    path("swagger.json", schema_view.without_ui(cache_timeout=0),     name="swagger-json"),
]
