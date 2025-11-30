"""
Unit tests for authentication system.
"""

import sys
import os
import unittest
import tempfile
import shutil
from pathlib import Path
import uuid

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


class TestAuthentication(unittest.TestCase):
    """Test authentication functionality."""
    
    def test_phone_number_validation(self):
        """Test phone number format validation."""
        # Valid Iranian phone numbers
        self.assertTrue(db.validate_phone_number('09123456789'))
        self.assertTrue(db.validate_phone_number('09987654321'))
        
        # Invalid phone numbers
        self.assertFalse(db.validate_phone_number('9123456789'))  # Missing 0
        self.assertFalse(db.validate_phone_number('0912345678'))  # Too short
        self.assertFalse(db.validate_phone_number('091234567890'))  # Too long
        self.assertFalse(db.validate_phone_number('08123456789'))  # Wrong prefix
        self.assertFalse(db.validate_phone_number(''))  # Empty
        self.assertFalse(db.validate_phone_number('abcdefghijk'))  # Non-numeric
    
    def test_token_generation(self):
        """Test token generation."""
        token1 = db.generate_token()
        token2 = db.generate_token()
        
        # Tokens should be strings
        self.assertIsInstance(token1, str)
        self.assertIsInstance(token2, str)
        
        # Tokens should be non-empty
        self.assertGreater(len(token1), 0)
        self.assertGreater(len(token2), 0)
        
        # Tokens should be unique
        self.assertNotEqual(token1, token2)
    
    def test_create_and_validate_token(self):
        """Test creating and validating authentication tokens."""
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user
            user_id = db.create_user('09123456789', role='user')
            
            # Create token
            token = db.create_auth_token(user_id)
            self.assertIsNotNone(token)
            self.assertIsInstance(token, str)
            
            # Validate token
            validated_user_id = db.validate_token(token)
            self.assertEqual(validated_user_id, user_id)
            
            # Invalid token should return None
            invalid_user_id = db.validate_token('invalid_token_12345')
            self.assertIsNone(invalid_user_id)
            
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    def test_delete_token(self):
        """Test deleting authentication tokens."""
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user and token
            user_id = db.create_user('09123456789', role='user')
            token = db.create_auth_token(user_id)
            
            # Token should be valid
            self.assertEqual(db.validate_token(token), user_id)
            
            # Delete token
            db.delete_token(token)
            
            # Token should no longer be valid
            self.assertIsNone(db.validate_token(token))
            
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    def test_get_or_create_user_existing(self):
        """Test get_or_create_user with existing user."""
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            phone = '09123456789'
            
            # Create user
            user_id = db.create_user(phone, role='user')
            
            # Get or create should return existing user
            user = db.get_or_create_user(phone)
            self.assertIsNotNone(user)
            self.assertEqual(user['id'], user_id)
            self.assertEqual(user['phone_number'], phone)
            
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    def test_get_or_create_user_new(self):
        """Test get_or_create_user with new user."""
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            phone = '09123456789'
            
            # Get or create should create new user
            user = db.get_or_create_user(phone)
            self.assertIsNotNone(user)
            self.assertEqual(user['phone_number'], phone)
            self.assertEqual(user['role'], 'user')  # Default role
            
            # Verify user exists in database
            user_check = db.get_user_by_phone(phone)
            self.assertIsNotNone(user_check)
            self.assertEqual(user_check['id'], user['id'])
            
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    def test_get_or_create_user_invalid_phone(self):
        """Test get_or_create_user with invalid phone number."""
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Invalid phone should raise ValueError
            with self.assertRaises(ValueError):
                db.get_or_create_user('invalid_phone')
            
            with self.assertRaises(ValueError):
                db.get_or_create_user('1234567890')
            
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    def test_multiple_tokens_per_user(self):
        """Test that a user can have multiple valid tokens."""
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user
            user_id = db.create_user('09123456789', role='user')
            
            # Create multiple tokens
            token1 = db.create_auth_token(user_id)
            token2 = db.create_auth_token(user_id)
            
            # Both tokens should be valid
            self.assertEqual(db.validate_token(token1), user_id)
            self.assertEqual(db.validate_token(token2), user_id)
            
            # Tokens should be different
            self.assertNotEqual(token1, token2)
            
        finally:
            cleanup_test_db(db_path, original_path, test_dir)
    
    def test_delete_user_tokens(self):
        """Test deleting all tokens for a user."""
        db_path, original_path, test_dir = setup_test_db()
        
        try:
            # Create user and multiple tokens
            user_id = db.create_user('09123456789', role='user')
            token1 = db.create_auth_token(user_id)
            token2 = db.create_auth_token(user_id)
            
            # Both tokens should be valid
            self.assertEqual(db.validate_token(token1), user_id)
            self.assertEqual(db.validate_token(token2), user_id)
            
            # Delete all user tokens
            db.delete_user_tokens(user_id)
            
            # Both tokens should no longer be valid
            self.assertIsNone(db.validate_token(token1))
            self.assertIsNone(db.validate_token(token2))
            
        finally:
            cleanup_test_db(db_path, original_path, test_dir)


if __name__ == '__main__':
    unittest.main()
