"""
Test Django API with Image Upload
Tests the YOLO detection endpoints with actual images
"""

import requests
import sys
from pathlib import Path

API_BASE = "http://localhost:8000/api"

def test_detect_plate(image_path):
    """Test plate detection endpoint"""
    print(f"\nTesting plate detection with: {image_path}")
    print("-" * 70)
    
    if not Path(image_path).exists():
        print(f"✗ Image not found: {image_path}")
        return
    
    url = f"{API_BASE}/detect-plate/"
    
    with open(image_path, 'rb') as f:
        files = {'image': f}
        
        try:
            response = requests.post(url, files=files, timeout=30)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"\n✓ Plate detected: {data.get('plate')}")
                    print(f"  Confidence: {data.get('confidence', 0):.2%}")
                    print(f"  BBox: {data.get('bbox')}")
                else:
                    print(f"\n✗ Detection failed: {data.get('error')}")
            else:
                print(f"\n✗ Request failed")
                
        except requests.exceptions.ConnectionError:
            print("✗ Could not connect to server")
            print("  Make sure Django server is running: python backend/manage.py runserver 8000")
        except Exception as e:
            print(f"✗ Error: {e}")


def test_detect_entry(image_path):
    """Test detect and register entry endpoint"""
    print(f"\nTesting entry detection with: {image_path}")
    print("-" * 70)
    
    if not Path(image_path).exists():
        print(f"✗ Image not found: {image_path}")
        return
    
    url = f"{API_BASE}/detect-entry/"
    
    with open(image_path, 'rb') as f:
        files = {'image': f}
        
        try:
            response = requests.post(url, files=files, timeout=30)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            
            if response.status_code == 201:
                data = response.json()
                print(f"\n✓ Entry registered!")
                print(f"  Plate: {data.get('plate')}")
                print(f"  Entry ID: {data.get('entry_id')}")
                print(f"  Confidence: {data.get('confidence', 0):.2%}")
            else:
                print(f"\n✗ Entry registration failed")
                
        except requests.exceptions.ConnectionError:
            print("✗ Could not connect to server")
            print("  Make sure Django server is running: python backend/manage.py runserver 8000")
        except Exception as e:
            print(f"✗ Error: {e}")


def test_detect_exit(image_path):
    """Test detect and register exit endpoint"""
    print(f"\nTesting exit detection with: {image_path}")
    print("-" * 70)
    
    if not Path(image_path).exists():
        print(f"✗ Image not found: {image_path}")
        return
    
    url = f"{API_BASE}/detect-exit/"
    
    with open(image_path, 'rb') as f:
        files = {'image': f}
        
        try:
            response = requests.post(url, files=files, timeout=30)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✓ Exit registered!")
                print(f"  Plate: {data.get('plate')}")
                print(f"  Duration: {data.get('duration')} minutes")
                print(f"  Cost: {data.get('cost')} IQD")
                print(f"  Confidence: {data.get('confidence', 0):.2%}")
            else:
                print(f"\n✗ Exit registration failed")
                
        except requests.exceptions.ConnectionError:
            print("✗ Could not connect to server")
            print("  Make sure Django server is running: python backend/manage.py runserver 8000")
        except Exception as e:
            print(f"✗ Error: {e}")


def test_parking_status():
    """Test parking status endpoint"""
    print(f"\nTesting parking status...")
    print("-" * 70)
    
    url = f"{API_BASE}/status/"
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ Parking Status:")
            print(f"  Capacity: {data.get('capacity')}")
            print(f"  Active Cars: {data.get('active_cars')}")
            print(f"  Free Slots: {data.get('free_slots')}")
            print(f"  Price/Hour: {data.get('price_per_hour')} IQD")
        else:
            print(f"\n✗ Request failed")
            
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server")
        print("  Make sure Django server is running: python backend/manage.py runserver 8000")
    except Exception as e:
        print(f"✗ Error: {e}")


def main():
    print("=" * 70)
    print("Django API Test with Images")
    print("=" * 70)
    
    # Test parking status first (doesn't need image)
    test_parking_status()
    
    # Check for test images
    if len(sys.argv) < 2:
        print("\n" + "=" * 70)
        print("Usage:")
        print("  python backend/test_api_with_image.py <image_path>")
        print("\nExample:")
        print("  python backend/test_api_with_image.py test_plate.jpg")
        print("\nThis will test all three detection endpoints with the image")
        print("=" * 70)
        return
    
    image_path = sys.argv[1]
    
    # Test all endpoints
    test_detect_plate(image_path)
    test_detect_entry(image_path)
    
    # For exit, you need a car already in the system
    print("\n" + "=" * 70)
    print("Note: To test exit detection, first register an entry,")
    print("then use the same plate image for exit detection")
    print("=" * 70)
    
    # Uncomment to test exit
    # test_detect_exit(image_path)


if __name__ == "__main__":
    main()
