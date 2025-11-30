"""
Script to create test users for the parking system
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parking_api.settings')
django.setup()

from src.database import (
    create_user, get_user_by_phone, get_user_by_id, 
    charge_wallet, update_user_role
)

def create_test_users():
    """Create test users with specified phone numbers and roles"""
    
    print("Creating test users...")
    
    # Create admin user
    admin_phone = "09124669509"
    try:
        # Check if user already exists
        existing_admin = get_user_by_phone(admin_phone)
        if existing_admin:
            print(f"ℹ Admin user already exists: {admin_phone}")
            admin_user = existing_admin
            # Update role to admin if not already
            if admin_user['role'] != 'admin':
                update_user_role(admin_user['id'], 'admin')
                admin_user = get_user_by_id(admin_user['id'])
                print(f"  - Role updated to: admin")
        else:
            # Create new admin user
            user_id = create_user(admin_phone, role='admin')
            admin_user = get_user_by_id(user_id)
            print(f"✓ Admin user created: {admin_phone}")
        
        print(f"  - User ID: {admin_user['id']}")
        print(f"  - Role: {admin_user['role']}")
        
        # Charge admin wallet with 1,000,000 Rials
        charge_result = charge_wallet(admin_user['id'], 1000000)
        if charge_result:
            print(f"  - Wallet charged with 1,000,000 Rials")
            print(f"  - New balance: {charge_result.get('new_balance', 0)} Rials")
    except Exception as e:
        print(f"✗ Failed to create admin user: {admin_phone}")
        print(f"  Error: {str(e)}")
    
    print()
    
    # Create regular user
    user_phone = "09144669509"
    try:
        # Check if user already exists
        existing_user = get_user_by_phone(user_phone)
        if existing_user:
            print(f"ℹ Regular user already exists: {user_phone}")
            regular_user = existing_user
        else:
            # Create new regular user
            user_id = create_user(user_phone, role='user')
            regular_user = get_user_by_id(user_id)
            print(f"✓ Regular user created: {user_phone}")
        
        print(f"  - User ID: {regular_user['id']}")
        print(f"  - Role: {regular_user['role']}")
        
        # Charge regular user wallet with 500,000 Rials
        charge_result = charge_wallet(regular_user['id'], 500000)
        if charge_result:
            print(f"  - Wallet charged with 500,000 Rials")
            print(f"  - New balance: {charge_result.get('new_balance', 0)} Rials")
    except Exception as e:
        print(f"✗ Failed to create regular user: {user_phone}")
        print(f"  Error: {str(e)}")
    
    print()
    print("Test users created successfully!")
    print()
    print("You can now login with:")
    print(f"  Admin: {admin_phone}")
    print(f"  User:  {user_phone}")

if __name__ == '__main__':
    create_test_users()
