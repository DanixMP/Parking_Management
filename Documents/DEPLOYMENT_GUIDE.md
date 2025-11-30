# Deployment Guide - Parking Management System

## 📋 Overview

This guide covers deploying the Parking Management System for different environments and platforms.

## 🏠 Local Development (Current Setup)

### Backend
```bash
cd backend
DjangoEnv\Scripts\activate
python manage.py runserver 8000
```

### Frontend
```bash
cd frontend/parking
flutter run -d windows
```

## 🌐 Production Deployment

### Option 1: Windows Server Deployment

#### Backend Setup

1. **Install Python 3.11+**
```bash
python --version
```

2. **Create production virtual environment**
```bash
cd backend
python -m venv prod_env
prod_env\Scripts\activate
pip install -r requirements-django.txt
```

3. **Configure Django for production**

Edit `backend/parking_api/settings.py`:
```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'your-server-ip']

# Use PostgreSQL for production (recommended)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'parking_db',
        'USER': 'parking_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

4. **Collect static files**
```bash
python manage.py collectstatic
```

5. **Run with Gunicorn**
```bash
pip install gunicorn
gunicorn parking_api.wsgi:application --bind 0.0.0.0:8000
```

#### Frontend Build

1. **Build Windows executable**
```bash
cd frontend/parking
flutter build windows --release
```
Output: `build/windows/runner/Release/parking.exe`

2. **Create installer (optional)**
Use Inno Setup or NSIS to create Windows installer

### Option 2: Web Deployment

#### Backend on Cloud (Heroku, AWS, DigitalOcean)

**Heroku Example:**

1. **Create Procfile**
```
web: gunicorn parking_api.wsgi --log-file -
```

2. **Create runtime.txt**
```
python-3.11.0
```

3. **Update requirements.txt**
```bash
cd backend
pip freeze > requirements.txt
```

4. **Deploy**
```bash
heroku create parking-system
git push heroku main
heroku run python manage.py migrate
```

#### Frontend as Web App

1. **Build for web**
```bash
cd frontend/parking
flutter build web --release
```

2. **Deploy to hosting**
- **Firebase Hosting**
  ```bash
  firebase init hosting
  firebase deploy
  ```

- **Netlify**
  - Drag and drop `build/web` folder
  - Or use Netlify CLI

- **GitHub Pages**
  ```bash
  # Copy build/web contents to gh-pages branch
  ```

### Option 3: Docker Deployment

#### Backend Dockerfile
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-django.txt .
RUN pip install --no-cache-dir -r requirements-django.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "parking_api.wsgi:application", "--bind", "0.0.0.0:8000"]
```

#### Frontend Dockerfile
```dockerfile
# frontend/parking/Dockerfile
FROM nginx:alpine

COPY build/web /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=sqlite:///db.sqlite3
    volumes:
      - ./backend/src/parking.db:/app/src/parking.db

  frontend:
    build: ./frontend/parking
    ports:
      - "80:80"
    depends_on:
      - backend
```

**Deploy:**
```bash
docker-compose up -d
```

## 📱 Mobile App Deployment

### Android

1. **Configure signing**
Create `android/key.properties`:
```properties
storePassword=your_store_password
keyPassword=your_key_password
keyAlias=your_key_alias
storeFile=path/to/keystore.jks
```

2. **Build APK**
```bash
flutter build apk --release
```

3. **Build App Bundle (for Play Store)**
```bash
flutter build appbundle --release
```

4. **Upload to Google Play Console**

### iOS

1. **Configure signing in Xcode**
```bash
open ios/Runner.xcworkspace
```

2. **Build**
```bash
flutter build ios --release
```

3. **Upload to App Store Connect**

## 🔒 Security Checklist

### Backend Security

- [ ] Set `DEBUG = False` in production
- [ ] Use strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Enable HTTPS/SSL
- [ ] Use environment variables for secrets
- [ ] Set up CORS properly
- [ ] Enable CSRF protection
- [ ] Use secure cookies
- [ ] Implement rate limiting
- [ ] Set up logging
- [ ] Regular security updates

### Frontend Security

- [ ] Use HTTPS for API calls
- [ ] Validate all inputs
- [ ] Sanitize user data
- [ ] Implement proper error handling
- [ ] Don't expose sensitive data
- [ ] Use secure storage for tokens

## 🗄️ Database Migration

### From SQLite to PostgreSQL

1. **Install PostgreSQL**
```bash
pip install psycopg2-binary
```

2. **Update settings.py**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'parking_db',
        'USER': 'parking_user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

3. **Migrate data**
```bash
python manage.py dumpdata > data.json
# Update database settings
python manage.py migrate
python manage.py loaddata data.json
```

## 🔄 Backup Strategy

### Database Backup

**SQLite:**
```bash
# Backup
copy backend\src\parking.db backup\parking_backup_2025-11-30.db

# Restore
copy backup\parking_backup_2025-11-30.db backend\src\parking.db
```

**PostgreSQL:**
```bash
# Backup
pg_dump parking_db > backup_2025-11-30.sql

# Restore
psql parking_db < backup_2025-11-30.sql
```

### Automated Backup Script

```batch
@echo off
REM backup_database.bat
set BACKUP_DIR=D:\Backups\Parking
set DATE=%date:~-4,4%%date:~-10,2%%date:~-7,2%
copy backend\src\parking.db %BACKUP_DIR%\parking_%DATE%.db
echo Backup completed: parking_%DATE%.db
```

Schedule with Windows Task Scheduler for daily backups.

## 📊 Monitoring

### Backend Monitoring

1. **Django Logging**
```python
# settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

2. **Error Tracking**
- Sentry integration
- Email notifications
- Log aggregation

### Performance Monitoring

- Response time tracking
- Database query optimization
- Memory usage monitoring
- API endpoint analytics

## 🔧 Environment Variables

Create `.env` file:
```bash
# Backend
DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost/dbname
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# API
API_BASE_URL=https://api.yourdomain.com

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password
```

Load in Django:
```python
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
```

## 🚀 CI/CD Pipeline

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements-django.txt
    
    - name: Run tests
      run: |
        cd backend
        python manage.py test
    
    - name: Deploy to server
      run: |
        # Your deployment script
```

## 📱 App Store Submission

### Google Play Store

1. Create developer account
2. Prepare store listing
3. Upload APK/AAB
4. Set pricing and distribution
5. Submit for review

### Apple App Store

1. Create App Store Connect account
2. Prepare app metadata
3. Upload build via Xcode
4. Submit for review

## 🔍 Testing in Production

### Smoke Tests
```bash
# Test API endpoints
curl https://your-domain.com/api/status/
curl https://your-domain.com/api/entries/

# Test frontend
# Open browser and verify all features
```

### Load Testing
```bash
# Using Apache Bench
ab -n 1000 -c 10 https://your-domain.com/api/status/

# Using Locust
pip install locust
locust -f load_test.py
```

## 📞 Post-Deployment

### Checklist

- [ ] Verify all endpoints working
- [ ] Test entry/exit registration
- [ ] Check database connections
- [ ] Verify CORS settings
- [ ] Test on different devices
- [ ] Monitor error logs
- [ ] Set up backups
- [ ] Configure monitoring
- [ ] Document deployment
- [ ] Train users

### Maintenance

- Regular security updates
- Database optimization
- Log rotation
- Backup verification
- Performance monitoring
- User feedback collection

## 🆘 Rollback Plan

If deployment fails:

1. **Stop new services**
```bash
docker-compose down
# or
systemctl stop parking-backend
```

2. **Restore database backup**
```bash
copy backup\parking_backup.db backend\src\parking.db
```

3. **Revert to previous version**
```bash
git checkout previous-stable-tag
docker-compose up -d
```

4. **Verify system**
```bash
curl http://localhost:8000/api/status/
```

## 📚 Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Flutter Deployment Guide](https://flutter.dev/docs/deployment)
- [Docker Documentation](https://docs.docker.com/)
- [Nginx Configuration](https://nginx.org/en/docs/)

---

**Last Updated**: November 30, 2025  
**Version**: 1.0.0
