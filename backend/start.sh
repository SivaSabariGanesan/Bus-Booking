#!/bin/bash

# Bus Booking System - Railway Startup Script
set -e

echo "🚀 Starting Bus Booking System on Railway..."

# Get the port from Railway environment variable
PORT=${PORT:-8080}
echo "📡 Using port: $PORT"

# Show environment variables
echo "🔧 Environment variables:"
echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
echo "SECRET_KEY: ${SECRET_KEY:0:10}..."
echo "DEBUG: $DEBUG"
echo "ALLOWED_HOSTS: $ALLOWED_HOSTS"

# Change to backend directory
cd backend

# Test Python and Django
echo "🐍 Testing Python and Django..."
python --version
python -c "import django; print(f'Django version: {django.get_version()}')"

# Run startup test
echo "🧪 Running startup test..."
python test_startup.py

# Run Django configuration check
echo "🔍 Checking Django configuration..."
python manage.py check --settings=transport_booking.settings_production

# Start Gunicorn
echo "🚀 Starting Gunicorn server..."
exec gunicorn transport_booking.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --timeout 120 \
    --worker-class gthread \
    --env DJANGO_SETTINGS_MODULE=transport_booking.settings_production \
    --log-level debug
