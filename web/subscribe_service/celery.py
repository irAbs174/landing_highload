import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'subscribe_service.settings')

app = Celery('subscribe_service')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
