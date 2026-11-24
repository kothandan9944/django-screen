FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_DEBUG=0 \
    DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN DJANGO_SECRET_KEY=collectstatic-build-key python manage.py collectstatic --noinput \
    && mkdir -p /app/data \
    && chown -R app:app /app

USER app

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && gunicorn djangoproject.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --access-logfile -"]
