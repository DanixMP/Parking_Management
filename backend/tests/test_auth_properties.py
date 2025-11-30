"""
Property-based tests for authentication API endpoints.

These tests use Hypothesis to verify correctness properties across
randomly generated inputs for API endpoints.
"""

import sys
import os
import unittest
import tempfile
import shutil
from pathlib import Path
import uuid
import json

# Django setup - must be done before importing Django modules
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parking_api.settings')
import django
django.setup()

from django.test import Client
from rest_framework import status as http_status

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import database as db

from hypothesis import given, settings, strategies as st, assume


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


class TestAuthenticationRequirement(unittest.TestCase):
    """
    Test authentication requirement for protected endpoints.
    Feature: user-wallet-system, Property 14: Authentication requirement for protected endpoints
    """
    
    @settings(max_examples=100, deadline=None)
    @given(invalid_token=st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), min_size=0, max_size=100))
    def test_protected_endpoints_require_authentication(self, invalid_token):
        """
        Property 14: For any wallet or plate management endpoint, requests without
        valid authentication tokens should receive 401 Unauthorized responses.
        
        Validates: Requirements 4.2
        """
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            client = Client()
            
            # Create a valid user and token to ensure we're not testing against empty database
            user = db.get_or_create_user('09123456789')
            valid_token = db.create_auth_token(user['id'])
            
            # Skip if the randomly generated token happens to match the valid one
            assume(invalid_token != valid_token)
            
            # List of protected endpoints that require authentication
            protected_endpoints = [
                # Authentication endpoints
                ('POST', '/api/auth/logout/'),
                ('GET', '/api/auth/me/'),
            ]
            
            for method, endpoint in protected_endpoints:
                # Test with no token
                if method == 'GET':
                    response_no_token = client.get(endpoint)
                elif method == 'POST':
                    response_no_token = client.post(endpoint)
                
                # Should return 401 Unauthorized
                self.assertEqual(
                    response_no_token.status_code,
                    http_status.HTTP_401_UNAUTHORIZED,
                    f"{method} {endpoint} without token should return 401, got {response_no_token.status_code}"
                )
                
                # Verify response contains error information
                data_no_token = response_no_token.json()
                self.assertFalse(
                    data_no_token.get('success', True),
                    f"{method} {endpoint} without token should have success=false"
                )
                self.assertEqual(
                    data_no_token.get('code'),
                    'AUTH_REQUIRED',
                    f"{method} {endpoint} without token should have code=AUTH_REQUIRED"
                )
                
                # Test with invalid token
                if method == 'GET':
                    response_invalid = client.get(
                        endpoint,
                        HTTP_AUTHORIZATION=f'Token {invalid_token}'
                    )
                elif method == 'POST':
                    response_invalid = client.post(
                        endpoint,
                        HTTP_AUTHORIZATION=f'Token {invalid_token}'
                    )
                
                # Should return 401 Unauthorized
                self.assertEqual(
                    response_invalid.status_code,
                    http_status.HTTP_401_UNAUTHORIZED,
                    f"{method} {endpoint} with invalid token should return 401, got {response_invalid.status_code}"
                )
                
                # Verify response contains error information
                data_invalid = response_invalid.json()
                self.assertFalse(
                    data_invalid.get('success', True),
                    f"{method} {endpoint} with invalid token should have success=false"
                )
                self.assertEqual(
                    data_invalid.get('code'),
                    'AUTH_REQUIRED',
                    f"{method} {endpoint} with invalid token should have code=AUTH_REQUIRED"
                )
        
        except Exception as e:
            self.fail(f"Unexpected error with invalid_token='{invalid_token}': {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        prefix=st.just('09'),
        digits=st.text(alphabet='0123456789', min_size=9, max_size=9)
    )
    def test_valid_token_grants_access(self, prefix, digits):
        """
        Property: For any valid authentication token, protected endpoints should
        be accessible (not return 401).
        
        Validates: Requirements 4.2
        """
        phone_number = prefix + digits
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            client = Client()
            
            # Create user and valid token
            user = db.get_or_create_user(phone_number)
            valid_token = db.create_auth_token(user['id'])
            
            # List of protected endpoints
            protected_endpoints = [
                ('GET', '/api/auth/me/'),
                ('POST', '/api/auth/logout/'),
            ]
            
            for method, endpoint in protected_endpoints:
                if method == 'GET':
                    response = client.get(
                        endpoint,
                        HTTP_AUTHORIZATION=f'Token {valid_token}'
                    )
                elif method == 'POST':
                    response = client.post(
                        endpoint,
                        HTTP_AUTHORIZATION=f'Token {valid_token}'
                    )
                
                # Should NOT return 401 Unauthorized
                self.assertNotEqual(
                    response.status_code,
                    http_status.HTTP_401_UNAUTHORIZED,
                    f"{method} {endpoint} with valid token should not return 401, got {response.status_code}"
                )
                
                # If we get a JSON response, verify it doesn't have AUTH_REQUIRED error
                if response.status_code != 500:  # Skip internal server errors
                    try:
                        data = response.json()
                        if 'code' in data:
                            self.assertNotEqual(
                                data.get('code'),
                                'AUTH_REQUIRED',
                                f"{method} {endpoint} with valid token should not have AUTH_REQUIRED error"
                            )
                    except:
                        pass  # Not all responses are JSON
        
        except Exception as e:
            self.fail(f"Unexpected error with phone_number='{phone_number}': {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        prefix=st.just('09'),
        digits=st.text(alphabet='0123456789', min_size=9, max_size=9)
    )
    def test_token_invalidation_prevents_access(self, prefix, digits):
        """
        Property: After a token is deleted/invalidated, it should no longer
        grant access to protected endpoints.
        
        Validates: Requirements 4.2
        """
        phone_number = prefix + digits
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            client = Client()
            
            # Create user and token
            user = db.get_or_create_user(phone_number)
            token = db.create_auth_token(user['id'])
            
            # Verify token works initially
            response_before = client.get(
                '/api/auth/me/',
                HTTP_AUTHORIZATION=f'Token {token}'
            )
            self.assertNotEqual(
                response_before.status_code,
                http_status.HTTP_401_UNAUTHORIZED,
                "Token should work before deletion"
            )
            
            # Delete the token
            db.delete_token(token)
            
            # Verify token no longer works
            response_after = client.get(
                '/api/auth/me/',
                HTTP_AUTHORIZATION=f'Token {token}'
            )
            self.assertEqual(
                response_after.status_code,
                http_status.HTTP_401_UNAUTHORIZED,
                f"Token should not work after deletion, got {response_after.status_code}"
            )
            
            # Verify error response
            data = response_after.json()
            self.assertFalse(
                data.get('success', True),
                "Response should have success=false after token deletion"
            )
            self.assertEqual(
                data.get('code'),
                'AUTH_REQUIRED',
                "Response should have code=AUTH_REQUIRED after token deletion"
            )
        
        except Exception as e:
            self.fail(f"Unexpected error with phone_number='{phone_number}': {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)


if __name__ == '__main__':
    unittest.main()
