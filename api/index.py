import os
import sys

# Add project root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
django.setup()

# Run migrations (safe for Vercel)
from django.core.management import call_command

try:
    call_command("migrate", verbosity=0, interactive=False)
except Exception as e:
    print("Migration error:", e)

# ✅ IMPORTANT: define app at top level (NO try/except wrapping)
from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()