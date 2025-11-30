"""
End-to-end scenario tests simulating real-world usage.
Tests complete workflows from user perspective.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import database as db


@pytest.fixture(scope='function')
def clean_db():
    """Clean database before each test"""
    db.init_db()
    
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


class TestRealWorldScenarios:
    """Test real-world usage scenarios"""
    
    def test_scenario_daily_commuter(self, clean_db):
        """
        Scenario: Daily commuter using the parking system
        - User registers and charges wallet once
        - Uses parking multiple times per week
        - Automatic payments work seamlessly
        """
        # Day 1: User registers
        phone = "09121234567"
        user = db.get_or_create_user(phone)
        
        # User charges wallet with enough for a week
        weekly_budget = 500000  # ~25 parking sessions
        db.charge_wallet(user['id'], weekly_budget)
        
        # User registers their car
        plate = "12ب345-67"
        db.register_user_plate(user['id'], plate)
        
        # Simulate 5 days of parking (morning and evening)
        total_cost = 0
        for day in range(5):
            # Morning: Park for ~8 hours
            db.register_entry(plate, f"day{day}_morning_in.jpg")
            exit_result = db.register_exit(plate, f"day{day}_morning_out.jpg")
            
            assert exit_result['payment_status'] == 'auto_paid'
            total_cost += exit_result['cost']
            
            # Evening: Park for ~2 hours
            db.register_entry(plate, f"day{day}_evening_in.jpg")
            exit_result = db.register_exit(plate, f"day{day}_evening_out.jpg")
            
            assert exit_result['payment_status'] == 'auto_paid'
            total_cost += exit_result['cost']
        
        # Verify final balance
        wallet = db.get_wallet_by_user_id(user['id'])
        assert wallet['balance'] == weekly_budget - total_cost
        
        # Verify transaction history
        transactions = db.get_wallet_transactions(user['id'])
        # 1 charge + 10 payments (5 days × 2 sessions)
        assert transactions['count'] == 11
        
        payment_count = sum(1 for t in transactions['results'] if t['transaction_type'] == 'payment')
        assert payment_count == 10
    
    def test_scenario_family_with_multiple_cars(self, clean_db):
        """
        Scenario: Family with multiple cars sharing one account
        - User registers multiple plates
        - All cars use automatic payment
        - Transaction history shows all vehicles
        """
        # Family creates account
        phone = "09129876543"
        user = db.get_or_create_user(phone)
        db.charge_wallet(user['id'], 1000000)
        
        # Register family vehicles
        car1 = "12ب345-67"  # Dad's car
        car2 = "13الف111-10"  # Mom's car
        car3 = "14پ222-20"  # Son's car
        
        db.register_user_plate(user['id'], car1)
        db.register_user_plate(user['id'], car2)
        db.register_user_plate(user['id'], car3)
        
        # Verify all plates registered
        plates = db.get_user_plates(user['id'])
        assert len(plates) == 3
        
        # Simulate different family members using parking
        # Dad parks
        db.register_entry(car1, "car1_in.jpg")
        exit1 = db.register_exit(car1, "car1_out.jpg")
        assert exit1['payment_status'] == 'auto_paid'
        
        # Mom parks
        db.register_entry(car2, "car2_in.jpg")
        exit2 = db.register_exit(car2, "car2_out.jpg")
        assert exit2['payment_status'] == 'auto_paid'
        
        # Son parks
        db.register_entry(car3, "car3_in.jpg")
        exit3 = db.register_exit(car3, "car3_out.jpg")
        assert exit3['payment_status'] == 'auto_paid'
        
        # Verify all payments deducted from same wallet
        wallet = db.get_wallet_by_user_id(user['id'])
        total_cost = exit1['cost'] + exit2['cost'] + exit3['cost']
        assert wallet['balance'] == 1000000 - total_cost
        
        # Verify transaction history shows all vehicles
        transactions = db.get_wallet_transactions(user['id'])
        assert transactions['count'] == 4  # 1 charge + 3 payments
    
    def test_scenario_low_balance_warning(self, clean_db):
        """
        Scenario: User runs low on balance
        - User starts with low balance
        - First parking succeeds
        - Second parking fails due to insufficient balance
        - User recharges and continues
        """
        phone = "09123334444"
        user = db.get_or_create_user(phone)
        
        # Charge with barely enough for one session
        price_per_hour = db.get_price_per_hour()
        low_balance = price_per_hour + 5000  # Just enough for 1 hour + small buffer
        db.charge_wallet(user['id'], low_balance)
        
        plate = "15ت555-55"
        db.register_user_plate(user['id'], plate)
        
        # First parking: Should succeed
        db.register_entry(plate, "first_in.jpg")
        exit1 = db.register_exit(plate, "first_out.jpg")
        assert exit1['payment_status'] == 'auto_paid'
        
        # Check remaining balance
        wallet = db.get_wallet_by_user_id(user['id'])
        remaining = wallet['balance']
        assert remaining < price_per_hour  # Not enough for another session
        
        # Second parking: Should fail
        db.register_entry(plate, "second_in.jpg")
        exit2 = db.register_exit(plate, "second_out.jpg")
        assert exit2['payment_status'] == 'insufficient_balance'
        
        # Balance should be unchanged
        wallet = db.get_wallet_by_user_id(user['id'])
        assert wallet['balance'] == remaining
        
        # User recharges
        db.charge_wallet(user['id'], 200000)
        
        # Third parking: Should succeed again
        db.register_entry(plate, "third_in.jpg")
        exit3 = db.register_exit(plate, "third_out.jpg")
        assert exit3['payment_status'] == 'auto_paid'
    
    def test_scenario_mixed_parking_lot(self, clean_db):
        """
        Scenario: Parking lot with both registered and non-registered users
        - Some users have accounts, some don't
        - System handles both types seamlessly
        - No interference between user types
        """
        # Create registered user
        phone = "09125555555"
        user = db.get_or_create_user(phone)
        db.charge_wallet(user['id'], 500000)
        
        registered_plate = "16ج666-66"
        db.register_user_plate(user['id'], registered_plate)
        
        # Non-registered plates
        guest_plate1 = "77ح777-77"
        guest_plate2 = "88خ888-88"
        
        # All enter parking
        db.register_entry(registered_plate, "reg_in.jpg")
        db.register_entry(guest_plate1, "guest1_in.jpg")
        db.register_entry(guest_plate2, "guest2_in.jpg")
        
        # Verify all are active
        assert db.count_active_cars() == 3
        
        # Guest 1 exits (manual payment)
        exit_guest1 = db.register_exit(guest_plate1, "guest1_out.jpg")
        assert exit_guest1['payment_status'] == 'manual'
        assert db.count_active_cars() == 2
        
        # Registered user exits (automatic payment)
        exit_reg = db.register_exit(registered_plate, "reg_out.jpg")
        assert exit_reg['payment_status'] == 'auto_paid'
        assert db.count_active_cars() == 1
        
        # Guest 2 exits (manual payment)
        exit_guest2 = db.register_exit(guest_plate2, "guest2_out.jpg")
        assert exit_guest2['payment_status'] == 'manual'
        assert db.count_active_cars() == 0
        
        # Verify registered user's wallet was debited
        wallet = db.get_wallet_by_user_id(user['id'])
        assert wallet['balance'] == 500000 - exit_reg['cost']
        
        # Verify only registered user has transactions
        transactions = db.get_wallet_transactions(user['id'])
        assert transactions['count'] == 2  # 1 charge + 1 payment
    
    def test_scenario_user_removes_plate(self, clean_db):
        """
        Scenario: User sells car and removes plate from account
        - User has plate registered
        - User removes plate
        - Plate no longer triggers automatic payment
        """
        phone = "09126666666"
        user = db.get_or_create_user(phone)
        db.charge_wallet(user['id'], 500000)
        
        plate = "17د777-77"
        plate_id = db.register_user_plate(user['id'], plate)
        
        # Use parking with registered plate
        db.register_entry(plate, "before_removal_in.jpg")
        exit_before = db.register_exit(plate, "before_removal_out.jpg")
        assert exit_before['payment_status'] == 'auto_paid'
        
        balance_before_removal = db.get_wallet_by_user_id(user['id'])['balance']
        
        # User sells car and removes plate
        db.delete_user_plate(plate_id, user_id=user['id'])
        
        # Verify plate is removed
        plates = db.get_user_plates(user['id'])
        assert len(plates) == 0
        
        # New owner (or same person without registration) uses parking
        db.register_entry(plate, "after_removal_in.jpg")
        exit_after = db.register_exit(plate, "after_removal_out.jpg")
        
        # Should use manual payment now
        assert exit_after['payment_status'] == 'manual'
        
        # Wallet should not be debited
        balance_after_removal = db.get_wallet_by_user_id(user['id'])['balance']
        assert balance_after_removal == balance_before_removal
    
    def test_scenario_admin_manages_users(self, clean_db):
        """
        Scenario: Admin managing user accounts
        - Admin views all users
        - SuperUser changes user roles
        - Role changes affect permissions
        """
        # Create regular users
        user1 = db.get_or_create_user("09121111111")
        user2 = db.get_or_create_user("09122222222")
        user3 = db.get_or_create_user("09123333333")
        
        # Create admin
        admin_phone = "09129999999"
        admin_user = db.get_or_create_user(admin_phone)
        db.update_user_role(admin_user['id'], 'admin')
        
        # Create superuser
        super_phone = "09120000000"
        super_user = db.get_or_create_user(super_phone)
        db.update_user_role(super_user['id'], 'superuser')
        
        # Admin views all users
        all_users = db.get_all_users()
        assert all_users['count'] == 5  # 3 regular + 1 admin + 1 superuser
        
        # SuperUser promotes user1 to admin
        db.update_user_role(user1['id'], 'admin')
        
        # Verify role change
        updated_user1 = db.get_user_by_id(user1['id'])
        assert updated_user1['role'] == 'admin'
        
        # Regular users remain unchanged
        check_user2 = db.get_user_by_id(user2['id'])
        assert check_user2['role'] == 'user'
    
    def test_scenario_transaction_history_review(self, clean_db):
        """
        Scenario: User reviews their transaction history
        - User performs multiple operations over time
        - User views paginated transaction history
        - Transactions are in correct order
        """
        phone = "09127777777"
        user = db.get_or_create_user(phone)
        
        plate = "18ذ888-88"
        db.register_user_plate(user['id'], plate)
        
        # Simulate a month of activity
        # Week 1: Charge wallet
        db.charge_wallet(user['id'], 300000)
        
        # Week 1: Use parking 3 times
        for i in range(3):
            db.register_entry(plate, f"week1_{i}_in.jpg")
            db.register_exit(plate, f"week1_{i}_out.jpg")
        
        # Week 2: Charge wallet again
        db.charge_wallet(user['id'], 200000)
        
        # Week 2: Use parking 4 times
        for i in range(4):
            db.register_entry(plate, f"week2_{i}_in.jpg")
            db.register_exit(plate, f"week2_{i}_out.jpg")
        
        # Week 3: Use parking 2 times
        for i in range(2):
            db.register_entry(plate, f"week3_{i}_in.jpg")
            db.register_exit(plate, f"week3_{i}_out.jpg")
        
        # Week 4: Charge wallet
        db.charge_wallet(user['id'], 150000)
        
        # Get full transaction history
        all_transactions = db.get_wallet_transactions(user['id'], limit=100)
        
        # Should have: 3 charges + 9 payments = 12 transactions
        assert all_transactions['count'] == 12
        
        # Verify chronological order (most recent first)
        timestamps = [t['timestamp'] for t in all_transactions['results']]
        for i in range(len(timestamps) - 1):
            assert timestamps[i] >= timestamps[i + 1]
        
        # Test pagination
        page1 = db.get_wallet_transactions(user['id'], limit=5, offset=0)
        page2 = db.get_wallet_transactions(user['id'], limit=5, offset=5)
        page3 = db.get_wallet_transactions(user['id'], limit=5, offset=10)
        
        assert len(page1['results']) == 5
        assert len(page2['results']) == 5
        assert len(page3['results']) == 2  # Only 2 remaining
        
        # Verify no duplicates across pages
        all_ids = (
            [t['id'] for t in page1['results']] +
            [t['id'] for t in page2['results']] +
            [t['id'] for t in page3['results']]
        )
        assert len(all_ids) == len(set(all_ids))  # All unique


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
