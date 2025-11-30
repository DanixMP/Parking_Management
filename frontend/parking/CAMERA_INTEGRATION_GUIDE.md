# 📷 Camera Integration Guide - Automatic System

## Overview
This guide explains how to integrate cameras for the fully automatic parking system.

## Step 1: Add Camera Package

### Update pubspec.yaml
```yaml
dependencies:
  flutter:
    sdk: flutter
  provider: ^6.1.1
  http: ^1.1.2
  camera: ^0.10.5+5  # Add this
  image_picker: ^1.0.4  # For testing
```

Run:
```bash
flutter pub get
```

## Step 2: Camera Permissions

### Windows (windows/runner/main.cpp)
No special permissions needed for desktop.

### Android (android/app/src/main/AndroidManifest.xml)
```xml
<uses-permission android:name="android.permission.CAMERA"/>
<uses-feature android:name="android.hardware.camera"/>
```

### iOS (ios/Runner/Info.plist)
```xml
<key>NSCameraUsageDescription</key>
<string>Camera access for automatic plate detection</string>
```

## Step 3: Create Camera Service

### lib/services/camera_service.dart
```dart
import 'package:camera/camera.dart';
import 'package:flutter/foundation.dart';

class CameraService extends ChangeNotifier {
  CameraController? _entryController;
  CameraController? _exitController;
  
  List<CameraDescription> _cameras = [];
  bool _isInitialized = false;
  
  CameraController? get entryController => _entryController;
  CameraController? get exitController => _exitController;
  bool get isInitialized => _isInitialized;
  
  Future<void> initialize() async {
    try {
      _cameras = await availableCameras();
      
      if (_cameras.isEmpty) {
        print('No cameras available');
        return;
      }
      
      // Initialize entry camera (first camera)
      if (_cameras.isNotEmpty) {
        _entryController = CameraController(
          _cameras[0],
          ResolutionPreset.medium,
          enableAudio: false,
        );
        await _entryController!.initialize();
      }
      
      // Initialize exit camera (second camera if available)
      if (_cameras.length > 1) {
        _exitController = CameraController(
          _cameras[1],
          ResolutionPreset.medium,
          enableAudio: false,
        );
        await _exitController!.initialize();
      }
      
      _isInitialized = true;
      notifyListeners();
    } catch (e) {
      print('Error initializing cameras: $e');
    }
  }
  
  Future<Uint8List?> captureFromEntry() async {
    if (_entryController == null || !_entryController!.value.isInitialized) {
      return null;
    }
    
    try {
      final image = await _entryController!.takePicture();
      return await image.readAsBytes();
    } catch (e) {
      print('Error capturing from entry camera: $e');
      return null;
    }
  }
  
  Future<Uint8List?> captureFromExit() async {
    if (_exitController == null || !_exitController!.value.isInitialized) {
      return null;
    }
    
    try {
      final image = await _exitController!.takePicture();
      return await image.readAsBytes();
    } catch (e) {
      print('Error capturing from exit camera: $e');
      return null;
    }
  }
  
  @override
  void dispose() {
    _entryController?.dispose();
    _exitController?.dispose();
    super.dispose();
  }
}
```

## Step 4: Update API Service

### lib/services/api_service.dart
Add YOLO detection methods:

```dart
Future<Map<String, dynamic>?> detectPlateEntry(Uint8List imageBytes) async {
  try {
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/detect-entry/'),
    );
    
    request.files.add(
      http.MultipartFile.fromBytes(
        'image',
        imageBytes,
        filename: 'entry_${DateTime.now().millisecondsSinceEpoch}.jpg',
      ),
    );
    
    var response = await request.send();
    var responseData = await response.stream.bytesToString();
    
    if (response.statusCode == 201) {
      return json.decode(responseData);
    }
    
    return null;
  } catch (e) {
    print('Error detecting entry plate: $e');
    return null;
  }
}

Future<Map<String, dynamic>?> detectPlateExit(Uint8List imageBytes) async {
  try {
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/detect-exit/'),
    );
    
    request.files.add(
      http.MultipartFile.fromBytes(
        'image',
        imageBytes,
        filename: 'exit_${DateTime.now().millisecondsSinceEpoch}.jpg',
      ),
    );
    
    var response = await request.send();
    var responseData = await response.stream.bytesToString();
    
    if (response.statusCode == 200) {
      return json.decode(responseData);
    }
    
    return null;
  } catch (e) {
    print('Error detecting exit plate: $e');
    return null;
  }
}
```

## Step 5: Update Home Screen

### Add Camera Preview Widget

```dart
Widget _buildCameraPreview(CameraController? controller, Color color) {
  if (controller == null || !controller.value.isInitialized) {
    return Container(
      height: 180,
      decoration: BoxDecoration(
        color: const Color(0xFF0F1C2E),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.videocam_off, size: 48, color: Colors.white24),
            const SizedBox(height: 8),
            const Text(
              'دوربین در دسترس نیست',
              style: TextStyle(color: Colors.white54, fontSize: 13),
            ),
          ],
        ),
      ),
    );
  }
  
  return Container(
    height: 180,
    decoration: BoxDecoration(
      borderRadius: BorderRadius.circular(8),
      border: Border.all(color: color.withOpacity(0.3), width: 2),
    ),
    child: ClipRRect(
      borderRadius: BorderRadius.circular(8),
      child: CameraPreview(controller),
    ),
  );
}
```

### Add Auto-Detection Timer

```dart
Timer? _entryDetectionTimer;
Timer? _exitDetectionTimer;

void _startAutoDetection() {
  // Entry camera auto-detection every 2 seconds
  _entryDetectionTimer = Timer.periodic(
    const Duration(seconds: 2),
    (timer) async {
      final cameraService = Provider.of<CameraService>(context, listen: false);
      final imageBytes = await cameraService.captureFromEntry();
      
      if (imageBytes != null) {
        await _processEntryDetection(imageBytes);
      }
    },
  );
  
  // Exit camera auto-detection every 2 seconds
  _exitDetectionTimer = Timer.periodic(
    const Duration(seconds: 2),
    (timer) async {
      final cameraService = Provider.of<CameraService>(context, listen: false);
      final imageBytes = await cameraService.captureFromExit();
      
      if (imageBytes != null) {
        await _processExitDetection(imageBytes);
      }
    },
  );
}

Future<void> _processEntryDetection(Uint8List imageBytes) async {
  final apiService = ApiService();
  final result = await apiService.detectPlateEntry(imageBytes);
  
  if (result != null && result['success'] == true) {
    // Update UI with detection result
    setState(() {
      // Update entry zone stats
    });
    
    // Reload data
    await _loadData();
    
    // Show notification
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('ورود تشخیص داده شد: ${result['plate']}'),
          backgroundColor: Colors.green,
        ),
      );
    }
  }
}

Future<void> _processExitDetection(Uint8List imageBytes) async {
  final apiService = ApiService();
  final result = await apiService.detectPlateExit(imageBytes);
  
  if (result != null && result['success'] == true) {
    // Update UI with detection result
    setState(() {
      // Update exit zone stats
    });
    
    // Reload data
    await _loadData();
    
    // Show notification with cost
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'خروج: ${result['plate']} - هزینه: ${result['cost']} تومان'
          ),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
}

@override
void dispose() {
  _entryDetectionTimer?.cancel();
  _exitDetectionTimer?.cancel();
  super.dispose();
}
```

## Step 6: Initialize in Main

### lib/main.dart
```dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize camera service
  final cameraService = CameraService();
  await cameraService.initialize();
  
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ParkingProvider()),
        ChangeNotifierProvider.value(value: cameraService),
      ],
      child: const MyApp(),
    ),
  );
}
```

## Step 7: Testing

### Test with Single Camera
```dart
// For testing with one camera, use it for both entry and exit
if (_cameras.length == 1) {
  _entryController = CameraController(_cameras[0], ResolutionPreset.medium);
  _exitController = _entryController; // Reuse for testing
}
```

### Test with Image Picker
```dart
// For testing without camera
Future<void> _testWithImagePicker() async {
  final ImagePicker picker = ImagePicker();
  final XFile? image = await picker.pickImage(source: ImageSource.gallery);
  
  if (image != null) {
    final bytes = await image.readAsBytes();
    await _processEntryDetection(bytes);
  }
}
```

## Configuration

### Detection Settings
```dart
class DetectionConfig {
  static const int detectionInterval = 2000; // ms
  static const double minConfidence = 0.75;
  static const int cooldownPeriod = 5000; // ms
  static const bool autoRegister = true;
}
```

### Camera Settings
```dart
class CameraConfig {
  static const ResolutionPreset resolution = ResolutionPreset.medium;
  static const bool enableAudio = false;
  static const int maxRetries = 3;
}
```

## Troubleshooting

### Camera Not Found
```dart
if (_cameras.isEmpty) {
  // Show error message
  // Fallback to image picker
}
```

### Permission Denied
```dart
try {
  await controller.initialize();
} catch (e) {
  if (e is CameraException) {
    if (e.code == 'CameraAccessDenied') {
      // Show permission request dialog
    }
  }
}
```

### Detection Errors
```dart
if (result == null || result['success'] != true) {
  // Log error
  // Show user-friendly message
  // Continue monitoring
}
```

## Performance Optimization

### 1. Reduce Detection Frequency
```dart
// Adjust based on traffic
Timer.periodic(Duration(seconds: 3), ...); // Less frequent
```

### 2. Lower Camera Resolution
```dart
CameraController(camera, ResolutionPreset.low); // Faster processing
```

### 3. Skip Frames
```dart
int frameCount = 0;
if (frameCount++ % 3 == 0) {
  // Process every 3rd frame
}
```

## Next Steps

1. ✅ Add camera package
2. ✅ Create camera service
3. ✅ Update API service
4. ✅ Integrate with UI
5. ✅ Add auto-detection
6. ✅ Test with real cameras
7. ✅ Deploy and monitor

---

**Status**: Ready for implementation
**Estimated Time**: 2-3 hours
**Difficulty**: Medium
**Dependencies**: camera package, working YOLO API
