"""
Script to verify test users in the database
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parking_api.settings')
django.setup()

from src.database import get_user_by_phone, get_wallet_by_user_id, get_user_plates

def verify_users():
    """Verify test users exist and display their information"""
    
    print("=" * 60)
    print("TEST USERS VERIFICATION")
    print("=" * 60)
    print()
    
    users = [
        ("09124669509", "Admin"),
        ("09144669509", "Regular User")
    ]
    
    for phone, label in users:
        print(f"{label}: {phone}")
        print("-" * 60)
        
        user = get_user_by_phone(phone)
        if user:
            print(f"✓ User found")
            print(f"  ID:         {user['id']}")
            print(f"  Phone:      {user['phone_number']}")
            print(f"  Role:       {user['role']}")
            print(f"  Active:     {user['is_active']}")
            print(f"  Created:    {user['created_at']}")
            
            # Get wallet info
            wallet = get_wallet_by_user_id(user['id'])
            if wallet:
                print(f"  Wallet ID:  {wallet['id']}")
                print(f"  Balance:    {wallet['balance']:,} Rials")
                print(f"  Updated:    {wallet['last_updated']}")
            
            # Get plates
            plates = get_user_plates(user['id'])
            if plates:
                print(f"  Plates:     {len(plates)} registered")
                for plate in plates:
                    print(f"    - {plate['plate']}")
            else:
                print(f"  Plates:     None registered")
        else:
            print(f"✗ User not found")
        
        print()
    
    print("=" * 60)

if __name__ == '__main__':
    verify_users()
