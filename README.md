# 🚗 Parking Management System

A comprehensive parking management system with automatic license plate recognition, built with Django REST API backend and Flutter frontend.

## ✨ Features

- 🎯 **Real-time Dashboard** - Monitor capacity, active vehicles, and availability
- 🚘 **Automatic Plate Detection** - YOLO-based license plate recognition
- 💰 **Cost Calculation** - Automatic parking fee calculation
- 📊 **Activity Tracking** - Complete entry/exit history
- ⚙️ **Settings Management** - Configure capacity and pricing
- 🌐 **Cross-platform** - Windows Desktop and Web support
- 🇮🇷 **Persian Support** - Full RTL and Persian language support

## 🏗️ Architecture

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Flutter   │◄───────►│   Django    │◄───────►│   SQLite    │
│   Frontend  │  HTTP   │  REST API   │         │  Database   │
└─────────────┘  JSON   └─────────────┘         └─────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Flutter SDK
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Parking
```

2. **Start the complete system**
```bash
start_full_system.bat
```

That's it! The system will start both backend and frontend automatically.

### Manual Start

**Backend:**
```bash
cd backend
start_django.bat
```

**Frontend:**
```bash
cd frontend/parking
flutter run -d windows
```

## 📁 Project Structure

```
Parking/
├── backend/              # Django REST API
│   ├── api/             # API endpoints
│   ├── parking_api/     # Django project
│   ├── src/             # Core logic & YOLO models
│   └── DjangoEnv/       # Virtual environment
├── frontend/            # Flutter application
│   └── parking/         # Flutter project
├── Documents/           # Documentation
└── start_full_system.bat # Quick launcher
```

## 🔌 API Endpoints

### Standard Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/status/` | Get parking status |
| GET | `/api/entries/` | List all entries |
| GET | `/api/exits/` | List all exits |
| GET | `/api/active-cars/` | List parked vehicles |
| POST | `/api/entry/` | Register entry |
| POST | `/api/exit/` | Register exit |
| GET/PUT | `/api/settings/` | Get/Update settings |
| POST | `/api/reset/` | Reset database |

### YOLO Detection Endpoints ✨
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/detect-plate/` | Detect plate from image |
| POST | `/api/detect-entry/` | Detect & register entry |
| POST | `/api/detect-exit/` | Detect & register exit |

## 🛠️ Technology Stack

### Backend
- Django 5.2.8
- Django REST Framework 3.16.1
- SQLite Database
- YOLO (License Plate Detection)
- OpenCV (Image Processing)

### Frontend
- Flutter (Cross-platform)
- Provider (State Management)
- Material Design 3
- HTTP Client

## 📱 Screenshots

### Dashboard
- Real-time capacity monitoring
- Active vehicles count
- Free slots display
- Pricing information

### Features
- Manual entry/exit registration
- Automatic cost calculation
- Activity history
- Settings configuration

## 📚 Documentation

Comprehensive documentation available in the `Documents/` folder:

### Core Documentation
- **[START_HERE.md](START_HERE.md)** - Start here for quick setup
- **[API_DOCUMENTATION.md](Documents/API_DOCUMENTATION.md)** - Complete API reference
- **[DJANGO_README.md](Documents/DJANGO_README.md)** - Django setup guide
- **[FLUTTER_INTEGRATION_GUIDE.md](Documents/FLUTTER_INTEGRATION_GUIDE.md)** - Flutter integration
- **[SYSTEM_OVERVIEW.md](Documents/SYSTEM_OVERVIEW.md)** - Complete system overview
- **[QUICK_START.md](Documents/QUICK_START.md)** - Quick reference

### YOLO Integration Documentation
- **[YOLO_INTEGRATION_COMPLETE.md](YOLO_INTEGRATION_COMPLETE.md)** - YOLO integration summary
- **[backend/YOLO_TEST_GUIDE.md](backend/YOLO_TEST_GUIDE.md)** - Complete testing guide
- **[backend/QUICK_TEST.md](backend/QUICK_TEST.md)** - Quick YOLO reference
- **[YOLO_SETUP_SUMMARY.md](YOLO_SETUP_SUMMARY.md)** - Setup details

## 🧪 Testing

### Test the API
```bash
cd backend
DjangoEnv\Scripts\activate
python test_api.py
```

### Test YOLO Integration
```bash
# Quick test
TEST_YOLO_NOW.bat

# Detailed integration test
cd backend
python test_yolo_integration.py

# Test with image
python test_api_with_image.py path\to\plate_image.jpg
```

### Manual API Test
```bash
# Test status
curl http://localhost:8000/api/status/

# Test plate detection
curl -X POST http://localhost:8000/api/detect-plate/ -F "image=@plate.jpg"
```

## 🔧 Configuration

### Backend Configuration
Edit `backend/parking_api/settings.py`:
- Database path
- CORS origins
- API settings

### Frontend Configuration
Edit `frontend/parking/lib/services/api_service.dart`:
- API base URL
- Timeout settings

## 🌐 Supported Platforms

- ✅ Windows Desktop
- ✅ Web Browser
- 📱 Android (ready to build)
- 📱 iOS (ready to build)

## 📈 Features & Enhancements

### ✅ Completed
- [x] YOLO license plate detection
- [x] Automatic plate recognition API
- [x] Image-based entry/exit registration
- [x] Real-time parking status
- [x] Cost calculation
- [x] Persian/RTL support

### 🔜 Future Enhancements
- [ ] Camera integration for live detection
- [ ] Reports and analytics
- [ ] User authentication
- [ ] Reservation system
- [ ] Payment integration
- [ ] SMS notifications
- [ ] Receipt printing

## 🐛 Troubleshooting

### Backend not starting?
```bash
cd backend
DjangoEnv\Scripts\activate
python manage.py runserver 8000
```

### Frontend connection error?
Make sure Django backend is running on port 8000

### CORS errors?
Add your frontend URL to `CORS_ALLOWED_ORIGINS` in Django settings

## 📝 License

This project is private and proprietary.

## 👥 Contributors

Development Team

## 📞 Support

For issues or questions, check the documentation in the `Documents/` folder.

---

**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Last Updated**: November 30, 2025

## 🎯 Getting Started Checklist

- [ ] Install Python 3.11+
- [ ] Install Flutter SDK
- [ ] Clone repository
- [ ] Run `start_full_system.bat`
- [ ] Access dashboard at http://localhost:8000
- [ ] Test entry/exit registration
- [ ] Configure settings
- [ ] Review documentation

## 🔗 Quick Links

- Backend API: http://localhost:8000/api/
- Django Admin: http://localhost:8000/admin/
- API Documentation: [Documents/API_DOCUMENTATION.md](Documents/API_DOCUMENTATION.md)
- System Overview: [Documents/SYSTEM_OVERVIEW.md](Documents/SYSTEM_OVERVIEW.md)

---

Made with ❤️ for efficient parking management
