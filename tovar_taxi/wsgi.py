# tovar_taxi/wsgi.py
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tovar_taxi.settings')

application = get_wsgi_application()
