"""
Simple script to test the Django API endpoints
Run this after starting the Django server
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_status():
    """Test parking status endpoint"""
    print("\n=== Testing Status Endpoint ===")
    response = requests.get(f"{BASE_URL}/status/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_settings():
    """Test settings endpoint"""
    print("\n=== Testing Settings Endpoint ===")
    response = requests.get(f"{BASE_URL}/settings/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_active_cars():
    """Test active cars endpoint"""
    print("\n=== Testing Active Cars Endpoint ===")
    response = requests.get(f"{BASE_URL}/active-cars/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_entries():
    """Test entries endpoint"""
    print("\n=== Testing Entries Endpoint ===")
    response = requests.get(f"{BASE_URL}/entries/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_exits():
    """Test exits endpoint"""
    print("\n=== Testing Exits Endpoint ===")
    response = requests.get(f"{BASE_URL}/exits/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def main():
    print("=" * 50)
    print("Django API Test Suite")
    print("=" * 50)
    print("\nMake sure the Django server is running on port 8000!")
    print("Run: python manage.py runserver 8000")
    
    try:
        tests = [
            ("Status", test_status),
            ("Settings", test_settings),
            ("Active Cars", test_active_cars),
            ("Entries", test_entries),
            ("Exits", test_exits),
        ]
        
        results = []
        for name, test_func in tests:
            try:
                success = test_func()
                results.append((name, success))
            except Exception as e:
                print(f"Error in {name}: {e}")
                results.append((name, False))
        
        print("\n" + "=" * 50)
        print("Test Results Summary")
        print("=" * 50)
        for name, success in results:
            status = "✓ PASS" if success else "✗ FAIL"
            print(f"{name}: {status}")
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        print(f"\nTotal: {passed}/{total} tests passed")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the server!")
        print("Make sure Django server is running on http://localhost:8000")

if __name__ == "__main__":
    main()
