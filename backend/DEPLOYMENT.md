# Bus Booking System - Backend Deployment Guide

## 🚀 Production Deployment Checklist

### 1. Environment Setup

#### Environment Variables
Create a `.env` file in the backend directory:

```bash
# Django Settings
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (for PostgreSQL)
DB_NAME=busbooking
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# CORS Settings
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 2. Database Setup

#### Option A: SQLite (Simple)
- No additional setup required
- Database file: `db.sqlite3`

#### Option B: PostgreSQL (Recommended for Production)
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb busbooking

# Create user
sudo -u postgres createuser your_db_user

# Set password
sudo -u postgres psql
ALTER USER your_db_user WITH PASSWORD 'your_db_password';
GRANT ALL PRIVILEGES ON DATABASE busbooking TO your_db_user;
\q

# Install psycopg2
pip install psycopg2-binary

# Update settings_production.py to use PostgreSQL
```

### 3. Installation Steps

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements_production.txt

# 4. Set environment variables
cp .env.example .env
# Edit .env with your production values

# 5. Run migrations
python manage.py migrate --settings=transport_booking.settings_production

# 6. Create superuser
python manage.py createsuperuser --settings=transport_booking.settings_production

# 7. Collect static files
python manage.py collectstatic --settings=transport_booking.settings_production

# 8. Create logs directory
mkdir logs
```

### 4. Server Configuration

#### Using Gunicorn
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn transport_booking.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

#### Using Nginx (Recommended)
Create `/etc/nginx/sites-available/busbooking`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /path/to/your/backend;
    }

    location /media/ {
        root /path/to/your/backend;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/busbooking.sock;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/busbooking /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl reload nginx
```

#### Systemd Service
Create `/etc/systemd/system/busbooking.service`:

```ini
[Unit]
Description=Bus Booking System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/backend
Environment="PATH=/path/to/your/backend/venv/bin"
ExecStart=/path/to/your/backend/venv/bin/gunicorn --workers 3 --bind unix:/run/busbooking.sock transport_booking.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

Start the service:
```bash
sudo systemctl start busbooking
sudo systemctl enable busbooking
```

### 5. Security Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Enable HTTPS (SSL/TLS)
- [ ] Set up proper CORS origins
- [ ] Configure email settings
- [ ] Set up database with strong passwords
- [ ] Enable security headers
- [ ] Set up logging
- [ ] Configure backup strategy

### 6. Monitoring and Maintenance

#### Logs
- Application logs: `logs/django.log`
- Nginx logs: `/var/log/nginx/`
- System logs: `journalctl -u busbooking`

#### Backup
```bash
# Database backup
python manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json

# PostgreSQL backup
pg_dump busbooking > backup_$(date +%Y%m%d_%H%M%S).sql
```

#### Updates
```bash
# Pull latest code
git pull origin main

# Install new dependencies
pip install -r requirements_production.txt

# Run migrations
python manage.py migrate --settings=transport_booking.settings_production

# Collect static files
python manage.py collectstatic --settings=transport_booking.settings_production

# Restart service
sudo systemctl restart busbooking
```

### 7. Performance Optimization

- Enable database connection pooling
- Configure caching (Redis/Memcached)
- Optimize static files with CDN
- Enable compression
- Monitor database queries
- Set up load balancing if needed

### 8. Troubleshooting

#### Common Issues
1. **Permission errors**: Check file permissions and ownership
2. **Database connection**: Verify database credentials and connectivity
3. **Static files not loading**: Run `collectstatic` and check nginx configuration
4. **Email not sending**: Verify SMTP settings and credentials
5. **CORS errors**: Check `CORS_ALLOWED_ORIGINS` configuration

#### Health Check
```bash
# Check if service is running
sudo systemctl status busbooking

# Check logs
sudo journalctl -u busbooking -f

# Test database connection
python manage.py dbshell --settings=transport_booking.settings_production
```

### 9. SSL/HTTPS Setup (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🎯 Quick Deployment Script

Create `deploy.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Starting deployment..."

# Pull latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements_production.txt

# Run migrations
python manage.py migrate --settings=transport_booking.settings_production

# Collect static files
python manage.py collectstatic --settings=transport_booking.settings_production --noinput

# Restart service
sudo systemctl restart busbooking

echo "✅ Deployment completed successfully!"
```

Make it executable:
```bash
chmod +x deploy.sh
```

## 📞 Support

For deployment issues:
1. Check the logs: `sudo journalctl -u busbooking -f`
2. Verify configuration files
3. Test database connectivity
4. Check nginx configuration: `sudo nginx -t`

---

**Remember**: Always test in a staging environment before deploying to production!
