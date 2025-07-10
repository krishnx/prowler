import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prowler_scanner.settings')

app = Celery('prowler_scanner')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_url = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
app.autodiscover_tasks()

# This ensures
# 1. balanced distribution of tasks in the celery workers
# 2. parallel scans do not block each other
# 3. if a worker crashes, the task is re-queued
app.conf.update(
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)
