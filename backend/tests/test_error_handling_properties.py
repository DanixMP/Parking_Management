"""
Property-based tests for API error handling and response formatting.

These tests use Hypothesis to verify correctness properties across
randomly generated inputs for error handling and data filtering.
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


class TestSensitiveDataExclusion(unittest.TestCase):
    """
    Test that API responses exclude sensitive information.
    Feature: user-wallet-system, Property 15: Sensitive data exclusion
    """
    
    @settings(max_examples=100, deadline=None)
    @given(
        prefix=st.just('09'),
        digits=st.text(alphabet='0123456789', min_size=9, max_size=9)
    )
    def test_user_data_excludes_sensitive_fields(self, prefix, digits):
        """
        Property 15: For any API response containing user data, the response should
        not include internal fields such as password hashes or raw token values.
        
        Validates: Requirements 4.5
        """
        phone_number = prefix + digits
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            client = Client()
            
            # Create user and authenticate
            user = db.get_or_create_user(phone_number)
            token = db.create_auth_token(user['id'])
            
            # List of endpoints that return user data
            user_data_endpoints = [
                ('POST', '/api/auth/login/', {'phone_number': phone_number}),
                ('GET', '/api/auth/me/', None),
            ]
            
            # Sensitive fields that should NEVER appear in responses
            sensitive_fields = [
                'password',
                'password_hash',
                'hashed_password',
                'pwd',
                'secret',
                'private_key',
                'auth_token',  # The actual token value in user object
                'token_hash',
            ]
            
            for method, endpoint, data in user_data_endpoints:
                if method == 'GET':
                    response = client.get(
                        endpoint,
                        HTTP_AUTHORIZATION=f'Token {token}'
                    )
                elif method == 'POST':
                    response = client.post(
                        endpoint,
                        data=json.dumps(data) if data else None,
                        content_type='application/json'
                    )
                
                # Should return success
                self.assertIn(
                    response.status_code,
                    [http_status.HTTP_200_OK, http_status.HTTP_201_CREATED],
                    f"{method} {endpoint} should return 200/201, got {response.status_code}"
                )
                
                # Parse response
                response_data = response.json()
                
                # Convert response to string to check for sensitive field names
                response_str = json.dumps(response_data).lower()
                
                # Check that no sensitive fields appear in the response
                for sensitive_field in sensitive_fields:
                    self.assertNotIn(
                        f'"{sensitive_field}"',
                        response_str,
                        f"{method} {endpoint} response should not contain sensitive field '{sensitive_field}'"
                    )
                
                # If response contains user object, verify it has expected safe fields
                if 'user' in response_data:
                    user_obj = response_data['user']
                    
                    # Should have safe fields
                    safe_fields = ['id', 'phone_number', 'role', 'created_at', 'is_active']
                    for safe_field in safe_fields:
                        self.assertIn(
                            safe_field,
                            user_obj,
                            f"User object should contain safe field '{safe_field}'"
                        )
                    
                    # Should NOT have sensitive fields
                    for sensitive_field in sensitive_fields:
                        self.assertNotIn(
                            sensitive_field,
                            user_obj,
                            f"User object should not contain sensitive field '{sensitive_field}'"
                        )
        
        except Exception as e:
            self.fail(f"Unexpected error with phone_number='{phone_number}': {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        prefix=st.just('09'),
        digits=st.text(alphabet='0123456789', min_size=9, max_size=9)
    )
    def test_admin_endpoints_exclude_sensitive_data(self, prefix, digits):
        """
        Property: Admin endpoints that return user lists should also exclude
        sensitive information from all user records.
        
        Validates: Requirements 4.5
        """
        phone_number = prefix + digits
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            client = Client()
            
            # Create superuser
            superuser = db.get_or_create_user('09999999999')
            db.update_user_role(superuser['id'], 'superuser')
            superuser_token = db.create_auth_token(superuser['id'])
            
            # Create regular user
            user = db.get_or_create_user(phone_number)
            
            # Get all users via admin endpoint
            response = client.get(
                '/api/admin/users/',
                HTTP_AUTHORIZATION=f'Token {superuser_token}'
            )
            
            # Should return success
            self.assertEqual(
                response.status_code,
                http_status.HTTP_200_OK,
                f"Admin users endpoint should return 200, got {response.status_code}"
            )
            
            # Parse response
            response_data = response.json()
            
            # Sensitive fields that should NEVER appear
            sensitive_fields = [
                'password',
                'password_hash',
                'hashed_password',
                'pwd',
                'secret',
                'private_key',
                'auth_token',
                'token_hash',
            ]
            
            # Convert response to string to check for sensitive field names
            response_str = json.dumps(response_data).lower()
            
            # Check that no sensitive fields appear anywhere in the response
            for sensitive_field in sensitive_fields:
                self.assertNotIn(
                    f'"{sensitive_field}"',
                    response_str,
                    f"Admin users response should not contain sensitive field '{sensitive_field}'"
                )
            
            # Check each user in results
            if 'results' in response_data:
                for user_obj in response_data['results']:
                    # Should have safe fields
                    safe_fields = ['id', 'phone_number', 'role', 'created_at', 'is_active']
                    for safe_field in safe_fields:
                        self.assertIn(
                            safe_field,
                            user_obj,
                            f"User object should contain safe field '{safe_field}'"
                        )
                    
                    # Should NOT have sensitive fields
                    for sensitive_field in sensitive_fields:
                        self.assertNotIn(
                            sensitive_field,
                            user_obj,
                            f"User object should not contain sensitive field '{sensitive_field}'"
                        )
        
        except Exception as e:
            self.fail(f"Unexpected error with phone_number='{phone_number}': {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)


class TestErrorResponseConsistency(unittest.TestCase):
    """
    Test that API error responses follow consistent format.
    Feature: user-wallet-system, Property 16: Error response consistency
    """
    
    @settings(max_examples=100, deadline=None)
    @given(
        invalid_phone=st.text(
            alphabet=st.characters(min_codepoint=32, max_codepoint=126),
            min_size=1,
            max_size=20
        )
    )
    def test_client_errors_return_4xx_with_error_message(self, invalid_phone):
        """
        Property 16: For any API error condition, the response should include an
        appropriate HTTP status code (4xx for client errors, 5xx for server errors)
        and a JSON body with an error message.
        
        Validates: Requirements 4.6
        """
        # Skip valid phone numbers
        assume(not (invalid_phone.startswith('09') and len(invalid_phone) == 11 and invalid_phone[2:].isdigit()))
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            client = Client()
            
            # Test login with invalid phone number (client error)
            response = client.post(
                '/api/auth/login/',
                data=json.dumps({'phone_number': invalid_phone}),
                content_type='application/json'
            )
            
            # Should return 4xx status code (client error)
            self.assertGreaterEqual(
                response.status_code,
                400,
                f"Invalid phone should return 4xx error, got {response.status_code}"
            )
            self.assertLess(
                response.status_code,
                500,
                f"Invalid phone should return 4xx error (not 5xx), got {response.status_code}"
            )
            
            # Response should be JSON
            self.assertEqual(
                response['Content-Type'],
                'application/json',
                "Error response should be JSON"
            )
            
            # Parse response
            response_data = response.json()
            
            # Should have success=false
            self.assertIn(
                'success',
                response_data,
                "Error response should contain 'success' field"
            )
            self.assertFalse(
                response_data['success'],
                "Error response should have success=false"
            )
            
            # Should have error message
            self.assertIn(
                'error',
                response_data,
                "Error response should contain 'error' field with message"
            )
            self.assertIsInstance(
                response_data['error'],
                str,
                "Error message should be a string"
            )
            self.assertGreater(
                len(response_data['error']),
                0,
                "Error message should not be empty"
            )
            
            # Should have error code
            self.assertIn(
                'code',
                response_data,
                "Error response should contain 'code' field"
            )
            self.assertIsInstance(
                response_data['code'],
                str,
                "Error code should be a string"
            )
            self.assertGreater(
                len(response_data['code']),
                0,
                "Error code should not be empty"
            )
        
        except Exception as e:
            self.fail(f"Unexpected error with invalid_phone='{invalid_phone}': {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        prefix=st.just('09'),
        digits=st.text(alphabet='0123456789', min_size=9, max_size=9),
        invalid_amount=st.integers(max_value=0)
    )
    def test_validation_errors_have_consistent_format(self, prefix, digits, invalid_amount):
        """
        Property: Validation errors (like invalid amounts) should return consistent
        error response format with 400 status code.
        
        Validates: Requirements 4.6
        """
        phone_number = prefix + digits
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            client = Client()
            
            # Create user and authenticate
            user = db.get_or_create_user(phone_number)
            token = db.create_auth_token(user['id'])
            
            # Try to charge wallet with invalid amount (0 or negative)
            response = client.post(
                '/api/wallet/charge/',
                data=json.dumps({'amount': invalid_amount}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Token {token}'
            )
            
            # Should return 400 Bad Request
            self.assertEqual(
                response.status_code,
                http_status.HTTP_400_BAD_REQUEST,
                f"Invalid amount should return 400, got {response.status_code}"
            )
            
            # Response should be JSON
            self.assertEqual(
                response['Content-Type'],
                'application/json',
                "Error response should be JSON"
            )
            
            # Parse response
            response_data = response.json()
            
            # Should have consistent error format
            self.assertIn('success', response_data, "Should have 'success' field")
            self.assertFalse(response_data['success'], "Should have success=false")
            
            self.assertIn('error', response_data, "Should have 'error' field")
            self.assertIsInstance(response_data['error'], str, "Error should be string")
            self.assertGreater(len(response_data['error']), 0, "Error message should not be empty")
            
            self.assertIn('code', response_data, "Should have 'code' field")
            self.assertIsInstance(response_data['code'], str, "Code should be string")
            self.assertGreater(len(response_data['code']), 0, "Error code should not be empty")
        
        except Exception as e:
            self.fail(f"Unexpected error with phone_number='{phone_number}', amount={invalid_amount}: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        prefix=st.just('09'),
        digits=st.text(alphabet='0123456789', min_size=9, max_size=9)
    )
    def test_not_found_errors_return_404_with_error_message(self, prefix, digits):
        """
        Property: Resource not found errors should return 404 status code with
        consistent error response format.
        
        Validates: Requirements 4.6
        """
        phone_number = prefix + digits
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            client = Client()
            
            # Create user and authenticate
            user = db.get_or_create_user(phone_number)
            token = db.create_auth_token(user['id'])
            
            # Try to delete a plate that doesn't exist
            non_existent_plate_id = 99999
            response = client.delete(
                f'/api/plates/{non_existent_plate_id}/',
                HTTP_AUTHORIZATION=f'Token {token}'
            )
            
            # Should return 404 Not Found
            self.assertEqual(
                response.status_code,
                http_status.HTTP_404_NOT_FOUND,
                f"Non-existent plate should return 404, got {response.status_code}"
            )
            
            # Response should be JSON
            self.assertEqual(
                response['Content-Type'],
                'application/json',
                "Error response should be JSON"
            )
            
            # Parse response
            response_data = response.json()
            
            # Should have consistent error format
            self.assertIn('success', response_data, "Should have 'success' field")
            self.assertFalse(response_data['success'], "Should have success=false")
            
            self.assertIn('error', response_data, "Should have 'error' field")
            self.assertIsInstance(response_data['error'], str, "Error should be string")
            self.assertGreater(len(response_data['error']), 0, "Error message should not be empty")
            
            self.assertIn('code', response_data, "Should have 'code' field")
            self.assertIsInstance(response_data['code'], str, "Code should be string")
            self.assertGreater(len(response_data['code']), 0, "Error code should not be empty")
        
        except Exception as e:
            self.fail(f"Unexpected error with phone_number='{phone_number}': {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        prefix=st.just('09'),
        digits=st.text(alphabet='0123456789', min_size=9, max_size=9)
    )
    def test_forbidden_errors_return_403_with_error_message(self, prefix, digits):
        """
        Property: Permission denied errors should return 403 status code with
        consistent error response format.
        
        Validates: Requirements 4.6
        """
        phone_number = prefix + digits
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            client = Client()
            
            # Create regular user (not admin)
            user = db.get_or_create_user(phone_number)
            token = db.create_auth_token(user['id'])
            
            # Try to access admin endpoint (should be forbidden)
            response = client.get(
                '/api/admin/users/',
                HTTP_AUTHORIZATION=f'Token {token}'
            )
            
            # Should return 403 Forbidden
            self.assertEqual(
                response.status_code,
                http_status.HTTP_403_FORBIDDEN,
                f"Non-admin accessing admin endpoint should return 403, got {response.status_code}"
            )
            
            # Response should be JSON
            self.assertEqual(
                response['Content-Type'],
                'application/json',
                "Error response should be JSON"
            )
            
            # Parse response
            response_data = response.json()
            
            # Should have consistent error format
            self.assertIn('success', response_data, "Should have 'success' field")
            self.assertFalse(response_data['success'], "Should have success=false")
            
            self.assertIn('error', response_data, "Should have 'error' field")
            self.assertIsInstance(response_data['error'], str, "Error should be string")
            self.assertGreater(len(response_data['error']), 0, "Error message should not be empty")
            
            self.assertIn('code', response_data, "Should have 'code' field")
            self.assertIsInstance(response_data['code'], str, "Code should be string")
            self.assertGreater(len(response_data['code']), 0, "Error code should not be empty")
        
        except Exception as e:
            self.fail(f"Unexpected error with phone_number='{phone_number}': {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)


if __name__ == '__main__':
    unittest.main()
