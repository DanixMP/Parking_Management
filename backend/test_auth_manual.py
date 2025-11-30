"""
Manual test script for authentication API.
Run Django server first, then run this script.
"""

import requests
import json

BASE_URL = 'http://localhost:8000/api'

def test_authentication():
    """Test authentication endpoints."""
    print("=" * 60)
    print("Testing Authentication System")
    print("=" * 60)
    
    # Test 1: Login with valid phone number
    print("\n1. Testing login with valid phone number...")
    response = requests.post(
        f'{BASE_URL}/auth/login/',
        json={'phone_number': '09123456789'}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        token = response.json()['token']
        print(f"✓ Login successful! Token: {token[:20]}...")
    else:
        print("✗ Login failed!")
        return
    
    # Test 2: Get current user with token
    print("\n2. Testing get current user with token...")
    response = requests.get(
        f'{BASE_URL}/auth/me/',
        headers={'Authorization': f'Token {token}'}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✓ Get current user successful!")
    else:
        print("✗ Get current user failed!")
    
    # Test 3: Get current user without token
    print("\n3. Testing get current user without token...")
    response = requests.get(f'{BASE_URL}/auth/me/')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 401:
        print("✓ Correctly rejected unauthenticated request!")
    else:
        print("✗ Should have rejected unauthenticated request!")
    
    # Test 4: Login with invalid phone number
    print("\n4. Testing login with invalid phone number...")
    response = requests.post(
        f'{BASE_URL}/auth/login/',
        json={'phone_number': 'invalid'}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 400:
        print("✓ Correctly rejected invalid phone number!")
    else:
        print("✗ Should have rejected invalid phone number!")
    
    # Test 5: Logout
    print("\n5. Testing logout...")
    response = requests.post(
        f'{BASE_URL}/auth/logout/',
        headers={'Authorization': f'Token {token}'}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✓ Logout successful!")
    else:
        print("✗ Logout failed!")
    
    # Test 6: Try to use token after logout
    print("\n6. Testing token after logout...")
    response = requests.get(
        f'{BASE_URL}/auth/me/',
        headers={'Authorization': f'Token {token}'}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 401:
        print("✓ Token correctly invalidated after logout!")
    else:
        print("✗ Token should be invalid after logout!")
    
    # Test 7: Login idempotency
    print("\n7. Testing login idempotency...")
    response1 = requests.post(
        f'{BASE_URL}/auth/login/',
        json={'phone_number': '09987654321'}
    )
    user_id_1 = response1.json()['user']['id']
    
    response2 = requests.post(
        f'{BASE_URL}/auth/login/',
        json={'phone_number': '09987654321'}
    )
    user_id_2 = response2.json()['user']['id']
    
    print(f"First login user ID: {user_id_1}")
    print(f"Second login user ID: {user_id_2}")
    
    if user_id_1 == user_id_2:
        print("✓ Login is idempotent - same user returned!")
    else:
        print("✗ Login should return same user!")
    
    print("\n" + "=" * 60)
    print("Authentication tests complete!")
    print("=" * 60)


if __name__ == '__main__':
    try:
        test_authentication()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Django server.")
        print("Please start the Django server first:")
        print("  cd backend")
        print("  python manage.py runserver")
