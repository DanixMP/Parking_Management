import sys
import os
import sqlite3
import datetime
import shutil

import pandas as pd

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QTableWidget, QTableWidgetItem,
    QMessageBox, QGroupBox, QSpinBox, QHeaderView, QComboBox
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QFont, QIcon

from database import (
    init_db,
    reset_database,
    get_last_reset,
    set_last_reset,
    get_capacity,
    set_capacity,
    get_price_per_hour,
    set_price_per_hour,
)
from archive_utils import archive_day, ARCHIVE_ROOT

# تلاش برای ایمپورت تشخیص نوع پلاک (ملی / مناطق آزاد و...)
try:
    from plate_utils import get_plate_region
except ImportError:
    def get_plate_region(_plate: str) -> str | None:
        # اگر plate_utils نداری، موقتاً همیشه National برمی‌گردونیم
        return "National"

DB_PATH = "parking.db"


def query(sql, params=()):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df


def full_reset_system():
    """حذف کامل دیتابیس و آرشیوها و ساخت دوباره DB خالی"""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    if os.path.exists(ARCHIVE_ROOT):
        shutil.rmtree(ARCHIVE_ROOT)
    init_db()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # ---------- جهت کلی برنامه RTL ----------
        self.setLayoutDirection(Qt.RightToLeft)

        # ---------- تنظیمات پنجره ----------
        self.setWindowTitle("سیستم مدیریت پارکینگ - ANPR")
        self.resize(1300, 750)

        # آیکن برنامه (اگر لوگو داری در assets/logo.png)
        if os.path.exists("assets/logo.png"):
            self.setWindowIcon(QIcon("assets/logo.png"))

        # فونت پیش‌فرض
        base_font = QFont("Segoe UI", 9)
        QApplication.instance().setFont(base_font)

        # ---------- ویجت اصلی ----------
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # ---------- هدر (لوگو + عنوان) ----------
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        logo_label = QLabel()
        if os.path.exists("assets/logo.png"):
            pix = QPixmap("assets/logo.png")
            pix = pix.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pix)
        header_layout.addWidget(logo_label)

        title_label = QLabel("سیستم هوشمند مدیریت پارکینگ")
        title_font = QFont("Segoe UI", 14, QFont.Bold)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        header_layout.addStretch()
        main_layout.addWidget(header_widget)

        # ---------- کادر وضعیت لحظه‌ای + تنظیمات ----------
        status_group = QGroupBox("وضعیت لحظه‌ای پارکینگ")
        status_layout = QHBoxLayout(status_group)

        self.lbl_capacity = QLabel("کل ظرفیت: -")
        self.lbl_active = QLabel("خودروهای داخل: -")
        self.lbl_free = QLabel("جای خالی: -")

        bold_font = QFont("Segoe UI", 10, QFont.Bold)
        self.lbl_capacity.setFont(bold_font)
        self.lbl_active.setFont(bold_font)
        self.lbl_free.setFont(bold_font)

        status_layout.addWidget(self.lbl_capacity)
        status_layout.addWidget(self.lbl_active)
        status_layout.addWidget(self.lbl_free)
        status_layout.addStretch()

        # تنظیم ظرفیت
        self.spin_capacity = QSpinBox()
        self.spin_capacity.setRange(1, 5000)
        btn_cap = QPushButton("ذخیره ظرفیت")

        # تنظیم تعرفه
        self.spin_price = QSpinBox()
        self.spin_price.setRange(1000, 1_000_000)
        self.spin_price.setSingleStep(1000)
        btn_price = QPushButton("ذخیره تعرفه")

        status_layout.addWidget(QLabel("ظرفیت:"))
        status_layout.addWidget(self.spin_capacity)
        status_layout.addWidget(btn_cap)
        status_layout.addSpacing(10)
        status_layout.addWidget(QLabel("تعرفه (تومان/ساعت):"))
        status_layout.addWidget(self.spin_price)
        status_layout.addWidget(btn_price)

        main_layout.addWidget(status_group)

        # ---------- نوار دکمه‌های مدیریتی ----------
        btn_bar = QHBoxLayout()
        btn_refresh = QPushButton("↻ رفرش دستی")
        btn_reset_day = QPushButton("بستن روز جاری + آرشیو")
        btn_clear_db = QPushButton("پاکسازی دیتابیس (بدون آرشیو)")
        btn_full_reset = QPushButton("🧨 ریست کامل سیستم")

        btn_bar.addWidget(btn_refresh)
        btn_bar.addWidget(btn_reset_day)
        btn_bar.addWidget(btn_clear_db)
        btn_bar.addWidget(btn_full_reset)
        btn_bar.addStretch()
        main_layout.addLayout(btn_bar)

        # ---------- تب‌ها ----------
        self.tabs = QTabWidget()

        # === تب ۱: خودروهای داخل ===
        self._build_tab_active()
        self.tabs.addTab(self.tab_active, "خودروهای داخل")

        # === تب ۲: تاریخچه ورودها ===
        self._build_tab_entries()
        self.tabs.addTab(self.tab_entries, "تاریچه ورودها")

        # === تب ۳: تاریخچه خروج‌ها ===
        self._build_tab_exits()
        self.tabs.addTab(self.tab_exits, "تاریخچه خروج‌ها")

        # === تب ۴: آرشیو و گزارش‌ها ===
        self._build_tab_archive()
        self.tabs.addTab(self.tab_archive, "آرشیو و گزارش‌ها")

        main_layout.addWidget(self.tabs, 1)

        self.setCentralWidget(main_widget)

        # ---------- رویداد انتخاب ردیف‌ها ----------
        self.table_active.itemSelectionChanged.connect(self.on_active_selected)
        self.table_entries.itemSelectionChanged.connect(self.on_entry_selected)
        self.table_exits.itemSelectionChanged.connect(self.on_exit_selected)

        # ---------- دکمه‌ها ----------
        btn_refresh.clicked.connect(self.refresh_all)
        btn_reset_day.clicked.connect(self.reset_day_archive)
        btn_clear_db.clicked.connect(self.clear_db_only)
        btn_full_reset.clicked.connect(self.full_reset_clicked)
        btn_cap.clicked.connect(self.save_capacity)
        btn_price.clicked.connect(self.save_price)

        # رویدادهای تب آرشیو
        self.cmb_days.currentIndexChanged.connect(self.on_archive_day_changed)
        self.btn_refresh_days.clicked.connect(self.refresh_archive_days)
        self.btn_refresh_income.clicked.connect(self.refresh_income_report)
        self.btn_open_pdf.clicked.connect(self.open_archive_pdf)
        self.btn_export_excel.clicked.connect(self.export_archive_excel)

        # ---------- تایمر رفرش خودکار ----------
        self.timer = QTimer(self)
        self.timer.setInterval(2000)  # هر ۲ ثانیه
        self.timer.timeout.connect(self.refresh_all)
        self.timer.start()

        # ---------- مقداردهی اولیه ----------
        self.load_settings()
        self.refresh_all()
        self.refresh_archive_days()
        self.refresh_income_report()

    # ================= ساخت تب‌ها =================

    def _build_tab_active(self):
        self.tab_active = QWidget()
        active_layout = QHBoxLayout(self.tab_active)

        self.table_active = QTableWidget()
        self.table_active.setColumnCount(5)
        self.table_active.setHorizontalHeaderLabels(
            ["entry_id", "پلاک", "منطقه", "زمان ورود", "مسیر تصویر"]
        )
        self.table_active.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_active.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_active.horizontalHeader().setDefaultAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )
        self.table_active.verticalHeader().setDefaultSectionSize(26)

        self.lbl_active_img = QLabel("تصویر خودرو نمایش داده می‌شود")
        self.lbl_active_img.setAlignment(Qt.AlignCenter)
        self.lbl_active_img.setMinimumWidth(400)

        active_layout.addWidget(self.table_active, 2)
        active_layout.addWidget(self.lbl_active_img, 1)

    def _build_tab_entries(self):
        self.tab_entries = QWidget()
        entries_layout = QHBoxLayout(self.tab_entries)

        self.table_entries = QTableWidget()
        self.table_entries.setColumnCount(5)
        self.table_entries.setHorizontalHeaderLabels(
            ["id", "پلاک", "منطقه", "زمان ورود", "مسیر تصویر"]
        )
        self.table_entries.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_entries.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_entries.horizontalHeader().setDefaultAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )
        self.table_entries.verticalHeader().setDefaultSectionSize(26)

        self.lbl_entry_img = QLabel("تصویر ورود نمایش داده می‌شود")
        self.lbl_entry_img.setAlignment(Qt.AlignCenter)
        self.lbl_entry_img.setMinimumWidth(400)

        entries_layout.addWidget(self.table_entries, 2)
        entries_layout.addWidget(self.lbl_entry_img, 1)

    def _build_tab_exits(self):
        self.tab_exits = QWidget()
        exits_layout = QHBoxLayout(self.tab_exits)

        self.table_exits = QTableWidget()
        self.table_exits.setColumnCount(7)
        self.table_exits.setHorizontalHeaderLabels(
            ["id", "پلاک", "منطقه", "زمان خروج", "مدت (دقیقه)", "هزینه", "مسیر تصویر"]
        )
        self.table_exits.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_exits.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_exits.horizontalHeader().setDefaultAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )
        self.table_exits.verticalHeader().setDefaultSectionSize(26)

        self.lbl_exit_img = QLabel("تصویر خروج نمایش داده می‌شود")
        self.lbl_exit_img.setAlignment(Qt.AlignCenter)
        self.lbl_exit_img.setMinimumWidth(400)

        exits_layout.addWidget(self.table_exits, 2)
        exits_layout.addWidget(self.lbl_exit_img, 1)

    def _build_tab_archive(self):
        """تب آرشیو و گزارش‌ها"""

        self.tab_archive = QWidget()
        layout = QVBoxLayout(self.tab_archive)

        # --- انتخاب روز آرشیو ---
        top_box = QGroupBox("انتخاب روز آرشیوشده")
        top_layout = QHBoxLayout(top_box)

        self.cmb_days = QComboBox()
        self.btn_refresh_days = QPushButton("↻ رفرش لیست روزها")

        top_layout.addWidget(QLabel("روز:"))
        top_layout.addWidget(self.cmb_days)
        top_layout.addWidget(self.btn_refresh_days)
        top_layout.addStretch()

        layout.addWidget(top_box)

        # --- خلاصه آماری روز منتخب ---
        summary_box = QGroupBox("خلاصه روز انتخاب‌شده")
        summary_layout = QHBoxLayout(summary_box)

        self.lbl_sum_entries = QLabel("ورودی‌ها: -")
        self.lbl_sum_exits = QLabel("خروجی‌ها: -")
        self.lbl_sum_active_end = QLabel("خودروهای باقی‌مانده در پایان روز: -")
        self.lbl_sum_revenue = QLabel("درآمد روز (تومان): -")
        self.lbl_sum_avg_duration = QLabel("میانگین مدت توقف (دقیقه): -")

        for lbl in [
            self.lbl_sum_entries,
            self.lbl_sum_exits,
            self.lbl_sum_active_end,
            self.lbl_sum_revenue,
            self.lbl_sum_avg_duration,
        ]:
            lbl.setFont(QFont("Segoe UI", 9, QFont.Bold))

        summary_layout.addWidget(self.lbl_sum_entries)
        summary_layout.addWidget(self.lbl_sum_exits)
        summary_layout.addWidget(self.lbl_sum_active_end)
        summary_layout.addWidget(self.lbl_sum_revenue)
        summary_layout.addWidget(self.lbl_sum_avg_duration)
        summary_layout.addStretch()

        layout.addWidget(summary_box)

        # --- جدول‌های آرشیو: ورود / خروج ---
        tables_box = QGroupBox("جزئیات ورود و خروج در روز انتخابی")
        tables_layout = QHBoxLayout(tables_box)

        # جدول ورودها
        self.table_archive_entries = QTableWidget()
        self.table_archive_entries.setColumnCount(4)
        self.table_archive_entries.setHorizontalHeaderLabels(
            ["id", "پلاک", "زمان ورود", "مسیر تصویر"]
        )
        self.table_archive_entries.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_archive_entries.horizontalHeader().setDefaultAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )
        self.table_archive_entries.verticalHeader().setDefaultSectionSize(24)

        # جدول خروج‌ها
        self.table_archive_exits = QTableWidget()
        self.table_archive_exits.setColumnCount(6)
        self.table_archive_exits.setHorizontalHeaderLabels(
            ["id", "پلاک", "زمان خروج", "مدت (دقیقه)", "هزینه", "مسیر تصویر"]
        )
        self.table_archive_exits.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_archive_exits.horizontalHeader().setDefaultAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )
        self.table_archive_exits.verticalHeader().setDefaultSectionSize(24)

        tables_layout.addWidget(self.table_archive_entries, 1)
        tables_layout.addWidget(self.table_archive_exits, 1)

        layout.addWidget(tables_box, 1)

        # --- خروجی فایل‌ها: PDF و Excel ---
        files_box = QGroupBox("دریافت گزارش و خروجی فایل‌ها")
        files_layout = QHBoxLayout(files_box)

        self.btn_open_pdf = QPushButton("باز کردن گزارش PDF")
        self.btn_export_excel = QPushButton("تبدیل دیتای روز به Excel و باز کردن")

        files_layout.addWidget(self.btn_open_pdf)
        files_layout.addWidget(self.btn_export_excel)
        files_layout.addStretch()

        layout.addWidget(files_box)

        # --- گزارش درآمد کلی ---
        income_box = QGroupBox("گزارش درآمد کلی پارکینگ")
        income_layout = QHBoxLayout(income_box)

        self.lbl_income_today = QLabel("درآمد امروز: - تومان")
        self.lbl_income_archived = QLabel("درآمد از آرشیو روزها: - تومان")
        self.lbl_income_total = QLabel("مجموع کل درآمد: - تومان")
        self.btn_refresh_income = QPushButton("↻ رفرش گزارش درآمد")

        for lbl in [self.lbl_income_today, self.lbl_income_archived, self.lbl_income_total]:
            lbl.setFont(QFont("Segoe UI", 9, QFont.Bold))

        income_layout.addWidget(self.lbl_income_today)
        income_layout.addWidget(self.lbl_income_archived)
        income_layout.addWidget(self.lbl_income_total)
        income_layout.addWidget(self.btn_refresh_income)
        income_layout.addStretch()

        layout.addWidget(income_box)

    # ================= تنظیمات ظرفیت / تعرفه =================
    def load_settings(self):
        try:
            cap = get_capacity()
        except Exception:
            cap = 200
        self.spin_capacity.setValue(cap)

        try:
            price = get_price_per_hour()
        except Exception:
            price = 20000
        self.spin_price.setValue(price)

    def save_capacity(self):
        new_cap = self.spin_capacity.value()
        set_capacity(new_cap)
        QMessageBox.information(self, "ظرفیت", "ظرفیت ذخیره شد.")
        self.refresh_capacity()

    def save_price(self):
        new_price = self.spin_price.value()
        set_price_per_hour(new_price)
        QMessageBox.information(self, "تعرفه", "تعرفه ذخیره شد.")

    # ================= رفرش داده‌ها =================
    def refresh_all(self):
        self.refresh_capacity()
        self.refresh_active()
        self.refresh_entries()
        self.refresh_exits()

    def refresh_capacity(self):
        try:
            capacity = get_capacity()
        except Exception:
            capacity = 0

        df_active = query("SELECT COUNT(*) AS c FROM active_cars")
        active = int(df_active["c"].iloc[0]) if not df_active.empty else 0
        free = max(0, capacity - active)

        self.lbl_capacity.setText(f"کل ظرفیت: {capacity}")
        self.lbl_active.setText(f"خودروهای داخل: {active}")
        self.lbl_free.setText(f"جای خالی: {free}")

    def refresh_active(self):
        df = query("""
            SELECT ac.entry_id, ac.plate, ac.timestamp_in, e.image_in
            FROM active_cars ac
            JOIN entries e ON ac.entry_id = e.id
        """)
        if not df.empty:
            df["region"] = df["plate"].apply(lambda p: get_plate_region(p) or "National")
        self.fill_table_active(df)

    def refresh_entries(self):
        df = query("SELECT * FROM entries ORDER BY id DESC LIMIT 100")
        if not df.empty:
            df["region"] = df["plate"].apply(lambda p: get_plate_region(p) or "National")
        self.fill_table_entries(df)

    def refresh_exits(self):
        df = query("SELECT * FROM exits ORDER BY id DESC LIMIT 100")
        if not df.empty:
            df["region"] = df["plate"].apply(lambda p: get_plate_region(p) or "National")
        self.fill_table_exits(df)

    # ================= آرشیو: لیست روزها =================
    def refresh_archive_days(self):
        self.cmb_days.clear()
        if not os.path.exists(ARCHIVE_ROOT):
            return
        days = [
            d for d in os.listdir(ARCHIVE_ROOT)
            if os.path.isdir(os.path.join(ARCHIVE_ROOT, d))
        ]
        days = sorted(days, reverse=True)
        self.cmb_days.addItems(days)

    def on_archive_day_changed(self, index: int):
        if index < 0:
            return
        day = self.cmb_days.currentText()
        if not day:
            return
        self.load_archive_day(day)

    def load_archive_day(self, day: str):
        day_dir = os.path.join(ARCHIVE_ROOT, day)
        entries_csv = os.path.join(day_dir, "entries.csv")
        exits_csv = os.path.join(day_dir, "exits.csv")

        if os.path.exists(entries_csv):
            entries_df = pd.read_csv(entries_csv)
        else:
            entries_df = pd.DataFrame()

        if os.path.exists(exits_csv):
            exits_df = pd.read_csv(exits_csv)
        else:
            exits_df = pd.DataFrame()

        self.fill_archive_entries_table(entries_df)
        self.fill_archive_exits_table(exits_df)
        self.update_archive_summary(entries_df, exits_df)

    def update_archive_summary(self, entries_df: pd.DataFrame, exits_df: pd.DataFrame):
        total_entries = len(entries_df)
        total_exits = len(exits_df)
        active_end = total_entries - total_exits

        if not exits_df.empty and "cost" in exits_df.columns:
            total_revenue = int(exits_df["cost"].sum())
            avg_duration = float(exits_df["duration_minutes"].mean())
        else:
            total_revenue = 0
            avg_duration = 0.0

        self.lbl_sum_entries.setText(f"ورودی‌ها: {total_entries}")
        self.lbl_sum_exits.setText(f"خروجی‌ها: {total_exits}")
        self.lbl_sum_active_end.setText(f"خودروهای باقی‌مانده در پایان روز: {active_end}")
        self.lbl_sum_revenue.setText(f"درآمد روز (تومان): {total_revenue}")
        self.lbl_sum_avg_duration.setText(f"میانگین مدت توقف (دقیقه): {avg_duration:.1f}")

    def fill_archive_entries_table(self, df: pd.DataFrame):
        self.table_archive_entries.setRowCount(0)
        if df.empty:
            return
        self.table_archive_entries.setRowCount(len(df))
        for r, (_, row) in enumerate(df.iterrows()):
            # id
            item_id = QTableWidgetItem(str(row.get("id", "")))
            item_id.setTextAlignment(Qt.AlignCenter)
            self.table_archive_entries.setItem(r, 0, item_id)
            # plate
            item_plate = QTableWidgetItem(str(row.get("plate", "")))
            item_plate.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table_archive_entries.setItem(r, 1, item_plate)
            # timestamp_in
            item_ts = QTableWidgetItem(str(row.get("timestamp_in", "")))
            item_ts.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table_archive_entries.setItem(r, 2, item_ts)
            # image_in
            item_img = QTableWidgetItem(str(row.get("image_in", "")))
            item_img.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table_archive_entries.setItem(r, 3, item_img)

    def fill_archive_exits_table(self, df: pd.DataFrame):
        self.table_archive_exits.setRowCount(0)
        if df.empty:
            return
        self.table_archive_exits.setRowCount(len(df))
        for r, (_, row) in enumerate(df.iterrows()):
            # id
            item_id = QTableWidgetItem(str(row.get("id", "")))
            item_id.setTextAlignment(Qt.AlignCenter)
            self.table_archive_exits.setItem(r, 0, item_id)
            # plate
            item_plate = QTableWidgetItem(str(row.get("plate", "")))
            item_plate.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table_archive_exits.setItem(r, 1, item_plate)
            # timestamp_out
            item_ts = QTableWidgetItem(str(row.get("timestamp_out", "")))
            item_ts.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table_archive_exits.setItem(r, 2, item_ts)
            # duration_minutes
            item_dur = QTableWidgetItem(str(row.get("duration_minutes", "")))
            item_dur.setTextAlignment(Qt.AlignCenter)
            self.table_archive_exits.setItem(r, 3, item_dur)
            # cost
            item_cost = QTableWidgetItem(str(row.get("cost", "")))
            item_cost.setTextAlignment(Qt.AlignCenter)
            self.table_archive_exits.setItem(r, 4, item_cost)
            # image_out
            item_img = QTableWidgetItem(str(row.get("image_out", "")))
            item_img.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table_archive_exits.setItem(r, 5, item_img)

    # ================= گزارش درآمد کلی =================
    def refresh_income_report(self):
        # درآمد امروز (دیتابیس فعلی)
        df_exits_today = query("SELECT cost, timestamp_out FROM exits")
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        if not df_exits_today.empty:
            df_today = df_exits_today[
                df_exits_today["timestamp_out"].astype(str).str.startswith(today_str)
            ]
            income_today = int(df_today["cost"].sum()) if not df_today.empty else 0
        else:
            income_today = 0

        # درآمد آرشیو (از تمام exits.csv ها)
        income_archived = 0
        if os.path.exists(ARCHIVE_ROOT):
            for d in os.listdir(ARCHIVE_ROOT):
                day_dir = os.path.join(ARCHIVE_ROOT, d)
                exits_csv = os.path.join(day_dir, "exits.csv")
                if os.path.exists(exits_csv):
                    try:
                        df = pd.read_csv(exits_csv)
                        if "cost" in df.columns and not df.empty:
                            income_archived += int(df["cost"].sum())
                    except Exception:
                        pass

        total = income_today + income_archived

        self.lbl_income_today.setText(f"درآمد امروز: {income_today} تومان")
        self.lbl_income_archived.setText(f"درآمد از آرشیو روزها: {income_archived} تومان")
        self.lbl_income_total.setText(f"مجموع کل درآمد: {total} تومان")

    # ================= PDF و Excel برای روز آرشیوشده =================
    def _get_selected_archive_day_dir(self):
        idx = self.cmb_days.currentIndex()
        if idx < 0:
            return None
        day = self.cmb_days.currentText()
        if not day:
            return None
        day_dir = os.path.join(ARCHIVE_ROOT, day)
        if not os.path.exists(day_dir):
            return None
        return day_dir

    def open_archive_pdf(self):
        day_dir = self._get_selected_archive_day_dir()
        if day_dir is None:
            QMessageBox.warning(self, "آرشیو", "هیچ روزی انتخاب نشده یا پوشه آرشیو وجود ندارد.")
            return

        pdf_path = os.path.join(day_dir, "summary.pdf")
        if not os.path.exists(pdf_path):
            QMessageBox.warning(self, "آرشیو", "فایل summary.pdf برای این روز یافت نشد.")
            return

        try:
            os.startfile(pdf_path)  # در ویندوز
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"امکان باز کردن فایل PDF نیست:\n{e}")

    def export_archive_excel(self):
        day_dir = self._get_selected_archive_day_dir()
        if day_dir is None:
            QMessageBox.warning(self, "آرشیو", "هیچ روزی انتخاب نشده یا پوشه آرشیو وجود ندارد.")
            return

        entries_csv = os.path.join(day_dir, "entries.csv")
        exits_csv = os.path.join(day_dir, "exits.csv")

        if not os.path.exists(entries_csv) and not os.path.exists(exits_csv):
            QMessageBox.warning(self, "آرشیو", "هیچ داده‌ای (entries/exits) برای این روز یافت نشد.")
            return

        try:
            entries_df = pd.read_csv(entries_csv) if os.path.exists(entries_csv) else pd.DataFrame()
            exits_df = pd.read_csv(exits_csv) if os.path.exists(exits_csv) else pd.DataFrame()

            excel_path = os.path.join(day_dir, "report.xlsx")
            with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
                if not entries_df.empty:
                    entries_df.to_excel(writer, sheet_name="entries", index=False)
                if not exits_df.empty:
                    exits_df.to_excel(writer, sheet_name="exits", index=False)

            try:
                os.startfile(excel_path)
            except Exception:
                QMessageBox.information(self, "خروجی اکسل", f"فایل اکسل ساخته شد:\n{excel_path}")

        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ساخت فایل اکسل:\n{e}")

    # ================= پر کردن جدول‌های اصلی (راست‌چین) =================
    def fill_table_active(self, df):
        self.table_active.setRowCount(0)
        if df.empty:
            return
        self.table_active.setRowCount(len(df))
        for r, (_, row) in enumerate(df.iterrows()):
            # entry_id
            item_id = QTableWidgetItem(str(row["entry_id"]))
            item_id.setTextAlignment(Qt.AlignCenter)
            self.table_active.setItem(r, 0, item_id)

            # plate
            item_plate = QTableWidgetItem(str(row["plate"]))
            item_plate.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table_active.setItem(r, 1, item_plate)

            # region
            item_region = QTableWidgetItem(str(row["region"]))
            item_region.setTextAlignment(Qt.AlignCenter)
            self.table_active.setItem(r, 2, item_region)

            # timestamp_in
            item_ts = QTableWidgetItem(str(row["timestamp_in"]))
            item_ts.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table_active.setItem(r, 3, item_ts)

            # image_in
            item_img = QTableWidgetItem(str(row["image_in"]))
            item_img.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table_active.setItem(r, 4, item_img)

    def fill_table_entries(self, df):
        self.table_entries.setRowCount(0)
        if df.empty:
            return
        self.table_entries.setRowCount(len(df))
        for r, (_, row) in enumerate(df.iterrows()):
            # id
            item_id = QTableWidgetItem(str(row["id"]))
            item_id.setTextAlignment(Qt.AlignCenter)
            self.table_entries.setItem(r, 0, item_id)

            # plate
            item_plate = QTableWidgetItem(str(row["plate"]))
            item_plate.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table_entries.setItem(r, 1, item_plate)

            # region
            item_region = QTableWidgetItem(str(row["region"]))
            item_region.setTextAlignment(Qt.AlignCenter)
            self.table_entries.setItem(r, 2, item_region)

            # timestamp_in
            item_ts = QTableWidgetItem(str(row["timestamp_in"]))
            item_ts.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table_entries.setItem(r, 3, item_ts)

            # image_in
            item_img = QTableWidgetItem(str(row["image_in"]))
            item_img.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table_entries.setItem(r, 4, item_img)

    def fill_table_exits(self, df):
        self.table_exits.setRowCount(0)
        if df.empty:
            return
        self.table_exits.setRowCount(len(df))
        for r, (_, row) in enumerate(df.iterrows()):
            # id
            item_id = QTableWidgetItem(str(row["id"]))
            item_id.setTextAlignment(Qt.AlignCenter)
            self.table_exits.setItem(r, 0, item_id)

            # plate
            item_plate = QTableWidgetItem(str(row["plate"]))
            item_plate.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table_exits.setItem(r, 1, item_plate)

            # region
            item_region = QTableWidgetItem(str(row["region"]))
            item_region.setTextAlignment(Qt.AlignCenter)
            self.table_exits.setItem(r, 2, item_region)

            # timestamp_out
            item_ts = QTableWidgetItem(str(row["timestamp_out"]))
            item_ts.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table_exits.setItem(r, 3, item_ts)

            # duration_minutes
            item_dur = QTableWidgetItem(str(row["duration_minutes"]))
            item_dur.setTextAlignment(Qt.AlignCenter)
            self.table_exits.setItem(r, 4, item_dur)

            # cost
            item_cost = QTableWidgetItem(str(row["cost"]))
            item_cost.setTextAlignment(Qt.AlignCenter)
            self.table_exits.setItem(r, 5, item_cost)

            # image_out
            item_img = QTableWidgetItem(str(row["image_out"]))
            item_img.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table_exits.setItem(r, 6, item_img)

    # ================= نمایش تصویر =================
    def _load_image_to_label(self, label: QLabel, path: str):
        if not os.path.exists(path):
            label.setText(f"تصویر یافت نشد:\n{path}")
            label.setPixmap(QPixmap())
            return

        pix = QPixmap(path)
        if pix.isNull():
            label.setText(f"امکان باز کردن تصویر نیست:\n{path}")
            label.setPixmap(QPixmap())
            return

        w = label.width() if label.width() > 0 else 400
        h = label.height() if label.height() > 0 else 300
        pix = pix.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(pix)
        label.setText("")

    def on_active_selected(self):
        sel = self.table_active.selectedItems()
        if not sel:
            return
        row = sel[0].row()
        img_item = self.table_active.item(row, 4)
        if img_item:
            self._load_image_to_label(self.lbl_active_img, img_item.text())

    def on_entry_selected(self):
        sel = self.table_entries.selectedItems()
        if not sel:
            return
        row = sel[0].row()
        img_item = self.table_entries.item(row, 4)
        if img_item:
            self._load_image_to_label(self.lbl_entry_img, img_item.text())

    def on_exit_selected(self):
        sel = self.table_exits.selectedItems()
        if not sel:
            return
        row = sel[0].row()
        img_item = self.table_exits.item(row, 6)
        if img_item:
            self._load_image_to_label(self.lbl_exit_img, img_item.text())

    # ================= دکمه‌های ریست / آرشیو =================
    def reset_day_archive(self):
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        last_reset = get_last_reset()

        if last_reset is None:
            set_last_reset(today_str)
            QMessageBox.information(self, "Reset Day", "اولین اجرای سیستم؛ تاریخ ریست ثبت شد.")
            return

        if last_reset != today_str:
            archive_day(last_reset)
            reset_database()
            set_last_reset(today_str)
            QMessageBox.information(
                self,
                "Reset Day",
                f"آرشیو روز {last_reset} ساخته شد و دیتابیس برای روز جدید ریست شد."
            )
        else:
            archive_day(today_str)
            reset_database()
            QMessageBox.information(
                self,
                "Reset Day",
                f"روز {today_str} آرشیو و دیتابیس خالی شد."
            )

        self.refresh_all()
        self.refresh_archive_days()
        self.refresh_income_report()

    def clear_db_only(self):
        ret = QMessageBox.question(
            self,
            "پاکسازی دیتابیس",
            "آیا مطمئن هستید؟ تمام اطلاعات (ورود/خروج/خودروهای فعال) حذف می‌شوند.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if ret == QMessageBox.Yes:
            reset_database()
            self.refresh_all()

    def full_reset_clicked(self):
        ret = QMessageBox.warning(
            self,
            "ریست کامل سیستم",
            "این کار تمام دیتابیس و همه آرشیوها را حذف می‌کند و همه‌چیز مثل روز اول می‌شود.\nادامه می‌دهید؟",
            QMessageBox.Yes | QMessageBox.No,
        )
        if ret == QMessageBox.Yes:
            full_reset_system()
            self.refresh_all()
            self.refresh_archive_days()
            self.refresh_income_report()


def main():
    # اگر دیتابیس نیست، بساز
    if not os.path.exists(DB_PATH):
        init_db()

    app = QApplication(sys.argv)

    # اگر فایل استایل (style.qss) داشتی اینجا لود می‌شود
    if os.path.exists("style.qss"):
        with open("style.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
