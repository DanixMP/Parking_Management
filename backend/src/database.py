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
    """ثبت خروج بر اساس آخرین ورود فعال همین پلاک"""
    conn = get_conn()
    cur = conn.cursor()

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

    # حذف از active_cars
    cur.execute("DELETE FROM active_cars WHERE entry_id=?", (entry_id,))

    conn.commit()
    conn.close()

    return {
        "entry_id": entry_id,
        "plate": plate,
        "duration": duration,
        "cost": cost,
    }
    
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