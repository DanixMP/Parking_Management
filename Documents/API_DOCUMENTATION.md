# Parking System API Documentation

## Base URL
```
http://localhost:8000/api/
```

## Endpoints

### 1. Get Parking Status
**GET** `/api/status/`

Returns current parking status including capacity, active cars, and pricing.

**Response:**
```json
{
  "capacity": 200,
  "active_cars": 45,
  "free_slots": 155,
  "price_per_hour": 20000
}
```

---

### 2. List All Entries
**GET** `/api/entries/`

Get all vehicle entry records (paginated).

**Response:**
```json
[
  {
    "id": 1,
    "plate": "ABC123",
    "image_in": "path/to/image.jpg",
    "timestamp_in": "2025-11-30T10:30:00Z"
  }
]
```

---

### 3. List All Exits
**GET** `/api/exits/`

Get all vehicle exit records (paginated).

**Response:**
```json
[
  {
    "id": 1,
    "entry": 1,
    "plate": "ABC123",
    "image_out": "path/to/image.jpg",
    "timestamp_out": "2025-11-30T12:30:00Z",
    "duration_minutes": 120,
    "cost": 40000
  }
]
```

---

### 4. List Active Cars
**GET** `/api/active-cars/`

Get all currently parked vehicles.

**Response:**
```json
[
  {
    "entry": 1,
    "plate": "ABC123",
    "timestamp_in": "2025-11-30T10:30:00Z"
  }
]
```

---

### 5. Register Entry
**POST** `/api/entry/`

Register a new vehicle entry.

**Request Body:**
```json
{
  "plate": "ABC123",
  "image_path": "path/to/image.jpg"
}
```

**Response:**
```json
{
  "success": true,
  "entry_id": 1,
  "plate": "ABC123"
}
```

**Error Response (400):**
```json
{
  "error": "Vehicle was recently recorded"
}
```

---

### 6. Register Exit
**POST** `/api/exit/`

Register a vehicle exit and calculate cost.

**Request Body:**
```json
{
  "plate": "ABC123",
  "image_path": "path/to/image.jpg"
}
```

**Response:**
```json
{
  "success": true,
  "entry_id": 1,
  "plate": "ABC123",
  "duration": 120,
  "cost": 40000
}
```

**Error Response (404):**
```json
{
  "error": "Vehicle not found in parking"
}
```

---

### 7. Get/Update Settings
**GET** `/api/settings/`

Get current parking settings.

**Response:**
```json
{
  "capacity": 200,
  "price_per_hour": 20000
}
```

**PUT** `/api/settings/`

Update parking settings.

**Request Body:**
```json
{
  "capacity": 250,
  "price_per_hour": 25000
}
```

**Response:**
```json
{
  "success": true,
  "capacity": 250,
  "price_per_hour": 25000
}
```

---

### 8. Reset Database
**POST** `/api/reset/`

Reset all parking data (entries, exits, active cars).

**Response:**
```json
{
  "success": true,
  "message": "Database reset successfully"
}
```

---

## CORS Configuration

The API allows requests from:
- `http://localhost:3000`
- `http://localhost:8080`
- `http://localhost:5000`

To add more origins, update `CORS_ALLOWED_ORIGINS` in `parking_api/settings.py`.

---

## Running the Server

### Option 1: Using batch file
```bash
start_django.bat
```

### Option 2: Manual
```bash
cd backend
DjangoEnv\Scripts\activate
python manage.py runserver 8000
```

---

## Testing the API

### Using curl:
```bash
# Get status
curl http://localhost:8000/api/status/

# Register entry
curl -X POST http://localhost:8000/api/entry/ \
  -H "Content-Type: application/json" \
  -d "{\"plate\":\"ABC123\",\"image_path\":\"test.jpg\"}"

# Register exit
curl -X POST http://localhost:8000/api/exit/ \
  -H "Content-Type: application/json" \
  -d "{\"plate\":\"ABC123\",\"image_path\":\"test.jpg\"}"
```

### Using Python requests:
```python
import requests

# Get status
response = requests.get('http://localhost:8000/api/status/')
print(response.json())

# Register entry
response = requests.post('http://localhost:8000/api/entry/', 
    json={'plate': 'ABC123', 'image_path': 'test.jpg'})
print(response.json())
```
