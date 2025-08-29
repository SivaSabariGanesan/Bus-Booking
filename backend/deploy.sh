#!/bin/bash

# Bus Booking System - Production Deployment Script
set -e

echo "🚀 Starting Bus Booking System deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found. Please create it first:"
    echo "python -m venv venv"
    echo "source venv/bin/activate"
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
print_status "Installing production dependencies..."
pip install -r requirements_production.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Please create it with your production settings."
    echo "See DEPLOYMENT.md for required environment variables."
fi

# Run database migrations
print_status "Running database migrations..."
python manage.py migrate --settings=transport_booking.settings_production

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --settings=transport_booking.settings_production --noinput

# Create logs directory if it doesn't exist
if [ ! -d "logs" ]; then
    print_status "Creating logs directory..."
    mkdir logs
fi

# Check if logs directory is writable
if [ ! -w "logs" ]; then
    print_warning "Logs directory is not writable. Please check permissions."
fi

# Test the application
print_status "Testing application..."
python manage.py check --settings=transport_booking.settings_production

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    print_status "Installing gunicorn..."
    pip install gunicorn
fi

print_status "Deployment completed successfully! 🎉"

echo ""
echo "Next steps:"
echo "1. Configure your web server (nginx/apache)"
echo "2. Set up systemd service (see DEPLOYMENT.md)"
echo "3. Configure SSL/HTTPS"
echo "4. Set up monitoring and backups"
echo ""
echo "To run the application:"
echo "gunicorn transport_booking.wsgi:application --bind 0.0.0.0:8000 --workers 3"
echo ""
echo "For detailed instructions, see DEPLOYMENT.md"
