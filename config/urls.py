from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Django Auth API",
        default_version='v1',
        description="""
## 🔐 Authentication API

A complete Django REST authentication system with JWT tokens.

### How to Use
1. **Register** a new user via `POST /api/auth/register/`
2. **Login** with credentials via `POST /api/auth/login/` — you'll receive a JWT token
3. Click **Authorize** (🔒) above and enter: `Bearer <your_token>`
4. Access **protected endpoints** like `/api/auth/profile/` and `/api/auth/change-password/`
5. **Logout** via `POST /api/auth/logout/` to invalidate the token

### Token Format
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="admin@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('', RedirectView.as_view(url='/swagger/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api/auth/', include('auth_app.urls')),

    # Swagger UI
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
