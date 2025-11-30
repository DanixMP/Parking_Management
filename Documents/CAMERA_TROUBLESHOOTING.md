# 📷 Camera Troubleshooting Guide

## Issue: Camera Not Showing

### Quick Checks

1. **Check Console Output**
   Look for these messages in the terminal:
   ```
   ✓ Camera initialized successfully  ← Good!
   No cameras available               ← Problem!
   Error initializing camera: ...     ← Problem!
   ```

2. **Check Camera Status**
   In the app, look at the stats panel:
   ```
   وضعیت دوربین: آماده        ← Camera is ready
   وضعیت دوربین: در حال راه‌اندازی  ← Camera is initializing
   ```

3. **Visual Indicators**
   - **Loading spinner**: Camera is initializing
   - **"دوربین در دسترس نیست"**: Camera not available
   - **Live feed**: Camera working!

## Common Issues & Solutions

### 1. Camera Permission Not Granted

**Symptoms:**
- Black screen
- "دوربین در دسترس نیست" message
- Console: "Error initializing camera: CameraAccessDenied"

**Solutions:**

**Windows:**
1. Open Windows Settings
2. Go to Privacy & Security → Camera
3. Enable "Let apps access your camera"
4. Enable for your app
5. Restart the app

**Alternative:**
```bash
# Run as administrator
flutter run -d windows
```

### 2. Camera In Use by Another App

**Symptoms:**
- "Error initializing camera" in console
- Camera was working, then stopped

**Solutions:**
1. Close other apps using camera (Zoom, Teams, Skype, etc.)
2. Check Task Manager for camera processes
3. Restart the app

### 3. No Camera Detected

**Symptoms:**
- "No cameras available" in console
- "دوربین در دسترس نیست" message

**Solutions:**
1. **Check physical connection**:
   - USB webcam plugged in?
   - Built-in camera enabled?

2. **Check Device Manager** (Windows):
   - Open Device Manager
   - Look under "Cameras" or "Imaging devices"
   - If yellow warning, update driver

3. **Test camera in other apps**:
   - Open Camera app (Windows)
   - If works there, restart Flutter app

### 4. Camera Initializing Forever

**Symptoms:**
- Loading spinner forever
- "در حال راه‌اندازی دوربین..." message
- No error in console

**Solutions:**
1. **Click "راه‌اندازی مجدد دوربین" button**
2. **Restart the app**
3. **Check camera in Device Manager**

### 5. Camera Shows But Frozen

**Symptoms:**
- Camera preview shows but doesn't update
- Old frame stuck on screen

**Solutions:**
1. Toggle camera mode (Entry/Exit)
2. Restart the app
3. Check if camera is working in other apps

## Debug Steps

### Step 1: Check Camera Package Installation
```bash
cd frontend/parking
flutter pub get
```

Look for:
```
✓ camera 0.10.5+5
```

### Step 2: Check Available Cameras
Add this to camera_service.dart temporarily:
```dart
Future<void> initialize() async {
  try {
    _cameras = await availableCameras();
    
    print('Found ${_cameras.length} cameras:');
    for (var camera in _cameras) {
      print('  - ${camera.name}');
      print('    Lens: ${camera.lensDirection}');
    }
    
    // ... rest of code
  }
}
```

### Step 3: Test Camera Manually
Create a test button in the UI:
```dart
ElevatedButton(
  onPressed: () async {
    final cameras = await availableCameras();
    print('Cameras: ${cameras.length}');
    if (cameras.isNotEmpty) {
      print('First camera: ${cameras[0].name}');
    }
  },
  child: Text('Test Camera Detection'),
)
```

### Step 4: Check Permissions (Windows)
Run this PowerShell command:
```powershell
Get-AppxPackage | Select Name, PackageFamilyName
```

## Manual Camera Initialization

If automatic initialization fails, add a manual button:

```dart
// In home_screen.dart
ElevatedButton.icon(
  onPressed: () async {
    final cameraService = Provider.of<CameraService>(context, listen: false);
    await cameraService.initialize();
    setState(() {});
  },
  icon: Icon(Icons.camera),
  label: Text('Initialize Camera'),
)
```

## Testing Camera Feed

### Test 1: Check if Camera Opens
```dart
// Should see this in console:
✓ Camera initialized successfully
```

### Test 2: Check Preview Size
```dart
// Add to camera_service.dart after initialization:
print('Preview size: ${_controller!.value.previewSize}');
print('Aspect ratio: ${_controller!.value.aspectRatio}');
```

### Test 3: Capture Test Image
```dart
// Add a test button:
ElevatedButton(
  onPressed: () async {
    final bytes = await cameraService.captureImage();
    print('Captured ${bytes?.length ?? 0} bytes');
  },
  child: Text('Test Capture'),
)
```

## Platform-Specific Issues

### Windows

**Issue**: Camera permission dialog doesn't appear
**Solution**: 
1. Settings → Privacy → Camera
2. Manually enable for the app

**Issue**: Multiple cameras detected
**Solution**: Camera service uses first camera (index 0)
To change:
```dart
// In camera_service.dart
_controller = CameraController(
  _cameras[1],  // Use second camera
  ResolutionPreset.medium,
);
```

### Web (Future)

**Issue**: Camera not working in web
**Solution**: 
1. Use HTTPS (required for camera access)
2. Grant browser permission

## Verification Checklist

- [ ] Camera package installed (`flutter pub get`)
- [ ] Camera permission granted (Windows Settings)
- [ ] No other apps using camera
- [ ] Camera detected in Device Manager
- [ ] Console shows "Camera initialized successfully"
- [ ] UI shows "وضعیت دوربین: آماده"
- [ ] Live feed visible in preview area
- [ ] Can toggle between Entry/Exit modes

## Still Not Working?

### Collect Debug Info

1. **Console output**:
   ```
   Copy all messages from terminal
   ```

2. **Camera info**:
   ```dart
   print('Cameras: ${_cameras.length}');
   print('Controller: ${_controller != null}');
   print('Initialized: $_isInitialized');
   ```

3. **System info**:
   - Windows version
   - Flutter version (`flutter --version`)
   - Camera model

### Alternative: Use Image Picker for Testing

If camera won't work, test with image picker:

```dart
// Add to pubspec.yaml
dependencies:
  image_picker: ^1.0.4

// Add test button
ElevatedButton(
  onPressed: () async {
    final ImagePicker picker = ImagePicker();
    final XFile? image = await picker.pickImage(
      source: ImageSource.gallery,
    );
    if (image != null) {
      final bytes = await image.readAsBytes();
      // Test detection with this image
    }
  },
  child: Text('Pick Image Instead'),
)
```

## Expected Behavior

### On App Start
1. Camera service initializes
2. Console: "✓ Camera initialized successfully"
3. UI shows live camera feed
4. Status: "وضعیت دوربین: آماده"

### During Operation
1. Live feed updates continuously
2. Can toggle Entry/Exit modes
3. Auto-detection runs every 3 seconds
4. Notifications show detection results

### On Mode Toggle
1. Camera stays active
2. Mode indicator changes color
3. Statistics update for new mode
4. No camera restart needed

## Performance Tips

### If Camera is Laggy

1. **Lower resolution**:
```dart
CameraController(
  _cameras[0],
  ResolutionPreset.low,  // Instead of medium
);
```

2. **Increase detection interval**:
```dart
Timer.periodic(
  const Duration(seconds: 5),  // Instead of 3
);
```

3. **Close other apps**

## Success Indicators

✅ Console: "✓ Camera initialized successfully"
✅ UI: Live camera feed visible
✅ UI: "وضعیت دوربین: آماده"
✅ UI: Can toggle Entry/Exit modes
✅ UI: YOLO AI overlay visible
✅ Detection: Works every 3 seconds

---

**Need More Help?**
1. Check console for error messages
2. Try manual initialization button
3. Test camera in Windows Camera app
4. Restart the application
