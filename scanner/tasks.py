import time
import logging

from celery import shared_task
from django.utils import timezone
from .models import Scan
from .redis_provider import RedisProvider

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def run_scan_task(self, scan_id):
    self.update_state(state='PROGRESS', meta={'current': 0})

    redis_pro = RedisProvider()
    lock_key = redis_pro.get_key(scan_id)

    # acquire lock with 5 minutes TTL
    got_lock = redis_pro.conn.set(lock_key, 'locked', ex=300, nx=True)
    if not got_lock:
        logger.info(f'Scan {scan_id} is already running, skipping this duplicate task')
        return None

    scan = Scan.objects.get(id=scan_id)
    try:
        scan.status = 'in_progress'
        scan.save()

        # actual scan invocation logic should happen here and simulate realtime update for the celery status
        for idx in range(6):
            time.sleep(1)
            self.update_state(state='PROGRESS', meta={'current': idx + 1, 'total': 10})

        # Update Scan status to completed
        scan.status = 'completed'
        scan.ended_at = timezone.now()
        scan.save()

        logger.info(f'scan id {scan.id} completed')

    except Exception as e:
        scan.status = 'failed'
        scan.ended_at = timezone.now()
        scan.save()

        raise e

    finally:
        # delete the lock key from Redis
        redis_pro.delete(scan_id)
