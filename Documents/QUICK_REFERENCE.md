# Quick Reference Card

## 🚀 Start Backend (Recommended)
```bash
cd backend
python run_backend.py
```

## 🎯 Master Launcher
```bash
start_parking_system.bat
```
Choose option 1 for backend venv.

## 🧪 Quick Tests

### Test Models
```bash
C:\Users\Danix\anaconda3\Scripts\conda.exe run -p backend/venv python backend/src/yolo_loader.py
```

### Initialize Database
```bash
C:\Users\Danix\anaconda3\Scripts\conda.exe run -p backend/venv python backend/src/init_database.py
```

### Run Examples
```bash
cd backend
C:\Users\Danix\anaconda3\Scripts\conda.exe run -p venv python src/example_detection.py
```

## 🎮 Detection Scripts

### Entry Camera
```bash
C:\Users\Danix\anaconda3\Scripts\conda.exe run -p backend/venv python backend/src/detect_entry.py
```

### Exit Camera
```bash
C:\Users\Danix\anaconda3\Scripts\conda.exe run -p backend/venv python backend/src/detect_exit.py
```

## 🔧 Environment Management

### Activate venv
```bash
backend\activate_venv.bat
```

### Install Package
```bash
C:\Users\Danix\anaconda3\Scripts\conda.exe run -p backend/venv pip install package_name
```

### Update Dependencies
```bash
C:\Users\Danix\anaconda3\Scripts\conda.exe run -p backend/venv pip install -r backend/src/requirements-clean.txt --upgrade
```

## 📁 Key Locations

- **Backend venv:** `backend/venv/`
- **Source code:** `backend/src/`
- **Models:** `backend/src/*.pt`
- **Database:** `backend/src/parking.db`

## 📚 Documentation

- **README.md** - Overview
- **STARTUP_GUIDE.md** - How to start
- **VENV_GUIDE.md** - Virtual environment
- **FINAL_SETUP_SUMMARY.md** - Complete summary

## ✅ Status

| Item | Status |
|------|--------|
| Python 3.10.19 | ✅ Ready |
| Backend venv | ✅ Ready |
| YOLO Models | ✅ Ready |
| Database | ✅ Ready |
| GUI | ✅ Ready |
| Detection | ✅ Ready |

## 🎯 Next Steps

1. Start: `cd backend && python run_backend.py`
2. Connect cameras
3. Test detection
4. Monitor system

---

**Quick Start:** `cd backend && python run_backend.py`
