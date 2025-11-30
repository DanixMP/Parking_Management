# 🧪 YOLO System Testing Checklist

## Pre-Testing Verification

### ✅ System Components
- [x] Django server running on port 8000
- [x] YOLO models loaded (plateYolo.pt + CharsYolo.pt)
- [x] Database initialized
- [x] All dependencies installed
- [x] API endpoints registered

### ✅ Files Present
- [x] `backend/src/plateYolo.pt` (13.71 MB)
- [x] `backend/src/CharsYolo.pt` (13.88 MB)
- [x] `backend/src/parking.db` (initialized)
- [x] All test scripts created
- [x] Documentation complete

## Quick Tests

### 1. Server Status Test
```bash
curl http://localhost:8000/api/status/
```

**Expected Result:**
```json
{
  "capacity": 200,
  "active_cars": 0,
  "free_slots": 200,
  "price_per_hour": 20000
}
```

**Status**: ✅ PASSED

### 2. Integration Test
```bash
cd backend
python test_yolo_integration.py
```

**Expected Results:**
- ✅ Model files found
- ✅ Dependencies installed
- ✅ Models load successfully
- ✅ Django configured
- ✅ Endpoints registered

**Status**: ✅ PASSED

### 3. Quick System Test
```bash
TEST_YOLO_NOW.bat
```

**Expected Results:**
- ✅ Server responding
- ✅ Status endpoint working
- ✅ Endpoints listed
- ✅ Usage examples shown

**Status**: ✅ PASSED

## Image-Based Tests (Requires License Plate Images)

### Test 1: Plate Detection Only
```bash
curl -X POST http://localhost:8000/api/detect-plate/ \
  -F "image=@path/to/plate_image.jpg"
```

**Expected Response:**
```json
{
  "success": true,
  "plate": "12ب345-67",
  "confidence": 0.85,
  "bbox": {"x1": 100, "y1": 50, "x2": 300, "y2": 150}
}
```

**Status**: ⏳ PENDING (Needs test image)

### Test 2: Entry Registration with Detection
```bash
curl -X POST http://localhost:8000/api/detect-entry/ \
  -F "image=@path/to/plate_image.jpg"
```

**Expected Response:**
```json
{
  "success": true,
  "plate": "12ب345-67",
  "entry_id": 1,
  "confidence": 0.85
}
```

**Status**: ⏳ PENDING (Needs test image)

### Test 3: Exit Registration with Detection
```bash
curl -X POST http://localhost:8000/api/detect-exit/ \
  -F "image=@path/to/plate_image.jpg"
```

**Expected Response:**
```json
{
  "success": true,
  "plate": "12ب345-67",
  "entry_id": 1,
  "duration": 120,
  "cost": 40000,
  "confidence": 0.85
}
```

**Status**: ⏳ PENDING (Needs test image)

### Test 4: Complete Entry-Exit Workflow

**Step 1**: Check initial status
```bash
curl http://localhost:8000/api/status/
# Expected: active_cars: 0
```

**Step 2**: Register entry
```bash
curl -X POST http://localhost:8000/api/detect-entry/ \
  -F "image=@plate1.jpg"
# Expected: entry_id returned
```

**Step 3**: Verify entry
```bash
curl http://localhost:8000/api/status/
# Expected: active_cars: 1
```

**Step 4**: Register exit
```bash
curl -X POST http://localhost:8000/api/detect-exit/ \
  -F "image=@plate1.jpg"
# Expected: cost calculated
```

**Step 5**: Verify exit
```bash
curl http://localhost:8000/api/status/
# Expected: active_cars: 0
```

**Status**: ⏳ PENDING (Needs test images)

## Python Test Script

### Using test_api_with_image.py
```bash
cd backend
python test_api_with_image.py path/to/plate_image.jpg
```

**This will test:**
- ✅ Parking status
- ✅ Plate detection
- ✅ Entry registration
- ✅ Instructions for exit testing

**Status**: ⏳ PENDING (Needs test image)

## Flutter Integration Tests

### Test 1: API Connection
```dart
// Test if Flutter can reach the API
final response = await http.get(
  Uri.parse('http://YOUR_IP:8000/api/status/')
);
```

**Expected**: Status 200, JSON response

**Status**: ⏳ PENDING (Needs Flutter app update)

### Test 2: Image Upload
```dart
// Test image upload from Flutter
var request = http.MultipartRequest(
  'POST',
  Uri.parse('http://YOUR_IP:8000/api/detect-plate/'),
);
request.files.add(
  await http.MultipartFile.fromPath('image', imagePath),
);
var response = await request.send();
```

**Expected**: Plate detection result

**Status**: ⏳ PENDING (Needs Flutter app update)

## Performance Tests

### Test 1: First Request (Cold Start)
- **Expected**: 5-10 seconds (model loading)
- **Status**: ⏳ PENDING

### Test 2: Subsequent Requests
- **Expected**: < 1 second
- **Status**: ⏳ PENDING

### Test 3: Concurrent Requests
- **Test**: Send 5 requests simultaneously
- **Expected**: All complete within 5 seconds
- **Status**: ⏳ PENDING

## Error Handling Tests

### Test 1: Invalid Image Format
```bash
curl -X POST http://localhost:8000/api/detect-plate/ \
  -F "image=@invalid.txt"
```

**Expected**: Error message about invalid format

**Status**: ⏳ PENDING

### Test 2: No Plate in Image
```bash
curl -X POST http://localhost:8000/api/detect-plate/ \
  -F "image=@no_plate.jpg"
```

**Expected**: "No plate detected in image"

**Status**: ⏳ PENDING

### Test 3: Exit Without Entry
```bash
curl -X POST http://localhost:8000/api/detect-exit/ \
  -F "image=@unknown_plate.jpg"
```

**Expected**: "Vehicle not found in parking"

**Status**: ⏳ PENDING

### Test 4: Duplicate Entry
```bash
# Register same plate twice within cooldown period
curl -X POST http://localhost:8000/api/detect-entry/ \
  -F "image=@plate.jpg"
curl -X POST http://localhost:8000/api/detect-entry/ \
  -F "image=@plate.jpg"
```

**Expected**: "Vehicle was recently recorded"

**Status**: ⏳ PENDING

## Character Recognition Tests

### Test 1: Iraqi Plate Format
- **Format**: XX-YYYY-ZZ (where X=letter, Y=number, Z=number)
- **Example**: ب-1234-56
- **Status**: ⏳ PENDING

### Test 2: Different Lighting Conditions
- **Bright**: ⏳ PENDING
- **Dark**: ⏳ PENDING
- **Shadow**: ⏳ PENDING
- **Night**: ⏳ PENDING

### Test 3: Different Angles
- **Front**: ⏳ PENDING
- **Slight angle**: ⏳ PENDING
- **Side angle**: ⏳ PENDING

### Test 4: Different Distances
- **Close**: ⏳ PENDING
- **Medium**: ⏳ PENDING
- **Far**: ⏳ PENDING

## Accuracy Tests

### Plate Detection Accuracy
- **Test**: 100 images with plates
- **Target**: > 90% detection rate
- **Status**: ⏳ PENDING

### Character Recognition Accuracy
- **Test**: 100 detected plates
- **Target**: > 85% correct recognition
- **Status**: ⏳ PENDING

### End-to-End Accuracy
- **Test**: 100 complete workflows
- **Target**: > 80% fully correct
- **Status**: ⏳ PENDING

## Load Tests

### Test 1: Single User
- **Requests**: 100 sequential
- **Expected**: All successful
- **Status**: ⏳ PENDING

### Test 2: Multiple Users
- **Users**: 10 concurrent
- **Requests**: 10 each
- **Expected**: All successful
- **Status**: ⏳ PENDING

### Test 3: Peak Load
- **Users**: 50 concurrent
- **Duration**: 5 minutes
- **Expected**: < 5% error rate
- **Status**: ⏳ PENDING

## Database Tests

### Test 1: Entry Storage
- **Test**: Register 100 entries
- **Verify**: All stored correctly
- **Status**: ⏳ PENDING

### Test 2: Exit Calculation
- **Test**: Register 100 exits
- **Verify**: All costs calculated correctly
- **Status**: ⏳ PENDING

### Test 3: Active Cars Tracking
- **Test**: Mixed entry/exit operations
- **Verify**: Count always accurate
- **Status**: ⏳ PENDING

## Security Tests

### Test 1: SQL Injection
- **Test**: Malicious plate strings
- **Expected**: Properly escaped
- **Status**: ⏳ PENDING

### Test 2: File Upload Limits
- **Test**: Upload very large file
- **Expected**: Rejected with error
- **Status**: ⏳ PENDING

### Test 3: CORS
- **Test**: Request from unauthorized origin
- **Expected**: Blocked
- **Status**: ⏳ PENDING

## Documentation Tests

### Checklist
- [x] README.md updated
- [x] API documentation complete
- [x] Testing guides created
- [x] Troubleshooting included
- [x] Examples provided
- [x] Flutter integration guide
- [x] Deployment guide

## Summary

### ✅ Completed Tests (3/3)
1. ✅ Server status test
2. ✅ Integration test
3. ✅ Quick system test

### ⏳ Pending Tests (Require Images)
1. ⏳ Plate detection
2. ⏳ Entry registration
3. ⏳ Exit registration
4. ⏳ Complete workflow
5. ⏳ Error handling
6. ⏳ Character recognition
7. ⏳ Accuracy tests
8. ⏳ Performance tests
9. ⏳ Load tests
10. ⏳ Flutter integration

### 🎯 Next Steps
1. **Obtain test images** of Iraqi license plates
2. **Run image-based tests** using test scripts
3. **Measure accuracy** and performance
4. **Integrate with Flutter** app
5. **Conduct end-to-end** testing
6. **Optimize** based on results
7. **Deploy** to production

## Test Image Requirements

### Minimum Test Set
- 10 clear plate images (different plates)
- 5 challenging images (angle, lighting, distance)
- 3 invalid images (no plate, wrong format)

### Ideal Test Set
- 100+ Iraqi license plate images
- Various lighting conditions
- Various angles and distances
- Different plate types/formats
- Edge cases and challenges

## Testing Tools Available

1. ✅ `TEST_YOLO_NOW.bat` - Quick system test
2. ✅ `backend/test_yolo_integration.py` - Integration test
3. ✅ `backend/test_api_with_image.py` - Image-based API test
4. ✅ `backend/test_yolo_system.bat` - Batch test runner
5. ✅ cURL commands - Manual API testing
6. ✅ Postman collection - API testing (can be created)

## Status Summary

**System Status**: ✅ OPERATIONAL
**Basic Tests**: ✅ 3/3 PASSED
**Image Tests**: ⏳ PENDING (Need test images)
**Integration**: ⏳ PENDING (Need Flutter update)
**Production Ready**: ⏳ PENDING (Need full testing)

**Overall Progress**: 30% Complete
**Blocking Issue**: Need Iraqi license plate test images
**Next Action**: Obtain test images and run image-based tests

---

**Last Updated**: November 30, 2025
**Test Status**: System operational, awaiting test images
**Documentation**: Complete
**Tools**: Ready
