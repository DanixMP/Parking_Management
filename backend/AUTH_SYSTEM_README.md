# Authentication System Documentation

## Overview

The authentication system provides phone-based authentication with token-based session management for the parking application. It supports user registration, login, logout, and role-based access control.

## Features

- **Phone-based Authentication**: Users authenticate using Iranian mobile phone numbers (format: 09XXXXXXXXX)
- **Token-based Sessions**: Secure token generation and validation for API access
- **Automatic User Creation**: New users are automatically created on first login
- **Role-based Access Control**: Support for three user roles (user, admin, superuser)
- **Wallet Integration**: Automatic wallet creation for new users

## API Endpoints

### 1. Login

**Endpoint**: `POST /api/auth/login/`

**Request**:
```json
{
  "phone_number": "09123456789"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "token": "abc123...",
  "user": {
    "id": 1,
    "phone_number": "09123456789",
    "role": "user",
    "created_at": "2024-01-01 12:00:00",
    "is_active": true
  },
  "wallet": {
    "id": 1,
    "user_id": 1,
    "balance": 0,
    "last_updated": "2024-01-01 12:00:00"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid phone number format
- `500 Internal Server Error`: Server error during login

### 2. Logout

**Endpoint**: `POST /api/auth/logout/`

**Headers**:
```
Authorization: Token <your_token>
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `500 Internal Server Error`: Server error during logout

### 3. Get Current User

**Endpoint**: `GET /api/auth/me/`

**Headers**:
```
Authorization: Token <your_token>
```

**Response** (200 OK):
```json
{
  "success": true,
  "user": {
    "id": 1,
    "phone_number": "09123456789",
    "role": "user",
    "created_at": "2024-01-01 12:00:00",
    "is_active": true
  },
  "wallet": {
    "id": 1,
    "user_id": 1,
    "balance": 50000,
    "last_updated": "2024-01-01 12:30:00"
  }
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `500 Internal Server Error`: Server error

## Database Functions

### User Management

- `create_user(phone_number, role='user')`: Create a new user
- `get_user_by_phone(phone_number)`: Get user by phone number
- `get_user_by_id(user_id)`: Get user by ID
- `delete_user(user_id)`: Delete user and all associated data
- `get_or_create_user(phone_number)`: Get existing user or create new one

### Token Management

- `generate_token()`: Generate a secure random token
- `create_auth_token(user_id, expiry_hours=720)`: Create authentication token (default 30 days)
- `validate_token(token)`: Validate token and return user_id
- `delete_token(token)`: Delete a specific token
- `delete_user_tokens(user_id)`: Delete all tokens for a user

### Validation

- `validate_phone_number(phone_number)`: Validate Iranian phone number format

## Middleware

### TokenAuthenticationMiddleware

Automatically validates authentication tokens and attaches user data to requests.

**Request Attributes Added**:
- `request.user_data`: User dictionary (or None if not authenticated)
- `request.user_id`: User ID (or None if not authenticated)
- `request.auth_token`: Token string (or None if not authenticated)

### Decorators

#### @require_authentication

Requires valid authentication token for a view.

```python
from api.middleware import require_authentication

@api_view(['GET'])
@require_authentication
def my_protected_view(request):
    user = request.user_data
    # ... your code
```

#### @require_role(roles)

Requires specific role(s) for a view.

```python
from api.middleware import require_role

@api_view(['GET'])
@require_role(['admin', 'superuser'])
def admin_only_view(request):
    # ... your code
```

## Phone Number Format

Iranian mobile phone numbers must follow this format:
- **Pattern**: `09XXXXXXXXX`
- **Length**: 11 digits
- **Prefix**: Must start with `09`
- **Example**: `09123456789`

## Token Expiry

- Default token expiry: **720 hours (30 days)**
- Expired tokens are automatically rejected
- Users can have multiple valid tokens simultaneously
- Logout invalidates only the specific token used

## Security Considerations

1. **Token Storage**: Tokens should be stored securely on the client side
2. **HTTPS**: Use HTTPS in production to protect tokens in transit
3. **Token Rotation**: Consider implementing token refresh mechanism for long-lived sessions
4. **Rate Limiting**: Implement rate limiting on authentication endpoints to prevent abuse
5. **Phone Validation**: All phone numbers are validated before processing

## Testing

### Unit Tests

Run authentication unit tests:
```bash
cd backend
python -m pytest tests/test_authentication.py -v
```

### Manual API Testing

1. Start Django server:
```bash
cd backend
python manage.py runserver
```

2. Run manual test script:
```bash
python test_auth_manual.py
```

Or use curl:
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "09123456789"}'

# Get current user
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Token <your_token>"

# Logout
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Token <your_token>"
```

## Integration with Existing System

The authentication system integrates seamlessly with the existing parking system:

1. **Database**: Uses the same SQLite database with new tables
2. **Middleware**: Added to Django middleware stack
3. **URLs**: Authentication endpoints added to `/api/auth/` namespace
4. **Models**: New models for User, Wallet, Transaction, UserPlate, AuthToken

## Error Codes

| Code | Description |
|------|-------------|
| `INVALID_PHONE_FORMAT` | Phone number doesn't match required format |
| `INVALID_REQUEST` | Request data is invalid or missing required fields |
| `AUTH_REQUIRED` | Authentication token is missing or invalid |
| `INSUFFICIENT_PERMISSIONS` | User doesn't have required role for this action |
| `LOGIN_FAILED` | Server error during login process |
| `LOGOUT_FAILED` | Server error during logout process |
| `GET_USER_FAILED` | Server error retrieving user data |

## Next Steps

After implementing the authentication system, the following features can be added:

1. **Wallet Management**: Charge wallet, view transactions
2. **Plate Management**: Register plates, automatic payment
3. **Admin Endpoints**: User management, role assignment
4. **Frontend Integration**: Flutter UI for login and user management
