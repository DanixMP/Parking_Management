#!/usr/bin/env python
"""
Database Initialization Script
Run this to initialize the parking database before running the system
"""

import os
import sys
from pathlib import Path

# Ensure we're in the right directory
os.chdir(Path(__file__).parent)

from database import init_db, get_capacity, get_free_slots, count_active_cars

print("\n" + "="*70)
print("Parking Management System - Database Initialization")
print("="*70 + "\n")

try:
    print("Initializing database...")
    init_db()
    print("✓ Database initialized successfully\n")
    
    # Verify tables were created
    print("Verifying database...")
    capacity = get_capacity()
    free_slots = get_free_slots()
    active_cars = count_active_cars()
    
    print(f"✓ Capacity: {capacity}")
    print(f"✓ Free slots: {free_slots}")
    print(f"✓ Active cars: {active_cars}")
    print()
    
    print("="*70)
    print("✓ Database is ready!")
    print("="*70 + "\n")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
