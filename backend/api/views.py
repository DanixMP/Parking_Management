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
    SettingSerializer, ParkingStatusSerializer
)


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
