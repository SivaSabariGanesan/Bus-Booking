#!/bin/bash

# Bus Booking System - Railway Startup Script
set -e

echo "🚀 Starting Bus Booking System on Railway..."

# Get the port from Railway environment variable
PORT=${PORT:-8080}
echo "📡 Using port: $PORT"

# Change to backend directory
cd backend

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
    --env DJANGO_SETTINGS_MODULE=transport_booking.settings_production
