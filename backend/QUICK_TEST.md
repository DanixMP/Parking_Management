# Quick YOLO Test Guide

## 🚀 Quick Start (3 Steps)

### 1. Run Tests
```bash
cd backend
test_yolo_system.bat
```

### 2. Start Server
```bash
cd backend
call DjangoEnv\Scripts\activate.bat
python manage.py runserver 8000
```

### 3. Test Detection
```bash
# In new terminal
cd backend
python test_api_with_image.py path\to\plate_image.jpg
```

## 📋 Quick API Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/detect-plate/` | POST | Detect plate only |
| `/api/detect-entry/` | POST | Detect & register entry |
| `/api/detect-exit/` | POST | Detect & register exit |
| `/api/status/` | GET | Get parking status |

## 🧪 Test Commands

### Test with cURL
```bash
# Detect plate
curl -X POST http://localhost:8000/api/detect-plate/ -F "image=@test.jpg"

# Register entry
curl -X POST http://localhost:8000/api/detect-entry/ -F "image=@test.jpg"

# Check status
curl http://localhost:8000/api/status/
```

### Test with Python
```bash
python test_api_with_image.py test_plate.jpg
```

## ✅ Expected Results

### Successful Detection
```json
{
  "success": true,
  "plate": "12ب345-67",
  "confidence": 0.95
}
```

### Entry Registered
```json
{
  "success": true,
  "plate": "12ب345-67",
  "entry_id": 123,
  "confidence": 0.95
}
```

### Exit Registered
```json
{
  "success": true,
  "plate": "12ب345-67",
  "duration": 120,
  "cost": 40000
}
```

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Models not found | Check `backend/src/plateYolo.pt` and `CharsYolo.pt` exist |
| Import errors | Run `pip install yolov5 torch opencv-python` |
| Server won't start | Activate venv: `call DjangoEnv\Scripts\activate.bat` |
| No plate detected | Use clear image with visible plate |

## 📱 Flutter Integration

Update your Flutter app's API base URL:
```dart
static const String baseUrl = 'http://YOUR_IP:8000/api';
```

Then use the detection endpoints as shown in the guide.

## 📚 Full Documentation

See `YOLO_TEST_GUIDE.md` for complete documentation.
