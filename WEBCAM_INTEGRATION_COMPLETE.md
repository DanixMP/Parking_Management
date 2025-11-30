# 📷 Webcam Integration - Complete Guide

## ✅ What's Been Implemented

### 1. Camera Service
- **File**: `frontend/parking/lib/services/camera_service.dart`
- Single webcam with mode toggle
- Entry/Exit mode switching
- Detection statistics tracking
- Image capture functionality

### 2. API Service Updates
- **File**: `frontend/parking/lib/services/api_service.dart`
- `detectPlateEntry()` - YOLO entry detection
- `detectPlateExit()` - YOLO exit detection
- `detectPlateOnly()` - Test detection

### 3. Home Screen Integration
- **File**: `frontend/parking/lib/screens/home_screen.dart`
- Live camera preview (300px height)
- Mode toggle switch (Entry/Exit)
- Auto-detection every 3 seconds
- Real-time statistics
- Detection notifications

### 4. Main App Setup
- **File**: `frontend/parking/lib/main.dart`
- Camera service initialization
- Multi-provider setup

## 🎯 Features

### Mode Toggle Switch
```
[ورود] [خروج]  ← Click to switch modes
```
- **Green** when Entry mode active
- **Red** when Exit mode active
- Instant mode switching
- No camera restart needed

### Live Camera Feed
- Full webcam preview
- 300px height display
- YOLO AI overlay indicator
- Detection status overlay
- Responsive layout

### Auto-Detection
- Captures frame every 3 seconds
- Sends to YOLO API
- Auto-registers entry/exit
- Shows notifications
- Updates statistics

### Statistics Display
- Last detected plate
- Confidence percentage
- Daily count (entry/exit separate)
- Real-time updates

## 📦 Installation Steps

### Step 1: Install Camera Package
```bash
cd frontend/parking
flutter pub get
```

This will install the `camera: ^0.10.5+5` package that was added to pubspec.yaml.

### Step 2: Run the App
```bash
flutter run -d windows
```

### Step 3: Grant Camera Permission
- Windows will ask for camera permission
- Allow access to webcam
- Camera will initialize automatically

## 🎮 How to Use

### 1. Start the System
```bash
# Terminal 1: Start Django backend
cd backend
.\DjangoEnv\Scripts\python.exe manage.py runserver 8000

# Terminal 2: Start Flutter app
cd frontend/parking
flutter run -d windows
```

### 2. Use the Camera
1. **Camera initializes automatically** on app start
2. **Toggle between modes**:
   - Click "ورود" for Entry mode (Green)
   - Click "خروج" for Exit mode (Red)
3. **Auto-detection runs** every 3 seconds
4. **Watch for notifications** when plates are detected

### 3. Test Detection
1. **Entry Mode**: Hold a license plate image to webcam
2. **Wait 3 seconds** for auto-detection
3. **See notification**: "✓ ورود: [plate number]"
4. **Switch to Exit Mode**: Click "خروج" button
5. **Show same plate** to webcam
6. **See notification**: "✓ خروج: [plate] - [cost] تومان"

## 🎨 UI Layout

```
┌──────────────────────────────────────────────────────────┐
│ [Stats: Capacity | Active | Free | Price]                │
├──────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────────────────┐   │
│ │ 🎥 دوربین ورودی    [ورود][خروج]    ● فعال      │   │
│ ├────────────────────────────────────────────────────┤   │
│ │                                                    │   │
│ │          [Live Webcam Feed - 300px]               │   │
│ │              YOLO AI Overlay                      │   │
│ │                                                    │   │
│ ├────────────────────────────────────────────────────┤   │
│ │ آخرین تشخیص: 12ب345-67                           │   │
│ │ اطمینان: 95%                                      │   │
│ │ تعداد امروز: 5                                    │   │
│ └────────────────────────────────────────────────────┘   │
├──────────────────────────────────────────────────────────┤
│ Recent Activity (Auto)                  [Reset System]   │
│ [Activity Table]                                         │
└──────────────────────────────────────────────────────────┘
```

## 🔧 Configuration

### Detection Interval
Change in `home_screen.dart`:
```dart
Timer.periodic(
  const Duration(seconds: 3),  // Change this value
  (timer) async { ... }
);
```

### Camera Resolution
Change in `camera_service.dart`:
```dart
CameraController(
  _cameras[0],
  ResolutionPreset.medium,  // low, medium, high, veryHigh
  enableAudio: false,
);
```

### Confidence Threshold
The YOLO API handles this on the backend (default: 0.75).

## 🧪 Testing

### Test Entry Detection
1. Switch to Entry mode (Green)
2. Show license plate to camera
3. Wait for detection
4. Check notification
5. Verify in activity log

### Test Exit Detection
1. First register an entry (above)
2. Switch to Exit mode (Red)
3. Show same plate to camera
4. Wait for detection
5. Check cost in notification
6. Verify in activity log

### Test Mode Toggle
1. Click "ورود" button → Green highlight
2. Click "خروج" button → Red highlight
3. Camera stays active
4. Statistics update per mode

## 📊 Statistics Tracking

### Entry Mode
- Counts all entry detections
- Shows in "تعداد امروز"
- Resets on app restart

### Exit Mode
- Counts all exit detections
- Shows in "تعداد امروز"
- Resets on app restart

### Reset Counts
```dart
cameraService.resetCounts();  // Resets all counters
```

## 🐛 Troubleshooting

### Camera Not Showing
**Issue**: Black screen or "دوربین در دسترس نیست"
**Solutions**:
1. Check webcam is connected
2. Grant camera permission
3. Close other apps using camera
4. Restart the app

### No Detection
**Issue**: Camera works but no detections
**Solutions**:
1. Check Django server is running
2. Verify YOLO models are loaded
3. Check plate is visible and clear
4. Wait full 3 seconds
5. Check console for errors

### Wrong Mode
**Issue**: Detecting in wrong mode
**Solution**: Click the mode toggle button to switch

### Low Confidence
**Issue**: Detection confidence < 75%
**Solutions**:
1. Improve lighting
2. Hold plate steady
3. Move closer to camera
4. Ensure plate is in focus

## 🚀 Performance

### Expected Performance
- **Detection Speed**: 1-2 seconds
- **Frame Rate**: 30 FPS camera feed
- **Memory Usage**: ~200MB
- **CPU Usage**: 10-20%

### Optimization Tips
1. Lower camera resolution for faster processing
2. Increase detection interval to reduce load
3. Close unnecessary apps
4. Use good lighting

## 📱 Future Enhancements

### Planned Features
- [ ] Manual capture button
- [ ] Detection history view
- [ ] Confidence threshold slider
- [ ] Multiple camera support
- [ ] Detection sound alerts
- [ ] Save detected images
- [ ] Export detection log

### Advanced Features
- [ ] Real-time plate tracking
- [ ] Multi-plate detection
- [ ] License plate database
- [ ] Analytics dashboard
- [ ] Mobile app version

## 🎓 Code Structure

### Camera Service
```dart
CameraService
├── initialize()          // Setup camera
├── toggleMode()          // Switch entry/exit
├── captureImage()        // Take photo
├── updateDetection()     // Update stats
└── resetCounts()         // Reset counters
```

### Detection Flow
```
Timer (3s) → Capture Frame → Send to API → Process Result → Update UI
```

### State Management
```
CameraService (Provider)
├── mode (entry/exit)
├── lastDetectedPlate
├── confidence
├── entryCount
└── exitCount
```

## 📝 API Endpoints Used

### Entry Detection
```
POST /api/detect-entry/
- Multipart form data
- Returns: plate, entry_id, confidence
```

### Exit Detection
```
POST /api/detect-exit/
- Multipart form data
- Returns: plate, duration, cost, confidence
```

## ✅ Checklist

### Setup
- [x] Camera package added to pubspec.yaml
- [x] Camera service created
- [x] API methods implemented
- [x] Home screen updated
- [x] Main app configured
- [ ] Run `flutter pub get`
- [ ] Test camera access
- [ ] Test mode toggle
- [ ] Test detection

### Testing
- [ ] Camera initializes
- [ ] Live feed displays
- [ ] Mode toggle works
- [ ] Entry detection works
- [ ] Exit detection works
- [ ] Statistics update
- [ ] Notifications show

## 🎉 Summary

You now have a **fully automatic parking system** with:

✅ **Single webcam** with mode toggle
✅ **Entry/Exit switching** with one click
✅ **Live camera preview** (300px)
✅ **Auto-detection** every 3 seconds
✅ **YOLO AI integration**
✅ **Real-time statistics**
✅ **Automatic notifications**
✅ **Clean, modern UI**

**Next Step**: Run `flutter pub get` and test the system!

---

**Status**: ✅ Implementation Complete
**Ready**: Install dependencies and test
**Documentation**: Complete
**Support**: All guides provided
