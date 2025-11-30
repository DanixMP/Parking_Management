"""
Property-based tests for cross-platform API consistency.

Feature: user-wallet-system, Property 19: Cross-platform API consistency
Validates: Requirements 6.1, 6.4

This test verifies that both mobile and web interfaces use the same API endpoints
with consistent URLs, HTTP methods, and request/response formats.
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
from hypothesis import given, settings, strategies as st

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


class TestCrossPlatformAPIConsistency(unittest.TestCase):
    """
    Test that API endpoints are consistent across platforms.
    
    Feature: user-wallet-system, Property 19: Cross-platform API consistency
    
    Property: For any API endpoint, both the mobile and web interfaces should use
    the same URL, HTTP method, and request/response format.
    """
    
    def setUp(self):
        """Set up test client and database."""
        self.client = Client()
        self.db_path, self.original_path, self.test_dir = setup_test_db()
        
        # Define expected API endpoints based on Flutter ApiService
        # Each entry: (method, path, requires_auth, request_fields, response_fields)
        self.api_endpoints = {
            # Authentication endpoints
            'login': {
                'method': 'POST',
                'path': '/api/auth/login/',
                'requires_auth': False,
                'request_fields': ['phone_number'],
                'response_fields': ['success', 'token', 'user', 'wallet'],
                'success_status': status.HTTP_200_OK
            },
            'logout': {
                'method': 'POST',
                'path': '/api/auth/logout/',
                'requires_auth': True,
                'request_fields': [],
                'response_fields': ['success'],
                'success_status': status.HTTP_200_OK
            },
            'get_current_user': {
                'method': 'GET',
                'path': '/api/auth/me/',
                'requires_auth': True,
                'request_fields': [],
                'response_fields': ['success', 'user', 'wallet'],
                'success_status': status.HTTP_200_OK
            },
            # Wallet endpoints
            'get_balance': {
                'method': 'GET',
                'path': '/api/wallet/balance/',
                'requires_auth': True,
                'request_fields': [],
                'response_fields': ['balance', 'last_updated'],
                'success_status': status.HTTP_200_OK
            },
            'charge_wallet': {
                'method': 'POST',
                'path': '/api/wallet/charge/',
                'requires_auth': True,
                'request_fields': ['amount'],
                'response_fields': ['success', 'new_balance', 'transaction_id'],
                'success_status': status.HTTP_200_OK
            },
            'get_transactions': {
                'method': 'GET',
                'path': '/api/wallet/transactions/',
                'requires_auth': True,
                'request_fields': [],
                'response_fields': ['count', 'results'],
                'success_status': status.HTTP_200_OK
            },
            # Plate endpoints
            'get_plates': {
                'method': 'GET',
                'path': '/api/plates/',
                'requires_auth': True,
                'request_fields': [],
                'response_fields': [],  # Returns array directly
                'success_status': status.HTTP_200_OK,
                'returns_array': True
            },
            'add_plate': {
                'method': 'POST',
                'path': '/api/plates/',
                'requires_auth': True,
                'request_fields': ['plate'],
                'response_fields': ['id', 'plate', 'registered_at'],
                'success_status': status.HTTP_201_CREATED
            },
            # Admin endpoints
            'get_all_users': {
                'method': 'GET',
                'path': '/api/admin/users/',
                'requires_auth': True,
                'request_fields': [],
                'response_fields': ['count', 'results'],
                'success_status': status.HTTP_200_OK,
                'requires_role': ['admin', 'superuser']
            },
        }
    
    def tearDown(self):
        """Clean up test database."""
        cleanup_test_db(self.db_path, self.original_path, self.test_dir)
    
    def _create_test_user_and_login(self, phone='09123456789'):
        """Helper to create a user and get auth token."""
        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'phone_number': phone}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.json()['token']
    
    def test_authentication_endpoint_consistency(self):
        """
        Test that authentication endpoints are consistent.
        
        Verifies that login, logout, and get_current_user endpoints
        use the expected URLs, methods, and response formats.
        """
        # Test login endpoint
        login_spec = self.api_endpoints['login']
        response = self.client.post(
            login_spec['path'],
            data=json.dumps({'phone_number': '09123456789'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, login_spec['success_status'])
        data = response.json()
        
        # Verify all expected response fields are present
        for field in login_spec['response_fields']:
            self.assertIn(field, data, f"Missing field '{field}' in login response")
        
        # Test get_current_user endpoint
        token = data['token']
        me_spec = self.api_endpoints['get_current_user']
        response = self.client.get(
            me_spec['path'],
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        
        self.assertEqual(response.status_code, me_spec['success_status'])
        data = response.json()
        
        for field in me_spec['response_fields']:
            self.assertIn(field, data, f"Missing field '{field}' in get_current_user response")
        
        # Test logout endpoint
        logout_spec = self.api_endpoints['logout']
        response = self.client.post(
            logout_spec['path'],
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        
        self.assertEqual(response.status_code, logout_spec['success_status'])
        data = response.json()
        
        for field in logout_spec['response_fields']:
            self.assertIn(field, data, f"Missing field '{field}' in logout response")
    
    def test_wallet_endpoint_consistency(self):
        """
        Test that wallet endpoints are consistent.
        
        Verifies that wallet balance, charge, and transactions endpoints
        use the expected URLs, methods, and response formats.
        """
        # Login first
        token = self._create_test_user_and_login('09123456789')
        
        # Test get_balance endpoint
        balance_spec = self.api_endpoints['get_balance']
        response = self.client.get(
            balance_spec['path'],
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        
        self.assertEqual(response.status_code, balance_spec['success_status'])
        data = response.json()
        
        for field in balance_spec['response_fields']:
            self.assertIn(field, data, f"Missing field '{field}' in get_balance response")
        
        # Test charge_wallet endpoint
        charge_spec = self.api_endpoints['charge_wallet']
        response = self.client.post(
            charge_spec['path'],
            data=json.dumps({'amount': 100000}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        
        self.assertEqual(response.status_code, charge_spec['success_status'])
        data = response.json()
        
        for field in charge_spec['response_fields']:
            self.assertIn(field, data, f"Missing field '{field}' in charge_wallet response")
        
        # Test get_transactions endpoint
        trans_spec = self.api_endpoints['get_transactions']
        response = self.client.get(
            trans_spec['path'],
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        
        self.assertEqual(response.status_code, trans_spec['success_status'])
        data = response.json()
        
        for field in trans_spec['response_fields']:
            self.assertIn(field, data, f"Missing field '{field}' in get_transactions response")
    
    def test_plate_endpoint_consistency(self):
        """
        Test that plate management endpoints are consistent.
        
        Verifies that get_plates and add_plate endpoints
        use the expected URLs, methods, and response formats.
        """
        # Login first
        token = self._create_test_user_and_login('09123456789')
        
        # Test get_plates endpoint
        plates_spec = self.api_endpoints['get_plates']
        response = self.client.get(
            plates_spec['path'],
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        
        self.assertEqual(response.status_code, plates_spec['success_status'])
        data = response.json()
        
        # Should return an array
        self.assertIsInstance(data, list, "get_plates should return an array")
        
        # Test add_plate endpoint
        add_spec = self.api_endpoints['add_plate']
        response = self.client.post(
            add_spec['path'],
            data=json.dumps({'plate': '12ب345-67'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        
        self.assertEqual(response.status_code, add_spec['success_status'])
        data = response.json()
        
        for field in add_spec['response_fields']:
            self.assertIn(field, data, f"Missing field '{field}' in add_plate response")
    
    @settings(max_examples=100)
    @given(phone_number=st.from_regex(r'^09\d{9}$', fullmatch=True))
    def test_login_response_format_consistency(self, phone_number):
        """
        Property test: For any valid phone number, login response format is consistent.
        
        This ensures that regardless of the phone number used, the API always
        returns the same structure, which is critical for cross-platform consistency.
        """
        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'phone_number': phone_number}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Verify consistent response structure
        self.assertIn('success', data)
        self.assertIn('token', data)
        self.assertIn('user', data)
        self.assertIn('wallet', data)
        
        # Verify user structure
        user = data['user']
        self.assertIn('id', user)
        self.assertIn('phone_number', user)
        self.assertIn('role', user)
        self.assertIn('created_at', user)
        
        # Verify wallet structure
        wallet = data['wallet']
        self.assertIn('id', wallet)
        self.assertIn('user_id', wallet)
        self.assertIn('balance', wallet)
        self.assertIn('last_updated', wallet)
    
    @settings(max_examples=50)
    @given(amount=st.integers(min_value=1000, max_value=10000000))
    def test_charge_wallet_response_format_consistency(self, amount):
        """
        Property test: For any valid charge amount, response format is consistent.
        
        This ensures that wallet charge operations return consistent structures
        across all platforms.
        """
        # Create a unique phone number for each test iteration
        import random
        phone = f'09{random.randint(100000000, 999999999)}'
        token = self._create_test_user_and_login(phone)
        
        # Get initial balance
        balance_response = self.client.get(
            '/api/wallet/balance/',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        initial_balance = balance_response.json()['balance']
        
        # Charge wallet
        response = self.client.post(
            '/api/wallet/charge/',
            data=json.dumps({'amount': amount}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Verify consistent response structure
        self.assertIn('success', data)
        self.assertIn('new_balance', data)
        self.assertIn('transaction_id', data)
        
        # Verify data types
        self.assertIsInstance(data['success'], bool)
        self.assertIsInstance(data['new_balance'], int)
        self.assertIsInstance(data['transaction_id'], int)
        
        # Verify balance is correct (initial + amount)
        self.assertEqual(data['new_balance'], initial_balance + amount)
    
    def test_error_response_format_consistency(self):
        """
        Test that error responses have consistent format across all endpoints.
        
        This is critical for cross-platform error handling.
        """
        # Test unauthenticated request to protected endpoint
        response = self.client.get('/api/wallet/balance/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        data = response.json()
        
        # Verify error response structure
        self.assertIn('success', data)
        self.assertFalse(data['success'])
        self.assertIn('code', data)
        self.assertIn('error', data)
        
        # Test invalid phone number format
        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'phone_number': 'invalid'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        
        # Verify error response structure
        self.assertIn('success', data)
        self.assertFalse(data['success'])
        self.assertIn('code', data)
        self.assertIn('error', data)
    
    def test_authentication_header_format_consistency(self):
        """
        Test that authentication header format is consistent.
        
        Verifies that the 'Token' authentication scheme works consistently
        across all protected endpoints.
        """
        # Login to get token
        token = self._create_test_user_and_login('09111111111')
        
        # Test various protected endpoints with same auth header format
        protected_endpoints = [
            ('GET', '/api/auth/me/'),
            ('GET', '/api/wallet/balance/'),
            ('GET', '/api/wallet/transactions/'),
            ('GET', '/api/plates/'),
        ]
        
        for method, path in protected_endpoints:
            if method == 'GET':
                response = self.client.get(
                    path,
                    HTTP_AUTHORIZATION=f'Token {token}'
                )
            elif method == 'POST':
                response = self.client.post(
                    path,
                    HTTP_AUTHORIZATION=f'Token {token}'
                )
            
            # All should succeed with proper authentication
            self.assertIn(
                response.status_code,
                [status.HTTP_200_OK, status.HTTP_201_CREATED],
                f"Endpoint {method} {path} failed with status {response.status_code}"
            )
    
    def test_content_type_consistency(self):
        """
        Test that all endpoints accept and return JSON with consistent content-type.
        
        This ensures that both mobile and web clients can use the same
        content negotiation strategy.
        """
        # Test login endpoint
        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'phone_number': '09222222222'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Verify response is valid JSON
        try:
            data = response.json()
            self.assertIsInstance(data, dict)
        except json.JSONDecodeError:
            self.fail("Response is not valid JSON")
    
    def test_http_method_consistency(self):
        """
        Test that endpoints use the correct HTTP methods as expected by clients.
        
        This verifies that the backend uses standard RESTful conventions
        that both mobile and web clients expect.
        """
        token = self._create_test_user_and_login('09333333333')
        
        # Test that GET endpoints don't accept POST
        response = self.client.post(
            '/api/wallet/balance/',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Test that POST endpoints don't accept GET
        response = self.client.get(
            '/api/wallet/charge/',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


if __name__ == '__main__':
    unittest.main()
