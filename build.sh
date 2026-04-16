#!/bin/bash
# build.sh — run during Vercel build phase
set -e

pip install -r requirements.txt
python manage.py migrate --no-input
python manage.py collectstatic --no-input
