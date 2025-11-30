# 📋 کارت مرجع سریع - Quick Reference Card

## 🚀 شروع سریع / Quick Start

```bash
# روش آسان / Easy Way
START_SYSTEM.bat

# یا / Or manually:
# Terminal 1:
cd backend && DjangoEnv\Scripts\activate && python manage.py runserver 8000

# Terminal 2:
cd frontend/parking && flutter run -d windows
```

---

## 🔗 آدرس‌ها / URLs

| سرویس | آدرس | توضیحات |
|-------|------|---------|
| Django API | `http://localhost:8000/api/` | Backend API |
| Django Admin | `http://localhost:8000/admin/` | Admin Panel |
| Flutter App | Auto-opens | Desktop App |

---

## 📡 API Endpoints

### دریافت اطلاعات / GET Requests
```bash
# وضعیت پارکینگ
curl http://localhost:8000/api/status/

# خودروهای داخل
curl http://localhost:8000/api/active-cars/

# تنظیمات
curl http://localhost:8000/api/settings/
```

### ثبت اطلاعات / POST Requests
```bash
# ثبت ورود
curl -X POST http://localhost:8000/api/entry/ ^
  -H "Content-Type: application/json" ^
  -d "{\"plate\":\"12ب345-67\",\"image_path\":\"test.jpg\"}"

# ثبت خروج
curl -X POST http://localhost:8000/api/exit/ ^
  -H "Content-Type: application/json" ^
  -d "{\"plate\":\"12ب345-67\",\"image_path\":\"test.jpg\"}"
```

---

## 🛠️ دستورات مفید / Useful Commands

### Backend
```bash
# شروع سرور
python manage.py runserver 8000

# تست API
python test_api.py

# ایجاد superuser
python manage.py createsuperuser

# بررسی مشکلات
python manage.py check
```

### Frontend
```bash
# نصب dependencies
flutter pub get

# اجرا
flutter run

# اجرا روی Windows
flutter run -d windows

# Build
flutter build windows --release
```

### Database
```bash
# مشاهده دیتابیس
sqlite3 backend/src/parking.db

# دستورات SQLite
.tables                    # لیست جداول
SELECT * FROM entries;     # مشاهده ورودی‌ها
SELECT * FROM active_cars; # خودروهای داخل
.quit                      # خروج
```

---

## 📁 فایل‌های مهم / Important Files

| فایل | مسیر | کاربرد |
|------|------|--------|
| Django Settings | `backend/parking_api/settings.py` | تنظیمات Backend |
| API Views | `backend/api/views.py` | منطق API |
| API Service | `frontend/parking/lib/services/api_service.dart` | سرویس API |
| Home Screen | `frontend/parking/lib/screens/home_screen.dart` | صفحه اصلی |
| Database | `backend/src/parking.db` | دیتابیس |

---

## 🐛 عیب‌یابی سریع / Quick Troubleshooting

### مشکل: Backend روشن نمی‌شود
```bash
conda deactivate
cd backend
DjangoEnv\Scripts\activate
python manage.py runserver 8000
```

### مشکل: Frontend متصل نمی‌شود
1. بررسی: `http://localhost:8000/api/`
2. دکمه Refresh در اپ را بزنید
3. سرور Django را restart کنید

### مشکل: خطای CORS
```python
# backend/parking_api/settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
    # آدرس خود را اضافه کنید
]
```

### مشکل: دیتابیس خالی
```bash
cd backend/src
python init_database.py
```

---

## 🎨 رنگ‌های UI / UI Colors

```dart
Background:     #0F1C2E  // آبی تیره
Primary Card:   #1E3A5F  // آبی
Success:        #2E7D32  // سبز
Info:           #1976D2  // آبی روشن
Error:          #D32F2F  // قرمز
Purple:         #7B1FA2  // بنفش
```

---

## 📊 ساختار دیتابیس / Database Schema

```sql
-- جدول ورودی‌ها
entries (id, plate, image_in, timestamp_in)

-- جدول خروجی‌ها
exits (id, entry_id, plate, image_out, timestamp_out, duration_minutes, cost)

-- خودروهای داخل
active_cars (entry_id, plate, timestamp_in)

-- تنظیمات
settings (key, value)
```

---

## 🔑 متغیرهای مهم / Key Variables

### Backend
```python
DB_PATH = "parking.db"
DEFAULT_CAPACITY = 200
DEFAULT_PRICE_PER_HOUR = 20000
```

### Frontend
```dart
baseUrl = 'http://localhost:8000/api'
```

---

## 📞 دستورات اضطراری / Emergency Commands

### ریست کامل سیستم
```bash
# از طریق API
curl -X POST http://localhost:8000/api/reset/

# یا از طریق Flutter App
# دکمه "ریست کامل سیستم" را بزنید
```

### Backup دیتابیس
```bash
copy backend\src\parking.db backup\parking_backup_%date%.db
```

### پاک کردن Cache
```bash
# Flutter
cd frontend/parking
flutter clean
flutter pub get

# Django
cd backend
python manage.py clearsessions
```

---

## 📚 مستندات / Documentation

| سند | مسیر |
|-----|------|
| راهنمای کامل | `Documents/COMPLETE_SYSTEM_GUIDE.md` |
| API | `Documents/API_DOCUMENTATION.md` |
| Flutter | `Documents/FLUTTER_APP_GUIDE.md` |
| Django | `Documents/DJANGO_README.md` |
| یکپارچه‌سازی | `Documents/INTEGRATION_GUIDE.md` |

---

## ⚡ میانبرها / Shortcuts

```bash
# شروع سریع Backend
cd backend && start_django.bat

# شروع سریع همه چیز
START_SYSTEM.bat

# تست سریع API
cd backend && python test_api.py

# Build سریع Flutter
cd frontend/parking && flutter build windows --release
```

---

## 🎯 نکات مهم / Important Notes

✅ همیشه Backend را قبل از Frontend روشن کنید  
✅ پورت 8000 باید آزاد باشد  
✅ برای دستگاه واقعی از IP استفاده کنید  
✅ در Production از HTTPS استفاده کنید  
✅ دیتابیس را backup بگیرید  

---

## 📱 پلتفرم‌های پشتیبانی شده / Supported Platforms

- ✅ Windows Desktop
- ✅ Web Browser
- ✅ Android
- ✅ iOS (با macOS)
- ✅ Linux Desktop

---

## 🔢 اعداد مهم / Important Numbers

| مورد | مقدار |
|------|-------|
| پورت Backend | 8000 |
| ظرفیت پیش‌فرض | 200 |
| تعرفه پیش‌فرض | 20000 تومان/ساعت |
| Timeout API | 30 ثانیه |

---

**نسخه**: 1.0.0  
**تاریخ**: 30 نوامبر 2025  
**وضعیت**: ✅ آماده استفاده
