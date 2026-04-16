# 🔐 Django Auth API — Swagger UI + Vercel Deploy

A production-ready Django REST Framework authentication system with a full **Swagger UI** for interactive API exploration. Includes JWT-based auth, user registration, login, profile management, and password change.

---

## 📸 Live API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/auth/register/` | ❌ Public | Register a new user |
| `POST` | `/api/auth/login/` | ❌ Public | Login — returns JWT token |
| `POST` | `/api/auth/logout/` | ✅ Bearer | Logout |
| `GET` | `/api/auth/profile/` | ✅ Bearer | Get user profile |
| `PATCH` | `/api/auth/profile/` | ✅ Bearer | Update profile |
| `POST` | `/api/auth/change-password/` | ✅ Bearer | Change password |
| `GET` | `/api/auth/verify-token/` | ✅ Bearer | Verify JWT token |
| `GET` | `/swagger/` | ❌ Public | Swagger UI |
| `GET` | `/redoc/` | ❌ Public | ReDoc UI |

---

## 🚀 Quick Start (Local)

### 1. Clone & install

```bash
git clone <your-repo-url>
cd django-auth-swagger
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and set DJANGO_SECRET_KEY and JWT_SECRET
```

### 3. Run

```bash
python manage.py migrate
python manage.py runserver
```

### 4. Open Swagger UI

Navigate to → **http://localhost:8000/swagger/**

---

## 🧪 How to Test Authentication in Swagger

1. **Register** — expand `POST /api/auth/register/`, click **Try it out**, fill in `username`, `email`, `password`, `password2`, then **Execute**
2. **Copy the token** from the response
3. Click the **🔒 Authorize** button at the top of the page
4. Enter: `Bearer eyJhbGciO...` (your full token)
5. Click **Authorize** → **Close**
6. Now all 🔒 endpoints are unlocked — try **GET /api/auth/profile/**

---

## ☁️ Deploy to Vercel

### Prerequisites

- [Vercel CLI](https://vercel.com/docs/cli): `npm i -g vercel`
- A Vercel account (free tier works)

### Steps

```bash
# 1. Login to Vercel
vercel login

# 2. Deploy (first time — will prompt for project setup)
vercel

# 3. Set environment variables in Vercel dashboard:
#    DJANGO_SECRET_KEY = <strong random string>
#    JWT_SECRET        = <strong random string>
#    DEBUG             = False
```

Or set env vars via CLI:

```bash
vercel env add DJANGO_SECRET_KEY
vercel env add JWT_SECRET
vercel env add DEBUG
```

### Re-deploy after changes

```bash
vercel --prod
```

> ⚠️ **Vercel SQLite note**: Vercel functions are stateless — SQLite data won't persist between requests. For production, replace `DATABASES` in `settings.py` with PostgreSQL (e.g. [Neon](https://neon.tech) or [Supabase](https://supabase.com), both have free tiers).

---

## 🗂️ Project Structure

```
django-auth-swagger/
├── config/
│   ├── __init__.py
│   ├── settings.py        # Django settings + JWT + Swagger config
│   ├── urls.py            # Root URL conf + Swagger schema view
│   └── wsgi.py            # Vercel entry point
├── auth_app/
│   ├── authentication.py  # JWT encode/decode + DRF backend
│   ├── serializers.py     # Register, Login, Profile, ChangePassword
│   ├── views.py           # All API views with @swagger_auto_schema
│   ├── urls.py            # Auth URL patterns
│   └── models.py
├── requirements.txt
├── vercel.json            # Vercel build + routing config
├── build.sh               # migrate + collectstatic
├── manage.py
└── .env.example
```

---

## 🔑 JWT Token Details

- **Algorithm**: HS256
- **Expiry**: 24 hours (configurable via `JWT_EXPIRY_HOURS` in settings)
- **Header format**: `Authorization: Bearer <token>`

---

## 🛠️ Tech Stack

- **Django 4.2** — web framework
- **Django REST Framework** — REST API
- **drf-yasg** — Swagger/OpenAPI 2.0 schema generation
- **PyJWT** — JWT encode/decode
- **django-cors-headers** — CORS support
