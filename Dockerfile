# syntax=docker/dockerfile:1
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first so code changes don't bust the pip layer
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Source files carry host permissions (some are owner-only); make them world-readable
RUN chmod -R a+rX /app

# Collect static files at build time so WhiteNoise can serve them
RUN DJANGO_DEBUG=0 python manage.py collectstatic --noinput

# Non-root user; the data dir is owned by it so SQLite can write
RUN useradd --create-home app \
    && mkdir -p /data /app/media \
    && chown -R app:app /data /app/media
USER app

ENV DJANGO_DB_PATH=/data/db.sqlite3 \
    DJANGO_DEBUG=0

VOLUME ["/data"]
EXPOSE 8000

COPY --chmod=755 docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["gunicorn", "nakama.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
