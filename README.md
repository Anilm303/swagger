# 🔐 Django Auth API — Swagger UI + Vercel

A Django REST Framework authentication system with interactive Swagger docs,
ready to deploy on Vercel in minutes.

---

## 📋 Endpoints

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| `POST` | `/api/auth/register/` | Public | Register a new user |
| `POST` | `/api/auth/login/` | Public | Login → get JWT token |
| `POST` | `/api/auth/logout/` | Public | Logout |
| `GET`  | `/api/auth/verify/` | 🔒 Bearer | Verify token |
| `GET`  | `/api/auth/profile/` | 🔒 Bearer | Get profile |
| `PATCH`| `/api/auth/profile/` | 🔒 Bearer | Update profile |
| `POST` | `/api/auth/change-password/` | 🔒 Bearer | Change password |

Swagger UI: **`/swagger/`** · ReDoc: **`/redoc/`**

---

## 🚀 Deploy to Vercel (3 steps)

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "initial commit"
gh repo create my-django-auth --public --push
```

### 2. Import in Vercel

1. Go to [vercel.com/new](https://vercel.com/new)
2. Click **"Import Git Repository"** → select your repo
3. Framework Preset: **Other** (leave as-is)
4. Click **Deploy**

### 3. Add Environment Variables

In the Vercel dashboard → your project → **Settings → Environment Variables**:

| Name | Value |
|------|-------|
| `DJANGO_SECRET_KEY` | a long random string |
| `JWT_SECRET` | another long random string |
| `DEBUG` | `False` |

Then **Redeploy** — done! ✅

---

## 💻 Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Migrate database
python manage.py migrate

# Start server
python manage.py runserver

# Open Swagger UI
open http://localhost:8000/swagger/
```

---

## 🗂 Project Structure

```
django-vercel/
├── api/
│   └── index.py          ← Vercel serverless entry point
├── core/
│   ├── settings.py       ← Django settings
│   └── urls.py           ← URL routing + Swagger schema
├── auth_app/
│   ├── authentication.py ← JWT encode/decode + DRF backend
│   ├── serializers.py    ← Request/response serializers
│   ├── views.py          ← API views with Swagger docs
│   └── urls.py           ← Auth URL patterns
├── requirements.txt
├── vercel.json           ← Vercel build + routing config
└── manage.py
```

---

## 🔑 Using the Swagger UI

1. `POST /api/auth/register/` → fill in username, email, password
2. Copy the `token` from the response
3. Click **Authorize 🔒** at the top of `/swagger/`
4. Enter: `Bearer eyJhbGciO...`
5. All protected endpoints are now unlocked

---

## ⚠️ Production Notes

- **SQLite in `/tmp`** works on Vercel but data resets on cold starts.
  For persistence, replace `DATABASES` in `core/settings.py` with a
  free PostgreSQL from [Neon](https://neon.tech) or [Supabase](https://supabase.com).
- Always set `DEBUG=False` in production.
- Use a strong `DJANGO_SECRET_KEY` (50+ random characters).
