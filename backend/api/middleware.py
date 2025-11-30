"""
Authentication middleware for token-based authentication.
"""
import sys
import os

# Add src directory to path to import database functions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import database as db

from .error_responses import unauthorized_error, forbidden_error


class TokenAuthenticationMiddleware:
    """
    Middleware to validate authentication tokens and attach user to request.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Extract token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Token '):
            token = auth_header[6:]  # Remove 'Token ' prefix
            
            # Validate token
            user_id = db.validate_token(token)
            
            if user_id is not None:
                # Attach user to request
                user = db.get_user_by_id(user_id)
                request.user_data = user
                request.user_id = user_id
                request.auth_token = token
            else:
                request.user_data = None
                request.user_id = None
                request.auth_token = None
        else:
            request.user_data = None
            request.user_id = None
            request.auth_token = None
        
        response = self.get_response(request)
        return response


def require_authentication(view_func):
    """
    Decorator to require authentication for a view.
    Returns 401 if not authenticated.
    """
    from functools import wraps
    
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'user_id') or request.user_id is None:
            return unauthorized_error()
        return view_func(request, *args, **kwargs)
    
    return wrapper


def require_role(required_roles):
    """
    Decorator to require specific role(s) for a view.
    Returns 403 if user doesn't have required role.
    
    Usage:
        @require_role(['admin', 'superuser'])
        def my_view(request):
            ...
    """
    from functools import wraps
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, 'user_data') or request.user_data is None:
                return unauthorized_error()
            
            user_role = request.user_data.get('role')
            if user_role not in required_roles:
                return forbidden_error()
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    
    return decorator
