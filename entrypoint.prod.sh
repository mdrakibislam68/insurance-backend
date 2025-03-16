#!/bin/sh

python manage.py migrate
python manage.py collectstatic --no-input
gunicorn backend.wsgi:application --bind 0.0.0.0:8000  --timeout 120 --workers=3 --threads=3 --worker-connections=1000