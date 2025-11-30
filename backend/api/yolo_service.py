"""
YOLO Detection Service for Django
Handles license plate detection and character recognition
"""

import sys
import os
from pathlib import Path
import cv2
import numpy as np
import torch
import re
from collections import Counter

# Add src directory to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from yolo_loader import load_plate_model, load_char_model

# Global model cache
_plate_model = None
_char_model = None
_device = None


def get_device():
    """Get the best available device"""
    global _device
    if _device is None:
        _device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {_device}")
    return _device


def get_plate_model():
    """Get or load the plate detection model"""
    global _plate_model
    if _plate_model is None:
        print("Loading plate detection model...")
        _plate_model = load_plate_model(device=get_device())
        print("✓ Plate model loaded")
    return _plate_model


def get_char_model():
    """Get or load the character recognition model"""
    global _char_model
    if _char_model is None:
        print("Loading character recognition model...")
        _char_model = load_char_model(device=get_device())
        print("✓ Character model loaded")
    return _char_model


def detect_plate_in_image(image_bytes):
    """
    Detect license plate in image bytes
    
    Args:
        image_bytes: Image file bytes
        
    Returns:
        dict with 'success', 'plate', 'confidence', 'error'
    """
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return {
                'success': False,
                'error': 'Invalid image format'
            }
        
        # Detect plate region
        plate_model = get_plate_model()
        results = plate_model(img)
        
        # Handle yolov5 package results format
        detections = results.pred[0] if hasattr(results, 'pred') else results.xyxy[0]
        
        if len(detections) == 0:
            return {
                'success': False,
                'error': 'No plate detected in image'
            }
        
        # Get the plate with highest confidence
        detections_np = detections.cpu().numpy() if torch.is_tensor(detections) else detections
        best_detection = max(detections_np, key=lambda x: x[4])
        x1, y1, x2, y2, conf, cls = best_detection
        
        # Crop plate region
        plate_img = img[int(y1):int(y2), int(x1):int(x2)]
        
        # Recognize characters
        plate_text = recognize_characters(plate_img)
        
        if not plate_text:
            return {
                'success': False,
                'error': 'Could not recognize plate characters'
            }
        
        return {
            'success': True,
            'plate': plate_text,
            'confidence': float(conf),
            'bbox': {
                'x1': int(x1),
                'y1': int(y1),
                'x2': int(x2),
                'y2': int(y2)
            }
        }
        
    except Exception as e:
        import traceback
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }


def recognize_characters(plate_img):
    """
    Recognize characters in a cropped plate image
    
    Args:
        plate_img: Cropped plate image (numpy array)
        
    Returns:
        str: Recognized plate text or None
    """
    try:
        char_model = get_char_model()
        results = char_model(plate_img)
        
        # Handle yolov5 package results format
        detections = results.pred[0] if hasattr(results, 'pred') else results.xyxy[0]
        
        if len(detections) == 0:
            return None
        
        detections_np = detections.cpu().numpy() if torch.is_tensor(detections) else detections
        
        # Sort by x-coordinate (left to right)
        detections_sorted = sorted(detections_np, key=lambda x: x[0])
        
        # Map class IDs to characters
        # This mapping depends on your model's training
        # Adjust based on your CharsYolo.pt model
        char_map = {
            0: '0', 1: '1', 2: '2', 3: '3', 4: '4',
            5: '5', 6: '6', 7: '7', 8: '8', 9: '9',
            10: 'الف', 11: 'ب', 12: 'پ', 13: 'ت', 14: 'ث',
            15: 'ج', 16: 'چ', 17: 'ح', 18: 'خ', 19: 'د',
            20: 'ذ', 21: 'ر', 22: 'ز', 23: 'ژ', 24: 'س',
            25: 'ش', 26: 'ص', 27: 'ض', 28: 'ط', 29: 'ظ',
            30: 'ع', 31: 'غ', 32: 'ف', 33: 'ق', 34: 'ک',
            35: 'گ', 36: 'ل', 37: 'م', 38: 'ن', 39: 'و',
            40: 'ه', 41: 'ی'
        }
        
        # Extract characters
        chars = []
        for det in detections_sorted:
            x1, y1, x2, y2, conf, cls = det
            if conf > 0.3:  # Confidence threshold
                char = char_map.get(int(cls), '?')
                chars.append(char)
        
        # Join characters
        plate_text = ''.join(chars)
        
        # Clean up the text
        plate_text = clean_plate_text(plate_text)
        
        return plate_text if plate_text else None
        
    except Exception as e:
        print(f"Error recognizing characters: {e}")
        import traceback
        traceback.print_exc()
        return None


def clean_plate_text(text):
    """Clean and format plate text"""
    if not text:
        return None
    
    # Remove extra spaces
    text = re.sub(r'\s+', '', text)
    
    # Basic validation - should have numbers and possibly Persian letters
    if len(text) < 5:
        return None
    
    return text


def preload_models():
    """Preload models at startup"""
    try:
        print("Preloading YOLO models...")
        get_plate_model()
        get_char_model()
        print("✓ All models preloaded successfully")
        return True
    except Exception as e:
        print(f"✗ Error preloading models: {e}")
        return False
