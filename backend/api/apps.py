from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    
    def ready(self):
        """Initialize app - preload YOLO models"""
        # Only preload in production, not during migrations
        import sys
        if 'runserver' in sys.argv or 'gunicorn' in sys.argv[0]:
            try:
                print("\n" + "="*60)
                print("Preloading YOLO models...")
                print("="*60)
                from .yolo_service import preload_models
                preload_models()
                print("="*60)
                print("✓ YOLO models ready")
                print("="*60 + "\n")
            except Exception as e:
                print(f"⚠ Warning: Could not preload models: {e}")
                print("Models will be loaded on first request")
