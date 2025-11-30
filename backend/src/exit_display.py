import sys
import os
import sqlite3
from dataclasses import dataclass
from typing import Optional

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtGui import QPixmap, QFont, QFontDatabase
from PyQt5.QtCore import Qt, QTimer


DB_PATH = "parking.db"


@dataclass
class ExitInfo:
    exit_id: int
    plate: str
    timestamp_in: Optional[str]
    image_in: Optional[str]
    timestamp_out: Optional[str]
    image_out: Optional[str]
    duration_minutes: int
    cost: int


def get_last_exit() -> Optional[ExitInfo]:
    if not os.path.exists(DB_PATH):
        return None

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT 
                x.id,
                e.plate,
                e.timestamp_in,
                e.image_in,
                x.timestamp_out,
                x.image_out,
                x.duration_minutes,
                x.cost
            FROM exits x
            JOIN entries e ON x.entry_id = e.id
            ORDER BY x.id DESC LIMIT 1
        """)
        row = cur.fetchone()
        if not row:
            return None

        return ExitInfo(
            exit_id=row[0],
            plate=row[1],
            timestamp_in=row[2],
            image_in=row[3],
            timestamp_out=row[4],
            image_out=row[5],
            duration_minutes=row[6],
            cost=row[7],
        )
    finally:
        conn.close()


def format_time(ts):
    if not ts:
        return "-", "-"
    parts = str(ts).split()
    if len(parts) == 1:
        return parts[0], "-"
    return parts[0], parts[1]


def format_duration(m):
    if m is None:
        return "-"
    if m <= 0:
        return "کمتر از یک دقیقه"
    h = m // 60
    mm = m % 60
    if h and mm:
        return f"{h} ساعت و {mm} دقیقه"
    if h:
        return f"{h} ساعت"
    return f"{mm} دقیقه"


def format_cost(c):
    if c is None:
        return "-"
    return f"{c:,} تومان"


class ExitDisplay(QWidget):
    def __init__(self):
        super().__init__()

        self.last_exit_id = None

        # ---- فونت وزیر را لود کن ----
        font_family = "Vazirmatn"
        if os.path.exists("Vazirmatn-Regular.ttf"):
            fid = QFontDatabase.addApplicationFont("Vazirmatn-Regular.ttf")
            families = QFontDatabase.applicationFontFamilies(fid)
            if families:
                font_family = families[0]

        self.setWindowTitle("نمایش اطلاعات خروج خودرو")
        self.setLayoutDirection(Qt.RightToLeft)
        self.setStyleSheet("background-color: #FFFFFF;")

        self.font_title = QFont(font_family, 24, QFont.Bold)
        self.font_label = QFont(font_family, 18)
        self.font_plate = QFont(font_family, 40, QFont.Bold)

        # ===== عنوان اصلی =====
        self.lbl_title = QLabel("در انتظار خروج خودرو...")
        self.lbl_title.setFont(self.font_title)
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setStyleSheet("color: #333; margin: 12px;")
        self.base_title_style = "color: #333; margin: 12px;"

        # ===== عنوان عکس‌ها =====
        self.lbl_in_title = QLabel("عکس ورود")
        self.lbl_in_title.setFont(self.font_label)
        self.lbl_in_title.setAlignment(Qt.AlignCenter)

        self.lbl_out_title = QLabel("عکس خروج")
        self.lbl_out_title.setFont(self.font_label)
        self.lbl_out_title.setAlignment(Qt.AlignCenter)

        # ===== عکس‌ها (بزرگ‌تر از قبل) =====
        self.lbl_img_in = QLabel()
        self.lbl_img_in.setMinimumSize(640, 400)  # بزرگ‌تر
        self.lbl_img_in.setAlignment(Qt.AlignCenter)
        self.lbl_img_in.setStyleSheet(
            "border: 1px solid #AAAAAA; background-color: #F3F3F3;"
        )

        self.lbl_img_out = QLabel()
        self.lbl_img_out.setMinimumSize(640, 400)  # بزرگ‌تر
        self.lbl_img_out.setAlignment(Qt.AlignCenter)
        self.lbl_img_out.setStyleSheet(
            "border: 1px solid #AAAAAA; background-color: #F3F3F3;"
        )

        in_layout = QVBoxLayout()
        in_layout.addWidget(self.lbl_in_title)
        in_layout.addWidget(self.lbl_img_in)

        out_layout = QVBoxLayout()
        out_layout.addWidget(self.lbl_out_title)
        out_layout.addWidget(self.lbl_img_out)

        img_layout = QHBoxLayout()
        img_layout.addLayout(in_layout)
        img_layout.addLayout(out_layout)

        # ===== متن‌ها =====
        self.lbl_plate = QLabel("پلاک: -")
        self.lbl_plate.setFont(self.font_plate)
        self.lbl_plate.setAlignment(Qt.AlignCenter)
        self.lbl_plate.setLayoutDirection(Qt.LeftToRight)

        self.lbl_time_in = QLabel("تاریخ ورود: -\nساعت: -")
        self.lbl_time_in.setFont(self.font_label)
        self.lbl_time_in.setAlignment(Qt.AlignCenter)

        self.lbl_time_out = QLabel("تاریخ خروج: -\nساعت: -")
        self.lbl_time_out.setFont(self.font_label)
        self.lbl_time_out.setAlignment(Qt.AlignCenter)

        self.lbl_duration = QLabel("مدت توقف: -")
        self.lbl_duration.setFont(self.font_label)
        self.lbl_duration.setAlignment(Qt.AlignCenter)

        self.lbl_cost = QLabel("هزینه نهایی: -")
        self.lbl_cost.setFont(self.font_label)
        self.lbl_cost.setAlignment(Qt.AlignCenter)

        # ===== چیدمان نهایی =====
        main = QVBoxLayout()
        main.addWidget(self.lbl_title)
        main.addLayout(img_layout)
        main.addWidget(self.lbl_plate)
        main.addWidget(self.lbl_time_in)
        main.addWidget(self.lbl_time_out)
        main.addWidget(self.lbl_duration)
        main.addWidget(self.lbl_cost)

        self.setLayout(main)
        self.resize(1500, 950)  # کمی هم پنجره بزرگ‌تر

        # تایمر چک دیتابیس
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_update)
        self.timer.start(1000)

    def check_update(self):
        info = get_last_exit()
        if not info:
            return

        if self.last_exit_id == info.exit_id:
            return

        self.last_exit_id = info.exit_id
        self.show_info(info)

    def show_info(self, info: ExitInfo):
        # انیمیشن کوچک سبز روی عنوان
        self.lbl_title.setText("خروج خودرو ثبت شد")
        self.lbl_title.setStyleSheet(
            "background-color: #4CAF50; color: white; margin: 12px; "
            "padding: 6px; border-radius: 8px;"
        )
        QTimer.singleShot(700, lambda: self.lbl_title.setStyleSheet(self.base_title_style))

        # پلاک
        self.lbl_plate.setText(f"پلاک:   {info.plate}")
        self.lbl_plate.setLayoutDirection(Qt.LeftToRight)

        # زمان‌ها
        d_in, t_in = format_time(info.timestamp_in)
        d_out, t_out = format_time(info.timestamp_out)

        self.lbl_time_in.setText(f"تاریخ ورود: {d_in}\nساعت: {t_in}")
        self.lbl_time_out.setText(f"تاریخ خروج: {d_out}\nساعت: {t_out}")

        # مدت و هزینه
        self.lbl_duration.setText(f"مدت توقف: {format_duration(info.duration_minutes)}")
        self.lbl_cost.setText(f"هزینه نهایی: {format_cost(info.cost)}")

        # تصاویر
        self.load_image(self.lbl_img_in, info.image_in)
        self.load_image(self.lbl_img_out, info.image_out)

    def load_image(self, label: QLabel, path: Optional[str]):
        if not path or not isinstance(path, str) or not os.path.exists(path):
            label.setText("تصویر موجود نیست")
            label.setPixmap(QPixmap())
            return

        pix = QPixmap(path)
        if pix.isNull():
            label.setText("خطا در بارگذاری تصویر")
            label.setPixmap(QPixmap())
            return

        w = label.width() if label.width() > 0 else 640
        h = label.height() if label.height() > 0 else 400
        pix = pix.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(pix)
        label.setText("")


def main():
    app = QApplication(sys.argv)
    window = ExitDisplay()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
