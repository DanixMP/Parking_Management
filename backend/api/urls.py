from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'entries', views.EntryViewSet)
router.register(r'exits', views.ExitViewSet)
router.register(r'active-cars', views.ActiveCarViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('status/', views.parking_status, name='parking-status'),
    path('entry/', views.register_entry_api, name='register-entry'),
    path('exit/', views.register_exit_api, name='register-exit'),
    path('settings/', views.settings_view, name='settings'),
    path('reset/', views.reset_database_api, name='reset-database'),
    
    # YOLO Detection endpoints
    path('detect-plate/', views.detect_plate, name='detect-plate'),
    path('detect-entry/', views.detect_and_register_entry, name='detect-entry'),
    path('detect-exit/', views.detect_and_register_exit, name='detect-exit'),
]
