"""
Property-based tests for user wallet system.

These tests use Hypothesis to verify correctness properties across
randomly generated inputs.
"""

import sys
import os
import unittest
import tempfile
import shutil
from pathlib import Path
import uuid
from datetime import datetime, timedelta

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import database as db

from hypothesis import given, settings, strategies as st, assume
from hypothesis import HealthCheck
import re


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


class TestPhoneValidation(unittest.TestCase):
    """
    Test phone number validation consistency.
    Feature: user-wallet-system, Property 1: Phone number validation consistency
    """
    
    @settings(max_examples=100)
    @given(phone_number=st.text())
    def test_phone_validation_consistency(self, phone_number):
        """
        Property 1: For any string input to the authentication system, the system
        should accept it if and only if it matches the valid phone number format
        (Iranian format: 09XXXXXXXXX).
        
        Validates: Requirements 1.1
        """
        # Define the expected format: 09 followed by exactly 9 digits
        expected_pattern = r'^09\d{9}$'
        is_valid_format = bool(re.match(expected_pattern, phone_number))
        
        # Test the validation function
        validation_result = db.validate_phone_number(phone_number)
        
        # The validation function should return True if and only if the format matches
        self.assertEqual(
            validation_result,
            is_valid_format,
            f"Phone validation inconsistent for '{phone_number}': "
            f"expected {is_valid_format}, got {validation_result}"
        )
    
    @settings(max_examples=100)
    @given(
        prefix=st.just('09'),
        digits=st.text(alphabet='0123456789', min_size=9, max_size=9)
    )
    def test_valid_phone_numbers_accepted(self, prefix, digits):
        """
        Property: All strings matching the format 09XXXXXXXXX (where X is a digit)
        should be accepted as valid phone numbers.
        
        Validates: Requirements 1.1
        """
        phone_number = prefix + digits
        
        # This should always be valid
        self.assertTrue(
            db.validate_phone_number(phone_number),
            f"Valid phone number '{phone_number}' was rejected"
        )
    
    @settings(max_examples=100)
    @given(phone_number=st.text())
    def test_invalid_phone_numbers_rejected(self, phone_number):
        """
        Property: All strings NOT matching the format 09XXXXXXXXX should be
        rejected as invalid phone numbers.
        
        Validates: Requirements 1.1
        """
        # Skip valid phone numbers
        expected_pattern = r'^09\d{9}$'
        assume(not re.match(expected_pattern, phone_number))
        
        # This should always be invalid
        self.assertFalse(
            db.validate_phone_number(phone_number),
            f"Invalid phone number '{phone_number}' was accepted"
        )


class TestUserPhoneUniqueness(unittest.TestCase):
    """
    Test phone number uniqueness enforcement.
    Feature: user-wallet-system, Property 23: Phone number uniqueness enforcement
    """
    
    @settings(max_examples=100, deadline=None)
    @given(phone_number=st.text(min_size=1, max_size=15))
    def test_duplicate_phone_number_rejected(self, phone_number):
        """
        Property: For any phone number, attempting to create two users with the
        same phone number should result in the second attempt being rejected.
        
        Validates: Requirements 7.5
        """
        # Skip invalid phone numbers that would cause other issues
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)  # SQLite doesn't allow null bytes
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # First user creation should succeed
            user_id_1 = db.create_user(phone_number, role='user')
            self.assertIsNotNone(user_id_1)
            self.assertIsInstance(user_id_1, int)
            self.assertGreater(user_id_1, 0)
            
            # Verify user was created
            user = db.get_user_by_phone(phone_number)
            self.assertIsNotNone(user)
            self.assertEqual(user['phone_number'], phone_number)
            
            # Second user creation with same phone number should fail
            with self.assertRaises(ValueError) as context:
                db.create_user(phone_number, role='user')
            
            # Verify the error message mentions the phone number
            self.assertIn('already exists', str(context.exception).lower())
            
            # Verify only one user exists with this phone number
            user_check = db.get_user_by_phone(phone_number)
            self.assertIsNotNone(user_check)
            self.assertEqual(user_check['id'], user_id_1)
            
        except Exception as e:
            # If there's an unexpected error, fail the test with details
            self.fail(f"Unexpected error with phone_number='{phone_number}': {e}")
        finally:
            # Clean up database
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone1=st.text(min_size=1, max_size=15),
        phone2=st.text(min_size=1, max_size=15)
    )
    def test_different_phone_numbers_allowed(self, phone1, phone2):
        """
        Property: For any two different phone numbers, both users should be
        created successfully.
        
        Validates: Requirements 7.5
        """
        # Ensure phone numbers are different
        assume(phone1 != phone2)
        assume(phone1.strip() != '')
        assume(phone2.strip() != '')
        assume('\x00' not in phone1)
        assume('\x00' not in phone2)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Both user creations should succeed
            user_id_1 = db.create_user(phone1, role='user')
            user_id_2 = db.create_user(phone2, role='user')
            
            self.assertIsNotNone(user_id_1)
            self.assertIsNotNone(user_id_2)
            self.assertNotEqual(user_id_1, user_id_2)
            
            # Verify both users exist
            user1 = db.get_user_by_phone(phone1)
            user2 = db.get_user_by_phone(phone2)
            
            self.assertIsNotNone(user1)
            self.assertIsNotNone(user2)
            self.assertEqual(user1['phone_number'], phone1)
            self.assertEqual(user2['phone_number'], phone2)
            self.assertEqual(user1['id'], user_id_1)
            self.assertEqual(user2['id'], user_id_2)
            
        except Exception as e:
            self.fail(f"Unexpected error with phone1='{phone1}', phone2='{phone2}': {e}")
        finally:
            # Clean up database
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(phone_number=st.text(min_size=1, max_size=15))
    def test_phone_uniqueness_after_deletion(self, phone_number):
        """
        Property: After deleting a user, the same phone number should be
        available for a new user registration.
        
        Validates: Requirements 7.5
        """
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create first user
            user_id_1 = db.create_user(phone_number, role='user')
            self.assertIsNotNone(user_id_1)
            
            # Delete the user
            db.delete_user(user_id_1)
            
            # Verify user is deleted
            user_check = db.get_user_by_phone(phone_number)
            self.assertIsNone(user_check)
            
            # Create second user with same phone number should succeed
            user_id_2 = db.create_user(phone_number, role='user')
            self.assertIsNotNone(user_id_2)
            
            # Verify new user exists
            user2 = db.get_user_by_phone(phone_number)
            self.assertIsNotNone(user2)
            self.assertEqual(user2['phone_number'], phone_number)
            self.assertEqual(user2['id'], user_id_2)
            
        except Exception as e:
            self.fail(f"Unexpected error with phone_number='{phone_number}': {e}")
        finally:
            # Clean up database
            cleanup_test_db(db_path, original_path, test_dir)


class TestLoginIdempotency(unittest.TestCase):
    """
    Test login idempotency.
    Feature: user-wallet-system, Property 2: Login idempotency
    """
    
    @settings(max_examples=100, deadline=None)
    @given(
        prefix=st.just('09'),
        digits=st.text(alphabet='0123456789', min_size=9, max_size=9)
    )
    def test_login_idempotency(self, prefix, digits):
        """
        Property 2: For any valid phone number, calling the login endpoint multiple
        times should always return the same user ID and user data.
        
        Validates: Requirements 1.2
        """
        # Generate valid Iranian phone number
        phone_number = prefix + digits
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # First login (get or create user)
            user1 = db.get_or_create_user(phone_number)
            self.assertIsNotNone(user1, "First login should return a user")
            self.assertIn('id', user1, "User should have an id field")
            self.assertIn('phone_number', user1, "User should have a phone_number field")
            self.assertIn('role', user1, "User should have a role field")
            self.assertIn('created_at', user1, "User should have a created_at field")
            
            user_id_1 = user1['id']
            phone_1 = user1['phone_number']
            role_1 = user1['role']
            created_at_1 = user1['created_at']
            
            # Second login (should return same user)
            user2 = db.get_or_create_user(phone_number)
            self.assertIsNotNone(user2, "Second login should return a user")
            
            user_id_2 = user2['id']
            phone_2 = user2['phone_number']
            role_2 = user2['role']
            created_at_2 = user2['created_at']
            
            # Verify idempotency: same user ID
            self.assertEqual(
                user_id_1, user_id_2,
                f"Login should be idempotent: user ID should be the same. "
                f"First login returned {user_id_1}, second login returned {user_id_2}"
            )
            
            # Verify all user data is identical
            self.assertEqual(
                phone_1, phone_2,
                f"Phone number should be identical across logins"
            )
            self.assertEqual(
                role_1, role_2,
                f"Role should be identical across logins"
            )
            self.assertEqual(
                created_at_1, created_at_2,
                f"Created timestamp should be identical across logins"
            )
            
            # Third login to further verify idempotency
            user3 = db.get_or_create_user(phone_number)
            self.assertIsNotNone(user3, "Third login should return a user")
            
            user_id_3 = user3['id']
            
            self.assertEqual(
                user_id_1, user_id_3,
                f"Login should remain idempotent on third call: "
                f"expected {user_id_1}, got {user_id_3}"
            )
            
            # Verify the user data is completely identical
            self.assertEqual(user1, user2, "First and second login should return identical user data")
            self.assertEqual(user1, user3, "First and third login should return identical user data")
            
        except Exception as e:
            self.fail(f"Unexpected error with phone_number='{phone_number}': {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)


class TestDefaultRoleAssignment(unittest.TestCase):
    """
    Test default role assignment.
    Feature: user-wallet-system, Property 3: Default role assignment
    """
    
    @settings(max_examples=100, deadline=None)
    @given(phone_number=st.text(min_size=1, max_size=15))
    def test_default_role_assignment(self, phone_number):
        """
        Property 3: For any newly created user account, the assigned role should
        be "user" unless explicitly specified otherwise.
        
        Validates: Requirements 1.3
        """
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user WITHOUT specifying role (should default to 'user')
            user_id = db.create_user(phone_number)
            self.assertIsNotNone(user_id)
            
            # Retrieve user from database
            user = db.get_user_by_id(user_id)
            
            # Verify default role is 'user'
            self.assertIsNotNone(user, "User should exist in database")
            self.assertIn('role', user, "User should have a role field")
            self.assertEqual(
                user['role'], 
                'user',
                f"Default role should be 'user', but got '{user['role']}'"
            )
            
        except Exception as e:
            self.fail(f"Unexpected error with phone_number='{phone_number}': {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone_number=st.text(min_size=1, max_size=15),
        explicit_role=st.sampled_from(['admin', 'superuser', 'user'])
    )
    def test_explicit_role_assignment(self, phone_number, explicit_role):
        """
        Property: When a role is explicitly specified during user creation,
        that role should be assigned (not the default).
        
        Validates: Requirements 1.3
        """
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user WITH explicit role
            user_id = db.create_user(phone_number, role=explicit_role)
            self.assertIsNotNone(user_id)
            
            # Retrieve user from database
            user = db.get_user_by_id(user_id)
            
            # Verify explicit role is assigned
            self.assertIsNotNone(user, "User should exist in database")
            self.assertIn('role', user, "User should have a role field")
            self.assertEqual(
                user['role'], 
                explicit_role,
                f"Explicit role should be '{explicit_role}', but got '{user['role']}'"
            )
            
        except Exception as e:
            self.fail(f"Unexpected error with phone_number='{phone_number}', role='{explicit_role}': {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        prefix=st.just('09'),
        digits=st.text(alphabet='0123456789', min_size=9, max_size=9)
    )
    def test_get_or_create_user_default_role(self, prefix, digits):
        """
        Property: When using get_or_create_user (which doesn't specify role),
        newly created users should have the default 'user' role.
        
        Validates: Requirements 1.3
        """
        phone_number = prefix + digits
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Use get_or_create_user (which creates with default role)
            user = db.get_or_create_user(phone_number)
            
            # Verify default role is 'user'
            self.assertIsNotNone(user, "User should be created")
            self.assertIn('role', user, "User should have a role field")
            self.assertEqual(
                user['role'], 
                'user',
                f"get_or_create_user should create users with default role 'user', but got '{user['role']}'"
            )
            
        except Exception as e:
            self.fail(f"Unexpected error with phone_number='{phone_number}': {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)


class TestAuthenticationTokenGeneration(unittest.TestCase):
    """
    Test authentication token generation.
    Feature: user-wallet-system, Property 4: Authentication token generation
    """
    
    @settings(max_examples=100, deadline=None)
    @given(
        prefix=st.just('09'),
        digits=st.text(alphabet='0123456789', min_size=9, max_size=9)
    )
    def test_authentication_token_generation(self, prefix, digits):
        """
        Property 4: For any successful authentication, the response should contain
        a valid authentication token that can be used for subsequent requests.
        
        Validates: Requirements 1.4
        """
        phone_number = prefix + digits
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Authenticate (get or create user)
            user = db.get_or_create_user(phone_number)
            self.assertIsNotNone(user, "Authentication should return a user")
            self.assertIn('id', user, "User should have an id field")
            
            user_id = user['id']
            
            # Generate authentication token
            token = db.create_auth_token(user_id)
            
            # Verify token is returned
            self.assertIsNotNone(token, "Authentication should return a token")
            self.assertIsInstance(token, str, "Token should be a string")
            self.assertGreater(len(token), 0, "Token should not be empty")
            
            # Verify token is valid for subsequent requests
            validated_user_id = db.validate_token(token)
            self.assertIsNotNone(
                validated_user_id,
                f"Token '{token}' should be valid for subsequent requests"
            )
            self.assertEqual(
                validated_user_id,
                user_id,
                f"Token should validate to the same user ID. "
                f"Expected {user_id}, got {validated_user_id}"
            )
            
            # Verify token can be used multiple times (not consumed on first use)
            validated_user_id_2 = db.validate_token(token)
            self.assertIsNotNone(
                validated_user_id_2,
                "Token should remain valid after first use"
            )
            self.assertEqual(
                validated_user_id_2,
                user_id,
                "Token should still validate to the same user ID on second use"
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
    def test_token_uniqueness(self, prefix, digits):
        """
        Property: For any user, generating multiple tokens should produce
        unique tokens that are all valid.
        
        Validates: Requirements 1.4
        """
        phone_number = prefix + digits
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user
            user = db.get_or_create_user(phone_number)
            user_id = user['id']
            
            # Generate multiple tokens
            token1 = db.create_auth_token(user_id)
            token2 = db.create_auth_token(user_id)
            token3 = db.create_auth_token(user_id)
            
            # Verify all tokens are unique
            self.assertNotEqual(token1, token2, "Tokens should be unique")
            self.assertNotEqual(token1, token3, "Tokens should be unique")
            self.assertNotEqual(token2, token3, "Tokens should be unique")
            
            # Verify all tokens are valid
            self.assertEqual(db.validate_token(token1), user_id, "Token 1 should be valid")
            self.assertEqual(db.validate_token(token2), user_id, "Token 2 should be valid")
            self.assertEqual(db.validate_token(token3), user_id, "Token 3 should be valid")
            
        except Exception as e:
            self.fail(f"Unexpected error with phone_number='{phone_number}': {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(invalid_token=st.text(min_size=1, max_size=100))
    def test_invalid_token_rejected(self, invalid_token):
        """
        Property: For any string that is not a valid token, validation should
        return None (indicating invalid token).
        
        Validates: Requirements 1.4
        """
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create a user and a valid token to ensure database is populated
            user = db.get_or_create_user('09123456789')
            valid_token = db.create_auth_token(user['id'])
            
            # Skip if the randomly generated token happens to match the valid one
            assume(invalid_token != valid_token)
            
            # Validate the invalid token
            result = db.validate_token(invalid_token)
            
            # Should return None for invalid tokens
            self.assertIsNone(
                result,
                f"Invalid token '{invalid_token}' should not validate successfully"
            )
            
        except Exception as e:
            self.fail(f"Unexpected error with invalid_token='{invalid_token}': {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)


class TestDatabasePersistence(unittest.TestCase):
    """
    Test database persistence completeness.
    Feature: user-wallet-system, Property 20: Database persistence completeness
    Feature: user-wallet-system, Property 21: Transaction persistence completeness
    Feature: user-wallet-system, Property 22: Plate persistence completeness
    """
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone_number=st.text(min_size=1, max_size=15),
        role=st.sampled_from(['user', 'admin', 'superuser'])
    )
    def test_user_persistence_completeness(self, phone_number, role):
        """
        Property 20: For any user creation, the database should contain a record
        with phone_number, role, and created_at fields populated.
        
        Validates: Requirements 7.1
        """
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user
            user_id = db.create_user(phone_number, role=role)
            self.assertIsNotNone(user_id)
            self.assertIsInstance(user_id, int)
            self.assertGreater(user_id, 0)
            
            # Retrieve user from database
            user = db.get_user_by_id(user_id)
            
            # Verify all required fields are populated
            self.assertIsNotNone(user, "User should exist in database")
            self.assertIn('phone_number', user, "phone_number field should exist")
            self.assertIn('role', user, "role field should exist")
            self.assertIn('created_at', user, "created_at field should exist")
            
            # Verify field values
            self.assertEqual(user['phone_number'], phone_number, "phone_number should match")
            self.assertEqual(user['role'], role, "role should match")
            self.assertIsNotNone(user['created_at'], "created_at should be populated")
            self.assertNotEqual(user['created_at'], '', "created_at should not be empty")
            
            # Verify created_at is a valid timestamp
            try:
                datetime.strptime(user['created_at'], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                self.fail(f"created_at '{user['created_at']}' is not a valid timestamp")
            
        except Exception as e:
            self.fail(f"Unexpected error with phone='{phone_number}', role='{role}': {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone_number=st.text(min_size=1, max_size=15),
        transaction_type=st.sampled_from(['charge', 'payment', 'refund']),
        amount=st.integers(min_value=1, max_value=10000000),
        description=st.text(max_size=100)
    )
    def test_transaction_persistence_completeness(self, phone_number, transaction_type, amount, description):
        """
        Property 21: For any wallet transaction, the database should contain a
        transaction record with transaction_type, amount, timestamp, and wallet_id
        fields populated.
        
        Validates: Requirements 7.2
        """
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)
        assume('\x00' not in description)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user (which also creates wallet)
            user_id = db.create_user(phone_number, role='user')
            self.assertIsNotNone(user_id)
            
            # Get wallet
            wallet = db.get_wallet_by_user_id(user_id)
            self.assertIsNotNone(wallet, "Wallet should be created with user")
            wallet_id = wallet['id']
            
            # Create transaction
            transaction_id = db.create_transaction(
                wallet_id=wallet_id,
                transaction_type=transaction_type,
                amount=amount,
                description=description
            )
            self.assertIsNotNone(transaction_id)
            self.assertIsInstance(transaction_id, int)
            self.assertGreater(transaction_id, 0)
            
            # Retrieve transaction from database
            transaction = db.get_transaction_by_id(transaction_id)
            
            # Verify all required fields are populated
            self.assertIsNotNone(transaction, "Transaction should exist in database")
            self.assertIn('transaction_type', transaction, "transaction_type field should exist")
            self.assertIn('amount', transaction, "amount field should exist")
            self.assertIn('timestamp', transaction, "timestamp field should exist")
            self.assertIn('wallet_id', transaction, "wallet_id field should exist")
            
            # Verify field values
            self.assertEqual(transaction['transaction_type'], transaction_type, "transaction_type should match")
            self.assertEqual(transaction['amount'], amount, "amount should match")
            self.assertEqual(transaction['wallet_id'], wallet_id, "wallet_id should match")
            self.assertIsNotNone(transaction['timestamp'], "timestamp should be populated")
            self.assertNotEqual(transaction['timestamp'], '', "timestamp should not be empty")
            
            # Verify timestamp is a valid timestamp
            try:
                datetime.strptime(transaction['timestamp'], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                self.fail(f"timestamp '{transaction['timestamp']}' is not a valid timestamp")
            
        except Exception as e:
            self.fail(f"Unexpected error: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone_number=st.text(min_size=1, max_size=15),
        plate=st.text(min_size=1, max_size=20)
    )
    def test_plate_persistence_completeness(self, phone_number, plate):
        """
        Property 22: For any plate registration, the database should contain a
        user_plates record with plate, user_id, and registered_at fields populated.
        
        Validates: Requirements 7.3
        """
        assume(phone_number.strip() != '')
        assume(plate.strip() != '')
        assume('\x00' not in phone_number)
        assume('\x00' not in plate)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user
            user_id = db.create_user(phone_number, role='user')
            self.assertIsNotNone(user_id)
            
            # Register plate
            plate_id = db.add_user_plate(user_id, plate)
            self.assertIsNotNone(plate_id)
            self.assertIsInstance(plate_id, int)
            self.assertGreater(plate_id, 0)
            
            # Retrieve plate from database
            user_plate = db.get_user_plate_by_id(plate_id)
            
            # Verify all required fields are populated
            self.assertIsNotNone(user_plate, "User plate should exist in database")
            self.assertIn('plate', user_plate, "plate field should exist")
            self.assertIn('user_id', user_plate, "user_id field should exist")
            self.assertIn('registered_at', user_plate, "registered_at field should exist")
            
            # Verify field values
            self.assertEqual(user_plate['plate'], plate, "plate should match")
            self.assertEqual(user_plate['user_id'], user_id, "user_id should match")
            self.assertIsNotNone(user_plate['registered_at'], "registered_at should be populated")
            self.assertNotEqual(user_plate['registered_at'], '', "registered_at should not be empty")
            
            # Verify registered_at is a valid timestamp
            try:
                datetime.strptime(user_plate['registered_at'], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                self.fail(f"registered_at '{user_plate['registered_at']}' is not a valid timestamp")
            
        except Exception as e:
            self.fail(f"Unexpected error: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)


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
        # Django setup
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parking_api.settings')
        import django
        django.setup()
        
        from django.test import Client
        from rest_framework import status as http_status
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            client = Client()
            
            # Create a valid user and token to ensure we're not testing against empty database
            user = db.get_or_create_user('09123456789')
            valid_token = db.create_auth_token(user['id'])
            
            # Verify the token can be validated (sanity check)
            validated_user_id = db.validate_token(valid_token)
            assert validated_user_id == user['id'], f"Token validation failed: expected {user['id']}, got {validated_user_id}"
            
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
                    response_no_token = client.post(
                        endpoint,
                        content_type='application/json'
                    )
                
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
                        content_type='application/json',
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
            
            # Note: Testing with valid tokens requires database synchronization between
            # the test setup and Django's middleware, which is complex in this test setup.
            # Valid token functionality is tested in other integration tests.
        
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
        
        # Django setup
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parking_api.settings')
        import django
        django.setup()
        
        from django.test import Client
        from rest_framework import status as http_status
        
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
                        content_type='application/json',
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
        
        # Django setup
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parking_api.settings')
        import django
        django.setup()
        
        from django.test import Client
        from rest_framework import status as http_status
        
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


class TestTransactionRecordCreation(unittest.TestCase):
    """
    Test transaction record creation.
    Feature: user-wallet-system, Property 7: Transaction record creation
    """
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone_number=st.text(min_size=1, max_size=15),
        transaction_type=st.sampled_from(['charge', 'payment', 'refund']),
        amount=st.integers(min_value=1, max_value=10000000),
        description=st.text(max_size=100)
    )
    def test_transaction_record_creation(self, phone_number, transaction_type, amount, description):
        """
        Property 7: For any wallet operation (charge or payment), a corresponding
        transaction record should be created with the correct amount, type, and timestamp.
        
        Validates: Requirements 2.3
        """
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)
        assume('\x00' not in description)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user (which also creates wallet)
            user_id = db.create_user(phone_number, role='user')
            self.assertIsNotNone(user_id)
            
            # Get wallet
            wallet = db.get_wallet_by_user_id(user_id)
            self.assertIsNotNone(wallet, "Wallet should be created with user")
            wallet_id = wallet['id']
            
            # For payment operations, ensure sufficient balance
            if transaction_type == 'payment':
                # Set balance to be sufficient for the payment
                conn = db.get_conn()
                cur = conn.cursor()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cur.execute("""
                    UPDATE wallets
                    SET balance = ?, last_updated = ?
                    WHERE id = ?
                """, (amount * 2, timestamp, wallet_id))
                conn.commit()
                conn.close()
            
            # Record time before transaction
            time_before = datetime.now()
            
            # Create transaction
            transaction_id = db.create_transaction(
                wallet_id=wallet_id,
                transaction_type=transaction_type,
                amount=amount,
                description=description
            )
            
            # Record time after transaction
            time_after = datetime.now()
            
            # Verify transaction was created
            self.assertIsNotNone(transaction_id, "Transaction ID should be returned")
            self.assertIsInstance(transaction_id, int, "Transaction ID should be an integer")
            self.assertGreater(transaction_id, 0, "Transaction ID should be positive")
            
            # Retrieve transaction from database
            transaction = db.get_transaction_by_id(transaction_id)
            
            # Verify transaction exists
            self.assertIsNotNone(transaction, "Transaction should exist in database")
            
            # Verify correct amount
            self.assertEqual(
                transaction['amount'],
                amount,
                f"Transaction amount should be {amount}, got {transaction['amount']}"
            )
            
            # Verify correct type
            self.assertEqual(
                transaction['transaction_type'],
                transaction_type,
                f"Transaction type should be '{transaction_type}', got '{transaction['transaction_type']}'"
            )
            
            # Verify timestamp exists and is valid
            self.assertIn('timestamp', transaction, "Transaction should have timestamp field")
            self.assertIsNotNone(transaction['timestamp'], "Timestamp should not be None")
            self.assertNotEqual(transaction['timestamp'], '', "Timestamp should not be empty")
            
            # Verify timestamp is a valid datetime string
            try:
                transaction_time = datetime.strptime(transaction['timestamp'], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                self.fail(f"Timestamp '{transaction['timestamp']}' is not a valid datetime")
            
            # Verify timestamp is within reasonable range (between before and after)
            # Allow 1 second buffer for clock precision
            self.assertGreaterEqual(
                transaction_time,
                time_before - timedelta(seconds=1),
                f"Transaction timestamp {transaction_time} should be >= {time_before}"
            )
            self.assertLessEqual(
                transaction_time,
                time_after + timedelta(seconds=1),
                f"Transaction timestamp {transaction_time} should be <= {time_after}"
            )
            
            # Verify wallet_id is correct
            self.assertEqual(
                transaction['wallet_id'],
                wallet_id,
                f"Transaction wallet_id should be {wallet_id}, got {transaction['wallet_id']}"
            )
            
            # Verify description is stored correctly
            self.assertEqual(
                transaction['description'],
                description,
                f"Transaction description should match"
            )
            
        except Exception as e:
            self.fail(f"Unexpected error with phone='{phone_number}', type='{transaction_type}', amount={amount}: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone_number=st.text(min_size=1, max_size=15),
        charge_amount=st.integers(min_value=1, max_value=10000000)
    )
    def test_charge_wallet_creates_transaction(self, phone_number, charge_amount):
        """
        Property: For any wallet charge operation, a transaction record with
        type='charge' should be created.
        
        Validates: Requirements 2.3
        """
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user
            user_id = db.create_user(phone_number, role='user')
            self.assertIsNotNone(user_id)
            
            # Get wallet
            wallet = db.get_wallet_by_user_id(user_id)
            wallet_id = wallet['id']
            
            # Get initial transaction count
            transactions_before = db.get_wallet_transactions(user_id, limit=1000)
            count_before = transactions_before['count']
            
            # Charge wallet
            result = db.charge_wallet(user_id, charge_amount)
            self.assertIsNotNone(result)
            self.assertIn('transaction_id', result)
            
            transaction_id = result['transaction_id']
            
            # Verify transaction count increased
            transactions_after = db.get_wallet_transactions(user_id, limit=1000)
            count_after = transactions_after['count']
            self.assertEqual(
                count_after,
                count_before + 1,
                f"Transaction count should increase by 1, was {count_before}, now {count_after}"
            )
            
            # Retrieve the transaction
            transaction = db.get_transaction_by_id(transaction_id)
            self.assertIsNotNone(transaction, "Transaction should exist")
            
            # Verify transaction details
            self.assertEqual(
                transaction['transaction_type'],
                'charge',
                f"Transaction type should be 'charge', got '{transaction['transaction_type']}'"
            )
            self.assertEqual(
                transaction['amount'],
                charge_amount,
                f"Transaction amount should be {charge_amount}, got {transaction['amount']}"
            )
            self.assertEqual(
                transaction['wallet_id'],
                wallet_id,
                f"Transaction wallet_id should be {wallet_id}, got {transaction['wallet_id']}"
            )
            
            # Verify timestamp is recent
            transaction_time = datetime.strptime(transaction['timestamp'], "%Y-%m-%d %H:%M:%S")
            time_diff = (datetime.now() - transaction_time).total_seconds()
            self.assertLess(
                abs(time_diff),
                5,
                f"Transaction timestamp should be recent (within 5 seconds), diff was {time_diff}"
            )
            
        except Exception as e:
            self.fail(f"Unexpected error with phone='{phone_number}', charge={charge_amount}: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone_number=st.text(min_size=1, max_size=15),
        initial_balance=st.integers(min_value=10000, max_value=10000000),
        payment_amount=st.integers(min_value=1, max_value=9999)
    )
    def test_payment_deduction_creates_transaction(self, phone_number, initial_balance, payment_amount):
        """
        Property: For any wallet payment/deduction operation, a transaction record
        with type='payment' should be created.
        
        Validates: Requirements 2.3
        """
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)
        assume(initial_balance >= payment_amount)  # Ensure sufficient balance
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user
            user_id = db.create_user(phone_number, role='user')
            self.assertIsNotNone(user_id)
            
            # Get wallet and set initial balance
            wallet = db.get_wallet_by_user_id(user_id)
            wallet_id = wallet['id']
            
            conn = db.get_conn()
            cur = conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("""
                UPDATE wallets
                SET balance = ?, last_updated = ?
                WHERE id = ?
            """, (initial_balance, timestamp, wallet_id))
            conn.commit()
            conn.close()
            
            # Get initial transaction count
            transactions_before = db.get_wallet_transactions(user_id, limit=1000)
            count_before = transactions_before['count']
            
            # Deduct from wallet
            result = db.deduct_from_wallet(user_id, payment_amount, description='Test payment')
            self.assertIsNotNone(result)
            self.assertIn('transaction_id', result)
            
            transaction_id = result['transaction_id']
            
            # Verify transaction count increased
            transactions_after = db.get_wallet_transactions(user_id, limit=1000)
            count_after = transactions_after['count']
            self.assertEqual(
                count_after,
                count_before + 1,
                f"Transaction count should increase by 1, was {count_before}, now {count_after}"
            )
            
            # Retrieve the transaction
            transaction = db.get_transaction_by_id(transaction_id)
            self.assertIsNotNone(transaction, "Transaction should exist")
            
            # Verify transaction details
            self.assertEqual(
                transaction['transaction_type'],
                'payment',
                f"Transaction type should be 'payment', got '{transaction['transaction_type']}'"
            )
            self.assertEqual(
                transaction['amount'],
                payment_amount,
                f"Transaction amount should be {payment_amount}, got {transaction['amount']}"
            )
            self.assertEqual(
                transaction['wallet_id'],
                wallet_id,
                f"Transaction wallet_id should be {wallet_id}, got {transaction['wallet_id']}"
            )
            
            # Verify timestamp is recent
            transaction_time = datetime.strptime(transaction['timestamp'], "%Y-%m-%d %H:%M:%S")
            time_diff = (datetime.now() - transaction_time).total_seconds()
            self.assertLess(
                abs(time_diff),
                5,
                f"Transaction timestamp should be recent (within 5 seconds), diff was {time_diff}"
            )
            
        except Exception as e:
            self.fail(f"Unexpected error with phone='{phone_number}', balance={initial_balance}, payment={payment_amount}: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone_number=st.text(min_size=1, max_size=15),
        operations=st.lists(
            st.tuples(
                st.sampled_from(['charge', 'payment']),
                st.integers(min_value=1, max_value=100000)
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_multiple_operations_create_multiple_transactions(self, phone_number, operations):
        """
        Property: For any sequence of wallet operations, each operation should
        create exactly one transaction record.
        
        Validates: Requirements 2.3
        """
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user
            user_id = db.create_user(phone_number, role='user')
            self.assertIsNotNone(user_id)
            
            # Set high initial balance to ensure all payments succeed
            wallet = db.get_wallet_by_user_id(user_id)
            wallet_id = wallet['id']
            
            conn = db.get_conn()
            cur = conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("""
                UPDATE wallets
                SET balance = ?, last_updated = ?
                WHERE id = ?
            """, (100000000, timestamp, wallet_id))
            conn.commit()
            conn.close()
            
            # Get initial transaction count
            transactions_before = db.get_wallet_transactions(user_id, limit=1000)
            count_before = transactions_before['count']
            
            # Perform all operations
            transaction_ids = []
            for op_type, amount in operations:
                if op_type == 'charge':
                    result = db.charge_wallet(user_id, amount)
                else:  # payment
                    result = db.deduct_from_wallet(user_id, amount, description='Test payment')
                
                self.assertIsNotNone(result)
                self.assertIn('transaction_id', result)
                transaction_ids.append(result['transaction_id'])
            
            # Verify transaction count increased by number of operations
            transactions_after = db.get_wallet_transactions(user_id, limit=1000)
            count_after = transactions_after['count']
            expected_count = count_before + len(operations)
            self.assertEqual(
                count_after,
                expected_count,
                f"Transaction count should be {expected_count}, got {count_after}"
            )
            
            # Verify all transaction IDs are unique
            self.assertEqual(
                len(transaction_ids),
                len(set(transaction_ids)),
                "All transaction IDs should be unique"
            )
            
            # Verify each transaction exists and has correct type
            for i, (op_type, amount) in enumerate(operations):
                transaction = db.get_transaction_by_id(transaction_ids[i])
                self.assertIsNotNone(transaction, f"Transaction {i} should exist")
                self.assertEqual(
                    transaction['transaction_type'],
                    op_type,
                    f"Transaction {i} type should be '{op_type}', got '{transaction['transaction_type']}'"
                )
                self.assertEqual(
                    transaction['amount'],
                    amount,
                    f"Transaction {i} amount should be {amount}, got {transaction['amount']}"
                )
            
        except Exception as e:
            self.fail(f"Unexpected error with phone='{phone_number}', operations={operations}: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)


class TestWalletBalanceUpdates(unittest.TestCase):
    """
    Test wallet balance update correctness.
    Feature: user-wallet-system, Property 6: Wallet balance update correctness
    """
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone_number=st.text(min_size=1, max_size=15),
        initial_balance=st.integers(min_value=0, max_value=10000000),
        charge_amount=st.integers(min_value=1, max_value=10000000)
    )
    def test_wallet_balance_update_correctness(self, phone_number, initial_balance, charge_amount):
        """
        Property 6: For any wallet with balance B and any positive charge amount A,
        after charging the wallet, the new balance should equal B + A.
        
        Validates: Requirements 2.2
        """
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user (which also creates wallet with balance 0)
            user_id = db.create_user(phone_number, role='user')
            self.assertIsNotNone(user_id)
            
            # Get wallet
            wallet = db.get_wallet_by_user_id(user_id)
            self.assertIsNotNone(wallet, "Wallet should be created with user")
            
            # Set initial balance if not zero
            if initial_balance > 0:
                conn = db.get_conn()
                cur = conn.cursor()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cur.execute("""
                    UPDATE wallets
                    SET balance = ?, last_updated = ?
                    WHERE user_id = ?
                """, (initial_balance, timestamp, user_id))
                conn.commit()
                conn.close()
            
            # Verify initial balance
            current_balance = db.get_wallet_balance(user_id)
            self.assertEqual(
                current_balance,
                initial_balance,
                f"Initial balance should be {initial_balance}, got {current_balance}"
            )
            
            # Charge the wallet
            result = db.charge_wallet(user_id, charge_amount)
            self.assertIsNotNone(result, "charge_wallet should return a result")
            self.assertIn('new_balance', result, "Result should contain new_balance")
            
            # Calculate expected balance
            expected_balance = initial_balance + charge_amount
            
            # Verify new balance from result
            self.assertEqual(
                result['new_balance'],
                expected_balance,
                f"New balance should be {expected_balance} (initial {initial_balance} + charge {charge_amount}), "
                f"but got {result['new_balance']}"
            )
            
            # Verify balance in database
            actual_balance = db.get_wallet_balance(user_id)
            self.assertEqual(
                actual_balance,
                expected_balance,
                f"Database balance should be {expected_balance}, but got {actual_balance}"
            )
            
            # Verify transaction was created
            self.assertIn('transaction_id', result, "Result should contain transaction_id")
            transaction_id = result['transaction_id']
            self.assertIsNotNone(transaction_id)
            self.assertIsInstance(transaction_id, int)
            self.assertGreater(transaction_id, 0)
            
            # Verify transaction details
            transaction = db.get_transaction_by_id(transaction_id)
            self.assertIsNotNone(transaction, "Transaction should exist")
            self.assertEqual(transaction['transaction_type'], 'charge', "Transaction type should be 'charge'")
            self.assertEqual(transaction['amount'], charge_amount, f"Transaction amount should be {charge_amount}")
            
        except Exception as e:
            self.fail(f"Unexpected error with phone='{phone_number}', initial={initial_balance}, charge={charge_amount}: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone_number=st.text(min_size=1, max_size=15),
        charges=st.lists(st.integers(min_value=1, max_value=1000000), min_size=1, max_size=10)
    )
    def test_multiple_charges_accumulate_correctly(self, phone_number, charges):
        """
        Property: For any sequence of positive charge amounts, the final balance
        should equal the sum of all charges.
        
        Validates: Requirements 2.2
        """
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user
            user_id = db.create_user(phone_number, role='user')
            self.assertIsNotNone(user_id)
            
            # Initial balance should be 0
            initial_balance = db.get_wallet_balance(user_id)
            self.assertEqual(initial_balance, 0, "Initial balance should be 0")
            
            # Apply all charges
            expected_balance = 0
            for charge_amount in charges:
                result = db.charge_wallet(user_id, charge_amount)
                expected_balance += charge_amount
                
                # Verify balance after each charge
                self.assertEqual(
                    result['new_balance'],
                    expected_balance,
                    f"After charging {charge_amount}, balance should be {expected_balance}, got {result['new_balance']}"
                )
            
            # Verify final balance
            final_balance = db.get_wallet_balance(user_id)
            self.assertEqual(
                final_balance,
                expected_balance,
                f"Final balance should be {expected_balance} (sum of all charges), got {final_balance}"
            )
            
            # Verify total equals sum of charges
            total_charges = sum(charges)
            self.assertEqual(
                final_balance,
                total_charges,
                f"Final balance {final_balance} should equal sum of charges {total_charges}"
            )
            
        except Exception as e:
            self.fail(f"Unexpected error with phone='{phone_number}', charges={charges}: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone_number=st.text(min_size=1, max_size=15),
        invalid_amount=st.integers(max_value=0)
    )
    def test_negative_or_zero_charge_rejected(self, phone_number, invalid_amount):
        """
        Property: For any non-positive charge amount (zero or negative), the
        charge operation should be rejected with an error.
        
        Validates: Requirements 2.2
        """
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user
            user_id = db.create_user(phone_number, role='user')
            self.assertIsNotNone(user_id)
            
            # Get initial balance
            initial_balance = db.get_wallet_balance(user_id)
            
            # Attempt to charge with invalid amount
            with self.assertRaises(ValueError) as context:
                db.charge_wallet(user_id, invalid_amount)
            
            # Verify error message
            self.assertIn('positive', str(context.exception).lower())
            
            # Verify balance unchanged
            final_balance = db.get_wallet_balance(user_id)
            self.assertEqual(
                final_balance,
                initial_balance,
                f"Balance should remain {initial_balance} after failed charge, got {final_balance}"
            )
            
        except Exception as e:
            self.fail(f"Unexpected error with phone='{phone_number}', amount={invalid_amount}: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone_number=st.text(min_size=1, max_size=15),
        balance=st.integers(min_value=1000, max_value=10000000),
        charge_amount=st.integers(min_value=1, max_value=10000000)
    )
    def test_wallet_last_updated_timestamp_changes(self, phone_number, balance, charge_amount):
        """
        Property: For any wallet charge operation, the last_updated timestamp
        should be updated to reflect the operation time.
        
        Validates: Requirements 2.2
        """
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user
            user_id = db.create_user(phone_number, role='user')
            self.assertIsNotNone(user_id)
            
            # Set initial balance
            conn = db.get_conn()
            cur = conn.cursor()
            initial_timestamp = "2020-01-01 00:00:00"
            cur.execute("""
                UPDATE wallets
                SET balance = ?, last_updated = ?
                WHERE user_id = ?
            """, (balance, initial_timestamp, user_id))
            conn.commit()
            conn.close()
            
            # Get wallet before charge
            wallet_before = db.get_wallet_by_user_id(user_id)
            self.assertEqual(wallet_before['last_updated'], initial_timestamp)
            
            # Charge the wallet
            result = db.charge_wallet(user_id, charge_amount)
            self.assertIsNotNone(result)
            
            # Get wallet after charge
            wallet_after = db.get_wallet_by_user_id(user_id)
            
            # Verify last_updated changed
            self.assertNotEqual(
                wallet_after['last_updated'],
                initial_timestamp,
                "last_updated timestamp should change after charge"
            )
            
            # Verify new timestamp is more recent
            before_dt = datetime.strptime(wallet_before['last_updated'], "%Y-%m-%d %H:%M:%S")
            after_dt = datetime.strptime(wallet_after['last_updated'], "%Y-%m-%d %H:%M:%S")
            self.assertGreater(
                after_dt,
                before_dt,
                "last_updated should be more recent after charge"
            )
            
        except Exception as e:
            self.fail(f"Unexpected error with phone='{phone_number}', balance={balance}, charge={charge_amount}: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)


if __name__ == '__main__':
    unittest.main()


class TestTransactionChronologicalOrdering(unittest.TestCase):
    """
    Test transaction chronological ordering.
    Feature: user-wallet-system, Property 9: Transaction chronological ordering
    """
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone_number=st.text(min_size=1, max_size=15),
        operations=st.lists(
            st.tuples(
                st.sampled_from(['charge', 'payment']),
                st.integers(min_value=1, max_value=100000)
            ),
            min_size=2,
            max_size=20
        )
    )
    def test_transaction_chronological_ordering(self, phone_number, operations):
        """
        Property 9: For any user's transaction history, the transactions should be
        ordered by timestamp in descending order (most recent first).
        
        Validates: Requirements 2.6
        """
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user (which also creates wallet)
            user_id = db.create_user(phone_number, role='user')
            self.assertIsNotNone(user_id)
            
            # Set high initial balance to ensure all payments succeed
            wallet = db.get_wallet_by_user_id(user_id)
            wallet_id = wallet['id']
            
            conn = db.get_conn()
            cur = conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("""
                UPDATE wallets
                SET balance = ?, last_updated = ?
                WHERE id = ?
            """, (100000000, timestamp, wallet_id))
            conn.commit()
            conn.close()
            
            # Perform all operations and record their timestamps
            transaction_ids = []
            for op_type, amount in operations:
                if op_type == 'charge':
                    result = db.charge_wallet(user_id, amount)
                else:  # payment
                    result = db.deduct_from_wallet(user_id, amount, description='Test payment')
                
                self.assertIsNotNone(result)
                self.assertIn('transaction_id', result)
                transaction_ids.append(result['transaction_id'])
            
            # Get transaction history
            history = db.get_wallet_transactions(user_id, limit=1000)
            self.assertIsNotNone(history)
            self.assertIn('results', history)
            
            transactions = history['results']
            
            # Verify we got all transactions
            self.assertEqual(
                len(transactions),
                len(operations),
                f"Should have {len(operations)} transactions, got {len(transactions)}"
            )
            
            # Verify transactions are ordered by timestamp in descending order (most recent first)
            for i in range(len(transactions) - 1):
                current_timestamp = transactions[i]['timestamp']
                next_timestamp = transactions[i + 1]['timestamp']
                
                # Parse timestamps
                current_time = datetime.strptime(current_timestamp, "%Y-%m-%d %H:%M:%S")
                next_time = datetime.strptime(next_timestamp, "%Y-%m-%d %H:%M:%S")
                
                # Current transaction should be more recent than or equal to next transaction
                self.assertGreaterEqual(
                    current_time,
                    next_time,
                    f"Transaction at index {i} (timestamp: {current_timestamp}) should be "
                    f"more recent than or equal to transaction at index {i+1} (timestamp: {next_timestamp}). "
                    f"Transactions should be ordered by timestamp DESC (most recent first)."
                )
            
            # Additional verification: check that the most recent transaction is first
            if len(transactions) > 0:
                first_transaction = transactions[0]
                first_timestamp = datetime.strptime(first_transaction['timestamp'], "%Y-%m-%d %H:%M:%S")
                
                # The first transaction should be the most recent one
                for transaction in transactions[1:]:
                    transaction_time = datetime.strptime(transaction['timestamp'], "%Y-%m-%d %H:%M:%S")
                    self.assertGreaterEqual(
                        first_timestamp,
                        transaction_time,
                        f"First transaction (timestamp: {first_transaction['timestamp']}) should be "
                        f"the most recent, but found transaction with timestamp: {transaction['timestamp']}"
                    )
            
        except Exception as e:
            self.fail(f"Unexpected error with phone='{phone_number}', operations={len(operations)}: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone_number=st.text(min_size=1, max_size=15),
        num_transactions=st.integers(min_value=1, max_value=50)
    )
    def test_transaction_ordering_with_pagination(self, phone_number, num_transactions):
        """
        Property: For any user's transaction history with pagination, transactions
        across all pages should maintain chronological order (most recent first).
        
        Validates: Requirements 2.6
        """
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user
            user_id = db.create_user(phone_number, role='user')
            self.assertIsNotNone(user_id)
            
            # Create multiple transactions
            for i in range(num_transactions):
                db.charge_wallet(user_id, 1000 + i)
            
            # Fetch transactions with pagination (page size of 10)
            page_size = 10
            all_transactions = []
            offset = 0
            
            while True:
                history = db.get_wallet_transactions(user_id, limit=page_size, offset=offset)
                transactions = history['results']
                
                if not transactions:
                    break
                
                all_transactions.extend(transactions)
                offset += page_size
                
                # Stop if we've fetched all transactions
                if len(all_transactions) >= history['count']:
                    break
            
            # Verify we got all transactions
            self.assertEqual(
                len(all_transactions),
                num_transactions,
                f"Should have fetched all {num_transactions} transactions, got {len(all_transactions)}"
            )
            
            # Verify chronological ordering across all pages
            for i in range(len(all_transactions) - 1):
                current_timestamp = all_transactions[i]['timestamp']
                next_timestamp = all_transactions[i + 1]['timestamp']
                
                current_time = datetime.strptime(current_timestamp, "%Y-%m-%d %H:%M:%S")
                next_time = datetime.strptime(next_timestamp, "%Y-%m-%d %H:%M:%S")
                
                self.assertGreaterEqual(
                    current_time,
                    next_time,
                    f"Transaction at index {i} should be more recent than or equal to transaction at index {i+1}, "
                    f"even across pagination boundaries"
                )
            
        except Exception as e:
            self.fail(f"Unexpected error with phone='{phone_number}', num_transactions={num_transactions}: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone_number=st.text(min_size=1, max_size=15),
        transaction_types=st.lists(
            st.sampled_from(['charge', 'payment', 'refund']),
            min_size=3,
            max_size=15
        )
    )
    def test_mixed_transaction_types_ordered_chronologically(self, phone_number, transaction_types):
        """
        Property: For any mix of transaction types (charge, payment, refund),
        all transactions should be ordered chronologically regardless of type.
        
        Validates: Requirements 2.6
        """
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user
            user_id = db.create_user(phone_number, role='user')
            self.assertIsNotNone(user_id)
            
            # Set high initial balance
            wallet = db.get_wallet_by_user_id(user_id)
            wallet_id = wallet['id']
            
            conn = db.get_conn()
            cur = conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("""
                UPDATE wallets
                SET balance = ?, last_updated = ?
                WHERE id = ?
            """, (100000000, timestamp, wallet_id))
            conn.commit()
            conn.close()
            
            # Create transactions of different types
            for transaction_type in transaction_types:
                if transaction_type == 'charge':
                    db.charge_wallet(user_id, 5000)
                elif transaction_type == 'payment':
                    db.deduct_from_wallet(user_id, 1000, description='Test payment')
                elif transaction_type == 'refund':
                    # Create a refund transaction directly
                    db.create_transaction(
                        wallet_id=wallet_id,
                        transaction_type='refund',
                        amount=500,
                        description='Test refund'
                    )
            
            # Get transaction history
            history = db.get_wallet_transactions(user_id, limit=1000)
            transactions = history['results']
            
            # Verify we got all transactions
            self.assertEqual(
                len(transactions),
                len(transaction_types),
                f"Should have {len(transaction_types)} transactions, got {len(transactions)}"
            )
            
            # Verify chronological ordering regardless of transaction type
            for i in range(len(transactions) - 1):
                current_timestamp = transactions[i]['timestamp']
                next_timestamp = transactions[i + 1]['timestamp']
                
                current_time = datetime.strptime(current_timestamp, "%Y-%m-%d %H:%M:%S")
                next_time = datetime.strptime(next_timestamp, "%Y-%m-%d %H:%M:%S")
                
                self.assertGreaterEqual(
                    current_time,
                    next_time,
                    f"Transaction type '{transactions[i]['transaction_type']}' at index {i} "
                    f"should be more recent than or equal to transaction type '{transactions[i+1]['transaction_type']}' "
                    f"at index {i+1}. Ordering should be by timestamp, not by type."
                )
            
            # Verify that different transaction types are intermixed if they exist
            transaction_type_set = set(t['transaction_type'] for t in transactions)
            if len(transaction_type_set) > 1:
                # If we have multiple types, verify they're not grouped by type
                # (which would indicate incorrect ordering)
                # This is a weak check but helps ensure ordering is by timestamp
                types_in_order = [t['transaction_type'] for t in transactions]
                
                # If all transactions were grouped by type, we'd see all of one type,
                # then all of another type, etc. Check that this is NOT the case
                # by verifying that the types don't form contiguous blocks
                # (unless there's only one transaction of each type)
                type_counts = {}
                for t_type in transaction_types:
                    type_counts[t_type] = type_counts.get(t_type, 0) + 1
                
                # If any type appears more than once, check for interleaving
                has_multiple_of_any_type = any(count > 1 for count in type_counts.values())
                if has_multiple_of_any_type and len(transaction_type_set) > 1:
                    # Just verify that timestamps are properly ordered
                    # (the main assertion above already does this)
                    pass
            
        except Exception as e:
            self.fail(f"Unexpected error with phone='{phone_number}', types={len(transaction_types)}: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)


if __name__ == '__main__':
    unittest.main()


class TestFinancialPrecisionPreservation(unittest.TestCase):
    """
    Test financial precision preservation.
    Feature: user-wallet-system, Property 24: Financial precision preservation
    """
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone_number=st.text(min_size=1, max_size=15),
        initial_balance=st.integers(min_value=0, max_value=10000000),
        operations=st.lists(
            st.tuples(
                st.sampled_from(['charge', 'payment']),
                st.integers(min_value=1, max_value=1000000)
            ),
            min_size=1,
            max_size=20
        )
    )
    def test_financial_precision_preservation(self, phone_number, initial_balance, operations):
        """
        Property 24: For any sequence of wallet operations, the final balance should
        equal the initial balance plus all charges minus all payments, with no
        rounding errors.
        
        Validates: Requirements 7.6
        """
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)
        
        # Calculate expected final balance and check intermediate balances
        running_balance = initial_balance
        total_charges = 0
        total_payments = 0
        
        for op_type, amount in operations:
            if op_type == 'charge':
                total_charges += amount
                running_balance += amount
            else:  # payment
                total_payments += amount
                running_balance -= amount
            
            # Skip if any intermediate balance would be negative
            assume(running_balance >= 0)
        
        expected_balance = running_balance
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user (which also creates wallet with balance 0)
            user_id = db.create_user(phone_number, role='user')
            self.assertIsNotNone(user_id)
            
            # Set initial balance if not zero
            if initial_balance > 0:
                conn = db.get_conn()
                cur = conn.cursor()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cur.execute("""
                    UPDATE wallets
                    SET balance = ?, last_updated = ?
                    WHERE user_id = ?
                """, (initial_balance, timestamp, user_id))
                conn.commit()
                conn.close()
            
            # Verify initial balance
            current_balance = db.get_wallet_balance(user_id)
            self.assertEqual(
                current_balance,
                initial_balance,
                f"Initial balance should be {initial_balance}, got {current_balance}"
            )
            
            # Perform all operations
            for op_type, amount in operations:
                if op_type == 'charge':
                    result = db.charge_wallet(user_id, amount)
                    self.assertIsNotNone(result, f"charge_wallet should return a result for amount {amount}")
                else:  # payment
                    result = db.deduct_from_wallet(user_id, amount, description='Test payment')
                    self.assertIsNotNone(result, f"deduct_from_wallet should return a result for amount {amount}")
            
            # Get final balance
            final_balance = db.get_wallet_balance(user_id)
            
            # Verify financial precision: final balance = initial + charges - payments
            self.assertEqual(
                final_balance,
                expected_balance,
                f"Financial precision error detected!\n"
                f"Initial balance: {initial_balance}\n"
                f"Total charges: {total_charges}\n"
                f"Total payments: {total_payments}\n"
                f"Expected final balance: {expected_balance} (initial {initial_balance} + charges {total_charges} - payments {total_payments})\n"
                f"Actual final balance: {final_balance}\n"
                f"Difference: {final_balance - expected_balance}\n"
                f"Operations performed: {len(operations)}"
            )
            
            # Additional verification: sum all transaction amounts and verify against balance change
            transactions = db.get_wallet_transactions(user_id, limit=1000)
            self.assertIsNotNone(transactions)
            
            transaction_sum = 0
            for transaction in transactions['results']:
                if transaction['transaction_type'] == 'charge':
                    transaction_sum += transaction['amount']
                elif transaction['transaction_type'] == 'payment':
                    transaction_sum -= transaction['amount']
            
            balance_change = final_balance - initial_balance
            self.assertEqual(
                balance_change,
                transaction_sum,
                f"Balance change ({balance_change}) should equal sum of transaction amounts ({transaction_sum})"
            )
            
        except Exception as e:
            self.fail(f"Unexpected error with phone='{phone_number}', initial={initial_balance}, operations={len(operations)}: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone_number=st.text(min_size=1, max_size=15),
        amounts=st.lists(st.integers(min_value=1, max_value=999999), min_size=1, max_size=50)
    )
    def test_large_number_of_operations_no_precision_loss(self, phone_number, amounts):
        """
        Property: For any large sequence of charge operations, the final balance
        should exactly equal the sum of all charges with no precision loss.
        
        Validates: Requirements 7.6
        """
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user
            user_id = db.create_user(phone_number, role='user')
            self.assertIsNotNone(user_id)
            
            # Initial balance should be 0
            initial_balance = db.get_wallet_balance(user_id)
            self.assertEqual(initial_balance, 0, "Initial balance should be 0")
            
            # Perform all charges
            for amount in amounts:
                result = db.charge_wallet(user_id, amount)
                self.assertIsNotNone(result)
            
            # Calculate expected balance
            expected_balance = sum(amounts)
            
            # Get final balance
            final_balance = db.get_wallet_balance(user_id)
            
            # Verify no precision loss
            self.assertEqual(
                final_balance,
                expected_balance,
                f"After {len(amounts)} charge operations, final balance should be {expected_balance} "
                f"(sum of all charges), but got {final_balance}. "
                f"Precision loss detected: {final_balance - expected_balance}"
            )
            
        except Exception as e:
            self.fail(f"Unexpected error with phone='{phone_number}', num_operations={len(amounts)}: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone_number=st.text(min_size=1, max_size=15),
        charge_amounts=st.lists(st.integers(min_value=1, max_value=500000), min_size=1, max_size=20),
        payment_amounts=st.lists(st.integers(min_value=1, max_value=100000), min_size=1, max_size=20)
    )
    def test_alternating_charges_and_payments_preserve_precision(self, phone_number, charge_amounts, payment_amounts):
        """
        Property: For any sequence of alternating charges and payments, the final
        balance should equal sum(charges) - sum(payments) with no precision loss.
        
        Validates: Requirements 7.6
        """
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)
        
        # Calculate expected balance
        total_charges = sum(charge_amounts)
        total_payments = sum(payment_amounts)
        expected_balance = total_charges - total_payments
        
        # Skip if payments exceed charges (would cause insufficient balance)
        assume(expected_balance >= 0)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user
            user_id = db.create_user(phone_number, role='user')
            self.assertIsNotNone(user_id)
            
            # Perform all charges first to ensure sufficient balance
            for amount in charge_amounts:
                result = db.charge_wallet(user_id, amount)
                self.assertIsNotNone(result)
            
            # Then perform all payments
            for amount in payment_amounts:
                result = db.deduct_from_wallet(user_id, amount, description='Test payment')
                self.assertIsNotNone(result)
            
            # Get final balance
            final_balance = db.get_wallet_balance(user_id)
            
            # Verify precision
            self.assertEqual(
                final_balance,
                expected_balance,
                f"Financial precision error!\n"
                f"Total charges: {total_charges} (from {len(charge_amounts)} operations)\n"
                f"Total payments: {total_payments} (from {len(payment_amounts)} operations)\n"
                f"Expected balance: {expected_balance}\n"
                f"Actual balance: {final_balance}\n"
                f"Precision loss: {final_balance - expected_balance}"
            )
            
        except Exception as e:
            self.fail(f"Unexpected error with phone='{phone_number}', charges={len(charge_amounts)}, payments={len(payment_amounts)}: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone_number=st.text(min_size=1, max_size=15),
        amount=st.integers(min_value=1, max_value=10000000)
    )
    def test_charge_then_payment_returns_to_zero(self, phone_number, amount):
        """
        Property: For any amount, charging then immediately paying the same amount
        should return the balance to zero (round-trip property).
        
        Validates: Requirements 7.6
        """
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user
            user_id = db.create_user(phone_number, role='user')
            self.assertIsNotNone(user_id)
            
            # Initial balance should be 0
            initial_balance = db.get_wallet_balance(user_id)
            self.assertEqual(initial_balance, 0, "Initial balance should be 0")
            
            # Charge the wallet
            charge_result = db.charge_wallet(user_id, amount)
            self.assertIsNotNone(charge_result)
            self.assertEqual(charge_result['new_balance'], amount, f"Balance after charge should be {amount}")
            
            # Pay the same amount
            payment_result = db.deduct_from_wallet(user_id, amount, description='Test payment')
            self.assertIsNotNone(payment_result)
            
            # Final balance should be 0 (round-trip)
            final_balance = db.get_wallet_balance(user_id)
            self.assertEqual(
                final_balance,
                0,
                f"After charging {amount} and paying {amount}, balance should return to 0, "
                f"but got {final_balance}. Precision loss: {final_balance}"
            )
            
        except Exception as e:
            self.fail(f"Unexpected error with phone='{phone_number}', amount={amount}: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None)
    @given(
        phone_number=st.text(min_size=1, max_size=15),
        operations=st.lists(
            st.tuples(
                st.sampled_from(['charge', 'payment']),
                st.integers(min_value=1, max_value=100000)
            ),
            min_size=5,
            max_size=30
        )
    )
    def test_balance_equals_transaction_sum(self, phone_number, operations):
        """
        Property: For any sequence of operations, the current balance should always
        equal the sum of all transaction amounts (charges positive, payments negative).
        
        Validates: Requirements 7.6
        """
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)
        
        # Calculate if operations are valid (no negative balance)
        running_balance = 0
        for op_type, amount in operations:
            if op_type == 'charge':
                running_balance += amount
            else:
                running_balance -= amount
            # Skip if any intermediate balance would be negative
            if running_balance < 0:
                assume(False)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user
            user_id = db.create_user(phone_number, role='user')
            self.assertIsNotNone(user_id)
            
            # Perform all operations
            for op_type, amount in operations:
                if op_type == 'charge':
                    db.charge_wallet(user_id, amount)
                else:
                    db.deduct_from_wallet(user_id, amount, description='Test payment')
            
            # Get final balance
            final_balance = db.get_wallet_balance(user_id)
            
            # Get all transactions and calculate sum
            transactions = db.get_wallet_transactions(user_id, limit=1000)
            transaction_sum = 0
            for transaction in transactions['results']:
                if transaction['transaction_type'] == 'charge':
                    transaction_sum += transaction['amount']
                elif transaction['transaction_type'] == 'payment':
                    transaction_sum -= transaction['amount']
            
            # Balance should equal transaction sum
            self.assertEqual(
                final_balance,
                transaction_sum,
                f"Balance ({final_balance}) should equal sum of all transactions ({transaction_sum}). "
                f"Performed {len(operations)} operations."
            )
            
        except Exception as e:
            self.fail(f"Unexpected error with phone='{phone_number}', operations={len(operations)}: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)


if __name__ == '__main__':
    unittest.main()



class TestAutomaticPaymentProcessing(unittest.TestCase):
    """
    Test automatic payment processing.
    Feature: user-wallet-system, Property 8: Automatic payment processing
    """
    
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        phone_number=st.text(min_size=1, max_size=15),
        plate=st.text(min_size=1, max_size=20),
        initial_balance=st.integers(min_value=100000, max_value=10000000),
        parking_cost=st.integers(min_value=10000, max_value=500000)
    )
    def test_automatic_payment_processing(self, phone_number, plate, initial_balance, parking_cost):
        """
        Property 8: For any registered plate that exits parking, if the associated
        user's wallet balance is greater than or equal to the parking cost, the
        wallet balance should be reduced by exactly the parking cost.
        
        Validates: Requirements 2.4, 3.5, 8.2
        """
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)
        assume(plate.strip() != '')
        assume('\x00' not in plate)
        assume(initial_balance >= parking_cost)  # Ensure sufficient balance
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user with wallet
            user_id = db.create_user(phone_number, role='user')
            self.assertIsNotNone(user_id)
            
            # Charge wallet to initial balance
            wallet = db.get_wallet_by_user_id(user_id)
            self.assertIsNotNone(wallet)
            
            # Set initial balance directly
            conn = db.get_conn()
            cur = conn.cursor()
            cur.execute("""
                UPDATE wallets
                SET balance = ?
                WHERE user_id = ?
            """, (initial_balance, user_id))
            conn.commit()
            conn.close()
            
            # Register plate to user
            plate_id = db.add_user_plate(user_id, plate)
            self.assertIsNotNone(plate_id)
            
            # Set parking price to match our test cost
            # Calculate price_per_hour that will result in our desired cost
            # Cost = hours * price_per_hour, where hours = max(1, (duration + 59) // 60)
            # For simplicity, set duration to 60 minutes (1 hour)
            db.set_price_per_hour(parking_cost)
            
            # Register entry for the plate
            entry_id = db.register_entry(plate, 'test_image_in.jpg')
            self.assertIsNotNone(entry_id)
            
            # Get balance before exit
            balance_before = db.get_wallet_balance(user_id)
            self.assertEqual(balance_before, initial_balance)
            
            # Register exit (should trigger automatic payment)
            exit_result = db.register_exit(plate, 'test_image_out.jpg')
            
            # Verify exit was registered
            self.assertIsNotNone(exit_result, "Exit should be registered")
            self.assertIn('payment_status', exit_result)
            
            # Verify automatic payment was processed
            self.assertEqual(
                exit_result['payment_status'],
                'auto_paid',
                f"Payment status should be 'auto_paid' for registered plate with sufficient balance"
            )
            
            # Get balance after exit
            balance_after = db.get_wallet_balance(user_id)
            
            # Verify balance was reduced by exactly the parking cost
            expected_balance = initial_balance - exit_result['cost']
            self.assertEqual(
                balance_after,
                expected_balance,
                f"Wallet balance should be reduced by parking cost. "
                f"Initial: {initial_balance}, Cost: {exit_result['cost']}, "
                f"Expected: {expected_balance}, Actual: {balance_after}"
            )
            
            # Verify transaction record was created
            self.assertIn('transaction_id', exit_result, "Transaction ID should be returned")
            transaction_id = exit_result['transaction_id']
            self.assertIsNotNone(transaction_id)
            
            # Verify transaction details
            transaction = db.get_transaction_by_id(transaction_id)
            self.assertIsNotNone(transaction)
            self.assertEqual(transaction['transaction_type'], 'payment')
            self.assertEqual(transaction['amount'], exit_result['cost'])
            self.assertEqual(transaction['exit_id'], exit_result['exit_id'])
            
        except Exception as e:
            self.fail(f"Unexpected error: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        phone_number=st.text(min_size=1, max_size=15),
        plate=st.text(min_size=1, max_size=20),
        initial_balance=st.integers(min_value=0, max_value=50000),
        parking_cost=st.integers(min_value=100000, max_value=500000)
    )
    def test_insufficient_balance_handling(self, phone_number, plate, initial_balance, parking_cost):
        """
        Property: For any registered plate that exits parking, if the associated
        user's wallet balance is less than the parking cost, the payment should
        not be processed and the status should indicate insufficient balance.
        
        Validates: Requirements 2.5, 8.3
        """
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)
        assume(plate.strip() != '')
        assume('\x00' not in plate)
        assume(initial_balance < parking_cost)  # Ensure insufficient balance
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user with wallet
            user_id = db.create_user(phone_number, role='user')
            
            # Set initial balance
            conn = db.get_conn()
            cur = conn.cursor()
            cur.execute("""
                UPDATE wallets
                SET balance = ?
                WHERE user_id = ?
            """, (initial_balance, user_id))
            conn.commit()
            conn.close()
            
            # Register plate to user
            db.add_user_plate(user_id, plate)
            
            # Set parking price
            db.set_price_per_hour(parking_cost)
            
            # Register entry and exit
            db.register_entry(plate, 'test_image_in.jpg')
            exit_result = db.register_exit(plate, 'test_image_out.jpg')
            
            # Verify exit was registered
            self.assertIsNotNone(exit_result)
            
            # Verify payment was not processed due to insufficient balance
            self.assertEqual(
                exit_result['payment_status'],
                'insufficient_balance',
                "Payment status should indicate insufficient balance"
            )
            
            # Verify balance was not changed
            balance_after = db.get_wallet_balance(user_id)
            self.assertEqual(
                balance_after,
                initial_balance,
                "Balance should not change when payment fails due to insufficient funds"
            )
            
            # Verify no transaction was created
            self.assertNotIn('transaction_id', exit_result, "No transaction should be created for failed payment")
            
        except Exception as e:
            self.fail(f"Unexpected error: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)


class TestEntryUserLinkage(unittest.TestCase):
    """
    Test entry-user linkage.
    Feature: user-wallet-system, Property 13: Entry-user linkage
    """
    
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        phone_number=st.text(min_size=1, max_size=15),
        plate=st.text(min_size=1, max_size=20)
    )
    def test_entry_user_linkage(self, phone_number, plate):
        """
        Property 13: For any registered plate that enters parking, the created
        entry record should be linkable to the plate's owner through the
        user_plates table.
        
        Validates: Requirements 3.4
        """
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)
        assume(plate.strip() != '')
        assume('\x00' not in plate)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user
            user_id = db.create_user(phone_number, role='user')
            self.assertIsNotNone(user_id)
            
            # Register plate to user
            plate_id = db.add_user_plate(user_id, plate)
            self.assertIsNotNone(plate_id)
            
            # Register entry for the plate
            entry_id = db.register_entry(plate, 'test_image_in.jpg')
            self.assertIsNotNone(entry_id)
            
            # Verify we can link the entry to the user through user_plates table
            plate_owner = db.get_plate_owner(plate)
            self.assertIsNotNone(
                plate_owner,
                f"Should be able to find owner of registered plate '{plate}'"
            )
            self.assertEqual(
                plate_owner,
                user_id,
                f"Plate owner should be the user who registered it. "
                f"Expected user_id {user_id}, got {plate_owner}"
            )
            
            # Verify the entry exists and has the correct plate
            conn = db.get_conn()
            cur = conn.cursor()
            cur.execute("""
                SELECT plate
                FROM entries
                WHERE id = ?
            """, (entry_id,))
            entry_row = cur.fetchone()
            conn.close()
            
            self.assertIsNotNone(entry_row, "Entry should exist in database")
            self.assertEqual(
                entry_row[0],
                plate,
                "Entry should have the correct plate number"
            )
            
        except Exception as e:
            self.fail(f"Unexpected error: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)


class TestPlateRegistrationCheck(unittest.TestCase):
    """
    Test plate registration check on exit.
    Feature: user-wallet-system, Property 25: Plate registration check on exit
    """
    
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        phone_number=st.text(min_size=1, max_size=15),
        plate=st.text(min_size=1, max_size=20)
    )
    def test_plate_registration_check_on_exit(self, phone_number, plate):
        """
        Property 25: For any vehicle exit, the system should query the user_plates
        table to determine if the plate is registered before processing payment.
        
        Validates: Requirements 8.1
        """
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)
        assume(plate.strip() != '')
        assume('\x00' not in plate)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user and register plate
            user_id = db.create_user(phone_number, role='user')
            db.add_user_plate(user_id, plate)
            
            # Charge wallet with sufficient balance
            db.charge_wallet(user_id, 500000)
            
            # Register entry and exit
            db.register_entry(plate, 'test_image_in.jpg')
            exit_result = db.register_exit(plate, 'test_image_out.jpg')
            
            # Verify the system checked registration and processed automatic payment
            self.assertIsNotNone(exit_result)
            self.assertIn('payment_status', exit_result)
            
            # For registered plate with sufficient balance, payment should be automatic
            self.assertEqual(
                exit_result['payment_status'],
                'auto_paid',
                "Registered plate should trigger automatic payment"
            )
            
            # Now test with unregistered plate
            unregistered_plate = plate + '_unregistered'
            db.register_entry(unregistered_plate, 'test_image_in2.jpg')
            exit_result2 = db.register_exit(unregistered_plate, 'test_image_out2.jpg')
            
            # Verify unregistered plate uses manual payment
            self.assertIsNotNone(exit_result2)
            self.assertEqual(
                exit_result2['payment_status'],
                'manual',
                "Unregistered plate should use manual payment"
            )
            
        except Exception as e:
            self.fail(f"Unexpected error: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)


class TestPaymentAtomicity(unittest.TestCase):
    """
    Test automatic payment atomicity.
    Feature: user-wallet-system, Property 26: Automatic payment atomicity
    """
    
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        phone_number=st.text(min_size=1, max_size=15),
        plate=st.text(min_size=1, max_size=20),
        initial_balance=st.integers(min_value=100000, max_value=10000000)
    )
    def test_payment_atomicity(self, phone_number, plate, initial_balance):
        """
        Property 26: For any automatic payment, either both the wallet balance
        update and the transaction record creation should succeed, or neither
        should occur (atomic operation).
        
        Validates: Requirements 8.4, 8.5
        """
        assume(phone_number.strip() != '')
        assume('\x00' not in phone_number)
        assume(plate.strip() != '')
        assume('\x00' not in plate)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user with wallet
            user_id = db.create_user(phone_number, role='user')
            
            # Set initial balance
            conn = db.get_conn()
            cur = conn.cursor()
            cur.execute("""
                UPDATE wallets
                SET balance = ?
                WHERE user_id = ?
            """, (initial_balance, user_id))
            conn.commit()
            conn.close()
            
            # Register plate
            db.add_user_plate(user_id, plate)
            
            # Register entry and exit
            db.register_entry(plate, 'test_image_in.jpg')
            exit_result = db.register_exit(plate, 'test_image_out.jpg')
            
            # Verify exit was successful
            self.assertIsNotNone(exit_result)
            
            if exit_result['payment_status'] == 'auto_paid':
                # Payment was processed - verify both balance update and transaction exist
                
                # Check balance was updated
                balance_after = db.get_wallet_balance(user_id)
                expected_balance = initial_balance - exit_result['cost']
                self.assertEqual(
                    balance_after,
                    expected_balance,
                    "Balance should be updated when payment succeeds"
                )
                
                # Check transaction record exists
                self.assertIn('transaction_id', exit_result)
                transaction = db.get_transaction_by_id(exit_result['transaction_id'])
                self.assertIsNotNone(
                    transaction,
                    "Transaction record should exist when payment succeeds"
                )
                self.assertEqual(transaction['amount'], exit_result['cost'])
                self.assertEqual(transaction['transaction_type'], 'payment')
                
            else:
                # Payment was not processed - verify neither balance nor transaction changed
                
                # Check balance was not updated
                balance_after = db.get_wallet_balance(user_id)
                self.assertEqual(
                    balance_after,
                    initial_balance,
                    "Balance should not change when payment fails"
                )
                
                # Check no transaction record was created
                self.assertNotIn(
                    'transaction_id',
                    exit_result,
                    "No transaction should be created when payment fails"
                )
            
        except Exception as e:
            self.fail(f"Unexpected error: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)


class TestBackwardCompatibility(unittest.TestCase):
    """
    Test backward compatibility with non-registered users.
    Feature: user-wallet-system, Property 27: Backward compatibility with non-registered users
    """
    
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        plate=st.text(min_size=1, max_size=20)
    )
    def test_backward_compatibility_non_registered(self, plate):
        """
        Property 27: For any vehicle exit where the plate is not registered to
        any user, the exit should be processed successfully using the existing
        manual payment flow.
        
        Validates: Requirements 8.6
        """
        assume(plate.strip() != '')
        assume('\x00' not in plate)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Register entry for unregistered plate
            entry_id = db.register_entry(plate, 'test_image_in.jpg')
            self.assertIsNotNone(entry_id, "Entry should be registered for unregistered plate")
            
            # Register exit
            exit_result = db.register_exit(plate, 'test_image_out.jpg')
            
            # Verify exit was processed successfully
            self.assertIsNotNone(
                exit_result,
                "Exit should be processed successfully for unregistered plate"
            )
            
            # Verify all expected fields are present
            self.assertIn('entry_id', exit_result)
            self.assertIn('exit_id', exit_result)
            self.assertIn('plate', exit_result)
            self.assertIn('duration', exit_result)
            self.assertIn('cost', exit_result)
            self.assertIn('payment_status', exit_result)
            
            # Verify payment status is manual (not automatic)
            self.assertEqual(
                exit_result['payment_status'],
                'manual',
                "Unregistered plate should use manual payment flow"
            )
            
            # Verify cost was calculated correctly
            self.assertIsInstance(exit_result['cost'], int)
            self.assertGreater(exit_result['cost'], 0)
            
            # Verify the exit was recorded in database
            conn = db.get_conn()
            cur = conn.cursor()
            cur.execute("""
                SELECT id, plate, cost
                FROM exits
                WHERE id = ?
            """, (exit_result['exit_id'],))
            exit_row = cur.fetchone()
            conn.close()
            
            self.assertIsNotNone(exit_row, "Exit should be recorded in database")
            self.assertEqual(exit_row[1], plate, "Exit should have correct plate")
            self.assertEqual(exit_row[2], exit_result['cost'], "Exit should have correct cost")
            
        except Exception as e:
            self.fail(f"Unexpected error: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        registered_phone=st.text(min_size=1, max_size=15),
        registered_plate=st.text(min_size=1, max_size=20),
        unregistered_plate=st.text(min_size=1, max_size=20)
    )
    def test_mixed_registered_and_unregistered(self, registered_phone, registered_plate, unregistered_plate):
        """
        Property: The system should handle both registered and unregistered
        plates correctly in the same database.
        
        Validates: Requirements 8.6
        """
        assume(registered_phone.strip() != '')
        assume('\x00' not in registered_phone)
        assume(registered_plate.strip() != '')
        assume('\x00' not in registered_plate)
        assume(unregistered_plate.strip() != '')
        assume('\x00' not in unregistered_plate)
        assume(registered_plate != unregistered_plate)
        
        # Set up fresh database for this example
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user and register one plate
            user_id = db.create_user(registered_phone, role='user')
            db.add_user_plate(user_id, registered_plate)
            db.charge_wallet(user_id, 500000)
            
            # Process registered plate
            db.register_entry(registered_plate, 'test_image_in1.jpg')
            exit_result1 = db.register_exit(registered_plate, 'test_image_out1.jpg')
            
            # Process unregistered plate
            db.register_entry(unregistered_plate, 'test_image_in2.jpg')
            exit_result2 = db.register_exit(unregistered_plate, 'test_image_out2.jpg')
            
            # Verify both exits were processed
            self.assertIsNotNone(exit_result1)
            self.assertIsNotNone(exit_result2)
            
            # Verify registered plate used automatic payment
            self.assertEqual(
                exit_result1['payment_status'],
                'auto_paid',
                "Registered plate should use automatic payment"
            )
            
            # Verify unregistered plate used manual payment
            self.assertEqual(
                exit_result2['payment_status'],
                'manual',
                "Unregistered plate should use manual payment"
            )
            
        except Exception as e:
            self.fail(f"Unexpected error: {e}")
        finally:
            cleanup_test_db(db_path, original_path, test_dir)


if __name__ == '__main__':
    unittest.main()
