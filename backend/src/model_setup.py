"""
Model Setup and Loading Utilities
Handles downloading and loading YOLO models for plate and character detection
"""

import os
import torch
import cv2
from pathlib import Path

# Model paths
MODELS_DIR = Path(__file__).parent / "models"
PLATE_MODEL_PATH = MODELS_DIR / "plateYolo.pt"
CHAR_MODEL_PATH = MODELS_DIR / "CharsYolo.pt"


def ensure_models_exist():
    """Check if model files exist in the expected location"""
    MODELS_DIR.mkdir(exist_ok=True)
    
    missing = []
    if not PLATE_MODEL_PATH.exists():
        missing.append(f"Plate model: {PLATE_MODEL_PATH}")
    if not CHAR_MODEL_PATH.exists():
        missing.append(f"Character model: {CHAR_MODEL_PATH}")
    
    if missing:
        print("⚠ Missing model files:")
        for m in missing:
            print(f"  - {m}")
        print("\nPlease ensure the .pt files are in the models directory")
        return False
    
    return True


def load_plate_model(device="cpu"):
    """
    Load the plate detection YOLO model
    
    Args:
        device: "cpu" or "cuda"
    
    Returns:
        Loaded model or None if failed
    """
    try:
        if not PLATE_MODEL_PATH.exists():
            print(f"Error: Plate model not found at {PLATE_MODEL_PATH}")
            return None
        
        print(f"Loading plate model from {PLATE_MODEL_PATH}...")
        
        # Load using ultralytics (YOLOv8 style)
        try:
            from ultralytics import YOLO
            model = YOLO(str(PLATE_MODEL_PATH))
            model.to(device)
            print("✓ Plate model loaded successfully (ultralytics)")
            return model
        except ImportError:
            # Fallback to torch hub (YOLOv5 style)
            print("Falling back to torch hub...")
            model = torch.hub.load(
                "ultralytics/yolov5",
                "custom",
                path=str(PLATE_MODEL_PATH),
                force_reload=False
            )
            model.to(device)
            model.eval()
            print("✓ Plate model loaded successfully (torch hub)")
            return model
            
    except Exception as e:
        print(f"Error loading plate model: {e}")
        return None


def load_char_model(device="cpu"):
    """
    Load the character detection YOLO model
    
    Args:
        device: "cpu" or "cuda"
    
    Returns:
        Loaded model or None if failed
    """
    try:
        if not CHAR_MODEL_PATH.exists():
            print(f"Error: Character model not found at {CHAR_MODEL_PATH}")
            return None
        
        print(f"Loading character model from {CHAR_MODEL_PATH}...")
        
        # Load using ultralytics (YOLOv8 style)
        try:
            from ultralytics import YOLO
            model = YOLO(str(CHAR_MODEL_PATH))
            model.to(device)
            print("✓ Character model loaded successfully (ultralytics)")
            return model
        except ImportError:
            # Fallback to torch hub (YOLOv5 style)
            print("Falling back to torch hub...")
            model = torch.hub.load(
                "ultralytics/yolov5",
                "custom",
                path=str(CHAR_MODEL_PATH),
                force_reload=False
            )
            model.to(device)
            model.eval()
            print("✓ Character model loaded successfully (torch hub)")
            return model
            
    except Exception as e:
        print(f"Error loading character model: {e}")
        return None


def get_device():
    """Get the best available device (CUDA or CPU)"""
    if torch.cuda.is_available():
        device = "cuda"
        print(f"✓ CUDA available - Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = "cpu"
        print("⚠ CUDA not available - Using CPU (slower)")
    
    return device


def test_models():
    """Test if models can be loaded successfully"""
    print("\n" + "="*60)
    print("Testing Model Loading")
    print("="*60 + "\n")
    
    if not ensure_models_exist():
        print("\n❌ Models not found. Please add .pt files to backend/src/models/")
        return False
    
    device = get_device()
    print()
    
    # Test plate model
    plate_model = load_plate_model(device)
    if plate_model is None:
        print("❌ Failed to load plate model")
        return False
    
    print()
    
    # Test character model
    char_model = load_char_model(device)
    if char_model is None:
        print("❌ Failed to load character model")
        return False
    
    print("\n" + "="*60)
    print("✓ All models loaded successfully!")
    print("="*60 + "\n")
    
    return True


if __name__ == "__main__":
    test_models()
