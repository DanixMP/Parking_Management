# 🔍 Camera Debug Checklist

## What to Check Now

### 1. Look at the Console Output

When you run the app, you should see:

```
🔍 Looking for cameras...
📷 Found X camera(s)
  Camera 0: [Camera Name]
    Direction: [front/back/external]
🎥 Initializing camera: [Camera Name]
✅ Controller initialized
   Preview size: Size(width, height)
   Aspect ratio: X.XX
   Is initialized: true
✓ Camera ready!
```

**If you see:**
- ❌ `Found 0 camera(s)` → Camera not detected
- ❌ `Error initializing camera` → Permission or driver issue
- ✅ `Camera ready!` → Camera initialized successfully

### 2. Look at the Debug Panel (Orange Box)

The app now shows a debug panel with:
```
🔍 Debug Info:
isInitialized: true/false
controller != null: true/false
controller.isInitialized: true/false
previewSize: Size(width, height)
```

**What it means:**
- `isInitialized: false` → Camera service not ready
- `controller != null: false` → Controller not created
- `controller.isInitialized: false` → Controller created but not initialized

### 3. Look at the Camera Area

You should see one of these:

**✅ Success:**
- Live camera feed showing

**⏳ Loading:**
- Spinning circle
- "در حال راه‌اندازی دوربین..."
- "Check console for details"

**❌ Error:**
- Camera off icon
- "دوربین در دسترس نیست"
- "Check console for errors"

## Common Scenarios

### Scenario 1: "Found 0 camera(s)"

**Problem:** No camera detected

**Solutions:**
1. **Check physical connection:**
   ```
   - USB webcam plugged in?
   - Built-in camera enabled in BIOS?
   ```

2. **Check Device Manager (Windows):**
   ```
   Win + X → Device Manager → Cameras
   - Is your camera listed?
   - Any yellow warning icons?
   - Try "Update driver"
   ```

3. **Test in Windows Camera app:**
   ```
   Start → Camera
   - Does it work there?
   - If yes, restart Flutter app
   - If no, fix Windows camera first
   ```

### Scenario 2: "Error initializing camera: CameraAccessDenied"

**Problem:** Permission denied

**Solutions:**
1. **Windows Settings:**
   ```
   Settings → Privacy & Security → Camera
   → "Let apps access your camera" = ON
   → "Let desktop apps access your camera" = ON
   ```

2. **Restart the app** after granting permission

3. **Run as administrator:**
   ```bash
   # Right-click terminal → Run as administrator
   cd frontend/parking
   flutter run -d windows
   ```

### Scenario 3: Camera Initializes But No Preview

**Problem:** Controller initialized but preview not showing

**Check Console:**
```
✅ Controller initialized
   Preview size: Size(640.0, 480.0)  ← Should have values
   Aspect ratio: 1.33                ← Should be a number
   Is initialized: true              ← Should be true
```

**Then check:**
```
🎬 Building camera preview:
   isActive: true
   controller: true
   controller.isInitialized: true
   ✅ Showing camera preview  ← Should see this
```

**If you see "⏳ Showing loading" instead:**
- Controller not fully initialized
- Click "Initialize Camera" button in debug panel
- Check console for errors

### Scenario 4: Forever Loading

**Problem:** Stuck on loading spinner

**Solutions:**
1. **Click "Initialize Camera"** button in debug panel
2. **Check console** for error messages
3. **Restart the app**
4. **Close other apps** using camera

## Step-by-Step Debug Process

### Step 1: Run the App
```bash
cd frontend/parking
flutter run -d windows
```

### Step 2: Watch Console
Look for the camera initialization messages (🔍 📷 🎥 ✅)

### Step 3: Check Debug Panel
Look at the orange debug box in the app

### Step 4: Try Manual Init
Click "Initialize Camera" button if needed

### Step 5: Check Camera Area
Should show live feed or clear error message

## Quick Fixes

### Fix 1: Manual Initialization
```
1. Look at debug panel
2. Click "Initialize Camera" button
3. Watch console output
4. Wait for "✓ Camera ready!"
```

### Fix 2: Restart App
```bash
# In terminal where app is running:
Ctrl + C  (stop)
flutter run -d windows  (start again)
```

### Fix 3: Check Permissions
```
Windows Settings → Privacy → Camera → Enable
Restart app
```

### Fix 4: Close Other Apps
```
Close: Zoom, Teams, Skype, OBS, etc.
Restart app
```

## What Console Output Means

### Good Output ✅
```
🔍 Looking for cameras...
📷 Found 1 camera(s)
  Camera 0: Integrated Camera
    Direction: CameraLensDirection.front
🎥 Initializing camera: Integrated Camera
✅ Controller initialized
   Preview size: Size(640.0, 480.0)
   Aspect ratio: 1.3333333333333333
   Is initialized: true
✓ Camera ready!
🎬 Building camera preview:
   isActive: true
   controller: true
   controller.isInitialized: true
   ✅ Showing camera preview
```

### Bad Output ❌
```
🔍 Looking for cameras...
📷 Found 0 camera(s)
❌ No cameras available
```
**Fix:** Check camera connection and Device Manager

```
❌ Error initializing camera: CameraAccessDenied
```
**Fix:** Grant camera permission in Windows Settings

```
❌ Error initializing camera: CameraException
```
**Fix:** Close other apps using camera

## Testing Camera Manually

### Test 1: Check Available Cameras
Click "Initialize Camera" button and watch console:
```
📷 Found X camera(s)
```

### Test 2: Check Initialization
After clicking button, should see:
```
✅ Controller initialized
✓ Camera ready!
```

### Test 3: Check Preview
Debug panel should show:
```
isInitialized: true
controller != null: true
controller.isInitialized: true
previewSize: Size(640.0, 480.0)
```

## Expected Timeline

```
0s:  App starts
1s:  🔍 Looking for cameras...
2s:  📷 Found 1 camera(s)
3s:  🎥 Initializing camera...
4s:  ✅ Controller initialized
5s:  ✓ Camera ready!
5s:  🎬 Building camera preview
5s:  ✅ Showing camera preview
```

**If stuck at any step:** Check console for error message

## Still Not Working?

### Collect This Info:

1. **Console output** (copy all messages)
2. **Debug panel values** (screenshot)
3. **Windows Camera app** (does it work?)
4. **Device Manager** (camera listed?)
5. **Flutter version** (`flutter --version`)

### Try This:

1. **Simplest test:**
   ```bash
   # Test if Flutter can see camera at all
   flutter devices
   ```

2. **Camera package test:**
   ```dart
   // Add this button to test:
   ElevatedButton(
     onPressed: () async {
       final cameras = await availableCameras();
       print('TEST: Found ${cameras.length} cameras');
     },
     child: Text('Test Camera Detection'),
   )
   ```

3. **Alternative: Use image picker:**
   ```
   If camera won't work, you can test YOLO
   detection by picking images from files
   ```

---

**Next Steps:**
1. Run the app
2. Look at console output
3. Look at debug panel
4. Report what you see
