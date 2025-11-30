import cv2
import torch
import time
from collections import deque, Counter
import os
import math
from datetime import datetime
import re

from database import (
    register_exit,
    count_active_cars,
    get_capacity,
    get_free_slots,
)

# Patch for cv2 thread compatibility
if not hasattr(cv2, "setNumThreads"):
    cv2.setNumThreads = lambda x: None


##########################################
# Load Models
##########################################

def load_plate_model(device="cpu"):
    model = torch.hub.load(
        "./yolov5",
        "custom",
        path="model/plateYolo.pt",
        source="local"
    )
    model.to(device)
    model.eval()
    return model


def load_char_model(device="cpu"):
    model = torch.hub.load(
        "./yolov5",
        "custom",
        path="model/CharsYolo.pt",
        source="local"
    )
    model.to(device)
    model.eval()
    return model


##########################################
# Plate OCR Utils (ملی + مناطق آزاد)
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

def decode_plate(img, model):
    results = model(img)
    det = results.xyxy[0].cpu().numpy()
    det = [d for d in det if d[4] > 0.5]
    if not det:
        return ""
    det.sort(key=lambda x: x[0])
    names = model.names
    chars = [normalize(names[int(cls)]) for *_, cls in det]
    return format_plate("".join(chars))


##########################################
# Tracking Utilities
##########################################

def dist(a, b):
    return math.dist(a, b)

def assign_id(center, trackers, max_dist=80):
    for tid, tdata in trackers.items():
        if dist(center, tdata["center"]) < max_dist:
            return tid
    return None


##########################################
# EXIT CAMERA MAIN
##########################################

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("EXIT CAMERA ACTIVE")
    print("Using device:", device)

    save_dir = "captures/exit"
    os.makedirs(save_dir, exist_ok=True)

    plate_model = load_plate_model(device)
    char_model = load_char_model(device)

    # CAMERA INDEX FOR EXIT CAMERA
    cap = cv2.VideoCapture(0)  # اگر یک دوربین داری برای تست موقتاً 0 کن
    # یا RTSP:
    # cap = cv2.VideoCapture("rtsp://...")

    if not cap.isOpened():
        print("Exit camera error")
        return

    trackers = {}
    nextID = 1

    BUFFER_SIZE = 20
    MIN_VOTES = 15
    REMOVE_TIME = 1.0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        tnow = time.time()
        h, w = frame.shape[:2]

        results = plate_model(frame)
        dets = results.xyxy[0].cpu().numpy()

        for *xyxy, conf, cls in dets:
            if conf < 0.5:
                continue

            x1, y1, x2, y2 = map(int, xyxy)
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            # tracking ID
            tid = assign_id((cx, cy), trackers)
            if tid is None:
                tid = nextID
                trackers[tid] = {
                    "center": (cx, cy),
                    "buffer": deque(maxlen=BUFFER_SIZE),
                    "confirmed": "",
                    "last_seen": tnow,
                    "bbox": (x1, y1, x2, y2)
                }
                nextID += 1

            trackers[tid]["center"] = (cx, cy)
            trackers[tid]["last_seen"] = tnow
            trackers[tid]["bbox"] = (x1, y1, x2, y2)

            # crop + resize
            pad = 2
            x1p = max(0, x1 - pad)
            y1p = max(0, y1 - pad)
            x2p = min(w, x2 + pad)
            y2p = min(h, y2 + pad)
            crop = frame[y1p:y2p, x1p:x2p]

            if crop.size == 0:
                continue

            crop = cv2.resize(crop, (320, 80))
            text = decode_plate(crop, char_model)

            if text and 6 <= len(clean(text)) <= 9:
                trackers[tid]["buffer"].append(text)

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(frame, f"ID {tid}: {text}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Voting
        for tid, data in list(trackers.items()):
            if tnow - data["last_seen"] > REMOVE_TIME:
                del trackers[tid]
                continue

            buf = data["buffer"]
            if len(buf) < MIN_VOTES:
                continue

            best, count = Counter(buf).most_common(1)[0]

            if best == data["confirmed"]:
                continue

            if count >= MIN_VOTES:
                final_plate = best
                data["confirmed"] = final_plate

                print("EXIT CONFIRMED:", final_plate)

                # save full frame with bbox
                car_img = frame.copy()
                x1, y1, x2, y2 = data["bbox"]
                cv2.rectangle(car_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

                filename = f"{final_plate}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                img_path = os.path.join(save_dir, filename)
                cv2.imwrite(img_path, car_img)

                # register exit
                info = register_exit(final_plate, img_path)

                if info is None:
                    print("⚠ EXIT BLOCKED - Car was not inside:", final_plate)
                else:
                    print(
                        f"EXIT OK | plate={final_plate} | "
                        f"duration={info['duration']} min | cost={info['cost']}"
                    )

                buf.clear()

                print(f"Cars inside={count_active_cars()} | Free={get_free_slots()}/{get_capacity()}")

        cv2.imshow("EXIT CAMERA", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()