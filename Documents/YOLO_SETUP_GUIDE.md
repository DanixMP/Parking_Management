# YOLO Model Setup Guide

## Overview

This parking management system uses two YOLOv5 models:
1. **plateYolo.pt** - Detects license plates in images
2. **CharsYolo.pt** - Detects individual characters on license plates

## Current Status

✅ **Models are loaded and working!**

The models are located in `backend/src/` and are automatically loaded when needed.

## How to Use the Models

### 1. Quick Test

To verify the models are working:

```bash
cd backend/src
python yolo_loader.py
```

This will:
- Check if model files exist
- Load both models
- Verify they work correctly
- Show device info (CPU/GPU)

### 2. Using Models in Your Code

```python
from yolo_loader import load_plate_model, load_char_model
import torch

# Get device (CPU or GPU)
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load models
plate_model = load_plate_model(device)
char_model = load_char_model(device)

# Run inference on an image
import cv2
image = cv2.imread("path/to/image.jpg")

# Detect plates
plate_results = plate_model(image)

# Detect characters
char_results = char_model(image)
```

### 3. Running Detection Scripts

**Entry Camera Detection:**
```bash
cd backend/src
python detect_entry.py
```

**Exit Camera Detection:**
```bash
cd backend/src
python detect_exit.py
```

## Model Details

### Plate Detection Model (plateYolo.pt)
- **Size:** 13.7 MB
- **Purpose:** Detects license plate regions in images
- **Input:** Full image (any resolution)
- **Output:** Bounding boxes of detected plates

### Character Detection Model (CharsYolo.pt)
- **Size:** 13.9 MB
- **Purpose:** Detects individual characters on a license plate
- **Input:** Cropped plate image (typically 320x80)
- **Output:** Bounding boxes and class labels for each character

## How the System Works

### Entry Detection Flow:
1. Camera captures frame
2. Plate model detects plate regions
3. For each plate, crop the region
4. Character model detects characters in the cropped plate
5. Characters are sorted left-to-right and combined into text
6. Text is validated and formatted (Persian/Arabic support)
7. Entry is recorded in database

### Exit Detection Flow:
Same as entry, but records exit time and calculates parking duration/cost

## Troubleshooting

### Issue: "Model file not found"
**Solution:** Ensure `.pt` files are in `backend/src/`
```bash
ls backend/src/*.pt
```

### Issue: "CUDA not available"
**Solution:** Models will use CPU (slower but works)
- For GPU support, install CUDA-compatible PyTorch
- Current setup uses CPU by default

### Issue: "Module not found" errors
**Solution:** Reinstall dependencies
```bash
conda run -n parking pip install -r backend/src/requirements-clean.txt
```

### Issue: Models load but inference is slow
**Solution:** This is normal on CPU. For faster inference:
1. Use GPU (requires NVIDIA GPU + CUDA)
2. Reduce image resolution
3. Use model quantization

## Performance Notes

- **CPU Mode:** ~100-500ms per frame (depending on image size)
- **GPU Mode:** ~10-50ms per frame (with NVIDIA GPU)
- **Batch Processing:** Can process multiple images simultaneously

## Model Architecture

Both models are YOLOv5 variants:
- **Architecture:** YOLOv5s (small variant)
- **Framework:** PyTorch
- **Input Format:** RGB images (OpenCV uses BGR, auto-converted)
- **Output Format:** YOLO detection format (x, y, width, height, confidence, class)

## Character Classes

The character model recognizes:
- **Persian/Farsi letters:** آ، ب، پ، ت، ث، ج، چ، ح، خ، د، ذ، ر، ز، ژ، س، ش، ص، ض، ط، ظ، ع، غ، ف، ق، ک، گ، ل، م، ن، و، ه، ی
- **Digits:** 0-9

## License Plate Formats Supported

### National Plates (ملی)
Format: `XX Y XXX XX`
- 2 digits + 1 Persian letter + 3 digits + 2 digits

### Free Zone Plates (مناطق آزاد)
Format: `XXXXX XX`
- 5 digits + 2 digits (region code)

## Next Steps

1. ✅ Models are loaded and tested
2. Run detection scripts with camera input
3. Integrate with database for recording entries/exits
4. Set up web API for remote access
5. Deploy to production

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review detection script logs
3. Test models with `python yolo_loader.py`
4. Check camera connectivity
