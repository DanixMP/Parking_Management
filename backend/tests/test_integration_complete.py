"""
Comprehensive integration tests for the user wallet system.
Tests complete user journeys and backward compatibility.
"""

import pytest
import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import database as db


@pytest.fixture(scope='function')
def clean_db():
    """Clean database before each test"""
    # Initialize database
    db.init_db()
    
    # Clean up test data
    conn = db.get_conn()
    cur = conn.cursor()
    
    # Delete test data
    cur.execute("DELETE FROM auth_tokens")
    cur.execute("DELETE FROM transactions")
    cur.execute("DELETE FROM user_plates")
    cur.execute("DELETE FROM wallets")
    cur.execute("DELETE FROM users")
    cur.execute("DELETE FROM exits")
    cur.execute("DELETE FROM active_cars")
    cur.execute("DELETE FROM entries")
    
    conn.commit()
    conn.close()
    
    yield
    
    # Cleanup after test
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM auth_tokens")
    cur.execute("DELETE FROM transactions")
    cur.execute("DELETE FROM user_plates")
    cur.execute("DELETE FROM wallets")
    cur.execute("DELETE FROM users")
    cur.execute("DELETE FROM exits")
    cur.execute("DELETE FROM active_cars")
    cur.execute("DELETE FROM entries")
    conn.commit()
    conn.close()


class TestCompleteUserJourney:
    """Test complete user journey from registration to automatic payment"""
    
    def test_new_user_registration_and_first_wallet_charge(self, clean_db):
        """Test: New user registration and first wallet charge"""
        # Step 1: User logs in with phone number (creates account)
        phone = "09123456789"
        user = db.get_or_create_user(phone)
        
        assert user is not None
        assert user['phone_number'] == phone
        assert user['role'] == 'user'
        assert user['is_active'] == 1
        
        # Step 2: Verify wallet was created automatically
        wallet = db.get_wallet_by_user_id(user['id'])
        assert wallet is not None
        assert wallet['balance'] == 0
        
        # Step 3: User charges wallet for the first time
        charge_amount = 500000
        result = db.charge_wallet(user['id'], charge_amount)
        
        assert result['new_balance'] == charge_amount
        assert result['transaction_id'] is not None
        
        # Step 4: Verify transaction was recorded
        transaction = db.get_transaction_by_id(result['transaction_id'])
        assert transaction is not None
        assert transaction['transaction_type'] == 'charge'
        assert transaction['amount'] == charge_amount
        
        # Step 5: Verify wallet balance updated
        updated_wallet = db.get_wallet_by_user_id(user['id'])
        assert updated_wallet['balance'] == charge_amount
    
    def test_plate_registration_and_automatic_payment_on_first_parking(self, clean_db):
        """Test: Plate registration and automatic payment on first parking"""
        # Setup: Create user with wallet balance
        phone = "09123456789"
        user = db.get_or_create_user(phone)
        db.charge_wallet(user['id'], 500000)
        
        # Step 1: User registers their plate
        plate = "12ب345-67"
        plate_id = db.register_user_plate(user['id'], plate)
        
        assert plate_id is not None
        
        # Step 2: Verify plate is registered
        user_plates = db.get_user_plates(user['id'])
        assert len(user_plates) == 1
        assert user_plates[0]['plate'] == plate
        
        # Step 3: Vehicle enters parking
        entry_id = db.register_entry(plate, "test_image_in.jpg")
        assert entry_id is not None
        
        # Step 4: Vehicle exits parking (automatic payment should occur)
        exit_result = db.register_exit(plate, "test_image_out.jpg")
        
        assert exit_result is not None
        assert exit_result['payment_status'] == 'auto_paid'
        assert exit_result['transaction_id'] is not None
        assert exit_result['cost'] > 0
        
        # Step 5: Verify wallet was debited
        wallet = db.get_wallet_by_user_id(user['id'])
        expected_balance = 500000 - exit_result['cost']
        assert wallet['balance'] == expected_balance
        
        # Step 6: Verify transaction was recorded
        transaction = db.get_transaction_by_id(exit_result['transaction_id'])
        assert transaction is not None
        assert transaction['transaction_type'] == 'payment'
        assert transaction['amount'] == exit_result['cost']
        assert transaction['exit_id'] == exit_result['exit_id']
    
    def test_multiple_parking_sessions_with_balance_depletion(self, clean_db):
        """Test: Multiple parking sessions with balance depletion"""
        # Setup: Create user with limited balance
        phone = "09123456789"
        user = db.get_or_create_user(phone)
        initial_balance = 100000  # Enough for ~2-3 parking sessions
        db.charge_wallet(user['id'], initial_balance)
        
        plate = "12ب345-67"
        db.register_user_plate(user['id'], plate)
        
        # Session 1: Successful payment
        db.register_entry(plate, "img1_in.jpg")
        exit1 = db.register_exit(plate, "img1_out.jpg")
        
        assert exit1['payment_status'] == 'auto_paid'
        
        wallet_after_1 = db.get_wallet_by_user_id(user['id'])
        balance_after_1 = wallet_after_1['balance']
        assert balance_after_1 == initial_balance - exit1['cost']
        
        # Session 2: Successful payment
        db.register_entry(plate, "img2_in.jpg")
        exit2 = db.register_exit(plate, "img2_out.jpg")
        
        assert exit2['payment_status'] == 'auto_paid'
        
        wallet_after_2 = db.get_wallet_by_user_id(user['id'])
        balance_after_2 = wallet_after_2['balance']
        assert balance_after_2 == balance_after_1 - exit2['cost']
        
        # Session 3: May fail if insufficient balance
        db.register_entry(plate, "img3_in.jpg")
        exit3 = db.register_exit(plate, "img3_out.jpg")
        
        wallet_after_3 = db.get_wallet_by_user_id(user['id'])
        
        if balance_after_2 >= exit3['cost']:
            # Should succeed
            assert exit3['payment_status'] == 'auto_paid'
            assert wallet_after_3['balance'] == balance_after_2 - exit3['cost']
        else:
            # Should fail with insufficient balance
            assert exit3['payment_status'] == 'insufficient_balance'
            assert wallet_after_3['balance'] == balance_after_2  # Balance unchanged
    
    def test_insufficient_balance_scenario(self, clean_db):
        """Test: Insufficient balance scenario"""
        # Setup: Create user with very low balance
        phone = "09123456789"
        user = db.get_or_create_user(phone)
        low_balance = 1000  # Much less than typical parking cost
        db.charge_wallet(user['id'], low_balance)
        
        plate = "12ب345-67"
        db.register_user_plate(user['id'], plate)
        
        # Enter and exit parking
        db.register_entry(plate, "img_in.jpg")
        exit_result = db.register_exit(plate, "img_out.jpg")
        
        # Should fail with insufficient balance
        assert exit_result['payment_status'] == 'insufficient_balance'
        assert 'payment_error' in exit_result
        
        # Verify balance unchanged
        wallet = db.get_wallet_by_user_id(user['id'])
        assert wallet['balance'] == low_balance
        
        # Verify no payment transaction was created
        transactions = db.get_wallet_transactions(user['id'])
        payment_transactions = [t for t in transactions['results'] if t['transaction_type'] == 'payment']
        assert len(payment_transactions) == 0


class TestBackwardCompatibility:
    """Test backward compatibility with non-registered users"""
    
    def test_non_registered_plate_uses_manual_payment(self, clean_db):
        """Test: Non-registered plate uses manual payment flow"""
        # Use a plate that is NOT registered to any user
        plate = "99ز999-99"
        
        # Enter parking
        entry_id = db.register_entry(plate, "img_in.jpg")
        assert entry_id is not None
        
        # Exit parking
        exit_result = db.register_exit(plate, "img_out.jpg")
        
        # Should succeed with manual payment status
        assert exit_result is not None
        assert exit_result['payment_status'] == 'manual'
        assert 'transaction_id' not in exit_result or exit_result.get('transaction_id') is None
        assert exit_result['cost'] > 0
        
        # Verify exit was recorded properly
        assert exit_result['entry_id'] == entry_id
        assert exit_result['plate'] == plate
    
    def test_existing_parking_system_still_works(self, clean_db):
        """Test: Existing parking system functionality still works"""
        # Test basic parking operations without any user system
        
        # Test 1: Entry registration
        plate1 = "11الف111-11"
        entry1 = db.register_entry(plate1, "img1.jpg")
        assert entry1 is not None
        
        # Test 2: Check active cars
        active_count = db.count_active_cars()
        assert active_count == 1
        
        # Test 3: Exit registration
        exit1 = db.register_exit(plate1, "img1_out.jpg")
        assert exit1 is not None
        assert exit1['cost'] > 0
        
        # Test 4: Verify car removed from active
        active_count_after = db.count_active_cars()
        assert active_count_after == 0
        
        # Test 5: Multiple cars
        plate2 = "22ب222-22"
        plate3 = "33پ333-33"
        
        db.register_entry(plate2, "img2.jpg")
        db.register_entry(plate3, "img3.jpg")
        
        assert db.count_active_cars() == 2
        
        # Test 6: Capacity and free slots
        capacity = db.get_capacity()
        free_slots = db.get_free_slots()
        assert free_slots == capacity - 2
    
    def test_mixed_registered_and_non_registered_users(self, clean_db):
        """Test: System handles mix of registered and non-registered users"""
        # Create a registered user
        phone = "09123456789"
        user = db.get_or_create_user(phone)
        db.charge_wallet(user['id'], 500000)
        
        registered_plate = "12ب345-67"
        db.register_user_plate(user['id'], registered_plate)
        
        # Non-registered plate
        non_registered_plate = "99ز999-99"
        
        # Both enter parking
        entry1 = db.register_entry(registered_plate, "img1_in.jpg")
        entry2 = db.register_entry(non_registered_plate, "img2_in.jpg")
        
        assert db.count_active_cars() == 2
        
        # Registered user exits (automatic payment)
        exit1 = db.register_exit(registered_plate, "img1_out.jpg")
        assert exit1['payment_status'] == 'auto_paid'
        
        # Non-registered user exits (manual payment)
        exit2 = db.register_exit(non_registered_plate, "img2_out.jpg")
        assert exit2['payment_status'] == 'manual'
        
        # Verify both exits recorded properly
        assert exit1['entry_id'] == entry1
        assert exit2['entry_id'] == entry2
        
        # Verify wallet was only debited for registered user
        wallet = db.get_wallet_by_user_id(user['id'])
        assert wallet['balance'] == 500000 - exit1['cost']


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_duplicate_plate_registration(self, clean_db):
        """Test: Cannot register same plate twice for same user"""
        phone = "09123456789"
        user = db.get_or_create_user(phone)
        
        plate = "12ب345-67"
        
        # First registration should succeed
        plate_id1 = db.register_user_plate(user['id'], plate)
        assert plate_id1 is not None
        
        # Second registration should fail
        with pytest.raises(ValueError, match="already registered"):
            db.register_user_plate(user['id'], plate)
    
    def test_invalid_plate_format_rejected(self, clean_db):
        """Test: Invalid plate formats are rejected"""
        phone = "09123456789"
        user = db.get_or_create_user(phone)
        
        invalid_plates = [
            "invalid",
            "12345",
            "abc-def",
            "",
            "123456789012345"  # Too long
        ]
        
        for invalid_plate in invalid_plates:
            with pytest.raises(ValueError, match="Invalid license plate format"):
                db.register_user_plate(user['id'], invalid_plate)
    
    def test_exactly_sufficient_balance(self, clean_db):
        """Test: Payment succeeds when balance exactly equals cost"""
        phone = "09123456789"
        user = db.get_or_create_user(phone)
        
        plate = "12ب345-67"
        db.register_user_plate(user['id'], plate)
        
        # Enter parking
        db.register_entry(plate, "img_in.jpg")
        
        # Calculate expected cost (minimum 1 hour)
        price_per_hour = db.get_price_per_hour()
        expected_cost = price_per_hour  # Minimum charge
        
        # Charge wallet with exactly the expected cost
        db.charge_wallet(user['id'], expected_cost)
        
        # Exit immediately (should be charged for 1 hour minimum)
        exit_result = db.register_exit(plate, "img_out.jpg")
        
        # Payment should succeed
        assert exit_result['payment_status'] == 'auto_paid'
        
        # Balance should be exactly 0
        wallet = db.get_wallet_by_user_id(user['id'])
        assert wallet['balance'] == 0
    
    def test_multiple_plates_per_user(self, clean_db):
        """Test: User can register multiple plates"""
        phone = "09123456789"
        user = db.get_or_create_user(phone)
        db.charge_wallet(user['id'], 1000000)
        
        plates = ["12ب345-67", "13الف111-10", "14پ222-20"]
        
        # Register all plates
        for plate in plates:
            plate_id = db.register_user_plate(user['id'], plate)
            assert plate_id is not None
        
        # Verify all plates are registered
        user_plates = db.get_user_plates(user['id'])
        assert len(user_plates) == 3
        
        registered_plate_numbers = [p['plate'] for p in user_plates]
        for plate in plates:
            assert plate in registered_plate_numbers
        
        # Test automatic payment works for all plates
        for i, plate in enumerate(plates):
            db.register_entry(plate, f"img{i}_in.jpg")
            exit_result = db.register_exit(plate, f"img{i}_out.jpg")
            assert exit_result['payment_status'] == 'auto_paid'
    
    def test_deleted_plate_not_used_for_automatic_payment(self, clean_db):
        """Test: Deleted plate is not used for automatic payment"""
        phone = "09123456789"
        user = db.get_or_create_user(phone)
        db.charge_wallet(user['id'], 500000)
        
        plate = "12ب345-67"
        plate_id = db.register_user_plate(user['id'], plate)
        
        # Delete the plate
        db.delete_user_plate(plate_id, user_id=user['id'])
        
        # Try to use the plate
        db.register_entry(plate, "img_in.jpg")
        exit_result = db.register_exit(plate, "img_out.jpg")
        
        # Should use manual payment (plate no longer registered)
        assert exit_result['payment_status'] == 'manual'
        
        # Wallet should not be debited
        wallet = db.get_wallet_by_user_id(user['id'])
        assert wallet['balance'] == 500000


class TestTransactionHistory:
    """Test transaction history functionality"""
    
    def test_transaction_chronological_ordering(self, clean_db):
        """Test: Transactions are returned in chronological order"""
        phone = "09123456789"
        user = db.get_or_create_user(phone)
        
        # Create multiple transactions
        amounts = [100000, 200000, 50000, 150000]
        for amount in amounts:
            db.charge_wallet(user['id'], amount)
        
        # Get transactions
        transactions = db.get_wallet_transactions(user['id'])
        
        assert transactions['count'] == 4
        assert len(transactions['results']) == 4
        
        # Verify chronological order (most recent first)
        timestamps = [t['timestamp'] for t in transactions['results']]
        for i in range(len(timestamps) - 1):
            # Later timestamp should come first
            assert timestamps[i] >= timestamps[i + 1]
    
    def test_transaction_pagination(self, clean_db):
        """Test: Transaction pagination works correctly"""
        phone = "09123456789"
        user = db.get_or_create_user(phone)
        
        # Create 10 transactions
        for i in range(10):
            db.charge_wallet(user['id'], 10000 * (i + 1))
        
        # Test pagination
        page1 = db.get_wallet_transactions(user['id'], limit=5, offset=0)
        assert page1['count'] == 10
        assert len(page1['results']) == 5
        
        page2 = db.get_wallet_transactions(user['id'], limit=5, offset=5)
        assert page2['count'] == 10
        assert len(page2['results']) == 5
        
        # Verify no overlap
        page1_ids = [t['id'] for t in page1['results']]
        page2_ids = [t['id'] for t in page2['results']]
        assert len(set(page1_ids) & set(page2_ids)) == 0


class TestAuthenticationFlow:
    """Test authentication and token management"""
    
    def test_login_creates_token(self, clean_db):
        """Test: Login creates valid authentication token"""
        phone = "09123456789"
        user = db.get_or_create_user(phone)
        
        # Create token
        token = db.create_auth_token(user['id'])
        
        assert token is not None
        assert len(token) > 20  # Should be a long random string
        
        # Validate token
        validated_user_id = db.validate_token(token)
        assert validated_user_id == user['id']
    
    def test_logout_deletes_token(self, clean_db):
        """Test: Logout deletes authentication token"""
        phone = "09123456789"
        user = db.get_or_create_user(phone)
        
        # Create token
        token = db.create_auth_token(user['id'])
        
        # Verify token is valid
        assert db.validate_token(token) == user['id']
        
        # Delete token (logout)
        db.delete_token(token)
        
        # Verify token is no longer valid
        assert db.validate_token(token) is None
    
    def test_idempotent_login(self, clean_db):
        """Test: Multiple logins with same phone return same user"""
        phone = "09123456789"
        
        # First login
        user1 = db.get_or_create_user(phone)
        
        # Second login
        user2 = db.get_or_create_user(phone)
        
        # Should be the same user
        assert user1['id'] == user2['id']
        assert user1['phone_number'] == user2['phone_number']
        assert user1['role'] == user2['role']


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
