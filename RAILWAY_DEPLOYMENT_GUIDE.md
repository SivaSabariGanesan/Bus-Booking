# Railway Deployment Guide

## 🚀 Current Railway Configuration

### Build Command (Recommended)
```bash
pip install -r backend/requirements_production.txt && python backend/manage.py collectstatic --settings=transport_booking.settings_production --noinput
```

### Start Command (Current)
```bash
cd backend && gunicorn transport_booking.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120 --worker-class gthread --env DJANGO_SETTINGS_MODULE=transport_booking.settings_production
```

## ⚠️ Important Notes

### Why Remove Migrations from Build Command

**Current Build Command (Has Issues):**
```bash
cd backend ; pip install -r requirements_production.txt && python manage.py migrate --settings=transport_booking.settings_production && python manage.py collectstatic --settings=transport_booking.settings_production --noinput
```

**Problems:**
1. **Database Not Available**: During build phase, the database might not be accessible
2. **Build Failures**: If migrations fail, the entire build fails
3. **Race Conditions**: Multiple deployments could conflict

**Recommended Build Command:**
```bash
pip install -r backend/requirements_production.txt && python backend/manage.py collectstatic --settings=transport_booking.settings_production --noinput
```

### Migration Strategy

**Option 1: Pre-Deploy Hook (Recommended)**
- Use Railway's pre-deploy feature to run migrations
- Migrations run after build but before start
- More reliable and safer

**Option 2: Start Command with Migrations**
```bash
cd backend && python manage.py migrate --settings=transport_booking.settings_production --noinput && gunicorn transport_booking.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120 --worker-class gthread --env DJANGO_SETTINGS_MODULE=transport_booking.settings_production
```

## 🔧 Environment Variables

Make sure these are set in Railway:

```
DJANGO_SETTINGS_MODULE=transport_booking.settings_production
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-railway-domain.railway.app
```

## 📋 Deployment Checklist

- [ ] Build command excludes migrations
- [ ] Start command includes migrations (if not using pre-deploy)
- [ ] Environment variables are set
- [ ] Database is configured
- [ ] Static files are collected during build
- [ ] Health check endpoint is accessible

## 🚨 Troubleshooting

### Common Issues

1. **Build Fails on Migrations**
   - Remove migrations from build command
   - Use pre-deploy or start command for migrations

2. **Static Files Not Found**
   - Ensure collectstatic runs during build
   - Check STATIC_ROOT in settings

3. **Database Connection Issues**
   - Verify database environment variables
   - Check if database service is running

4. **Port Issues**
   - Use $PORT environment variable
   - Don't hardcode port numbers

## 🎯 Recommended Final Configuration

### Build Command
```bash
pip install -r backend/requirements_production.txt && python backend/manage.py collectstatic --settings=transport_booking.settings_production --noinput
```

### Start Command
```bash
cd backend && python manage.py migrate --settings=transport_booking.settings_production --noinput && gunicorn transport_booking.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120 --worker-class gthread --env DJANGO_SETTINGS_MODULE=transport_booking.settings_production
```

This ensures:
- ✅ Dependencies installed during build
- ✅ Static files collected during build
- ✅ Migrations run before app starts
- ✅ App starts with proper configuration

