# Railway Deployment Troubleshooting Guide

## 🚨 Current Issue: Health Check Failing

The `/health/` endpoint is returning "service unavailable", indicating the Django application isn't starting properly.

## 🔧 Debugging Steps Applied

### 1. **Simplified Startup Command**
Changed from complex Gunicorn setup to simple Django development server:
```bash
cd backend && python manage.py runserver 0.0.0.0:8080 --settings=transport_booking.settings_production
```

### 2. **Enhanced Debugging Script**
Created `backend/test_startup.py` to test Django components individually.

### 3. **Improved Startup Script**
Updated `backend/start.sh` with comprehensive logging and environment variable display.

## 📋 Required Environment Variables

Make sure these are set in Railway:

```
DJANGO_SETTINGS_MODULE=transport_booking.settings_production
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-railway-domain.railway.app
```

## 🔍 Common Issues & Solutions

### Issue 1: Database Connection
**Symptoms**: App fails to start, database errors in logs
**Solution**: 
- Check if `DATABASE_URL` is set in Railway
- Verify database service is running
- Check database credentials

### Issue 2: Missing Dependencies
**Symptoms**: Import errors, module not found
**Solution**:
- Verify all packages in `requirements_production.txt` are installed
- Check if `dj-database-url` is included

### Issue 3: Static Files
**Symptoms**: Static file errors, collectstatic failures
**Solution**:
- Ensure `collectstatic` runs during build
- Check `STATIC_ROOT` configuration

### Issue 4: Environment Variables
**Symptoms**: Configuration errors, missing settings
**Solution**:
- Verify all required environment variables are set
- Check variable names and values

## 🧪 Testing Commands

### Test Django Configuration
```bash
cd backend
python manage.py check --settings=transport_booking.settings_production
```

### Test Database Connection
```bash
cd backend
python manage.py dbshell --settings=transport_booking.settings_production
```

### Test Startup Script
```bash
cd backend
python test_startup.py
```

## 🚀 Alternative Startup Commands

### Option 1: Development Server (Current)
```bash
cd backend && python manage.py runserver 0.0.0.0:8080 --settings=transport_booking.settings_production
```

### Option 2: Gunicorn with Debug
```bash
cd backend && gunicorn transport_booking.wsgi:application --bind 0.0.0.0:8080 --workers 1 --log-level debug
```

### Option 3: Custom Startup Script
```bash
chmod +x backend/start.sh && backend/start.sh
```

## 📊 Next Steps

1. **Deploy with simplified command** (current setup)
2. **Check Railway logs** for specific error messages
3. **Verify environment variables** are properly set
4. **Test database connectivity** if using external database
5. **Check static files** are being collected properly

## 🔧 Quick Fixes to Try

### Fix 1: Enable Debug Mode Temporarily
Set `DEBUG=True` in environment variables to see detailed error pages.

### Fix 2: Use SQLite Database
Ensure the app can start with SQLite before configuring external database.

### Fix 3: Check File Permissions
Make sure all files have proper read permissions.

### Fix 4: Verify Python Path
Ensure Python can find all Django modules and apps.

## 📞 Getting Help

If issues persist:
1. Check Railway deployment logs
2. Run local tests with production settings
3. Verify all configuration files are correct
4. Test with minimal Django setup first
