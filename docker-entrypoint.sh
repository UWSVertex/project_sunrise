#!/bin/sh
set -e

# Apply migrations on every start; they are idempotent
python manage.py migrate --noinput

exec "$@"
