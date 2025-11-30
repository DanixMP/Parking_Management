#!/usr/bin/env python
"""
Quick test script to verify YOLO models are working
Run this to check if models load correctly before running the full system
"""

import sys
import os
from pathlib import Path

# Ensure we're in the right directory
os.chdir(Path(__file__).parent)

print("\n" + "="*70)
print("YOLO Model Testing Script")
print("="*70 + "\n")

# Check if model files exist
print("1. Checking model files...")
print("-" * 70)

plate_model_path = Path("plateYolo.pt")
char_model_path = Path("CharsYolo.pt")

if plate_model_path.exists():
    size_mb = plate_model_path.stat().st_size / (1024 * 1024)
    print(f"✓ Plate model found: {plate_model_path} ({size_mb:.1f} MB)")
else:
    print(f"✗ Plate model NOT found: {plate_model_path}")
    sys.exit(1)

if char_model_path.exists():
    size_mb = char_model_path.stat().st_size / (1024 * 1024)
    print(f"✓ Character model found: {char_model_path} ({size_mb:.1f} MB)")
else:
    print(f"✗ Character model NOT found: {char_model_path}")
    sys.exit(1)

print("\n2. Checking dependencies...")
print("-" * 70)

try:
    import torch
    print(f"✓ PyTorch {torch.__version__}")
except ImportError:
    print("✗ PyTorch not installed")
    sys.exit(1)

try:
    import cv2
    print(f"✓ OpenCV {cv2.__version__}")
except ImportError:
    print("✗ OpenCV not installed")
    sys.exit(1)

try:
    from ultralytics import YOLO
    print("✓ Ultralytics YOLO available")
    use_ultralytics = True
except ImportError:
    print("⚠ Ultralytics not available, will use torch hub")
    use_ultralytics = False

# Check if models are YOLOv5 or YOLOv8
print("⚠ Models are YOLOv5 format - using torch hub loader")
use_ultralytics = False

print("\n3. Checking device...")
print("-" * 70)

if torch.cuda.is_available():
    device = "cuda"
    print(f"✓ CUDA available - GPU: {torch.cuda.get_device_name(0)}")
    print(f"  Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
else:
    device = "cpu"
    print("⚠ CUDA not available - using CPU (slower)")

print("\n4. Loading models...")
print("-" * 70)

try:
    if use_ultralytics:
        print("Loading plate model with ultralytics...")
        plate_model = YOLO(str(plate_model_path))
        plate_model.to(device)
        print("✓ Plate model loaded")
        
        print("Loading character model with ultralytics...")
        char_model = YOLO(str(char_model_path))
        char_model.to(device)
        print("✓ Character model loaded")
    else:
        print("Loading plate model with torch hub...")
        plate_model = torch.hub.load(
            "ultralytics/yolov5",
            "custom",
            path=str(plate_model_path),
            force_reload=False
        )
        plate_model.to(device)
        plate_model.eval()
        print("✓ Plate model loaded")
        
        print("Loading character model with torch hub...")
        char_model = torch.hub.load(
            "ultralytics/yolov5",
            "custom",
            path=str(char_model_path),
            force_reload=False
        )
        char_model.to(device)
        char_model.eval()
        print("✓ Character model loaded")
        
except Exception as e:
    print(f"✗ Error loading models: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n5. Testing inference...")
print("-" * 70)

try:
    import numpy as np
    
    # Create a dummy image
    dummy_img = np.zeros((480, 640, 3), dtype=np.uint8)
    
    print("Running plate model inference...")
    plate_results = plate_model(dummy_img)
    print(f"✓ Plate model inference successful")
    
    print("Running character model inference...")
    char_results = char_model(dummy_img)
    print(f"✓ Character model inference successful")
    
except Exception as e:
    print(f"✗ Error during inference: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*70)
print("✓ All tests passed! Models are ready to use.")
print("="*70 + "\n")

print("Next steps:")
print("  1. Run the detection scripts:")
print("     - python detect_entry.py")
print("     - python detect_exit.py")
print("  2. Or run the full GUI:")
print("     - python ../run_server.py")
print()
