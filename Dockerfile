# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=transport_booking.settings_production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements_production.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Change to backend directory
WORKDIR /app/backend

# Run migrations and collect static files
RUN python manage.py migrate --settings=transport_booking.settings_production --noinput
RUN python manage.py collectstatic --settings=transport_booking.settings_production --noinput

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "transport_booking.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--worker-class", "gthread"]
