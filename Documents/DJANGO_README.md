# Django API Backend for Parking System

## Overview
This Django REST API provides endpoints for the parking management system, allowing the Flutter frontend to interact with the parking database.

## Project Structure
```
backend/
├── DjangoEnv/              # Virtual environment
├── parking_api/            # Django project settings
│   ├── settings.py         # Main configuration
│   ├── urls.py            # URL routing
│   └── wsgi.py            # WSGI config
├── api/                    # API application
│   ├── models.py          # Database models
│   ├── serializers.py     # REST serializers
│   ├── views.py           # API views/endpoints
│   └── urls.py            # API URL routing
├── src/                    # Original parking system code
│   ├── database.py        # Database functions
│   └── parking.db         # SQLite database
├── manage.py              # Django management script
├── start_django.bat       # Quick start script
└── requirements-django.txt # Python dependencies
```

## Setup Instructions

### 1. Activate Virtual Environment
```bash
cd backend
DjangoEnv\Scripts\activate
```

### 2. Install Dependencies (if needed)
```bash
pip install -r requirements-django.txt
```

### 3. Run Migrations
```bash
python manage.py migrate
```

### 4. Start the Server
```bash
python manage.py runserver 8000
```

Or simply double-click `start_django.bat`

## API Endpoints

### Status & Information
- `GET /api/status/` - Get parking status (capacity, active cars, free slots)
- `GET /api/settings/` - Get parking settings
- `PUT /api/settings/` - Update parking settings

### Vehicle Management
- `POST /api/entry/` - Register vehicle entry
- `POST /api/exit/` - Register vehicle exit
- `GET /api/active-cars/` - List currently parked vehicles

### Records
- `GET /api/entries/` - List all entry records
- `GET /api/exits/` - List all exit records

### Administration
- `POST /api/reset/` - Reset all parking data

See `API_DOCUMENTATION.md` for detailed endpoint documentation.

## Testing the API

### Option 1: Using the test script
```bash
# In a separate terminal (with Django server running)
python test_api.py
```

### Option 2: Using curl
```bash
curl http://localhost:8000/api/status/
```

### Option 3: Using browser
Navigate to: `http://localhost:8000/api/`

## Configuration

### CORS Settings
The API allows requests from:
- http://localhost:3000
- http://localhost:8080
- http://localhost:5000

To add more origins, edit `parking_api/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://your-frontend-url:port",
]
```

### Database
The API uses the existing SQLite database at `src/parking.db`. No migration needed for parking tables as they're managed externally.

## Integration with Flutter

### Example Flutter HTTP Request
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<Map<String, dynamic>> getParkingStatus() async {
  final response = await http.get(
    Uri.parse('http://localhost:8000/api/status/'),
  );
  
  if (response.statusCode == 200) {
    return json.decode(response.body);
  } else {
    throw Exception('Failed to load parking status');
  }
}
```

## Troubleshooting

### Port Already in Use
If port 8000 is busy, run on a different port:
```bash
python manage.py runserver 8080
```

### CORS Errors
Make sure your frontend URL is added to `CORS_ALLOWED_ORIGINS` in settings.py

### Database Not Found
Ensure `src/parking.db` exists. Run the original parking system once to create it.

## Development

### Creating a Superuser (for Django Admin)
```bash
python manage.py createsuperuser
```

Then access admin panel at: `http://localhost:8000/admin/`

### Adding New Endpoints
1. Add view function in `api/views.py`
2. Add URL pattern in `api/urls.py`
3. Update API documentation

## Notes
- The API uses the existing database functions from `src/database.py`
- Models are set to `managed = False` to prevent Django from modifying existing tables
- All timestamps are in ISO 8601 format
- Costs are in the original currency units (no conversion)
