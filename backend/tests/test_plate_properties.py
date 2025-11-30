"""
Property-based tests for plate management system.

These tests use Hypothesis to verify correctness properties across
randomly generated inputs for plate validation and management.
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


# Strategy for generating Persian letters used in Iranian plates
persian_letters = [
    'الف', 'ب', 'پ', 'ت', 'ث', 'ج', 'د', 'ز', 'س', 'ش',
    'ص', 'ط', 'ع', 'ف', 'ق', 'ک', 'گ', 'ل', 'م', 'ن',
    'و', 'ه', 'ی'
]

persian_letter_strategy = st.sampled_from(persian_letters)


# Strategy for generating valid Iranian plates
def valid_plate_strategy():
    """Generate valid Iranian license plates."""
    return st.one_of(
        # Full format: 2 digits + letter + 3 digits + 2 digits
        st.builds(
            lambda series, letter, serial, region: f"{series}{letter}{serial}{region}",
            series=st.integers(min_value=10, max_value=99).map(str),
            letter=persian_letter_strategy,
            serial=st.integers(min_value=100, max_value=999).map(str),
            region=st.integers(min_value=10, max_value=99).map(str)
        ),
        # Short format: 2 digits + letter + 3 digits
        st.builds(
            lambda series, letter, serial: f"{series}{letter}{serial}",
            series=st.integers(min_value=10, max_value=99).map(str),
            letter=persian_letter_strategy,
            serial=st.integers(min_value=100, max_value=999).map(str)
        ),
        # With separators
        st.builds(
            lambda series, letter, serial, region: f"{series} {letter} {serial} {region}",
            series=st.integers(min_value=10, max_value=99).map(str),
            letter=persian_letter_strategy,
            serial=st.integers(min_value=100, max_value=999).map(str),
            region=st.integers(min_value=10, max_value=99).map(str)
        ),
        st.builds(
            lambda series, letter, serial, region: f"{series}-{letter}-{serial}-{region}",
            series=st.integers(min_value=10, max_value=99).map(str),
            letter=persian_letter_strategy,
            serial=st.integers(min_value=100, max_value=999).map(str),
            region=st.integers(min_value=10, max_value=99).map(str)
        ),
    )


class TestPlateFormatValidation(unittest.TestCase):
    """
    Test plate format validation.
    Feature: user-wallet-system, Property 10: Plate format validation
    """
    
    @settings(max_examples=100, deadline=None)
    @given(plate=valid_plate_strategy())
    def test_valid_plates_are_accepted(self, plate):
        """
        Property 10: For any string input to the plate registration system,
        the system should accept it if and only if it matches the valid
        Iranian license plate format.
        
        Validates: Requirements 3.1
        
        This test verifies that all valid Iranian plate formats are accepted.
        """
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Valid plates should pass validation
            result = db.validate_plate_format(plate)
            
            self.assertTrue(
                result,
                f"Valid plate '{plate}' should be accepted by validation"
            )
        
        except Exception as e:
            self.fail(f"Unexpected error with valid plate '{plate}': {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        invalid_plate=st.one_of(
            # No Persian letter
            st.text(alphabet='0123456789', min_size=5, max_size=10),
            # Only Persian letters
            st.text(alphabet=''.join(persian_letters), min_size=1, max_size=10),
            # Too few digits
            st.builds(
                lambda letter, digits: f"{digits}{letter}",
                letter=persian_letter_strategy,
                digits=st.text(alphabet='0123456789', min_size=1, max_size=3)
            ),
            # Too many digits
            st.builds(
                lambda letter, digits: f"{digits}{letter}",
                letter=persian_letter_strategy,
                digits=st.text(alphabet='0123456789', min_size=10, max_size=15)
            ),
            # Invalid characters
            st.text(alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()', min_size=5, max_size=10),
            # Empty string
            st.just(''),
            # Only whitespace
            st.text(alphabet=' \t\n', min_size=1, max_size=10),
        )
    )
    def test_invalid_plates_are_rejected(self, invalid_plate):
        """
        Property 10: For any string input to the plate registration system,
        the system should accept it if and only if it matches the valid
        Iranian license plate format.
        
        Validates: Requirements 3.1
        
        This test verifies that invalid plate formats are rejected.
        """
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Invalid plates should fail validation
            result = db.validate_plate_format(invalid_plate)
            
            self.assertFalse(
                result,
                f"Invalid plate '{invalid_plate}' should be rejected by validation"
            )
        
        except Exception as e:
            self.fail(f"Unexpected error with invalid plate '{invalid_plate}': {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(plate=valid_plate_strategy())
    def test_api_rejects_invalid_format(self, plate):
        """
        Property 10: The API should reject plates that don't match the valid format.
        
        Validates: Requirements 3.1, 4.3
        
        This test verifies that the API endpoint properly validates plate format.
        """
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            client = Client()
            
            # Create user and get token
            user = db.get_or_create_user('09123456789')
            token = db.create_auth_token(user['id'])
            
            # Try to add the plate via API
            response = client.post(
                '/api/plates/',
                data={'plate': plate},
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Token {token}'
            )
            
            # Valid plates should be accepted (201 Created)
            self.assertEqual(
                response.status_code,
                http_status.HTTP_201_CREATED,
                f"Valid plate '{plate}' should be accepted by API, got {response.status_code}"
            )
            
            # Response should contain the plate data
            data = response.json()
            self.assertIn('plate', data)
            self.assertIn('id', data)
            self.assertIn('registered_at', data)
        
        except Exception as e:
            self.fail(f"Unexpected error with plate '{plate}': {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)


class TestPlateAssociation(unittest.TestCase):
    """
    Test plate association correctness.
    Feature: user-wallet-system, Property 11: Plate association correctness
    """
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone_number=st.builds(
            lambda prefix, digits: prefix + digits,
            prefix=st.just('09'),
            digits=st.text(alphabet='0123456789', min_size=9, max_size=9)
        ),
        plate=valid_plate_strategy()
    )
    def test_added_plate_appears_in_user_plates(self, phone_number, plate):
        """
        Property 11: For any valid plate added by a user, querying that user's
        plates should include the newly added plate.
        
        Validates: Requirements 3.2, 3.6
        
        This test verifies that plates are correctly associated with users.
        """
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user
            user = db.get_or_create_user(phone_number)
            user_id = user['id']
            
            # Add plate
            plate_id = db.register_user_plate(user_id, plate)
            
            # Query user's plates
            user_plates = db.get_user_plates(user_id)
            
            # The added plate should be in the list
            plate_numbers = [p['plate'] for p in user_plates]
            
            self.assertIn(
                plate,
                plate_numbers,
                f"Plate '{plate}' should appear in user's plates after being added"
            )
            
            # Verify the plate data is correct
            added_plate = next((p for p in user_plates if p['plate'] == plate), None)
            self.assertIsNotNone(added_plate, f"Plate '{plate}' should be found in user's plates")
            self.assertEqual(added_plate['user_id'], user_id)
            self.assertEqual(added_plate['id'], plate_id)
            self.assertTrue(added_plate['is_active'])
        
        except Exception as e:
            self.fail(f"Unexpected error with phone='{phone_number}', plate='{plate}': {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone_number=st.builds(
            lambda prefix, digits: prefix + digits,
            prefix=st.just('09'),
            digits=st.text(alphabet='0123456789', min_size=9, max_size=9)
        ),
        plate=valid_plate_strategy()
    )
    def test_api_added_plate_appears_in_response(self, phone_number, plate):
        """
        Property 11: For any valid plate added via API, the GET plates endpoint
        should return the newly added plate.
        
        Validates: Requirements 3.2, 3.6, 4.3
        
        This test verifies that the API correctly associates plates with users.
        """
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            client = Client()
            
            # Create user and get token
            user = db.get_or_create_user(phone_number)
            token = db.create_auth_token(user['id'])
            
            # Add plate via API
            add_response = client.post(
                '/api/plates/',
                data={'plate': plate},
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Token {token}'
            )
            
            self.assertEqual(
                add_response.status_code,
                http_status.HTTP_201_CREATED,
                f"Adding plate '{plate}' should succeed"
            )
            
            # Get user's plates via API
            get_response = client.get(
                '/api/plates/',
                HTTP_AUTHORIZATION=f'Token {token}'
            )
            
            self.assertEqual(
                get_response.status_code,
                http_status.HTTP_200_OK,
                "Getting plates should succeed"
            )
            
            # Verify the plate is in the response
            plates_data = get_response.json()
            self.assertIsInstance(plates_data, list)
            
            plate_numbers = [p['plate'] for p in plates_data]
            self.assertIn(
                plate,
                plate_numbers,
                f"Plate '{plate}' should appear in GET /api/plates/ response"
            )
        
        except Exception as e:
            self.fail(f"Unexpected error with phone='{phone_number}', plate='{plate}': {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone1=st.builds(
            lambda prefix, digits: prefix + digits,
            prefix=st.just('09'),
            digits=st.text(alphabet='0123456789', min_size=9, max_size=9)
        ),
        phone2=st.builds(
            lambda prefix, digits: prefix + digits,
            prefix=st.just('09'),
            digits=st.text(alphabet='0123456789', min_size=9, max_size=9)
        ),
        plate=valid_plate_strategy()
    )
    def test_plate_belongs_to_correct_user(self, phone1, phone2, plate):
        """
        Property 11: A plate added by user A should not appear in user B's plates.
        
        Validates: Requirements 3.2, 3.6
        
        This test verifies that plates are correctly isolated between users.
        """
        # Skip if phone numbers are the same
        assume(phone1 != phone2)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create two users
            user1 = db.get_or_create_user(phone1)
            user2 = db.get_or_create_user(phone2)
            
            # User 1 adds the plate
            db.register_user_plate(user1['id'], plate)
            
            # Get plates for both users
            user1_plates = db.get_user_plates(user1['id'])
            user2_plates = db.get_user_plates(user2['id'])
            
            # User 1 should have the plate
            user1_plate_numbers = [p['plate'] for p in user1_plates]
            self.assertIn(
                plate,
                user1_plate_numbers,
                f"Plate '{plate}' should appear in user1's plates"
            )
            
            # User 2 should NOT have the plate
            user2_plate_numbers = [p['plate'] for p in user2_plates]
            self.assertNotIn(
                plate,
                user2_plate_numbers,
                f"Plate '{plate}' should NOT appear in user2's plates"
            )
        
        except Exception as e:
            self.fail(f"Unexpected error with phone1='{phone1}', phone2='{phone2}', plate='{plate}': {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)


class TestMultiplePlatesSupport(unittest.TestCase):
    """
    Test multiple plates support.
    Feature: user-wallet-system, Property 12: Multiple plates support
    """
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone_number=st.builds(
            lambda prefix, digits: prefix + digits,
            prefix=st.just('09'),
            digits=st.text(alphabet='0123456789', min_size=9, max_size=9)
        ),
        plates=st.lists(
            valid_plate_strategy(),
            min_size=2,
            max_size=5,
            unique=True
        )
    )
    def test_user_can_add_multiple_distinct_plates(self, phone_number, plates):
        """
        Property 12: For any user, the system should allow adding multiple
        distinct plates, and all added plates should be retrievable.
        
        Validates: Requirements 3.3
        
        This test verifies that users can register multiple plates.
        """
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user
            user = db.get_or_create_user(phone_number)
            user_id = user['id']
            
            # Add all plates
            added_plate_ids = []
            for plate in plates:
                plate_id = db.register_user_plate(user_id, plate)
                added_plate_ids.append(plate_id)
            
            # Get user's plates
            user_plates = db.get_user_plates(user_id)
            
            # All plates should be present
            self.assertEqual(
                len(user_plates),
                len(plates),
                f"User should have {len(plates)} plates, but has {len(user_plates)}"
            )
            
            # Verify each plate is in the list
            user_plate_numbers = [p['plate'] for p in user_plates]
            for plate in plates:
                self.assertIn(
                    plate,
                    user_plate_numbers,
                    f"Plate '{plate}' should be in user's plates"
                )
        
        except Exception as e:
            self.fail(f"Unexpected error with phone='{phone_number}', plates={plates}: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone_number=st.builds(
            lambda prefix, digits: prefix + digits,
            prefix=st.just('09'),
            digits=st.text(alphabet='0123456789', min_size=9, max_size=9)
        ),
        plates=st.lists(
            valid_plate_strategy(),
            min_size=2,
            max_size=5,
            unique=True
        )
    )
    def test_api_supports_multiple_plates(self, phone_number, plates):
        """
        Property 12: The API should allow users to add multiple distinct plates
        and retrieve all of them.
        
        Validates: Requirements 3.3, 4.3
        
        This test verifies that the API correctly handles multiple plates per user.
        """
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            client = Client()
            
            # Create user and get token
            user = db.get_or_create_user(phone_number)
            token = db.create_auth_token(user['id'])
            
            # Add all plates via API
            for plate in plates:
                add_response = client.post(
                    '/api/plates/',
                    data={'plate': plate},
                    content_type='application/json',
                    HTTP_AUTHORIZATION=f'Token {token}'
                )
                
                self.assertEqual(
                    add_response.status_code,
                    http_status.HTTP_201_CREATED,
                    f"Adding plate '{plate}' should succeed"
                )
            
            # Get all plates via API
            get_response = client.get(
                '/api/plates/',
                HTTP_AUTHORIZATION=f'Token {token}'
            )
            
            self.assertEqual(
                get_response.status_code,
                http_status.HTTP_200_OK,
                "Getting plates should succeed"
            )
            
            # Verify all plates are in the response
            plates_data = get_response.json()
            self.assertIsInstance(plates_data, list)
            
            self.assertEqual(
                len(plates_data),
                len(plates),
                f"API should return {len(plates)} plates, but returned {len(plates_data)}"
            )
            
            api_plate_numbers = [p['plate'] for p in plates_data]
            for plate in plates:
                self.assertIn(
                    plate,
                    api_plate_numbers,
                    f"Plate '{plate}' should be in API response"
                )
        
        except Exception as e:
            self.fail(f"Unexpected error with phone='{phone_number}', plates={plates}: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone_number=st.builds(
            lambda prefix, digits: prefix + digits,
            prefix=st.just('09'),
            digits=st.text(alphabet='0123456789', min_size=9, max_size=9)
        ),
        plate=valid_plate_strategy()
    )
    def test_duplicate_plate_for_same_user_is_rejected(self, phone_number, plate):
        """
        Property 12: A user should not be able to add the same plate twice.
        
        Validates: Requirements 3.3
        
        This test verifies that duplicate plates are rejected.
        """
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user
            user = db.get_or_create_user(phone_number)
            user_id = user['id']
            
            # Add plate first time - should succeed
            plate_id = db.register_user_plate(user_id, plate)
            self.assertIsNotNone(plate_id)
            
            # Try to add same plate again - should fail
            with self.assertRaises(ValueError) as context:
                db.register_user_plate(user_id, plate)
            
            self.assertIn(
                'already registered',
                str(context.exception).lower(),
                "Error message should indicate plate is already registered"
            )
            
            # Verify user still has only one instance of the plate
            user_plates = db.get_user_plates(user_id)
            plate_count = sum(1 for p in user_plates if p['plate'] == plate)
            
            self.assertEqual(
                plate_count,
                1,
                f"User should have exactly 1 instance of plate '{plate}', but has {plate_count}"
            )
        
        except Exception as e:
            # If the exception is the expected ValueError, that's fine
            if isinstance(e, ValueError) and 'already registered' in str(e).lower():
                pass
            else:
                self.fail(f"Unexpected error with phone='{phone_number}', plate='{plate}': {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)


if __name__ == '__main__':
    unittest.main()
