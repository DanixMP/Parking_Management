#!/usr/bin/env python
"""
Example: How to use YOLO models for plate and character detection

This script demonstrates:
1. Loading the models
2. Running inference on an image
3. Processing the results
4. Displaying detections
"""

import cv2
import torch
import numpy as np
from pathlib import Path
from yolo_loader import load_plate_model, load_char_model


def example_with_webcam():
    """Example: Real-time detection from webcam"""
    print("\n" + "="*70)
    print("YOLO Detection Example - Webcam")
    print("="*70)
    print("Press 'q' to quit\n")
    
    # Setup
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}\n")
    
    # Load models
    print("Loading models...")
    plate_model = load_plate_model(device)
    char_model = load_char_model(device)
    print("✓ Models loaded\n")
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot open webcam")
        return
    
    print("Starting detection (press 'q' to quit)...\n")
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Resize for faster processing (optional)
        display_frame = frame.copy()
        h, w = frame.shape[:2]
        
        # Detect plates
        plate_results = plate_model(frame)
        plate_dets = plate_results.xyxy[0].cpu().numpy()
        
        # Draw plate detections
        for *xyxy, conf, cls in plate_dets:
            if conf < 0.5:  # Confidence threshold
                continue
            
            x1, y1, x2, y2 = map(int, xyxy)
            
            # Draw bounding box
            cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw confidence
            text = f"Plate: {conf:.2f}"
            cv2.putText(display_frame, text, (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Crop plate region
            plate_crop = frame[y1:y2, x1:x2]
            if plate_crop.size > 0:
                # Resize to standard size for character detection
                plate_resized = cv2.resize(plate_crop, (320, 80))
                
                # Detect characters
                char_results = char_model(plate_resized)
                char_dets = char_results.xyxy[0].cpu().numpy()
                
                # Extract character info
                if len(char_dets) > 0:
                    char_dets = sorted(char_dets, key=lambda x: x[0])  # Sort by x
                    char_names = char_model.names
                    chars = [char_names[int(cls)] for *_, cls in char_dets]
                    plate_text = "".join(chars)
                    
                    # Show character detections on cropped plate
                    plate_display = plate_resized.copy()
                    for *xyxy, conf, cls in char_dets:
                        if conf < 0.5:
                            continue
                        x1c, y1c, x2c, y2c = map(int, xyxy)
                        cv2.rectangle(plate_display, (x1c, y1c), (x2c, y2c),
                                    (255, 0, 0), 1)
                    
                    # Show plate crop in corner
                    h_crop, w_crop = plate_display.shape[:2]
                    display_frame[0:h_crop, 0:w_crop] = plate_display
        
        # Display info
        info_text = f"Frame: {frame_count} | Plates: {len(plate_dets)}"
        cv2.putText(display_frame, info_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Show frame
        cv2.imshow("YOLO Detection Example", display_frame)
        
        # Check for quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"\nProcessed {frame_count} frames")


def example_with_image(image_path):
    """Example: Detection on a single image"""
    print("\n" + "="*70)
    print(f"YOLO Detection Example - Image: {image_path}")
    print("="*70 + "\n")
    
    # Check if file exists
    if not Path(image_path).exists():
        print(f"Error: Image not found: {image_path}")
        return
    
    # Setup
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}\n")
    
    # Load models
    print("Loading models...")
    plate_model = load_plate_model(device)
    char_model = load_char_model(device)
    print("✓ Models loaded\n")
    
    # Load image
    print(f"Loading image: {image_path}")
    frame = cv2.imread(image_path)
    if frame is None:
        print("Error: Cannot load image")
        return
    print(f"✓ Image loaded: {frame.shape}\n")
    
    # Detect plates
    print("Detecting plates...")
    plate_results = plate_model(frame)
    plate_dets = plate_results.xyxy[0].cpu().numpy()
    print(f"✓ Found {len(plate_dets)} plate(s)\n")
    
    # Process each plate
    display_frame = frame.copy()
    for idx, (*xyxy, conf, cls) in enumerate(plate_dets):
        if conf < 0.5:
            continue
        
        x1, y1, x2, y2 = map(int, xyxy)
        print(f"Plate {idx+1}:")
        print(f"  Position: ({x1}, {y1}) to ({x2}, {y2})")
        print(f"  Confidence: {conf:.2%}")
        
        # Draw bounding box
        cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Crop and detect characters
        plate_crop = frame[y1:y2, x1:x2]
        if plate_crop.size > 0:
            plate_resized = cv2.resize(plate_crop, (320, 80))
            
            # Detect characters
            char_results = char_model(plate_resized)
            char_dets = char_results.xyxy[0].cpu().numpy()
            
            if len(char_dets) > 0:
                char_dets = sorted(char_dets, key=lambda x: x[0])
                char_names = char_model.names
                chars = [char_names[int(cls)] for *_, cls in char_dets]
                plate_text = "".join(chars)
                
                print(f"  Characters detected: {len(char_dets)}")
                print(f"  Plate text: {plate_text}")
                
                # Draw on frame
                cv2.putText(display_frame, plate_text, (x1, y1-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        print()
    
    # Display result
    cv2.imshow("Detection Result", display_frame)
    print("Press any key to close...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*70)
    print("YOLO Model Detection Examples")
    print("="*70)
    
    if len(sys.argv) > 1:
        # Use provided image
        example_with_image(sys.argv[1])
    else:
        # Use webcam
        print("\nNo image provided. Using webcam...")
        print("Usage: python example_detection.py <image_path>")
        print()
        example_with_webcam()
