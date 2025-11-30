import sqlite3
from datetime import datetime, date
import os
from pathlib import Path

# Use absolute path to database file in src directory
DB_PATH = Path(__file__).parent / "parking.db"


def get_conn():
    return sqlite3.connect(str(DB_PATH))


def init_db(default_capacity=200, default_price_per_hour=20000):
    conn = get_conn()
    cur = conn.cursor()

    # جدول ورود
    cur.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate TEXT NOT NULL,
            image_in TEXT NOT NULL,
            timestamp_in TEXT NOT NULL
        )
    """)

    # جدول خروج
    cur.execute("""
        CREATE TABLE IF NOT EXISTS exits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id INTEGER NOT NULL,
            plate TEXT NOT NULL,
            image_out TEXT NOT NULL,
            timestamp_out TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL,
            cost INTEGER NOT NULL,
            FOREIGN KEY(entry_id) REFERENCES entries(id)
        )
    """)

    # جدول خودروهای داخل
    cur.execute("""
        CREATE TABLE IF NOT EXISTS active_cars (
            entry_id INTEGER PRIMARY KEY,
            plate TEXT NOT NULL,
            timestamp_in TEXT NOT NULL,
            FOREIGN KEY(entry_id) REFERENCES entries(id)
        )
    """)

    # جدول تنظیمات عمومی
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    # جدول کاربران
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1
        )
    """)

    # جدول کیف پول
    cur.execute("""
        CREATE TABLE IF NOT EXISTS wallets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            balance INTEGER NOT NULL DEFAULT 0,
            last_updated TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # جدول تراکنش‌ها
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wallet_id INTEGER NOT NULL,
            transaction_type TEXT NOT NULL,
            amount INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            description TEXT,
            exit_id INTEGER,
            FOREIGN KEY(wallet_id) REFERENCES wallets(id),
            FOREIGN KEY(exit_id) REFERENCES exits(id)
        )
    """)

    # جدول پلاک‌های کاربران
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_plates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plate TEXT NOT NULL,
            registered_at TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY(user_id) REFERENCES users(id),
            UNIQUE(user_id, plate)
        )
    """)

    # جدول توکن‌های احراز هویت
    cur.execute("""
        CREATE TABLE IF NOT EXISTS auth_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # ظرفیت پیش‌فرض
    cur.execute("SELECT value FROM settings WHERE key='capacity'")
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?)",
            ("capacity", str(default_capacity)),
        )

    # تعرفه ساعتی پیش‌فرض
    cur.execute("SELECT value FROM settings WHERE key='price_per_hour'")
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?)",
            ("price_per_hour", str(default_price_per_hour)),
        )

    conn.commit()
    conn.close()


# ----------------- ورود -----------------


def register_entry(plate, image_path):
    """ثبت ورود خودرو"""
    conn = get_conn()
    cur = conn.cursor()

    t_in = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ثبت در entries
    cur.execute("""
        INSERT INTO entries (plate, image_in, timestamp_in)
        VALUES (?, ?, ?)
    """, (plate, image_path, t_in))
    entry_id = cur.lastrowid

    # اضافه به active_cars
    cur.execute("""
        INSERT OR REPLACE INTO active_cars (entry_id, plate, timestamp_in)
        VALUES (?, ?, ?)
    """, (entry_id, plate, t_in))

    conn.commit()
    conn.close()
    return entry_id


# ----------------- خروج -----------------


def register_exit(plate, image_path):
    """
    ثبت خروج بر اساس آخرین ورود فعال همین پلاک
    
    Integrates automatic payment processing for registered users:
    - Checks if the plate is registered to a user
    - If registered and sufficient balance, automatically deducts parking cost
    - Creates transaction record linking exit to wallet payment
    - Maintains backward compatibility with non-registered users
    """
    conn = get_conn()
    cur = conn.cursor()

    try:
        # آخرین ورود فعال
        cur.execute("""
            SELECT entry_id, timestamp_in
            FROM active_cars
            WHERE plate=?
        """, (plate,))
        row = cur.fetchone()

        if row is None:
            conn.close()
            return None  # این خودرو داخل نیست

        entry_id, t_in = row
        t_out_dt = datetime.now()
        t_in_dt = datetime.strptime(t_in, "%Y-%m-%d %H:%M:%S")

        duration = int((t_out_dt - t_in_dt).total_seconds() / 60)  # دقیقه

        # تعرفه
        cur.execute("SELECT value FROM settings WHERE key='price_per_hour'")
        price_per_hour = int(cur.fetchone()[0])

        # هزینه (رند به ساعت)
        hours = max(1, (duration + 59) // 60)
        cost = hours * price_per_hour

        # ثبت در exits
        cur.execute("""
            INSERT INTO exits (entry_id, plate, image_out, timestamp_out, duration_minutes, cost)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            entry_id,
            plate,
            image_path,
            t_out_dt.strftime("%Y-%m-%d %H:%M:%S"),
            duration,
            cost,
        ))
        
        exit_id = cur.lastrowid

        # حذف از active_cars
        cur.execute("DELETE FROM active_cars WHERE entry_id=?", (entry_id,))

        # Check if plate is registered to a user (automatic payment processing)
        cur.execute("""
            SELECT user_id
            FROM user_plates
            WHERE plate = ? AND is_active = 1
            LIMIT 1
        """, (plate,))
        
        plate_owner_row = cur.fetchone()
        
        payment_status = 'manual'  # Default for non-registered users
        payment_error = None
        transaction_id = None
        
        if plate_owner_row is not None:
            # Plate is registered - attempt automatic payment
            user_id = plate_owner_row[0]
            
            # Get user's wallet
            cur.execute("""
                SELECT id, balance
                FROM wallets
                WHERE user_id = ?
            """, (user_id,))
            
            wallet_row = cur.fetchone()
            
            if wallet_row is not None:
                wallet_id, current_balance = wallet_row
                
                # Check if sufficient balance
                if current_balance >= cost:
                    # Sufficient balance - process automatic payment
                    new_balance = current_balance - cost
                    timestamp = t_out_dt.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Update wallet balance
                    cur.execute("""
                        UPDATE wallets
                        SET balance = ?, last_updated = ?
                        WHERE id = ?
                    """, (new_balance, timestamp, wallet_id))
                    
                    # Create transaction record
                    cur.execute("""
                        INSERT INTO transactions (wallet_id, transaction_type, amount, timestamp, description, exit_id)
                        VALUES (?, 'payment', ?, ?, ?, ?)
                    """, (wallet_id, cost, timestamp, f'Automatic parking payment for plate {plate}', exit_id))
                    
                    transaction_id = cur.lastrowid
                    payment_status = 'auto_paid'
                else:
                    # Insufficient balance
                    payment_status = 'insufficient_balance'
                    payment_error = f'Insufficient balance. Required: {cost}, Available: {current_balance}'
            else:
                # Wallet not found (shouldn't happen, but handle gracefully)
                payment_status = 'wallet_not_found'
                payment_error = 'Wallet not found for registered user'

        conn.commit()
        
        result = {
            "entry_id": entry_id,
            "exit_id": exit_id,
            "plate": plate,
            "duration": duration,
            "cost": cost,
            "payment_status": payment_status,
        }
        
        # Add optional fields if automatic payment was attempted
        if payment_error is not None:
            result["payment_error"] = payment_error
        if transaction_id is not None:
            result["transaction_id"] = transaction_id
            
        return result
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
    
    # ----------------- وضعیت‌ها -----------------


def count_active_cars():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM active_cars")
    c = cur.fetchone()[0]
    conn.close()
    return c


def get_capacity():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key='capacity'")
    row = cur.fetchone()
    conn.close()
    return int(row[0]) if row else 0


def set_capacity(new_capacity: int):
    """تغییر ظرفیت پارکینگ"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        ("capacity", str(new_capacity)),
    )
    conn.commit()
    conn.close()


def get_free_slots():
    return max(0, get_capacity() - count_active_cars())


def get_price_per_hour():
    """گرفتن تعرفه هر ساعت"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key='price_per_hour'")
    row = cur.fetchone()
    conn.close()
    return int(row[0]) if row else 0


def set_price_per_hour(value: int):
    """تنظیم تعرفه هر ساعت توقف"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        ("price_per_hour", str(value)),
    )
    conn.commit()
    conn.close()


# ----------------- ریست و تاریخ ریست -----------------


def reset_database():
    """
    حذف تمام اطلاعات ورود، خروج و خودروهای فعال.
    تنظیمات (capacity, price_per_hour و last_reset) حفظ می‌شوند.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM entries")
    cur.execute("DELETE FROM exits")
    cur.execute("DELETE FROM active_cars")
    conn.commit()
    conn.close()


def get_last_reset():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key='last_reset'")
    row = cur.fetchone()
    conn.close()
    if row is None:
        return None
    return row[0]


def set_last_reset(date_str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        ("last_reset", date_str),
    )
    conn.commit()
    conn.close()


# ----------------- جلوگیری از ثبت تکراری ورود -----------------


def was_recently_recorded(plate, minutes=5):
    """
    آیا این پلاک در X دقیقه اخیر ورود جدید داشته؟
    برای جلوگیری از ثبت دوباره همان ماشین که جلوی دوربین می‌ایستد.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT timestamp_in FROM entries
        WHERE plate=?
        ORDER BY id DESC
        LIMIT 1
    """, (plate,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return False  # تا حالا ورود ثبت نشده

    last_time = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
    diff_minutes = (datetime.now() - last_time).total_seconds() / 60.0
    return diff_minutes < minutes


# ----------------- User Management -----------------


def create_user(phone_number, role='user'):
    """
    Create a new user with the given phone number and role.
    Returns user_id on success, raises exception if phone number already exists.
    """
    conn = get_conn()
    cur = conn.cursor()
    
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        cur.execute("""
            INSERT INTO users (phone_number, role, created_at, is_active)
            VALUES (?, ?, ?, 1)
        """, (phone_number, role, created_at))
        user_id = cur.lastrowid
        
        # Create wallet for the user
        cur.execute("""
            INSERT INTO wallets (user_id, balance, last_updated)
            VALUES (?, 0, ?)
        """, (user_id, created_at))
        
        conn.commit()
        return user_id
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise ValueError(f"Phone number {phone_number} already exists") from e
    finally:
        conn.close()


def get_user_by_phone(phone_number):
    """Get user by phone number. Returns user dict or None."""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, phone_number, role, created_at, is_active
        FROM users
        WHERE phone_number = ?
    """, (phone_number,))
    
    row = cur.fetchone()
    conn.close()
    
    if row is None:
        return None
    
    return {
        'id': row[0],
        'phone_number': row[1],
        'role': row[2],
        'created_at': row[3],
        'is_active': row[4]
    }


def delete_user(user_id):
    """Delete a user and all associated data."""
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        # Delete in order due to foreign key constraints
        cur.execute("DELETE FROM auth_tokens WHERE user_id = ?", (user_id,))
        cur.execute("DELETE FROM user_plates WHERE user_id = ?", (user_id,))
        
        # Get wallet_id before deleting wallet
        cur.execute("SELECT id FROM wallets WHERE user_id = ?", (user_id,))
        wallet_row = cur.fetchone()
        if wallet_row:
            wallet_id = wallet_row[0]
            cur.execute("DELETE FROM transactions WHERE wallet_id = ?", (wallet_id,))
            cur.execute("DELETE FROM wallets WHERE user_id = ?", (user_id,))
        
        cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        conn.commit()
    finally:
        conn.close()


def get_user_by_id(user_id):
    """Get user by ID. Returns user dict or None."""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, phone_number, role, created_at, is_active
        FROM users
        WHERE id = ?
    """, (user_id,))
    
    row = cur.fetchone()
    conn.close()
    
    if row is None:
        return None
    
    return {
        'id': row[0],
        'phone_number': row[1],
        'role': row[2],
        'created_at': row[3],
        'is_active': row[4]
    }


def get_wallet_by_user_id(user_id):
    """Get wallet for a user. Returns wallet dict or None."""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, user_id, balance, last_updated
        FROM wallets
        WHERE user_id = ?
    """, (user_id,))
    
    row = cur.fetchone()
    conn.close()
    
    if row is None:
        return None
    
    return {
        'id': row[0],
        'user_id': row[1],
        'balance': row[2],
        'last_updated': row[3]
    }


def create_transaction(wallet_id, transaction_type, amount, description='', exit_id=None):
    """
    Create a transaction record.
    Returns transaction_id on success.
    """
    conn = get_conn()
    cur = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        cur.execute("""
            INSERT INTO transactions (wallet_id, transaction_type, amount, timestamp, description, exit_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (wallet_id, transaction_type, amount, timestamp, description, exit_id))
        transaction_id = cur.lastrowid
        
        conn.commit()
        return transaction_id
    finally:
        conn.close()


def get_transaction_by_id(transaction_id):
    """Get transaction by ID. Returns transaction dict or None."""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, wallet_id, transaction_type, amount, timestamp, description, exit_id
        FROM transactions
        WHERE id = ?
    """, (transaction_id,))
    
    row = cur.fetchone()
    conn.close()
    
    if row is None:
        return None
    
    return {
        'id': row[0],
        'wallet_id': row[1],
        'transaction_type': row[2],
        'amount': row[3],
        'timestamp': row[4],
        'description': row[5],
        'exit_id': row[6]
    }


def add_user_plate(user_id, plate):
    """
    Register a plate for a user.
    Returns plate_id on success, raises exception if duplicate.
    """
    conn = get_conn()
    cur = conn.cursor()
    
    registered_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        cur.execute("""
            INSERT INTO user_plates (user_id, plate, registered_at, is_active)
            VALUES (?, ?, ?, 1)
        """, (user_id, plate, registered_at))
        plate_id = cur.lastrowid
        
        conn.commit()
        return plate_id
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise ValueError(f"Plate {plate} already registered for this user") from e
    finally:
        conn.close()


def get_user_plate_by_id(plate_id):
    """Get user plate by ID. Returns plate dict or None."""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, user_id, plate, registered_at, is_active
        FROM user_plates
        WHERE id = ?
    """, (plate_id,))
    
    row = cur.fetchone()
    conn.close()
    
    if row is None:
        return None
    
    return {
        'id': row[0],
        'user_id': row[1],
        'plate': row[2],
        'registered_at': row[3],
        'is_active': row[4]
    }


# ----------------- Authentication & Token Management -----------------

import secrets
import hashlib


def generate_token():
    """Generate a secure random token."""
    return secrets.token_urlsafe(32)


def create_auth_token(user_id, expiry_hours=720):
    """
    Create an authentication token for a user.
    Default expiry is 720 hours (30 days).
    Returns token string on success.
    """
    from datetime import timedelta
    
    conn = get_conn()
    cur = conn.cursor()
    
    token = generate_token()
    created_at = datetime.now()
    expires_at = created_at + timedelta(hours=expiry_hours)
    
    created_at_str = created_at.strftime("%Y-%m-%d %H:%M:%S")
    expires_at_str = expires_at.strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        cur.execute("""
            INSERT INTO auth_tokens (user_id, token, created_at, expires_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, token, created_at_str, expires_at_str))
        
        conn.commit()
        return token
    finally:
        conn.close()


def validate_token(token):
    """
    Validate an authentication token.
    Returns user_id if valid, None if invalid or expired.
    """
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT user_id, expires_at
        FROM auth_tokens
        WHERE token = ?
    """, (token,))
    
    row = cur.fetchone()
    conn.close()
    
    if row is None:
        return None
    
    user_id, expires_at_str = row
    expires_at = datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S")
    
    # Check if token is expired
    if datetime.now() > expires_at:
        return None
    
    return user_id


def delete_token(token):
    """Delete an authentication token (for logout)."""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM auth_tokens WHERE token = ?", (token,))
    
    conn.commit()
    conn.close()


def delete_user_tokens(user_id):
    """Delete all tokens for a user."""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM auth_tokens WHERE user_id = ?", (user_id,))
    
    conn.commit()
    conn.close()


def validate_phone_number(phone_number):
    """
    Validate Iranian phone number format.
    Returns True if valid, False otherwise.
    Format: 09XXXXXXXXX (11 digits starting with 09)
    """
    import re
    pattern = r'^09\d{9}$'
    return bool(re.match(pattern, phone_number))


def validate_plate_format(plate):
    """
    Validate Iranian license plate format.
    Returns True if valid, False otherwise.
    
    Valid formats:
    - Full format: 2 digits + Persian letter + 3 digits + 2 digits (e.g., "12ب345-67", "13الف111-10")
    - Short format: 2 digits + Persian letter + 3 digits (e.g., "12ب345")
    - Various separators allowed: space, dash, pipe, or none
    - Letter can be at different positions in the string
    
    Examples of valid plates:
    - "12ب345-67"
    - "12 ب 345 67"
    - "13الف111-10"
    - "12ب345"
    """
    import re
    
    if not plate or not isinstance(plate, str):
        return False
    
    # Normalize: remove common separators and "ایران"
    normalized = plate.strip()
    normalized = normalized.replace(' ', '').replace('-', '').replace('|', '').replace('ایران', '')
    
    if not normalized:
        return False
    
    # Persian letters used in Iranian plates (sorted by length, longest first to match multi-char letters first)
    persian_letters = [
        'الف', 'ب', 'پ', 'ت', 'ث', 'ج', 'د', 'ز', 'س', 'ش',
        'ص', 'ط', 'ع', 'ف', 'ق', 'ک', 'گ', 'ل', 'م', 'ن',
        'و', 'ه', 'ی'
    ]
    
    # Find Persian letter position and the letter itself
    # We need to check for multi-character letters first (like 'الف')
    letter_start = -1
    letter_end = -1
    letter = ''
    
    # First, try to find multi-character letters
    for persian_letter in persian_letters:
        idx = normalized.find(persian_letter)
        if idx != -1:
            letter_start = idx
            letter_end = idx + len(persian_letter)
            letter = persian_letter
            break
    
    # If no multi-character letter found, look for single Persian characters
    if letter_start == -1:
        for i, char in enumerate(normalized):
            if re.match(r'[آ-ی]', char):
                letter_start = i
                letter_end = i + 1
                letter = char
                break
    
    if letter_start == -1:
        return False
    
    # Extract numbers before and after the letter
    before = normalized[:letter_start]
    after = normalized[letter_end:]
    
    # Check if all non-letter characters are digits
    if before and not before.isdigit():
        return False
    if after and not after.isdigit():
        return False
    
    # Valid formats:
    # 1. Full format: 2 digits + letter + 3 digits + 2 digits (total 7 digits)
    # 2. Short format: 2 digits + letter + 3 digits (total 5 digits)
    
    total_digits = len(before) + len(after)
    
    # Must have at least 5 digits (short format) and at most 7 digits (full format)
    if total_digits < 5 or total_digits > 7:
        return False
    
    # For full format (7 digits), we need:
    # - At least 2 digits before or after the letter for series
    # - At least 3 digits for serial
    # - Exactly 2 digits for region
    if total_digits == 7:
        # Letter in middle: 2 before + 5 after OR 5 before + 2 after
        if (len(before) == 2 and len(after) == 5) or (len(before) == 5 and len(after) == 2):
            return True
        # Letter at start: 0 before + 7 after
        if len(before) == 0 and len(after) == 7:
            return True
        # Letter at end: 7 before + 0 after
        if len(before) == 7 and len(after) == 0:
            return True
        return False
    
    # For short format (5 digits), we need:
    # - At least 2 digits for series
    # - At least 3 digits for serial
    if total_digits == 5:
        # Letter in middle: 2 before + 3 after OR 3 before + 2 after
        if (len(before) == 2 and len(after) == 3) or (len(before) == 3 and len(after) == 2):
            return True
        # Letter at start: 0 before + 5 after
        if len(before) == 0 and len(after) == 5:
            return True
        # Letter at end: 5 before + 0 after
        if len(before) == 5 and len(after) == 0:
            return True
        return False
    
    # For 6 digits (edge case)
    if total_digits == 6:
        # Could be valid in some formats
        if (len(before) == 2 and len(after) == 4) or (len(before) == 4 and len(after) == 2):
            return True
        if (len(before) == 3 and len(after) == 3):
            return True
        if len(before) == 0 and len(after) == 6:
            return True
        if len(before) == 6 and len(after) == 0:
            return True
    
    return False


def get_or_create_user(phone_number):
    """
    Get existing user by phone number or create a new one.
    Returns user dict.
    """
    # Validate phone number format
    if not validate_phone_number(phone_number):
        raise ValueError(f"Invalid phone number format: {phone_number}")
    
    # Try to get existing user
    user = get_user_by_phone(phone_number)
    
    if user is not None:
        return user
    
    # Create new user
    user_id = create_user(phone_number, role='user')
    return get_user_by_id(user_id)


# ----------------- Wallet Management -----------------


def get_wallet_balance(user_id):
    """
    Get the current wallet balance for a user.
    Returns balance as integer or None if wallet not found.
    """
    wallet = get_wallet_by_user_id(user_id)
    if wallet is None:
        return None
    return wallet['balance']


def charge_wallet(user_id, amount):
    """
    Charge (add funds to) a user's wallet.
    Creates a transaction record and updates the balance.
    Returns the new balance on success, raises exception on error.
    """
    if amount <= 0:
        raise ValueError("Charge amount must be positive")
    
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        # Get current wallet
        wallet = get_wallet_by_user_id(user_id)
        if wallet is None:
            raise ValueError(f"Wallet not found for user {user_id}")
        
        wallet_id = wallet['id']
        current_balance = wallet['balance']
        new_balance = current_balance + amount
        
        # Update wallet balance
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
            UPDATE wallets
            SET balance = ?, last_updated = ?
            WHERE id = ?
        """, (new_balance, timestamp, wallet_id))
        
        # Create transaction record
        cur.execute("""
            INSERT INTO transactions (wallet_id, transaction_type, amount, timestamp, description)
            VALUES (?, 'charge', ?, ?, 'Wallet charge')
        """, (wallet_id, amount, timestamp))
        
        transaction_id = cur.lastrowid
        
        conn.commit()
        
        return {
            'new_balance': new_balance,
            'transaction_id': transaction_id
        }
    
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def deduct_from_wallet(user_id, amount, description='', exit_id=None):
    """
    Deduct funds from a user's wallet (for parking payments).
    Creates a transaction record and updates the balance.
    Returns the new balance on success, raises exception if insufficient balance or error.
    """
    if amount <= 0:
        raise ValueError("Deduction amount must be positive")
    
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        # Get current wallet
        wallet = get_wallet_by_user_id(user_id)
        if wallet is None:
            raise ValueError(f"Wallet not found for user {user_id}")
        
        wallet_id = wallet['id']
        current_balance = wallet['balance']
        
        # Check sufficient balance
        if current_balance < amount:
            raise ValueError(f"Insufficient wallet balance. Current: {current_balance}, Required: {amount}")
        
        new_balance = current_balance - amount
        
        # Update wallet balance
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
            UPDATE wallets
            SET balance = ?, last_updated = ?
            WHERE id = ?
        """, (new_balance, timestamp, wallet_id))
        
        # Create transaction record
        cur.execute("""
            INSERT INTO transactions (wallet_id, transaction_type, amount, timestamp, description, exit_id)
            VALUES (?, 'payment', ?, ?, ?, ?)
        """, (wallet_id, amount, timestamp, description, exit_id))
        
        transaction_id = cur.lastrowid
        
        conn.commit()
        
        return {
            'new_balance': new_balance,
            'transaction_id': transaction_id
        }
    
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_wallet_transactions(user_id, limit=50, offset=0):
    """
    Get transaction history for a user's wallet.
    Returns list of transactions in chronological order (most recent first).
    """
    conn = get_conn()
    cur = conn.cursor()
    
    # Get wallet_id
    wallet = get_wallet_by_user_id(user_id)
    if wallet is None:
        conn.close()
        return []
    
    wallet_id = wallet['id']
    
    # Get total count
    cur.execute("""
        SELECT COUNT(*)
        FROM transactions
        WHERE wallet_id = ?
    """, (wallet_id,))
    total_count = cur.fetchone()[0]
    
    # Get transactions
    cur.execute("""
        SELECT id, wallet_id, transaction_type, amount, timestamp, description, exit_id
        FROM transactions
        WHERE wallet_id = ?
        ORDER BY timestamp DESC
        LIMIT ? OFFSET ?
    """, (wallet_id, limit, offset))
    
    rows = cur.fetchall()
    conn.close()
    
    transactions = []
    for row in rows:
        transactions.append({
            'id': row[0],
            'wallet_id': row[1],
            'transaction_type': row[2],
            'amount': row[3],
            'timestamp': row[4],
            'description': row[5],
            'exit_id': row[6]
        })
    
    return {
        'count': total_count,
        'results': transactions
    }


# ----------------- Plate Management -----------------


def get_user_plates(user_id):
    """
    Get all active plates registered to a user.
    Returns list of plate dicts.
    """
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, user_id, plate, registered_at, is_active
        FROM user_plates
        WHERE user_id = ? AND is_active = 1
        ORDER BY registered_at DESC
    """, (user_id,))
    
    rows = cur.fetchall()
    conn.close()
    
    plates = []
    for row in rows:
        plates.append({
            'id': row[0],
            'user_id': row[1],
            'plate': row[2],
            'registered_at': row[3],
            'is_active': row[4]
        })
    
    return plates


def register_user_plate(user_id, plate):
    """
    Register a plate for a user.
    Validates plate format before registration.
    Returns plate_id on success, raises exception if invalid or duplicate.
    """
    # Validate plate format
    if not validate_plate_format(plate):
        raise ValueError(f"Invalid license plate format: {plate}")
    
    # Use the existing add_user_plate function
    return add_user_plate(user_id, plate)


def delete_user_plate(plate_id, user_id=None):
    """
    Delete (deactivate) a user's plate.
    If user_id is provided, verifies the plate belongs to that user.
    Returns True on success, raises exception if plate not found or unauthorized.
    """
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        # Get the plate
        plate = get_user_plate_by_id(plate_id)
        
        if plate is None:
            raise ValueError(f"Plate not found with id {plate_id}")
        
        # Verify ownership if user_id provided
        if user_id is not None and plate['user_id'] != user_id:
            raise ValueError(f"Plate {plate_id} does not belong to user {user_id}")
        
        # Deactivate the plate (soft delete)
        cur.execute("""
            UPDATE user_plates
            SET is_active = 0
            WHERE id = ?
        """, (plate_id,))
        
        conn.commit()
        return True
    
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_plate_owner(plate):
    """
    Find the user who owns a specific plate.
    Returns user_id if found, None otherwise.
    """
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT user_id
        FROM user_plates
        WHERE plate = ? AND is_active = 1
        LIMIT 1
    """, (plate,))
    
    row = cur.fetchone()
    conn.close()
    
    if row is None:
        return None
    
    return row[0]


# ----------------- Admin Functions -----------------


def get_all_users(limit=100, offset=0):
    """
    Get all users in the system (admin function).
    Returns list of user dicts with pagination.
    """
    conn = get_conn()
    cur = conn.cursor()
    
    # Get total count
    cur.execute("SELECT COUNT(*) FROM users")
    total_count = cur.fetchone()[0]
    
    # Get users
    cur.execute("""
        SELECT id, phone_number, role, created_at, is_active
        FROM users
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))
    
    rows = cur.fetchall()
    conn.close()
    
    users = []
    for row in rows:
        users.append({
            'id': row[0],
            'phone_number': row[1],
            'role': row[2],
            'created_at': row[3],
            'is_active': row[4]
        })
    
    return {
        'count': total_count,
        'results': users
    }


def update_user_role(user_id, new_role):
    """
    Update a user's role (admin function).
    Valid roles: 'user', 'admin', 'superuser'
    Returns True on success, raises exception if user not found or invalid role.
    """
    valid_roles = ['user', 'admin', 'superuser']
    
    if new_role not in valid_roles:
        raise ValueError(f"Invalid role: {new_role}. Must be one of {valid_roles}")
    
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        # Check if user exists
        user = get_user_by_id(user_id)
        if user is None:
            raise ValueError(f"User not found with id {user_id}")
        
        # Update role
        cur.execute("""
            UPDATE users
            SET role = ?
            WHERE id = ?
        """, (new_role, user_id))
        
        conn.commit()
        return True
    
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()