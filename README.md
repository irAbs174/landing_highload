# Subscribe Service

Lightweight Django-based subscription endpoint with immediate response and background processing via Celery.

Features:
- `/api/subscribe/` endpoint validates phone (phonenumbers), logs request to MongoDB, enqueues Celery task to persist subscriber into PostgreSQL.
- Redis used as Celery broker and cache.
- Nginx as reverse proxy with rate limiting and gzip.
- Docker Compose orchestration.

See ARCHITECTURE.md for design decisions.

## Quickstart (Docker)

1. Build and start services:
```bash
docker-compose up --build -d
```

2. Apply migrations:
```bash
docker-compose exec web python manage.py makemigrations subscriptions
docker-compose exec web python manage.py migrate
```

3. Create superuser (optional):
```bash
docker-compose exec web python manage.py createsuperuser
```

4. Test endpoint:
```bash
curl -X POST http://localhost/api/subscribe/ -H 'Content-Type: application/json' -d '{"phone":"+989121234567"}'
```

## Load testing

Recommended tools: k6 or Locust.

Example k6 script (simple):
```javascript
import http from 'k6/http';
import { check } from 'k6';

export default function () {
  const res = http.post('http://localhost/api/subscribe/', JSON.stringify({phone: '+989121234567'}), {headers: {'Content-Type':'application/json'}});
  check(res, { 'status 202': r => r.status === 202 });
}
```

Run:
```bash
k6 run script.js
```

