# API Error Handling Guide

This document describes the standardized error handling and response formatting used throughout the API.

## Error Response Format

All error responses follow a consistent JSON structure:

```json
{
    "success": false,
    "error": "Human-readable error message",
    "code": "ERROR_CODE",
    "details": {}  // Optional additional context
}
```

### Fields

- **success** (boolean): Always `false` for error responses
- **error** (string): Human-readable error message describing what went wrong
- **code** (string): Machine-readable error code for programmatic handling
- **details** (object, optional): Additional context about the error (e.g., validation errors)

## HTTP Status Codes

The API uses standard HTTP status codes to indicate the type of error:

### 4xx Client Errors

- **400 Bad Request**: Invalid request data, validation errors
- **401 Unauthorized**: Authentication required or invalid token
- **403 Forbidden**: Insufficient permissions for the requested resource
- **404 Not Found**: Requested resource does not exist
- **409 Conflict**: Request conflicts with current state (e.g., duplicate resource)

### 5xx Server Errors

- **500 Internal Server Error**: Unexpected server error
- **503 Service Unavailable**: Service temporarily unavailable (e.g., database connection failure)

## Common Error Codes

### Authentication Errors

- `AUTH_REQUIRED`: Authentication token is missing or invalid
- `INVALID_TOKEN`: Token is malformed or expired
- `LOGIN_FAILED`: Login attempt failed

### Authorization Errors

- `INSUFFICIENT_PERMISSIONS`: User lacks required permissions
- `FORBIDDEN`: Access to resource is forbidden

### Validation Errors

- `INVALID_REQUEST`: Request data is invalid or malformed
- `INVALID_PHONE_FORMAT`: Phone number format is invalid
- `INVALID_PLATE_FORMAT`: License plate format is invalid
- `INVALID_CHARGE_AMOUNT`: Wallet charge amount is invalid
- `INVALID_ROLE`: User role is invalid

### Resource Errors

- `NOT_FOUND`: Requested resource not found
- `USER_NOT_FOUND`: User not found
- `WALLET_NOT_FOUND`: Wallet not found
- `PLATE_NOT_FOUND`: Plate not found

### Business Logic Errors

- `INSUFFICIENT_BALANCE`: Wallet balance is insufficient
- `DUPLICATE_PLATE`: Plate already registered
- `PLATE_UNAUTHORIZED`: Attempting to modify another user's plate

### System Errors

- `INTERNAL_ERROR`: Unexpected internal server error
- `SERVICE_UNAVAILABLE`: Service temporarily unavailable
- `DATABASE_ERROR`: Database operation failed

## Usage Examples

### Using Error Response Utilities

The `error_responses.py` module provides utility functions for creating standardized error responses:

```python
from .error_responses import (
    bad_request_error,
    unauthorized_error,
    forbidden_error,
    not_found_error,
    server_error,
    validation_error_response
)

# Bad request error
if not plate:
    return bad_request_error('Plate number is required', 'PLATE_REQUIRED')

# Unauthorized error
if not token:
    return unauthorized_error()

# Forbidden error
if user_role != 'admin':
    return forbidden_error('Admin access required', 'ADMIN_REQUIRED')

# Not found error
if not user:
    return not_found_error('User not found', 'USER_NOT_FOUND')

# Validation error from serializer
if not serializer.is_valid():
    return validation_error_response(serializer.errors)

# Server error
try:
    # ... operation
except Exception as e:
    return server_error(str(e), 'OPERATION_FAILED')
```

### Example Error Responses

#### Invalid Phone Number (400)

```json
{
    "success": false,
    "error": "Invalid phone number format",
    "code": "INVALID_PHONE_FORMAT"
}
```

#### Authentication Required (401)

```json
{
    "success": false,
    "error": "Authentication required",
    "code": "AUTH_REQUIRED"
}
```

#### Insufficient Permissions (403)

```json
{
    "success": false,
    "error": "Insufficient permissions",
    "code": "INSUFFICIENT_PERMISSIONS"
}
```

#### Plate Not Found (404)

```json
{
    "success": false,
    "error": "Plate not found with id 123",
    "code": "PLATE_NOT_FOUND"
}
```

#### Validation Error with Details (400)

```json
{
    "success": false,
    "error": "Invalid request data",
    "code": "INVALID_REQUEST",
    "details": {
        "amount": ["This field is required."],
        "plate": ["Ensure this field has no more than 20 characters."]
    }
}
```

#### Insufficient Balance (400)

```json
{
    "success": false,
    "error": "Insufficient wallet balance. Current: 10000, Required: 50000",
    "code": "INSUFFICIENT_BALANCE"
}
```

## Sensitive Data Filtering

All API responses automatically exclude sensitive information:

### Excluded Fields

The following fields are NEVER included in API responses:

- `password`
- `password_hash`
- `hashed_password`
- `pwd`
- `secret`
- `private_key`
- `auth_token` (raw token values in user objects)
- `token_hash`

### Safe User Fields

User objects in responses include only these safe fields:

- `id`
- `phone_number`
- `role`
- `created_at`
- `is_active`

## Testing Error Handling

Property-based tests verify error handling consistency:

- **Property 15**: Sensitive data exclusion - Verifies no sensitive fields appear in responses
- **Property 16**: Error response consistency - Verifies all errors follow the standard format

Run tests:

```bash
python tests/test_error_handling_properties.py
```

## Best Practices

1. **Always use error response utilities** instead of manually creating Response objects
2. **Choose appropriate HTTP status codes** based on the error type
3. **Provide clear, actionable error messages** that help users understand what went wrong
4. **Use consistent error codes** for the same types of errors across endpoints
5. **Include details when helpful** (e.g., validation errors) but avoid exposing sensitive information
6. **Log server errors** for debugging while returning generic messages to clients
7. **Test error paths** to ensure consistent error handling across all endpoints

## Middleware Error Handling

The authentication middleware automatically handles:

- Missing authentication tokens → 401 Unauthorized
- Invalid/expired tokens → 401 Unauthorized
- Insufficient role permissions → 403 Forbidden

Use the `@require_authentication` and `@require_role()` decorators to protect endpoints:

```python
@api_view(['GET'])
@require_authentication
def protected_endpoint(request):
    # Only authenticated users can access
    pass

@api_view(['GET'])
@require_authentication
@require_role(['admin', 'superuser'])
def admin_endpoint(request):
    # Only admins and superusers can access
    pass
```
