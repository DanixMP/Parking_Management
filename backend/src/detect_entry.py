import cv2
import torch
import time
import os
import math
import re
from collections import deque, Counter
from datetime import datetime

from database import (
    init_db,
    register_entry,
    was_recently_recorded,
    count_active_cars,
    get_capacity,
    get_free_slots,
)

# Patch for cv2 thread compatibility (مشکل ultralytics با بعضی نسخه‌های OpenCV)
if not hasattr(cv2, "setNumThreads"):
    cv2.setNumThreads = lambda x: None


##########################################
# مدل‌ها
##########################################

def load_plate_model(device="cpu"):
    model = torch.hub.load(
        "./yolov5",
        "custom",
        path="model/plateYolo.pt",
        source="local",
    )
    model.to(device)
    model.eval()
    return model


def load_char_model(device="cpu"):
    model = torch.hub.load(
        "./yolov5",
        "custom",
        path="model/CharsYolo.pt",
        source="local",
    )
    model.to(device)
    model.eval()
    return model


##########################################
# توابع OCR (پلاک ملی + مناطق آزاد)
##########################################

def normalize(ch):
    if ch == "ه\u200d":
        ch = "ه"
    if ch.startswith("ژ"):
        ch = "ژ"
    return ch

def clean(txt):
    return re.sub(r"[^0-9آ-ی]", "", txt)

def format_plate(txt):
    s = clean(txt)

    # 1) پلاک ملی
    m1 = re.match(r"^(\d{2})([آ-ی])(\d{3})(\d{2})$", s)
    if m1:
        a, b, c, d = m1.groups()
        return f"{a} {b} {c} {d}"

    # 2) پلاک منطقه آزاد (۵+۲)
    m2 = re.match(r"^(\d{5})(\d{2})$", s)
    if m2:
        serial, region = m2.groups()
        return f"{serial} {region}"

    return s



def decode_plate(img, model, conf_thres=0.5) -> str:
    """خروجی YOLO کاراکتر → رشته‌ی کامل پلاک (با فرمت مناسب)"""
    results = model(img)
    det = results.xyxy[0].cpu().numpy()
    if len(det) == 0:
        return ""

    # فقط دتکشن‌های با کانفیدنس کافی
    det = [d for d in det if d[4] >= conf_thres]
    if not det:
        return ""

    # مرتب‌سازی براساس x1 (چپ به راست)
    det.sort(key=lambda x: x[0])
    names = model.names
    chars = [normalize(names[int(cls)]) for *_, cls in det]

    raw_text = "".join(chars)
    formatted = format_plate(raw_text)
    return formatted


##########################################
# Track by Plate — Voting
##########################################

def dist(a, b):
    return math.dist(a, b)


def assign_id(center, trackers, max_dist=80):
    """اگر پلاک نزدیک ID موجود باشد → همان ID، وگرنه None"""
    for tid, data in trackers.items():
        if dist(center, data["center"]) < max_dist:
            return tid
    return None


##########################################
# MAIN: ENTRY CAMERA
##########################################

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("ENTRY CAMERA ACTIVE")
    print("Using device:", device)

    # اطمینان از آماده بودن دیتابیس و تنظیمات
    init_db()

    # پوشه‌ی ذخیره عکس ورود
    save_dir = os.path.join("captures", "entry")
    os.makedirs(save_dir, exist_ok=True)

    # مدل‌ها
    plate_model = load_plate_model(device)
    char_model = load_char_model(device)

    # دوربین ورودی (در صورت نیاز اندیس را عوض کن)
    cap = cv2.VideoCapture(0)
    # اگر RTSP داری:
    # cap = cv2.VideoCapture("rtsp://...")

    if not cap.isOpened():
        print("Camera error (entry)")
        return

    trackers = {}  # tid → {center, buffer, confirmed, last_seen, bbox}
    next_id = 1

    BUFFER_SIZE = 20   # حداکثر تعداد پیش‌بینی برای هر ID
    MIN_VOTES = 15     # حداقل تعداد تکرار یک پلاک برای تایید
    REMOVE_TIME = 1.0  # ثانیه – اگر این زمان دیده نشد → حذف Track

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        tnow = time.time()
        h, w = frame.shape[:2]
        # تشخیص پلاک‌ها
        plate_results = plate_model(frame)
        dets = plate_results.xyxy[0].cpu().numpy()

        for *xyxy, conf, cls in dets:
            if conf < 0.5:
                continue

            x1, y1, x2, y2 = map(int, xyxy)
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            # تخصیص ID
            tid = assign_id((cx, cy), trackers)
            if tid is None:
                tid = next_id
                trackers[tid] = {
                    "center": (cx, cy),
                    "buffer": deque(maxlen=BUFFER_SIZE),
                    "confirmed": "",
                    "last_seen": tnow,
                    "bbox": (x1, y1, x2, y2),
                }
                next_id += 1

            trackers[tid]["center"] = (cx, cy)
            trackers[tid]["last_seen"] = tnow
            trackers[tid]["bbox"] = (x1, y1, x2, y2)

            # کراپ پلاک با کمی حاشیه
            pad = 2
            x1p = max(0, x1 - pad)
            y1p = max(0, y1 - pad)
            x2p = min(w - 1, x2 + pad)
            y2p = min(h - 1, y2 + pad)

            plate_img = frame[y1p:y2p, x1p:x2p]
            if plate_img.size == 0:
                continue

            plate_img_resized = cv2.resize(plate_img, (320, 80))
            text = decode_plate(plate_img_resized, char_model, conf_thres=0.5)

            # فیلتر رشته‌های خیلی کوتاه/عجیب
            if text and 6 <= len(clean(text)) <= 9:
                trackers[tid]["buffer"].append(text)

            # نمایش روی فریم (برای Debug)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"ID {tid}: {text}",
                (x1, max(0, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

        # رأی‌گیری روی هر Track
        for tid, data in list(trackers.items()):
            # اگر مدتی دیده نشده، حذف
            if tnow - data["last_seen"] > REMOVE_TIME:
                del trackers[tid]
                continue

            buf = data["buffer"]
            if len(buf) < MIN_VOTES:
                continue

            best, count = Counter(buf).most_common(1)[0]

            # اگر همین پلاک قبلاً برای این Track تایید شده، نیاز نیست دوباره
            if best == data["confirmed"]:
                continue

            if count >= MIN_VOTES:
                final_plate = best

                # جلوگیری از ثبت دوباره در X دقیقه اخیر
                if was_recently_recorded(final_plate, minutes=5):
                    print("ENTRY REJECTED (recent duplicate):", final_plate)
                    data["confirmed"] = final_plate
                    buf.clear()
                    continue

                data["confirmed"] = final_plate
                print("ENTRY CONFIRMED:", final_plate)

                # ذخیره عکس «کل ماشین» (کل فریم) با باکس دور پلاک
                car_img = frame.copy()
                x1, y1, x2, y2 = data.get("bbox", (0, 0, 0, 0))
                cv2.rectangle(car_img, (x1, y1), (x2, y2), (0, 255, 0), 2)

                filename = f"{final_plate}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                img_path = os.path.join(save_dir, filename)
                cv2.imwrite(img_path, car_img)

                # ثبت در دیتابیس (ورود)
                entry_id = register_entry(final_plate, img_path)

                free = get_free_slots()
                active = count_active_cars()
                cap_val = get_capacity()
                print(
                    f"Entry ID={entry_id} | Plate={final_plate} | Active={active} | Free={free}/{cap_val}"
                )

                # پاک کردن بافر این Track
                buf.clear()

        cv2.imshow("ENTRY CAMERA", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()