#!/bin/sh
cd hasker

python manage.py migrate --no-input
python manage.py collectstatic --no-input

gunicorn --bind 0.0.0.0:8000 hasker.wsgi & celery -A hasker worker -l INFO