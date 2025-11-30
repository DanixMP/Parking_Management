"""
Property-based tests for role-based access control.

These tests use Hypothesis to verify correctness properties across
randomly generated inputs for role-based access control.
"""

import sys
import os
import unittest
import tempfile
import shutil
from pathlib import Path
import uuid

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


class TestRoleBasedAccessControl(unittest.TestCase):
    """
    Test role-based access control for admin endpoints.
    Feature: user-wallet-system, Property 5: Role-based access control
    """
    
    @settings(max_examples=100, deadline=None)
    @given(
        user_digits=st.text(alphabet='0123456789', min_size=9, max_size=9),
        admin_digits=st.text(alphabet='0123456789', min_size=9, max_size=9),
        superuser_digits=st.text(alphabet='0123456789', min_size=9, max_size=9)
    )
    def test_admin_endpoints_require_admin_or_superuser_role(self, user_digits, admin_digits, superuser_digits):
        user_phone = '09' + user_digits
        admin_phone = '09' + admin_digits
        superuser_phone = '09' + superuser_digits
        """
        Property 5: For any API endpoint marked as requiring specific roles,
        users with insufficient roles should receive 403 Forbidden responses,
        while users with sufficient roles should be able to access the endpoint.
        
        Validates: Requirements 1.5, 1.6
        """
        # Ensure all phone numbers are unique
        assume(user_phone != admin_phone)
        assume(user_phone != superuser_phone)
        assume(admin_phone != superuser_phone)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            client = Client()
            
            # Create users with different roles
            regular_user = db.create_user(user_phone, role='user')
            admin_user = db.create_user(admin_phone, role='admin')
            superuser = db.create_user(superuser_phone, role='superuser')
            
            # Create tokens for each user
            regular_token = db.create_auth_token(regular_user)
            admin_token = db.create_auth_token(admin_user)
            superuser_token = db.create_auth_token(superuser)
            
            # Test GET /api/admin/users/ endpoint (requires admin or superuser)
            
            # Regular user should get 403 Forbidden
            response_user = client.get(
                '/api/admin/users/',
                HTTP_AUTHORIZATION=f'Token {regular_token}'
            )
            self.assertEqual(
                response_user.status_code,
                http_status.HTTP_403_FORBIDDEN,
                f"Regular user should get 403 for admin endpoint, got {response_user.status_code}"
            )
            data_user = response_user.json()
            self.assertFalse(
                data_user.get('success', True),
                "Regular user response should have success=false"
            )
            self.assertEqual(
                data_user.get('code'),
                'FORBIDDEN',
                "Regular user response should have code=FORBIDDEN"
            )
            
            # Admin user should be able to access
            response_admin = client.get(
                '/api/admin/users/',
                HTTP_AUTHORIZATION=f'Token {admin_token}'
            )
            self.assertNotEqual(
                response_admin.status_code,
                http_status.HTTP_403_FORBIDDEN,
                f"Admin user should not get 403 for admin endpoint, got {response_admin.status_code}"
            )
            self.assertNotEqual(
                response_admin.status_code,
                http_status.HTTP_401_UNAUTHORIZED,
                f"Admin user should not get 401 for admin endpoint, got {response_admin.status_code}"
            )
            
            # SuperUser should be able to access
            response_superuser = client.get(
                '/api/admin/users/',
                HTTP_AUTHORIZATION=f'Token {superuser_token}'
            )
            self.assertNotEqual(
                response_superuser.status_code,
                http_status.HTTP_403_FORBIDDEN,
                f"SuperUser should not get 403 for admin endpoint, got {response_superuser.status_code}"
            )
            self.assertNotEqual(
                response_superuser.status_code,
                http_status.HTTP_401_UNAUTHORIZED,
                f"SuperUser should not get 401 for admin endpoint, got {response_superuser.status_code}"
            )
        
        except Exception as e:
            self.fail(f"Unexpected error: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        user_digits=st.text(alphabet='0123456789', min_size=9, max_size=9),
        admin_digits=st.text(alphabet='0123456789', min_size=9, max_size=9),
        superuser_digits=st.text(alphabet='0123456789', min_size=9, max_size=9),
        target_digits=st.text(alphabet='0123456789', min_size=9, max_size=9),
        new_role=st.sampled_from(['user', 'admin', 'superuser'])
    )
    def test_superuser_only_endpoints_require_superuser_role(self, user_digits, admin_digits, superuser_digits, target_digits, new_role):
        user_phone = '09' + user_digits
        admin_phone = '09' + admin_digits
        superuser_phone = '09' + superuser_digits
        target_phone = '09' + target_digits
        """
        Property 5: For any API endpoint marked as requiring superuser role,
        only superusers should be able to access it. Regular users and admins
        should receive 403 Forbidden responses.
        
        Validates: Requirements 1.6
        """
        # Ensure all phone numbers are unique
        assume(user_phone != admin_phone)
        assume(user_phone != superuser_phone)
        assume(user_phone != target_phone)
        assume(admin_phone != superuser_phone)
        assume(admin_phone != target_phone)
        assume(superuser_phone != target_phone)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            client = Client()
            
            # Create users with different roles
            regular_user = db.create_user(user_phone, role='user')
            admin_user = db.create_user(admin_phone, role='admin')
            superuser = db.create_user(superuser_phone, role='superuser')
            target_user = db.create_user(target_phone, role='user')
            
            # Create tokens for each user
            regular_token = db.create_auth_token(regular_user)
            admin_token = db.create_auth_token(admin_user)
            superuser_token = db.create_auth_token(superuser)
            
            # Test PUT /api/admin/users/{id}/role/ endpoint (requires superuser only)
            
            # Regular user should get 403 Forbidden
            response_user = client.put(
                f'/api/admin/users/{target_user}/role/',
                data={'role': new_role},
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Token {regular_token}'
            )
            self.assertEqual(
                response_user.status_code,
                http_status.HTTP_403_FORBIDDEN,
                f"Regular user should get 403 for superuser endpoint, got {response_user.status_code}"
            )
            data_user = response_user.json()
            self.assertFalse(
                data_user.get('success', True),
                "Regular user response should have success=false"
            )
            self.assertEqual(
                data_user.get('code'),
                'FORBIDDEN',
                "Regular user response should have code=FORBIDDEN"
            )
            
            # Admin user should also get 403 Forbidden (not superuser)
            response_admin = client.put(
                f'/api/admin/users/{target_user}/role/',
                data={'role': new_role},
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Token {admin_token}'
            )
            self.assertEqual(
                response_admin.status_code,
                http_status.HTTP_403_FORBIDDEN,
                f"Admin user should get 403 for superuser-only endpoint, got {response_admin.status_code}"
            )
            data_admin = response_admin.json()
            self.assertFalse(
                data_admin.get('success', True),
                "Admin user response should have success=false"
            )
            self.assertEqual(
                data_admin.get('code'),
                'FORBIDDEN',
                "Admin user response should have code=FORBIDDEN"
            )
            
            # SuperUser should be able to access
            response_superuser = client.put(
                f'/api/admin/users/{target_user}/role/',
                data={'role': new_role},
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Token {superuser_token}'
            )
            self.assertNotEqual(
                response_superuser.status_code,
                http_status.HTTP_403_FORBIDDEN,
                f"SuperUser should not get 403 for superuser endpoint, got {response_superuser.status_code}"
            )
            self.assertNotEqual(
                response_superuser.status_code,
                http_status.HTTP_401_UNAUTHORIZED,
                f"SuperUser should not get 401 for superuser endpoint, got {response_superuser.status_code}"
            )
            
            # If successful, verify the role was actually updated
            if response_superuser.status_code == http_status.HTTP_200_OK:
                data_superuser = response_superuser.json()
                self.assertTrue(
                    data_superuser.get('success', False),
                    "SuperUser response should have success=true"
                )
                updated_user = data_superuser.get('user')
                self.assertIsNotNone(updated_user, "Response should contain updated user")
                self.assertEqual(
                    updated_user.get('role'),
                    new_role,
                    f"User role should be updated to {new_role}"
                )
        
        except Exception as e:
            self.fail(f"Unexpected error: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        digits=st.text(alphabet='0123456789', min_size=9, max_size=9),
        role=st.sampled_from(['user', 'admin', 'superuser'])
    )
    def test_role_assignment_persists(self, digits, role):
        phone = '09' + digits
        """
        Property: For any user with a specific role, that role should be
        consistently returned across different API calls.
        
        Validates: Requirements 1.5, 1.6
        """
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            client = Client()
            
            # Create user with specific role
            user_id = db.create_user(phone, role=role)
            token = db.create_auth_token(user_id)
            
            # Get user info via API
            response = client.get(
                '/api/auth/me/',
                HTTP_AUTHORIZATION=f'Token {token}'
            )
            
            self.assertEqual(
                response.status_code,
                http_status.HTTP_200_OK,
                f"Should be able to get user info, got {response.status_code}"
            )
            
            data = response.json()
            self.assertTrue(
                data.get('success', False),
                "Response should have success=true"
            )
            
            user_data = data.get('user')
            self.assertIsNotNone(user_data, "Response should contain user data")
            self.assertEqual(
                user_data.get('role'),
                role,
                f"User role should be {role}, got {user_data.get('role')}"
            )
        
        except Exception as e:
            self.fail(f"Unexpected error with phone='{phone}', role='{role}': {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)


if __name__ == '__main__':
    unittest.main()
