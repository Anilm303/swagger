import os
import django
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()

# Run migrations automatically
try:
    call_command('migrate', verbosity=0)
except Exception as e:
    print("Migration error:", e)

app = get_wsgi_application()