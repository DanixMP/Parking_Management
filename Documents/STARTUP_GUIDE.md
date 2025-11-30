# Parking Management System - Startup Guide

## ✅ Everything is Ready!

Your backend is fully set up and ready to run.

## Quick Start

### Option 1: Run with Python (Recommended)
```bash
python run_server.py
```

### Option 2: Run with Batch File (Windows)
```bash
start_server.bat
```

### Option 3: Run with Conda Directly
```bash
C:\Users\Danix\anaconda3\Scripts\conda.exe run -n parking python run_server.py
```

## What Happens When You Start

1. ✅ Conda environment `parking` is activated
2. ✅ Database is initialized (if needed)
3. ✅ YOLO models are loaded
4. ✅ PyQt5 GUI application starts

## First Time Setup

If this is your first time running:

```bash
# 1. Initialize database
python backend/src/init_database.py

# 2. Test YOLO models
python backend/src/yolo_loader.py

# 3. Run the server
python run_server.py
```

## Database

The database is automatically initialized with:
- **Capacity:** 200 cars
- **Price per hour:** 20,000 (currency units)
- **Tables:** entries, exits, active_cars, settings

To manually initialize:
```bash
python backend/src/init_database.py
```

## YOLO Models

Both models are automatically loaded when the system starts:
- **plateYolo.pt** - License plate detection
- **CharsYolo.pt** - Character detection

To test models separately:
```bash
python backend/src/yolo_loader.py
```

## Detection Scripts

Run detection independently:

**Entry Camera:**
```bash
cd backend/src
python detect_entry.py
```

**Exit Camera:**
```bash
cd backend/src
python detect_exit.py
```

## Troubleshooting

### Issue: "Database error"
**Solution:** Initialize database
```bash
python backend/src/init_database.py
```

### Issue: "Models not found"
**Solution:** Check models exist
```bash
ls backend/src/*.pt
```

### Issue: "Camera not working"
**Solution:** Check camera index in detect_entry.py or detect_exit.py
```python
cap = cv2.VideoCapture(0)  # Change 0 to 1, 2, etc. if needed
```

### Issue: "GUI doesn't appear"
**Solution:** GUI runs in background. Check console for errors.

### Issue: "Slow performance"
**Solution:** Normal on CPU. For GPU:
1. Install NVIDIA CUDA
2. Install GPU-compatible PyTorch
3. Models will auto-detect GPU

## File Structure

```
.
├── run_server.py              # Main server runner
├── start_server.bat           # Windows launcher
├── STARTUP_GUIDE.md           # This file
├── YOLO_QUICK_START.md        # YOLO reference
├── YOLO_SETUP_GUIDE.md        # Detailed YOLO guide
└── backend/
    └── src/
        ├── plateYolo.pt       # Plate detection model
        ├── CharsYolo.pt       # Character detection model
        ├── yolo_loader.py     # Model loading
        ├── init_database.py   # Database initialization
        ├── database.py        # Database operations
        ├── gui_qt.py          # PyQt5 GUI
        ├── detect_entry.py    # Entry detection
        ├── detect_exit.py     # Exit detection
        └── ...
```

## Environment Info

- **Python:** 3.10.19
- **PyTorch:** 2.4.0
- **OpenCV:** 4.9.0
- **Database:** SQLite (parking.db)
- **GUI:** PyQt5

## Next Steps

1. **Start the system**
   ```bash
   python run_server.py
   ```

2. **Test with cameras**
   - Connect entry camera
   - Connect exit camera
   - Run detection scripts

3. **Monitor database**
   - Check entries/exits
   - View active cars
   - Adjust settings

4. **Deploy**
   - Set up production cameras
   - Configure database backup
   - Deploy to server

## Support

- **YOLO Models:** See `YOLO_QUICK_START.md`
- **Database:** See `backend/src/database.py`
- **GUI:** See `backend/src/gui_qt.py`
- **Detection:** See `backend/src/detect_entry.py` and `detect_exit.py`

## Performance

- **CPU Mode:** ~100-500ms per frame
- **GPU Mode:** ~10-50ms per frame
- **Database:** SQLite (suitable for small-medium deployments)

## Security Notes

- Database is local SQLite (not suitable for multi-user production)
- Consider migrating to PostgreSQL for production
- Add authentication for API access
- Encrypt sensitive data

---

**Status:** ✅ Ready to run!

Start with: `python run_server.py`

