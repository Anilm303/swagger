import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

try:
    import django
    django.setup()

    from django.core.management import call_command
    call_command("migrate", verbosity=0, interactive=False)

    from django.core.wsgi import get_wsgi_application
    app = get_wsgi_application()

except Exception as e:
    def app(environ, start_response):
        start_response("500 Internal Server Error", [("Content-Type", "text/plain")])
        return [str(e).encode()]