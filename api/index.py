import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
django.setup()

# Run migrations automatically (IMPORTANT for Vercel)
from django.core.management import call_command

try:
    call_command("migrate", verbosity=0, interactive=False)
except Exception as e:
    print("Migration error:", e)

# Start Django app
from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()