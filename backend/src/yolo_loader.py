"""
Direct YOLO Model Loader
Loads YOLOv5 models using the yolov5 package
"""

import torch
import os
from pathlib import Path
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Patch torch.load to handle weights_only issue
_original_torch_load = torch.load

def _patched_torch_load(f, *args, **kwargs):
    """Patched torch.load that disables weights_only for compatibility"""
    kwargs['weights_only'] = False
    return _original_torch_load(f, *args, **kwargs)

torch.load = _patched_torch_load

try:
    import yolov5
    YOLOV5_AVAILABLE = True
except ImportError:
    YOLOV5_AVAILABLE = False


def load_yolo_model(model_path, device="cpu"):
    """
    Load a YOLOv5 model directly from a .pt file
    
    Args:
        model_path: Path to the .pt file
        device: "cpu" or "cuda"
    
    Returns:
        Loaded model
    """
    model_path = Path(model_path)
    
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    print(f"Loading model from {model_path}...")
    
    if not YOLOV5_AVAILABLE:
        raise ImportError("yolov5 package not installed. Install with: pip install yolov5")
    
    # Use yolov5 package to load the model
    model = yolov5.load(str(model_path), device=device)
    model.eval()
    
    print(f"✓ Model loaded successfully on {device}")
    return model


def load_plate_model(device="cpu"):
    """Load plate detection model"""
    model_path = Path(__file__).parent / "plateYolo.pt"
    return load_yolo_model(model_path, device)


def load_char_model(device="cpu"):
    """Load character detection model"""
    model_path = Path(__file__).parent / "CharsYolo.pt"
    return load_yolo_model(model_path, device)


if __name__ == "__main__":
    print("Testing YOLO model loading...\n")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}\n")
    
    try:
        print("Loading plate model...")
        plate_model = load_plate_model(device)
        print(f"Plate model: {plate_model}\n")
        
        print("Loading character model...")
        char_model = load_char_model(device)
        print(f"Character model: {char_model}\n")
        
        print("✓ All models loaded successfully!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
