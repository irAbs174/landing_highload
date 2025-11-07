# Architecture

## Diagram
- Client -> Nginx -> Gunicorn/Django -> Mongo (logs) + Celery -> PostgreSQL (subscribers)
- Redis used for Celery broker and caching.

## Decisions
- Django + DRF for rapid API development and validation.
- MongoDB for append-only request logs (fast writes, schemaless).
- PostgreSQL for authoritative subscriber data (ACID, relational).
- Celery + Redis to decouple immediate response from heavier DB writes.
- Nginx for SSL/Rate-limiting/Compression.

## Security & Ops
- Validate phone numbers using `phonenumbers`.
- Rate limiting at Nginx ensures per-IP throttling.
- Log all incoming requests in Mongo with IP & UA for audit.
- Run workers with limited concurrency, use retries for transient failures.
- Use environment variables for secrets; don't commit SECRET_KEY.
- Suggest monitoring: Prometheus + Grafana + alerting on Celery queue length, worker failures.

## Scalability
- Scale web and worker services horizontally; Redis/Celery handles work distribution.
- PostgreSQL can be scaled vertically or via read replicas.
- Mongo can be sharded for massive write throughput.

