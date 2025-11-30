# Backend Virtual Environment Guide

## Overview

A dedicated Python 3.10.19 virtual environment has been created in `backend/venv/` for the parking management system backend.

## Environment Details

- **Location:** `backend/venv/`
- **Python Version:** 3.10.19
- **Package Manager:** pip
- **Created with:** Conda

## Quick Start

### Option 1: Run Backend Server (Recommended)

```bash
cd backend
python run_backend.py
```

Or use the batch file:
```bash
backend\start_backend.bat
```

### Option 2: Activate Environment Manually

```bash
# Activate the environment
backend\activate_venv.bat

# Now you can run any Python command
python --version
python backend/src/yolo_loader.py
python backend/src/init_database.py
```

### Option 3: Use Conda Directly

```bash
# Run command in venv
C:\Users\Danix\anaconda3\Scripts\conda.exe run -p backend/venv python run_backend.py

# Or activate and use
C:\Users\Danix\anaconda3\Scripts\conda.exe activate backend/venv
python run_backend.py
```

## Available Commands

### Test YOLO Models
```bash
cd backend
C:\Users\Danix\anaconda3\Scripts\conda.exe run -p venv python src/yolo_loader.py
```

### Initialize Database
```bash
cd backend
C:\Users\Danix\anaconda3\Scripts\conda.exe run -p venv python src/init_database.py
```

### Run Detection Examples
```bash
cd backend
C:\Users\Danix\anaconda3\Scripts\conda.exe run -p venv python src/example_detection.py
```

### Run Entry Detection
```bash
cd backend
C:\Users\Danix\anaconda3\Scripts\conda.exe run -p venv python src/detect_entry.py
```

### Run Exit Detection
```bash
cd backend
C:\Users\Danix\anaconda3\Scripts\conda.exe run -p venv python src/detect_exit.py
```

## Environment Structure

```
backend/
├── venv/                      # Virtual environment
│   ├── Scripts/               # Executables (python.exe, pip.exe, etc.)
│   ├── Lib/                   # Python packages
│   └── pyvenv.cfg             # Configuration
├── src/                       # Source code
│   ├── plateYolo.pt           # Plate detection model
│   ├── CharsYolo.pt           # Character detection model
│   ├── yolo_loader.py         # Model loading
│   ├── database.py            # Database operations
│   ├── gui_qt.py              # PyQt5 GUI
│   ├── detect_entry.py        # Entry detection
│   ├── detect_exit.py         # Exit detection
│   └── ...
├── run_backend.py             # Backend server runner
├── start_backend.bat          # Windows launcher
├── activate_venv.bat          # Environment activation
└── VENV_GUIDE.md              # This file
```

## Installing Additional Packages

If you need to install additional packages:

```bash
# Using conda
C:\Users\Danix\anaconda3\Scripts\conda.exe run -p backend/venv pip install package_name

# Or activate first
backend\activate_venv.bat
pip install package_name
```

## Updating Dependencies

To update all dependencies:

```bash
cd backend
C:\Users\Danix\anaconda3\Scripts\conda.exe run -p venv pip install -r src/requirements-clean.txt --upgrade
```

## Troubleshooting

### Issue: "Python not found"
**Solution:** Make sure you're using the correct path to conda
```bash
C:\Users\Danix\anaconda3\Scripts\conda.exe run -p backend/venv python --version
```

### Issue: "Module not found"
**Solution:** Reinstall dependencies
```bash
C:\Users\Danix\anaconda3\Scripts\conda.exe run -p backend/venv pip install -r backend/src/requirements-clean.txt
```

### Issue: "Models not loading"
**Solution:** Test with yolo_loader.py
```bash
C:\Users\Danix\anaconda3\Scripts\conda.exe run -p backend/venv python backend/src/yolo_loader.py
```

### Issue: "Database error"
**Solution:** Initialize database
```bash
C:\Users\Danix\anaconda3\Scripts\conda.exe run -p backend/venv python backend/src/init_database.py
```

## Performance

- **Startup Time:** ~2-3 seconds
- **Model Loading:** ~5-10 seconds
- **Inference:** ~100-500ms per frame (CPU)

## Advantages of This Setup

1. **Isolated Environment** - Doesn't affect system Python
2. **Easy Management** - All dependencies in one place
3. **Reproducible** - Same environment on any machine
4. **Clean** - Easy to remove (just delete `backend/venv/`)
5. **Portable** - Can be moved or shared

## Switching Between Environments

### Use Backend venv (Recommended)
```bash
C:\Users\Danix\anaconda3\Scripts\conda.exe run -p backend/venv python script.py
```

### Use Main parking environment
```bash
C:\Users\Danix\anaconda3\Scripts\conda.exe run -n parking python script.py
```

## Size and Storage

- **venv Size:** ~2-3 GB (includes all packages)
- **Storage Location:** `backend/venv/`
- **Can be deleted:** Yes, but will need to be recreated

## Backup and Sharing

### Create a backup
```bash
# Freeze requirements
C:\Users\Danix\anaconda3\Scripts\conda.exe run -p backend/venv pip freeze > backend/requirements-frozen.txt
```

### Recreate environment
```bash
# Create new venv
C:\Users\Danix\anaconda3\Scripts\conda.exe create -p backend/venv python=3.10.19 -y

# Install from frozen requirements
C:\Users\Danix\anaconda3\Scripts\conda.exe run -p backend/venv pip install -r backend/requirements-frozen.txt
```

## Next Steps

1. **Start the backend:**
   ```bash
   cd backend
   python run_backend.py
   ```

2. **Or activate and explore:**
   ```bash
   backend\activate_venv.bat
   python src/yolo_loader.py
   ```

3. **Connect cameras and test detection**

4. **Monitor the system**

## Support

For issues:
1. Check this guide
2. Review error messages
3. Test with `yolo_loader.py`
4. Check database with `init_database.py`

---

**Status:** ✅ Backend venv ready to use!

Start with: `cd backend && python run_backend.py`
