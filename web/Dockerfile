FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./* /app

# collectstatic could be added for production if staticfiles used
CMD ["gunicorn", "subscribe_service.wsgi:application", "--bind", "0.0.0.0:8000"]
