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
    
    # Authentication endpoints
    path('auth/login/', views.login, name='auth-login'),
    path('auth/logout/', views.logout, name='auth-logout'),
    path('auth/me/', views.get_current_user, name='auth-me'),
    
    # Wallet endpoints
    path('wallet/balance/', views.get_wallet_balance, name='wallet-balance'),
    path('wallet/charge/', views.charge_wallet, name='wallet-charge'),
    path('wallet/transactions/', views.get_transactions, name='wallet-transactions'),
    
    # Plate management endpoints
    path('plates/', views.plates_api, name='plates'),
    path('plates/<int:plate_id>/', views.delete_plate_api, name='delete-plate'),
    
    # Admin endpoints
    path('admin/users/', views.get_all_users_api, name='admin-get-users'),
    path('admin/users/<int:user_id>/role/', views.update_user_role_api, name='admin-update-role'),
]
