# Quick Start Guide - Django API

## 🚀 Start the API Server

### Windows (Easy Way)
Double-click: `start_django.bat`

### Command Line
```bash
cd backend
DjangoEnv\Scripts\activate
python manage.py runserver 8000
```

## ✅ Verify It's Working

Open browser: http://localhost:8000/api/

You should see the API root with available endpoints.

## 🧪 Test the API

### Quick Test
```bash
# In a new terminal
cd backend
DjangoEnv\Scripts\activate
python test_api.py
```

### Manual Test
```bash
curl http://localhost:8000/api/status/
```

## 📱 Connect from Flutter

Update your Flutter app's API base URL to:
```dart
const String apiBaseUrl = 'http://localhost:8000/api';
```

## 🔧 Common Commands

```bash
# Start server
python manage.py runserver 8000

# Run on different port
python manage.py runserver 8080

# Create admin user
python manage.py createsuperuser

# Check for issues
python manage.py check
```

## 📚 Documentation

- Full API docs: `API_DOCUMENTATION.md`
- Detailed setup: `DJANGO_README.md`

## ⚠️ Troubleshooting

**Server won't start?**
- Make sure Anaconda base is deactivated: `conda deactivate`
- Activate Django environment: `DjangoEnv\Scripts\activate`

**CORS errors?**
- Add your frontend URL to `parking_api/settings.py` in `CORS_ALLOWED_ORIGINS`

**Database errors?**
- Ensure `src/parking.db` exists
- Run the original parking system once to initialize it
