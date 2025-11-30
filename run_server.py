#!/usr/bin/env python
"""
Parking Management System - Backend Server Runner
This script initializes and runs the parking management system backend.
"""

import sys
import os
import argparse
from pathlib import Path

# Add backend/src to Python path
backend_src = Path(__file__).parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

# Change to backend/src directory for relative imports
os.chdir(backend_src)


def run_gui():
    """Run the PyQt5 GUI application"""
    try:
        # Initialize database first
        print("=" * 60)
        print("Parking Management System - Backend")
        print("=" * 60)
        print("Initializing database...")
        
        from database import init_db
        init_db()
        print("✓ Database ready")
        print()
        
        print("Starting GUI application...")
        print()
        
        from gui_qt import QApplication, MainWindow
        
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        
        sys.exit(app.exec_())
        
    except ImportError as e:
        print(f"Error: Failed to import required modules: {e}")
        print("Make sure all dependencies are installed:")
        print("  conda run -n parking pip install -r backend/src/requirements-clean.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to start application: {e}")
        sys.exit(1)


def run_api():
    """Run as REST API server (placeholder for future implementation)"""
    print("=" * 60)
    print("Parking Management System - API Server")
    print("=" * 60)
    print("API server mode not yet implemented.")
    print("Please use GUI mode for now.")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Parking Management System Backend Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_server.py              # Run GUI (default)
  python run_server.py --gui        # Run GUI explicitly
  python run_server.py --api        # Run API server (future)
  python run_server.py --help       # Show this help message
        """
    )
    
    parser.add_argument(
        "--gui",
        action="store_true",
        default=True,
        help="Run GUI application (default)"
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="Run REST API server (experimental)"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="Parking Management System v1.0.0"
    )
    
    args = parser.parse_args()
    
    # Check if backend/src exists
    if not backend_src.exists():
        print(f"Error: Backend source directory not found: {backend_src}")
        sys.exit(1)
    
    # Check if database module exists
    if not (backend_src / "database.py").exists():
        print(f"Error: Required module 'database.py' not found in {backend_src}")
        sys.exit(1)
    
    try:
        if args.api:
            run_api()
        else:
            run_gui()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
