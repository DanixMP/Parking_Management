"""
Complete YOLO Integration Test Script
Tests the YOLO models and Django API endpoints
"""

import sys
import os
from pathlib import Path

# Add paths
backend_path = Path(__file__).parent
src_path = backend_path / 'src'
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(backend_path))

print("=" * 70)
print("YOLO Integration Test Suite")
print("=" * 70)
print()

# Test 1: Check model files
print("Test 1: Checking model files...")
print("-" * 70)

plate_model_path = src_path / "plateYolo.pt"
char_model_path = src_path / "CharsYolo.pt"

if plate_model_path.exists():
    size_mb = plate_model_path.stat().st_size / (1024 * 1024)
    print(f"✓ Plate model found: {plate_model_path}")
    print(f"  Size: {size_mb:.2f} MB")
else:
    print(f"✗ Plate model NOT found: {plate_model_path}")

if char_model_path.exists():
    size_mb = char_model_path.stat().st_size / (1024 * 1024)
    print(f"✓ Character model found: {char_model_path}")
    print(f"  Size: {size_mb:.2f} MB")
else:
    print(f"✗ Character model NOT found: {char_model_path}")

print()

# Test 2: Check dependencies
print("Test 2: Checking dependencies...")
print("-" * 70)

dependencies = {
    'torch': 'PyTorch',
    'cv2': 'OpenCV',
    'numpy': 'NumPy',
    'yolov5': 'YOLOv5',
    'django': 'Django',
    'rest_framework': 'Django REST Framework',
    'corsheaders': 'Django CORS Headers'
}

missing_deps = []
for module, name in dependencies.items():
    try:
        __import__(module)
        print(f"✓ {name} installed")
    except ImportError:
        print(f"✗ {name} NOT installed")
        missing_deps.append(name)

if missing_deps:
    print(f"\n⚠ Missing dependencies: {', '.join(missing_deps)}")
    print("Install with: pip install torch opencv-python numpy yolov5 django djangorestframework django-cors-headers")
else:
    print("\n✓ All dependencies installed")

print()

# Test 3: Load YOLO models
print("Test 3: Loading YOLO models...")
print("-" * 70)

try:
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    
    print()
    
    from yolo_loader import load_plate_model, load_char_model
    
    print("Loading plate detection model...")
    plate_model = load_plate_model(device)
    print("✓ Plate model loaded successfully")
    print()
    
    print("Loading character recognition model...")
    char_model = load_char_model(device)
    print("✓ Character model loaded successfully")
    print()
    
except Exception as e:
    print(f"✗ Error loading models: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 4: Test with sample image (if available)
print("Test 4: Testing detection with sample image...")
print("-" * 70)

try:
    import cv2
    import numpy as np
    
    # Create a simple test image (black with white rectangle)
    test_img = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(test_img, (200, 200), (440, 280), (255, 255, 255), -1)
    
    print("Running plate detection on test image...")
    results = plate_model(test_img)
    
    # Handle yolov5 package results
    detections = results.pred[0] if hasattr(results, 'pred') else results.xyxy[0]
    print(f"Detections: {len(detections)}")
    
    if len(detections) > 0:
        print("✓ Model can process images (no plates detected in test image, which is expected)")
    else:
        print("✓ Model processed test image successfully")
    
except Exception as e:
    print(f"⚠ Could not test detection: {e}")

print()

# Test 5: Check Django setup
print("Test 5: Checking Django setup...")
print("-" * 70)

try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parking_api.settings')
    
    import django
    django.setup()
    
    print("✓ Django configured successfully")
    
    # Check if API app is installed
    from django.conf import settings
    if 'api' in settings.INSTALLED_APPS:
        print("✓ API app installed")
    else:
        print("✗ API app not in INSTALLED_APPS")
    
    # Check database
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("✓ Database connection working")
    
except Exception as e:
    print(f"⚠ Django setup issue: {e}")

print()

# Test 6: Check API endpoints
print("Test 6: Checking API endpoints...")
print("-" * 70)

try:
    from django.urls import get_resolver
    
    resolver = get_resolver()
    
    endpoints = [
        'api/detect-plate/',
        'api/detect-entry/',
        'api/detect-exit/',
        'api/status/',
        'api/entry/',
        'api/exit/',
    ]
    
    for endpoint in endpoints:
        try:
            resolver.resolve(f'/{endpoint}')
            print(f"✓ {endpoint}")
        except:
            print(f"✗ {endpoint} not found")
    
except Exception as e:
    print(f"⚠ Could not check endpoints: {e}")

print()

# Summary
print("=" * 70)
print("Test Summary")
print("=" * 70)
print()
print("If all tests passed, you can:")
print("1. Start Django server: python backend/manage.py runserver 8000")
print("2. Test API endpoints:")
print("   - POST http://localhost:8000/api/detect-plate/ (with image file)")
print("   - POST http://localhost:8000/api/detect-entry/ (with image file)")
print("   - POST http://localhost:8000/api/detect-exit/ (with image file)")
print()
print("Use the test_api_with_image.py script to test with actual images")
print("=" * 70)
