"""API endpoints for subscriptions.

Behavior:
- Validate incoming phone using serializer (which uses phonenumbers)
- Persist request log in MongoDB immediately (with status 'pending')
- Trigger Celery task to process/store into PostgreSQL
- Return 202 Accepted immediately with log id
"""
import json
import os
import socket
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from .serializers import SubscribeSerializer
from django.conf import settings
from pymongo import MongoClient
from .tasks import process_subscription_task
import time
import redis

# initialize Mongo client (module level for reuse)
_mongo_client = None
def get_mongo():
    global _mongo_client
    if _mongo_client is None:
        cfg = settings.MONGO
        _mongo_client = MongoClient(host=cfg['HOST'], port=cfg['PORT'])
    return _mongo_client

_redis = None
def get_redis():
    global _redis
    if _redis is None:
        _redis = redis.StrictRedis.from_url(settings.CELERY_BROKER_URL)
    return _redis

@api_view(['POST'])
def subscribe_view(request):
    # ذخیره بدنه‌ی خام قبل از دسترسی به request.data
    raw_body = request.body.decode('utf-8', errors='ignore')

    serializer = SubscribeSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse({'errors': serializer.errors}, status=400)

    phone = serializer.validated_data['phone']
    client = get_mongo()
    db = client[settings.MONGO['DB']]
    logs = db.request_logs

    log_doc = {
        'phone': phone,
        'status': 'pending',
        'ip': request.META.get('REMOTE_ADDR'),
        'user_agent': request.META.get('HTTP_USER_AGENT'),
        'body': raw_body,   # از نسخه‌ی قبل ذخیره‌شده استفاده کن
        'created_at': __import__('datetime').datetime.utcnow(),
    }
    res = logs.insert_one(log_doc)
    log_id = str(res.inserted_id)

    process_subscription_task.delay(log_id)

    return JsonResponse({'status': 'accepted', 'log_id': log_id}, status=202)

def index(request):
    """
    Simple home page view with Redis caching.
    Renders HTML once, caches for 60 seconds.
    """
    r = get_redis()
    cache_key = "home_html"

    # سعی در گرفتن از کش
    cached_html = r.get(cache_key)
    if cached_html:
        return HttpResponse(cached_html.decode("utf-8"))

    # اگر کش وجود ندارد → render کن
    context = {
        'title': 'Subscribe Service (cached)',
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    html = render(request, 'index.html',context).content.decode("utf-8")

    # ذخیره در کش برای ۶۰ ثانیه
    r.setex(cache_key, 60, html)

    return HttpResponse(html)