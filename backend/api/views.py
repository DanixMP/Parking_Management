from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.db import connection
import sys
import os

# Add src directory to path to import existing database functions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import database as db

from .models import Entry, Exit, ActiveCar, Setting
from .serializers import (
    EntrySerializer, ExitSerializer, ActiveCarSerializer,
    SettingSerializer, ParkingStatusSerializer,
    UserSerializer, WalletSerializer, LoginRequestSerializer,
    LoginResponseSerializer, WalletBalanceSerializer,
    ChargeWalletRequestSerializer, ChargeWalletResponseSerializer,
    TransactionListSerializer, TransactionSerializer,
    UserPlateSerializer, AddPlateRequestSerializer, PlateListSerializer
)
from .middleware import require_authentication, require_role


class EntryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing entry records"""
    queryset = Entry.objects.all().order_by('-timestamp_in')
    serializer_class = EntrySerializer


class ExitViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing exit records"""
    queryset = Exit.objects.all().order_by('-timestamp_out')
    serializer_class = ExitSerializer


class ActiveCarViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing currently parked cars"""
    queryset = ActiveCar.objects.all()
    serializer_class = ActiveCarSerializer


@api_view(['GET'])
def parking_status(request):
    """Get current parking status"""
    capacity = db.get_capacity()
    active = db.count_active_cars()
    free = db.get_free_slots()
    price = db.get_price_per_hour()
    
    data = {
        'capacity': capacity,
        'active_cars': active,
        'free_slots': free,
        'price_per_hour': price
    }
    
    serializer = ParkingStatusSerializer(data)
    return Response(serializer.data)


@api_view(['POST'])
def register_entry_api(request):
    """Register a new vehicle entry"""
    plate = request.data.get('plate')
    image_path = request.data.get('image_path', '')
    
    if not plate:
        return Response(
            {'error': 'Plate number is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if recently recorded
    if db.was_recently_recorded(plate):
        return Response(
            {'error': 'Vehicle was recently recorded'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    entry_id = db.register_entry(plate, image_path)
    
    return Response({
        'success': True,
        'entry_id': entry_id,
        'plate': plate
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def register_exit_api(request):
    """Register a vehicle exit"""
    plate = request.data.get('plate')
    image_path = request.data.get('image_path', '')
    
    if not plate:
        return Response(
            {'error': 'Plate number is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    result = db.register_exit(plate, image_path)
    
    if result is None:
        return Response(
            {'error': 'Vehicle not found in parking'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response({
        'success': True,
        **result
    })


@api_view(['GET', 'PUT'])
def settings_view(request):
    """Get or update parking settings"""
    if request.method == 'GET':
        capacity = db.get_capacity()
        price = db.get_price_per_hour()
        
        return Response({
            'capacity': capacity,
            'price_per_hour': price
        })
    
    elif request.method == 'PUT':
        capacity = request.data.get('capacity')
        price = request.data.get('price_per_hour')
        
        if capacity is not None:
            db.set_capacity(int(capacity))
        
        if price is not None:
            db.set_price_per_hour(int(price))
        
        return Response({
            'success': True,
            'capacity': db.get_capacity(),
            'price_per_hour': db.get_price_per_hour()
        })


@api_view(['POST'])
def reset_database_api(request):
    """Reset all parking data"""
    db.reset_database()
    from datetime import datetime
    db.set_last_reset(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    return Response({
        'success': True,
        'message': 'Database reset successfully'
    })



# YOLO Detection Endpoints
from rest_framework.parsers import MultiPartParser, FormParser
from .yolo_service import detect_plate_in_image


@api_view(['POST'])
def detect_plate(request):
    """
    Detect license plate from uploaded image
    
    POST /api/detect-plate/
    Content-Type: multipart/form-data
    Body: image file
    
    Returns: {
        "success": true,
        "plate": "12ب345-67",
        "confidence": 0.95,
        "bbox": {"x1": 100, "y1": 50, "x2": 300, "y2": 150}
    }
    """
    if 'image' not in request.FILES:
        return Response(
            {'error': 'No image file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    image_file = request.FILES['image']
    image_bytes = image_file.read()
    
    # Detect plate
    result = detect_plate_in_image(image_bytes)
    
    if not result['success']:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(result)


@api_view(['POST'])
def detect_and_register_entry(request):
    """
    Detect plate and automatically register entry
    
    POST /api/detect-entry/
    Content-Type: multipart/form-data
    Body: image file
    
    Returns: {
        "success": true,
        "plate": "12ب345-67",
        "entry_id": 123,
        "confidence": 0.95
    }
    """
    if 'image' not in request.FILES:
        return Response(
            {'error': 'No image file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    image_file = request.FILES['image']
    image_bytes = image_file.read()
    
    # Detect plate
    result = detect_plate_in_image(image_bytes)
    
    if not result['success']:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    plate = result['plate']
    
    # Check if recently recorded
    if db.was_recently_recorded(plate):
        return Response(
            {
                'success': False,
                'error': 'Vehicle was recently recorded',
                'plate': plate
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Register entry
    entry_id = db.register_entry(plate, f"auto_{image_file.name}")
    
    return Response({
        'success': True,
        'plate': plate,
        'entry_id': entry_id,
        'confidence': result['confidence']
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def detect_and_register_exit(request):
    """
    Detect plate and automatically register exit
    
    POST /api/detect-exit/
    Content-Type: multipart/form-data
    Body: image file
    
    Returns: {
        "success": true,
        "plate": "12ب345-67",
        "entry_id": 123,
        "duration": 120,
        "cost": 40000,
        "confidence": 0.95
    }
    """
    if 'image' not in request.FILES:
        return Response(
            {'error': 'No image file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    image_file = request.FILES['image']
    image_bytes = image_file.read()
    
    # Detect plate
    result = detect_plate_in_image(image_bytes)
    
    if not result['success']:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    plate = result['plate']
    
    # Register exit
    exit_result = db.register_exit(plate, f"auto_{image_file.name}")
    
    if exit_result is None:
        return Response(
            {
                'success': False,
                'error': 'Vehicle not found in parking',
                'plate': plate
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response({
        'success': True,
        'plate': plate,
        'confidence': result['confidence'],
        **exit_result
    })


# Authentication Endpoints

@api_view(['POST'])
def login(request):
    """
    User login endpoint.
    
    POST /api/auth/login/
    Request: { "phone_number": "09123456789" }
    Response: { "success": true, "token": "...", "user": {...}, "wallet": {...} }
    """
    serializer = LoginRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {
                'success': False,
                'error': 'Invalid request data',
                'code': 'INVALID_REQUEST',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    phone_number = serializer.validated_data['phone_number']
    
    # Validate phone number format
    if not db.validate_phone_number(phone_number):
        return Response(
            {
                'success': False,
                'error': 'Invalid phone number format',
                'code': 'INVALID_PHONE_FORMAT'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Get or create user
        user = db.get_or_create_user(phone_number)
        
        # Get wallet
        wallet = db.get_wallet_by_user_id(user['id'])
        
        # Create authentication token
        token = db.create_auth_token(user['id'])
        
        # Serialize response
        response_data = {
            'success': True,
            'token': token,
            'user': user,
            'wallet': wallet
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {
                'success': False,
                'error': str(e),
                'code': 'LOGIN_FAILED'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@require_authentication
def logout(request):
    """
    User logout endpoint.
    
    POST /api/auth/logout/
    Headers: Authorization: Token <token>
    Response: { "success": true }
    """
    try:
        # Delete the current token
        if hasattr(request, 'auth_token') and request.auth_token:
            db.delete_token(request.auth_token)
        
        return Response({
            'success': True,
            'message': 'Logged out successfully'
        })
    
    except Exception as e:
        return Response(
            {
                'success': False,
                'error': str(e),
                'code': 'LOGOUT_FAILED'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@require_authentication
def get_current_user(request):
    """
    Get current authenticated user information.
    
    GET /api/auth/me/
    Headers: Authorization: Token <token>
    Response: { "user": {...}, "wallet": {...} }
    """
    try:
        user = request.user_data
        wallet = db.get_wallet_by_user_id(user['id'])
        
        return Response({
            'success': True,
            'user': user,
            'wallet': wallet
        })
    
    except Exception as e:
        return Response(
            {
                'success': False,
                'error': str(e),
                'code': 'GET_USER_FAILED'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Wallet Endpoints

@api_view(['GET'])
@require_authentication
def get_wallet_balance(request):
    """
    Get current wallet balance for authenticated user.
    
    GET /api/wallet/balance/
    Headers: Authorization: Token <token>
    Response: { "balance": 500000, "last_updated": "..." }
    """
    try:
        user = request.user_data
        wallet = db.get_wallet_by_user_id(user['id'])
        
        if wallet is None:
            return Response(
                {
                    'success': False,
                    'error': 'Wallet not found for user',
                    'code': 'WALLET_NOT_FOUND'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = WalletBalanceSerializer({
            'balance': wallet['balance'],
            'last_updated': wallet['last_updated']
        })
        
        return Response(serializer.data)
    
    except Exception as e:
        return Response(
            {
                'success': False,
                'error': str(e),
                'code': 'GET_BALANCE_FAILED'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@require_authentication
def charge_wallet(request):
    """
    Charge (add funds to) the authenticated user's wallet.
    
    POST /api/wallet/charge/
    Headers: Authorization: Token <token>
    Request: { "amount": 100000 }
    Response: { "success": true, "new_balance": 600000, "transaction_id": 123 }
    """
    serializer = ChargeWalletRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {
                'success': False,
                'error': 'Invalid request data',
                'code': 'INVALID_REQUEST',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    amount = serializer.validated_data['amount']
    
    try:
        user = request.user_data
        result = db.charge_wallet(user['id'], amount)
        
        response_data = {
            'success': True,
            'new_balance': result['new_balance'],
            'transaction_id': result['transaction_id']
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except ValueError as e:
        return Response(
            {
                'success': False,
                'error': str(e),
                'code': 'INVALID_CHARGE_AMOUNT'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        return Response(
            {
                'success': False,
                'error': str(e),
                'code': 'CHARGE_FAILED'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@require_authentication
def get_transactions(request):
    """
    Get transaction history for authenticated user's wallet.
    
    GET /api/wallet/transactions/
    Headers: Authorization: Token <token>
    Query: ?limit=50&offset=0
    Response: { "count": 150, "results": [...] }
    """
    try:
        # Get pagination parameters
        limit = int(request.GET.get('limit', 50))
        offset = int(request.GET.get('offset', 0))
        
        # Validate parameters
        if limit < 1 or limit > 100:
            limit = 50
        if offset < 0:
            offset = 0
        
        user = request.user_data
        result = db.get_wallet_transactions(user['id'], limit=limit, offset=offset)
        
        serializer = TransactionListSerializer(result)
        
        return Response(serializer.data)
    
    except Exception as e:
        return Response(
            {
                'success': False,
                'error': str(e),
                'code': 'GET_TRANSACTIONS_FAILED'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Plate Management Endpoints

@api_view(['GET', 'POST'])
@require_authentication
def plates_api(request):
    """
    Handle plate operations for the authenticated user.
    
    GET /api/plates/
    Headers: Authorization: Token <token>
    Response: [{ "id": 1, "plate": "12ب345-67", "registered_at": "...", ... }, ...]
    
    POST /api/plates/
    Headers: Authorization: Token <token>
    Request: { "plate": "12ب345-67" }
    Response: { "id": 1, "plate": "12ب345-67", "registered_at": "...", ... }
    """
    if request.method == 'GET':
        try:
            user = request.user_data
            plates = db.get_user_plates(user['id'])
            
            # Serialize the plates
            serializer = UserPlateSerializer(plates, many=True)
            
            return Response(serializer.data)
        
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'error': str(e),
                    'code': 'GET_PLATES_FAILED'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    elif request.method == 'POST':
        serializer = AddPlateRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    'success': False,
                    'error': 'Invalid request data',
                    'code': 'INVALID_REQUEST',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        plate = serializer.validated_data['plate']
        
        try:
            user = request.user_data
            
            # Register the plate
            plate_id = db.register_user_plate(user['id'], plate)
            
            # Get the created plate
            plate_data = db.get_user_plate_by_id(plate_id)
            
            # Serialize response
            response_serializer = UserPlateSerializer(plate_data)
            
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        except ValueError as e:
            # Handle validation errors (invalid format or duplicate)
            error_msg = str(e)
            if 'Invalid license plate format' in error_msg:
                code = 'INVALID_PLATE_FORMAT'
            elif 'already registered' in error_msg:
                code = 'DUPLICATE_PLATE'
            else:
                code = 'INVALID_PLATE'
            
            return Response(
                {
                    'success': False,
                    'error': error_msg,
                    'code': code
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'error': str(e),
                    'code': 'ADD_PLATE_FAILED'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['DELETE'])
@require_authentication
def delete_plate_api(request, plate_id):
    """
    Delete a plate registered to the authenticated user.
    
    DELETE /api/plates/{id}/
    Headers: Authorization: Token <token>
    Response: { "success": true }
    """
    try:
        user = request.user_data
        
        # Delete the plate (with ownership verification)
        db.delete_user_plate(plate_id, user_id=user['id'])
        
        return Response({
            'success': True,
            'message': 'Plate deleted successfully'
        })
    
    except ValueError as e:
        error_msg = str(e)
        if 'not found' in error_msg:
            code = 'PLATE_NOT_FOUND'
            status_code = status.HTTP_404_NOT_FOUND
        elif 'does not belong' in error_msg:
            code = 'PLATE_UNAUTHORIZED'
            status_code = status.HTTP_403_FORBIDDEN
        else:
            code = 'INVALID_PLATE'
            status_code = status.HTTP_400_BAD_REQUEST
        
        return Response(
            {
                'success': False,
                'error': error_msg,
                'code': code
            },
            status=status_code
        )
    
    except Exception as e:
        return Response(
            {
                'success': False,
                'error': str(e),
                'code': 'DELETE_PLATE_FAILED'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Admin Endpoints

@api_view(['GET'])
@require_authentication
@require_role(['admin', 'superuser'])
def get_all_users_api(request):
    """
    Get all users in the system (Admin/SuperUser only).
    
    GET /api/admin/users/
    Headers: Authorization: Token <token> (Admin/SuperUser only)
    Query: ?limit=100&offset=0
    Response: { "count": 150, "results": [...] }
    """
    try:
        # Get pagination parameters
        limit = int(request.GET.get('limit', 100))
        offset = int(request.GET.get('offset', 0))
        
        # Validate parameters
        if limit < 1 or limit > 500:
            limit = 100
        if offset < 0:
            offset = 0
        
        result = db.get_all_users(limit=limit, offset=offset)
        
        return Response(result)
    
    except Exception as e:
        return Response(
            {
                'success': False,
                'error': str(e),
                'code': 'GET_USERS_FAILED'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
@require_authentication
@require_role(['superuser'])
def update_user_role_api(request, user_id):
    """
    Update a user's role (SuperUser only).
    
    PUT /api/admin/users/{id}/role/
    Headers: Authorization: Token <token> (SuperUser only)
    Request: { "role": "admin" }
    Response: { "success": true, "user": {...} }
    """
    try:
        new_role = request.data.get('role')
        
        if not new_role:
            return Response(
                {
                    'success': False,
                    'error': 'Role is required',
                    'code': 'ROLE_REQUIRED'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the role
        db.update_user_role(user_id, new_role)
        
        # Get updated user
        user = db.get_user_by_id(user_id)
        
        return Response({
            'success': True,
            'user': user
        })
    
    except ValueError as e:
        error_msg = str(e)
        if 'not found' in error_msg:
            code = 'USER_NOT_FOUND'
            status_code = status.HTTP_404_NOT_FOUND
        elif 'Invalid role' in error_msg:
            code = 'INVALID_ROLE'
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            code = 'INVALID_REQUEST'
            status_code = status.HTTP_400_BAD_REQUEST
        
        return Response(
            {
                'success': False,
                'error': error_msg,
                'code': code
            },
            status=status_code
        )
    
    except Exception as e:
        return Response(
            {
                'success': False,
                'error': str(e),
                'code': 'UPDATE_ROLE_FAILED'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
