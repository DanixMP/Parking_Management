# راهنمای یکپارچه‌سازی - Flutter + Django

## 🔗 اتصال Frontend به Backend

### مرحله 1: راه‌اندازی Backend (Django)

```bash
# ترمینال 1
cd backend
DjangoEnv\Scripts\activate
python manage.py runserver 8000
```

سرور Django باید روی `http://localhost:8000` در حال اجرا باشد.

### مرحله 2: راه‌اندازی Frontend (Flutter)

```bash
# ترمینال 2
cd frontend/parking
flutter pub get
flutter run
```

## ✅ تست اتصال

### 1. بررسی سرور Django
مرورگر را باز کنید: `http://localhost:8000/api/`

باید لیست endpoint‌ها را ببینید.

### 2. تست API با curl

```bash
# دریافت وضعیت
curl http://localhost:8000/api/status/

# ثبت ورود
curl -X POST http://localhost:8000/api/entry/ ^
  -H "Content-Type: application/json" ^
  -d "{\"plate\":\"12ب345-67\",\"image_path\":\"test.jpg\"}"
```

### 3. تست از Flutter
1. اپلیکیشن Flutter را باز کنید
2. اگر سرور روشن باشد، داده‌ها نمایش داده می‌شوند
3. اگر خطا دیدید، دکمه "تلاش مجدد" را بزنید

## 🔧 تنظیمات شبکه

### اجرا روی دستگاه واقعی (Android/iOS)

1. **IP کامپیوتر را پیدا کنید**:
```bash
ipconfig
# یا
ipconfig | findstr IPv4
```

2. **در Flutter تغییر دهید**:

فایل: `frontend/parking/lib/services/api_service.dart`
```dart
// قبل
static const String baseUrl = 'http://localhost:8000/api';

// بعد (با IP واقعی)
static const String baseUrl = 'http://192.168.1.100:8000/api';
```

3. **Django را برای شبکه محلی تنظیم کنید**:

فایل: `backend/parking_api/settings.py`
```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.1.100']

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://192.168.1.100:3000",
]
```

4. **سرور را با IP اجرا کنید**:
```bash
python manage.py runserver 0.0.0.0:8000
```

## 📊 جریان داده

```
Flutter App
    ↓ HTTP Request
Django API
    ↓ Query
SQLite Database (parking.db)
    ↓ Response
Django API
    ↓ JSON Response
Flutter App
    ↓ Update UI
User sees data
```

## 🎯 سناریوهای استفاده

### سناریو 1: ثبت ورود خودرو

**Flutter**:
```dart
await provider.registerEntry('12ب345-67', 'image.jpg');
```

**Django API**:
```python
POST /api/entry/
{
  "plate": "12ب345-67",
  "image_path": "image.jpg"
}
```

**Database**:
```sql
INSERT INTO entries (plate, image_in, timestamp_in)
VALUES ('12ب345-67', 'image.jpg', '2025-11-30 10:30:00');

INSERT INTO active_cars (entry_id, plate, timestamp_in)
VALUES (1, '12ب345-67', '2025-11-30 10:30:00');
```

### سناریو 2: ثبت خروج خودرو

**Flutter**:
```dart
final result = await provider.registerExit('12ب345-67', 'image.jpg');
// result: {duration: 120, cost: 40000, ...}
```

**Django API**:
```python
POST /api/exit/
{
  "plate": "12ب345-67",
  "image_path": "image.jpg"
}
```

**Database**:
```sql
-- محاسبه مدت و هزینه
-- ثبت در exits
INSERT INTO exits (entry_id, plate, image_out, timestamp_out, duration_minutes, cost)
VALUES (1, '12ب345-67', 'image.jpg', '2025-11-30 12:30:00', 120, 40000);

-- حذف از active_cars
DELETE FROM active_cars WHERE entry_id = 1;
```

## 🔄 به‌روزرسانی خودکار

برای به‌روزرسانی خودکار داده‌ها، می‌توانید از Timer استفاده کنید:

```dart
// در home_screen.dart
Timer? _refreshTimer;

@override
void initState() {
  super.initState();
  _loadData();
  
  // هر 30 ثانیه به‌روزرسانی
  _refreshTimer = Timer.periodic(
    const Duration(seconds: 30),
    (_) => _loadData(),
  );
}

@override
void dispose() {
  _refreshTimer?.cancel();
  super.dispose();
}
```

## 🐛 مشکلات رایج و راه‌حل

### 1. خطای "Connection refused"

**علت**: سرور Django روشن نیست

**راه‌حل**:
```bash
cd backend
start_django.bat
```

### 2. خطای CORS

**علت**: Flutter از origin مجاز نیست

**راه‌حل**: در `settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
    # آدرس Flutter خود را اضافه کنید
]
```

### 3. خطای 404

**علت**: endpoint اشتباه است

**راه‌حل**: endpoint‌ها را چک کنید:
- ✅ `/api/status/`
- ❌ `/status/`
- ❌ `/api/status`

### 4. داده‌ها null هستند

**علت**: دیتابیس خالی است

**راه‌حل**:
```bash
cd backend/src
python init_database.py
```

## 📱 تست کامل سیستم

### چک‌لیست تست

- [ ] سرور Django روشن است
- [ ] API در مرورگر کار می‌کند
- [ ] Flutter اپ اجرا می‌شود
- [ ] کارت‌های وضعیت داده نمایش می‌دهند
- [ ] ثبت ورود کار می‌کند
- [ ] ثبت خروج کار می‌کند
- [ ] تنظیمات قابل تغییر است
- [ ] جدول فعالیت‌ها نمایش داده می‌شود

### تست دستی

1. **ثبت ورود**:
   - دکمه "ثبت ورود خودرو" را بزنید
   - پلاک وارد کنید: `12ب345-67`
   - ثبت کنید
   - بررسی: "خودروهای داخل" باید +1 شود

2. **ثبت خروج**:
   - دکمه "ثبت خروج خودرو" را بزنید
   - همان پلاک را وارد کنید
   - بررسی: هزینه محاسبه شود

3. **تنظیمات**:
   - آیکون تنظیمات را بزنید
   - ظرفیت را تغییر دهید
   - بررسی: کارت "کل ظرفیت" به‌روز شود

## 🚀 آماده‌سازی برای Production

### Backend (Django)

1. **تنظیمات امنیتی**:
```python
DEBUG = False
SECRET_KEY = 'your-secret-key-here'
ALLOWED_HOSTS = ['yourdomain.com']
```

2. **استفاده از PostgreSQL** (به جای SQLite)

3. **راه‌اندازی با Gunicorn**:
```bash
pip install gunicorn
gunicorn parking_api.wsgi:application
```

### Frontend (Flutter)

1. **Build برای Windows**:
```bash
flutter build windows --release
```

2. **Build برای Web**:
```bash
flutter build web --release
```

3. **Build برای Android**:
```bash
flutter build apk --release
```

## 📚 منابع بیشتر

- [Django REST Framework](https://www.django-rest-framework.org/)
- [Flutter HTTP Package](https://pub.dev/packages/http)
- [Provider State Management](https://pub.dev/packages/provider)

---

**نکته**: این راهنما برای محیط Development است. برای Production تنظیمات امنیتی بیشتری نیاز است.
