"""
Integration tests for authentication API endpoints.
"""

import sys
import os
import unittest
import tempfile
import shutil
from pathlib import Path
import uuid
import json

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parking_api.settings')
import django
django.setup()

from django.test import Client
from rest_framework import status

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import database as db


def setup_test_db():
    """Create a fresh test database and return its path."""
    test_dir = tempfile.mkdtemp()
    db_name = f"test_parking_{uuid.uuid4().hex}.db"
    db_path = Path(test_dir) / db_name
    
    # Save original path
    original_path = db.DB_PATH
    
    # Set new path and initialize
    db.DB_PATH = db_path
    db.init_db()
    
    return db_path, original_path, test_dir


def cleanup_test_db(db_path, original_path, test_dir):
    """Clean up test database and restore original path."""
    db.DB_PATH = original_path
    
    # Remove database file
    if db_path.exists():
        db_path.unlink()
    
    # Remove temp directory
    shutil.rmtree(test_dir, ignore_errors=True)


class TestAuthenticationAPI(unittest.TestCase):
    """Test authentication API endpoints."""
    
    def setUp(self):
        """Set up test client and database."""
        self.client = Client()
        self.db_path, self.original_path, self.test_dir = setup_test_db()
    
    def tearDown(self):
        """Clean up test database."""
        cleanup_test_db(self.db_path, self.original_path, self.test_dir)
    
    def test_login_with_valid_phone(self):
        """Test login with valid phone number."""
        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'phone_number': '09123456789'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('token', data)
        self.assertIn('user', data)
        self.assertIn('wallet', data)
        
        # Verify user data
        self.assertEqual(data['user']['phone_number'], '09123456789')
        self.assertEqual(data['user']['role'], 'user')
        
        # Verify wallet data
        self.assertEqual(data['wallet']['balance'], 0)
    
    def test_login_with_invalid_phone(self):
        """Test login with invalid phone number format."""
        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'phone_number': 'invalid'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('error', data)
        self.assertEqual(data['code'], 'INVALID_PHONE_FORMAT')
    
    def test_login_idempotency(self):
        """Test that logging in multiple times with same phone returns same user."""
        phone = '09123456789'
        
        # First login
        response1 = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'phone_number': phone}),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        data1 = response1.json()
        user_id_1 = data1['user']['id']
        
        # Second login
        response2 = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'phone_number': phone}),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        data2 = response2.json()
        user_id_2 = data2['user']['id']
        
        # Should return same user ID
        self.assertEqual(user_id_1, user_id_2)
        
        # Tokens should be different (new session)
        self.assertNotEqual(data1['token'], data2['token'])
    
    def test_get_current_user_authenticated(self):
        """Test getting current user with valid token."""
        # Login first
        login_response = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'phone_number': '09123456789'}),
            content_type='application/json'
        )
        token = login_response.json()['token']
        
        # Get current user
        response = self.client.get(
            '/api/auth/me/',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('user', data)
        self.assertIn('wallet', data)
        self.assertEqual(data['user']['phone_number'], '09123456789')
    
    def test_get_current_user_unauthenticated(self):
        """Test getting current user without token."""
        response = self.client.get('/api/auth/me/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['code'], 'AUTH_REQUIRED')
    
    def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token."""
        response = self.client.get(
            '/api/auth/me/',
            HTTP_AUTHORIZATION='Token invalid_token_12345'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['code'], 'AUTH_REQUIRED')
    
    def test_logout_authenticated(self):
        """Test logout with valid token."""
        # Login first
        login_response = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'phone_number': '09123456789'}),
            content_type='application/json'
        )
        token = login_response.json()['token']
        
        # Logout
        response = self.client.post(
            '/api/auth/logout/',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertTrue(data['success'])
        
        # Token should no longer be valid
        me_response = self.client.get(
            '/api/auth/me/',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        self.assertEqual(me_response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_logout_unauthenticated(self):
        """Test logout without token."""
        response = self.client.post('/api/auth/logout/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['code'], 'AUTH_REQUIRED')
    
    def test_login_missing_phone_number(self):
        """Test login without phone number."""
        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['code'], 'INVALID_REQUEST')


if __name__ == '__main__':
    unittest.main()
