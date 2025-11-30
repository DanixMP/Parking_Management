"""
Standardized error response utilities for the API.

This module provides consistent error response formatting across all API endpoints.
All error responses follow the format:
{
    "success": false,
    "error": "Human-readable error message",
    "code": "ERROR_CODE",
    "details": {}  // Optional additional context
}
"""

from rest_framework.response import Response
from rest_framework import status


def error_response(error_message, error_code, status_code=status.HTTP_400_BAD_REQUEST, details=None):
    """
    Create a standardized error response.
    
    Args:
        error_message (str): Human-readable error message
        error_code (str): Machine-readable error code (e.g., 'INVALID_PHONE_FORMAT')
        status_code (int): HTTP status code (default: 400)
        details (dict): Optional additional error details
    
    Returns:
        Response: Django REST Framework Response object with error data
    """
    response_data = {
        'success': False,
        'error': error_message,
        'code': error_code
    }
    
    if details is not None:
        response_data['details'] = details
    
    return Response(response_data, status=status_code)


def bad_request_error(error_message, error_code='INVALID_REQUEST', details=None):
    """
    Create a 400 Bad Request error response.
    
    Args:
        error_message (str): Human-readable error message
        error_code (str): Machine-readable error code
        details (dict): Optional additional error details
    
    Returns:
        Response: 400 Bad Request response
    """
    return error_response(error_message, error_code, status.HTTP_400_BAD_REQUEST, details)


def unauthorized_error(error_message='Authentication required', error_code='AUTH_REQUIRED'):
    """
    Create a 401 Unauthorized error response.
    
    Args:
        error_message (str): Human-readable error message
        error_code (str): Machine-readable error code
    
    Returns:
        Response: 401 Unauthorized response
    """
    return error_response(error_message, error_code, status.HTTP_401_UNAUTHORIZED)


def forbidden_error(error_message='Insufficient permissions', error_code='FORBIDDEN'):
    """
    Create a 403 Forbidden error response.
    
    Args:
        error_message (str): Human-readable error message
        error_code (str): Machine-readable error code
    
    Returns:
        Response: 403 Forbidden response
    """
    return error_response(error_message, error_code, status.HTTP_403_FORBIDDEN)


def not_found_error(error_message, error_code='NOT_FOUND'):
    """
    Create a 404 Not Found error response.
    
    Args:
        error_message (str): Human-readable error message
        error_code (str): Machine-readable error code
    
    Returns:
        Response: 404 Not Found response
    """
    return error_response(error_message, error_code, status.HTTP_404_NOT_FOUND)


def conflict_error(error_message, error_code='CONFLICT'):
    """
    Create a 409 Conflict error response.
    
    Args:
        error_message (str): Human-readable error message
        error_code (str): Machine-readable error code
    
    Returns:
        Response: 409 Conflict response
    """
    return error_response(error_message, error_code, status.HTTP_409_CONFLICT)


def server_error(error_message='Internal server error', error_code='INTERNAL_ERROR'):
    """
    Create a 500 Internal Server Error response.
    
    Args:
        error_message (str): Human-readable error message
        error_code (str): Machine-readable error code
    
    Returns:
        Response: 500 Internal Server Error response
    """
    return error_response(error_message, error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


def service_unavailable_error(error_message='Service temporarily unavailable', error_code='SERVICE_UNAVAILABLE'):
    """
    Create a 503 Service Unavailable error response.
    
    Args:
        error_message (str): Human-readable error message
        error_code (str): Machine-readable error code
    
    Returns:
        Response: 503 Service Unavailable response
    """
    return error_response(error_message, error_code, status.HTTP_503_SERVICE_UNAVAILABLE)


def validation_error_response(serializer_errors):
    """
    Create a standardized error response from serializer validation errors.
    
    Args:
        serializer_errors (dict): Serializer errors from serializer.errors
    
    Returns:
        Response: 400 Bad Request response with validation details
    """
    return error_response(
        'Invalid request data',
        'INVALID_REQUEST',
        status.HTTP_400_BAD_REQUEST,
        details=serializer_errors
    )
