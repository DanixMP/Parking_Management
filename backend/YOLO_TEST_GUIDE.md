# YOLO Integration Testing Guide

Complete guide to test the YOLO license plate detection system integrated with Django.

## Prerequisites

### 1. Model Files
Ensure these files exist in `backend/src/`:
- ✓ `plateYolo.pt` - Plate detection model
- ✓ `CharsYolo.pt` - Character recognition model

### 2. Python Environment
Activate the Django virtual environment:
```bash
cd backend
call DjangoEnv\Scripts\activate.bat
```

### 3. Install Dependencies
```bash
pip install torch opencv-python numpy yolov5
pip install django djangorestframework django-cors-headers
```

Or install from requirements:
```bash
pip install -r requirements-django.txt
pip install torch opencv-python numpy yolov5
```

## Testing Steps

### Step 1: Test Model Loading
Run the integration test to verify everything is set up correctly:

```bash
cd backend
python test_yolo_integration.py
```

This will check:
- ✓ Model files exist
- ✓ Dependencies installed
- ✓ Models can be loaded
- ✓ Django configuration
- ✓ API endpoints registered

### Step 2: Start Django Server
```bash
cd backend
python manage.py runserver 8000
```

The server should start on `http://localhost:8000`

### Step 3: Test API Endpoints

#### Option A: Test with Python Script
```bash
# In a new terminal
cd backend
python test_api_with_image.py path/to/your/plate_image.jpg
```

#### Option B: Test with cURL
```bash
# Test plate detection
curl -X POST http://localhost:8000/api/detect-plate/ \
  -F "image=@path/to/plate_image.jpg"

# Test entry registration
curl -X POST http://localhost:8000/api/detect-entry/ \
  -F "image=@path/to/plate_image.jpg"

# Test parking status
curl http://localhost:8000/api/status/
```

#### Option C: Test with Postman
1. Open Postman
2. Create POST request to `http://localhost:8000/api/detect-plate/`
3. In Body tab, select "form-data"
4. Add key "image" with type "File"
5. Select your plate image
6. Send request

## API Endpoints

### 1. Detect Plate Only
**Endpoint:** `POST /api/detect-plate/`
**Body:** `multipart/form-data` with `image` file
**Response:**
```json
{
  "success": true,
  "plate": "12ب345-67",
  "confidence": 0.95,
  "bbox": {"x1": 100, "y1": 50, "x2": 300, "y2": 150}
}
```

### 2. Detect and Register Entry
**Endpoint:** `POST /api/detect-entry/`
**Body:** `multipart/form-data` with `image` file
**Response:**
```json
{
  "success": true,
  "plate": "12ب345-67",
  "entry_id": 123,
  "confidence": 0.95
}
```

### 3. Detect and Register Exit
**Endpoint:** `POST /api/detect-exit/`
**Body:** `multipart/form-data` with `image` file
**Response:**
```json
{
  "success": true,
  "plate": "12ب345-67",
  "entry_id": 123,
  "duration": 120,
  "cost": 40000,
  "confidence": 0.95
}
```

### 4. Get Parking Status
**Endpoint:** `GET /api/status/`
**Response:**
```json
{
  "capacity": 100,
  "active_cars": 45,
  "free_slots": 55,
  "price_per_hour": 20000
}
```

## Testing Workflow

### Complete Entry-Exit Test

1. **Check initial status:**
```bash
curl http://localhost:8000/api/status/
```

2. **Register entry with plate detection:**
```bash
curl -X POST http://localhost:8000/api/detect-entry/ \
  -F "image=@test_plate.jpg"
```
Note the `entry_id` from response.

3. **Check status again (should show +1 active car):**
```bash
curl http://localhost:8000/api/status/
```

4. **Register exit with same plate:**
```bash
curl -X POST http://localhost:8000/api/detect-exit/ \
  -F "image=@test_plate.jpg"
```
Should return duration and cost.

5. **Verify status (active cars should decrease):**
```bash
curl http://localhost:8000/api/status/
```

## Troubleshooting

### Models Not Loading
**Error:** `Model file not found`
**Solution:** Ensure `plateYolo.pt` and `CharsYolo.pt` are in `backend/src/`

### Import Errors
**Error:** `No module named 'yolov5'`
**Solution:** 
```bash
pip install yolov5
```

### CUDA Errors
**Error:** CUDA-related errors
**Solution:** Models will automatically fall back to CPU. For GPU:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### No Plate Detected
**Error:** `No plate detected in image`
**Solutions:**
- Ensure image contains a visible license plate
- Check image quality and lighting
- Try different images
- Verify model files are correct

### Character Recognition Fails
**Error:** `Could not recognize plate characters`
**Solutions:**
- Check if plate region is clear in image
- Adjust confidence threshold in `yolo_service.py`
- Verify character model mapping matches your model's training

### Server Connection Failed
**Error:** `Could not connect to server`
**Solution:** Ensure Django server is running:
```bash
cd backend
python manage.py runserver 8000
```

## Performance Tips

1. **First Request is Slow:** Models load on first request (5-10 seconds). Subsequent requests are fast.

2. **Use GPU:** If available, models automatically use CUDA for faster processing.

3. **Image Size:** Smaller images process faster. Recommended: 640x480 or similar.

4. **Batch Processing:** For multiple images, send requests in parallel.

## Integration with Flutter App

The Flutter app can now use these endpoints:

```dart
// In your Flutter service
Future<String?> detectPlate(File imageFile) async {
  var request = http.MultipartRequest(
    'POST',
    Uri.parse('http://YOUR_IP:8000/api/detect-plate/'),
  );
  
  request.files.add(
    await http.MultipartFile.fromPath('image', imageFile.path),
  );
  
  var response = await request.send();
  var responseData = await response.stream.bytesToString();
  var jsonData = json.decode(responseData);
  
  if (jsonData['success']) {
    return jsonData['plate'];
  }
  return null;
}
```

## Next Steps

1. ✓ Test all endpoints with sample images
2. ✓ Verify entry/exit workflow
3. ✓ Integrate with Flutter app
4. ✓ Test end-to-end system
5. ✓ Deploy to production server

## Support

For issues or questions:
1. Check the error messages in Django console
2. Review the test output from `test_yolo_integration.py`
3. Verify all dependencies are installed
4. Check model files are present and valid
