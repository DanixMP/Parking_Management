# YOLO Models - Quick Start Guide

## ✅ Status: Ready to Use!

Your YOLO models are loaded and working. Here's how to use them.

## 1. Test Models

```bash
cd backend/src
python yolo_loader.py
```

Expected output:
```
✓ Plate model loaded successfully on cpu
✓ Character model loaded successfully on cpu
✓ All models loaded successfully!
```

## 2. Run Detection Examples

### Option A: Real-time Webcam Detection
```bash
cd backend/src
python example_detection.py
```
Press 'q' to quit.

### Option B: Detect on a Single Image
```bash
cd backend/src
python example_detection.py /path/to/image.jpg
```

## 3. Use Models in Your Code

```python
from yolo_loader import load_plate_model, load_char_model
import cv2
import torch

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load models
plate_model = load_plate_model(device)
char_model = load_char_model(device)

# Load image
image = cv2.imread("image.jpg")

# Detect plates
plate_results = plate_model(image)
plate_detections = plate_results.xyxy[0].cpu().numpy()

# For each plate, detect characters
for x1, y1, x2, y2, conf, cls in plate_detections:
    if conf < 0.5:
        continue
    
    # Crop plate
    plate_crop = image[int(y1):int(y2), int(x1):int(x2)]
    plate_resized = cv2.resize(plate_crop, (320, 80))
    
    # Detect characters
    char_results = char_model(plate_resized)
    char_detections = char_results.xyxy[0].cpu().numpy()
    
    # Extract text
    chars = [char_model.names[int(cls)] for *_, cls in char_detections]
    plate_text = "".join(chars)
    print(f"Detected plate: {plate_text}")
```

## 4. Run Full Detection Scripts

### Entry Camera
```bash
cd backend/src
python detect_entry.py
```

### Exit Camera
```bash
cd backend/src
python detect_exit.py
```

## 5. Run Full System

```bash
python run_server.py
```

## Model Files

- **plateYolo.pt** (13.7 MB) - Detects license plates
- **CharsYolo.pt** (13.9 MB) - Detects characters on plates

Both located in: `backend/src/`

## What Each Model Does

### Plate Model
- Input: Full image (any size)
- Output: Bounding boxes of license plates
- Confidence threshold: 0.5 (adjustable)

### Character Model
- Input: Cropped plate image (320x80 recommended)
- Output: Bounding boxes and class labels for each character
- Supports: Persian/Farsi letters + digits

## Performance

- **CPU:** ~100-500ms per frame
- **GPU:** ~10-50ms per frame (with NVIDIA GPU)

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Models not found | Check `backend/src/` for `.pt` files |
| Import errors | Run `pip install -r backend/src/requirements-clean.txt` |
| Slow inference | Normal on CPU; use GPU for faster speed |
| Camera not working | Check camera index (default: 0) |

## Next Steps

1. ✅ Models are loaded
2. Test with `python yolo_loader.py`
3. Try examples with `python example_detection.py`
4. Run detection scripts with camera
5. Integrate with database
6. Deploy to production

## File Structure

```
backend/src/
├── plateYolo.pt              # Plate detection model
├── CharsYolo.pt              # Character detection model
├── yolo_loader.py            # Model loading utilities
├── example_detection.py       # Example usage
├── detect_entry.py           # Entry camera detection
├── detect_exit.py            # Exit camera detection
├── database.py               # Database operations
└── ...
```

## Support

For detailed information, see: `YOLO_SETUP_GUIDE.md`
