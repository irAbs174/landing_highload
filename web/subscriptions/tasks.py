"""Celery tasks: normalize phone and upsert into Postgres, update Mongo log."""
from subscribe_service.celery import app
from celery.utils.log import get_task_logger
from pymongo import MongoClient
from django.conf import settings
import phonenumbers
from django.db import transaction, IntegrityError
from .models import Subscriber
import os
import django

logger = get_task_logger(__name__)

def get_mongo_client():
    cfg = settings.MONGO
    return MongoClient(host=cfg['HOST'], port=cfg['PORT'])

@app.task(bind=True, max_retries=3, default_retry_delay=5)
def process_subscription_task(self, log_id):
    try:
        client = get_mongo_client()
        db = client[settings.MONGO['DB']]
        logs = db.request_logs
        log_doc = logs.find_one({'_id': __import__('bson').ObjectId(log_id)})
        if not log_doc:
            logger.error("Log not found: %s", log_id)
            return

        raw_phone = log_doc.get('phone')
        # Normalize with phonenumbers
        try:
            parsed = phonenumbers.parse(raw_phone, None)
            normalized = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except Exception as e:
            logs.update_one({'_id': log_doc['_id']}, {'$set': {'status': 'error', 'error': str(e)}})
            return

        # Upsert into PostgreSQL
        # Django needs settings configured for standalone Celery worker if not already
        if not django.apps.apps.ready:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'subscribe_service.settings')
            django.setup()

        with transaction.atomic():
            obj, created = Subscriber.objects.update_or_create(
                phone=normalized,
                defaults={'raw_phone': raw_phone}
            )
        logs.update_one({'_id': log_doc['_id']}, {'$set': {'status': 'processed', 'normalized': normalized}})
        logger.info("Processed subscription %s -> %s", raw_phone, normalized)
    except Exception as exc:
        logger.exception("Error processing subscription: %s", exc)
        try:
            self.retry(exc=exc)
        except Exception:
            # final failure: mark error
            client = get_mongo_client()
            db = client[settings.MONGO['DB']]
            db.request_logs.update_one({'_id': __import__('bson').ObjectId(log_id)}, {'$set': {'status': 'error', 'error': str(exc)}})
            raise
