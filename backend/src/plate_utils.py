import re

FREE_ZONE_REGIONS = {
    "22": "KISH",
    "33": "ARVAND",
    "44": "MAKU",
    "55": "ARAS",
    "77": "CHABAHAR",
}

def get_plate_region(plate_str: str):
    """
    منطقه پلاک فقط وقتی تشخیص داده می‌شود که:
      - پلاک از نوع مناطق آزاد باشد (فقط عدد)
      - ساختار ۵ رقم + ۲ رقم باشد
    پلاک ملی که وسطش حرف دارد، هرگز منطقه آزاد نیست.
    """
    # فقط رقم‌ها را بگیر
    digits = re.sub(r"\D", "", plate_str)

    # اگر طولش دقیقاً 7 نیست → پلاک مناطق آزاد نیست
    if len(digits) != 7:
        return None

    # اگر پلاک ملی بود (حرف فارسی در متن اصلی)
    if re.search(r"[آ-ی]", plate_str):
        return None

    # ساختار 5 رقم + 2 رقم
    m = re.match(r"^(\d{5})(\d{2})$", digits)
    if not m:
        return None

    serial, region_code = m.groups()
    return FREE_ZONE_REGIONS.get(region_code)