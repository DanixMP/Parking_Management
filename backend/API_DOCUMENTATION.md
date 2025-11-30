# User Wallet System API Documentation

## Overview

This document provides comprehensive documentation for the User Wallet System API endpoints. The system extends the parking management application with user authentication, digital wallet functionality, and automatic payment processing.

**Base URL**: `http://localhost:8000/api/`

**Authentication**: Most endpoints require authentication via token-based authentication. Include the token in the `Authorization` header:
```
Authorization: Token <your-token-here>
```

**Response Format**: All responses are in JSON format and follow a consistent structure:
- Success responses include relevant data
- Error responses follow the format:
```json
{
  "success": false,
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": {}
}
```

---

## Table of Contents

1. [Authentication Endpoints](#authentication-endpoints)
2. [Wallet Management Endpoints](#wallet-management-endpoints)
3. [Plate Management Endpoints](#plate-management-endpoints)
4. [Admin Endpoints](#admin-endpoints)
5. [Error Codes Reference](#error-codes-reference)
6. [Common Error Responses](#common-error-responses)

---

## Authentication Endpoints

### 1. User Login

Authenticate a user with their phone number. Creates a new user account if the phone number doesn't exist.

**Endpoint**: `POST /api/auth/login/`

**Authentication Required**: No

**Request Body**:
```json
{
  "phone_number": "09123456789"
}
```

**Request Fields**:
- `phone_number` (string, required): Iranian mobile phone number in format `09XXXXXXXXX`

**Success Response** (200 OK):
```json
{
  "success": true,
  "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "user": {
    "id": 1,
    "phone_number": "09123456789",
    "role": "user",
    "created_at": "2024-12-01 10:30:00",
    "is_active": true
  },
  "wallet": {
    "id": 1,
    "user_id": 1,
    "balance": 0,
    "last_updated": "2024-12-01 10:30:00"
  }
}
```

**Error Responses**:

*Invalid Phone Format* (400 Bad Request):
```json
{
  "success": false,
  "error": "Invalid phone number format",
  "code": "INVALID_PHONE_FORMAT"
}
```

*Invalid Request Data* (400 Bad Request):
```json
{
  "success": false,
  "error": "Invalid request data",
  "code": "INVALID_REQUEST",
  "details": {
    "phone_number": ["This field is required."]
  }
}
```

*Server Error* (500 Internal Server Error):
```json
{
  "success": false,
  "error": "Database connection failed",
  "code": "LOGIN_FAILED"
}
```

**Example Usage**:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "09123456789"}'
```

---

### 2. User Logout

Invalidate the current authentication token and log out the user.

**Endpoint**: `POST /api/auth/logout/`

**Authentication Required**: Yes

**Request Headers**:
```
Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

**Request Body**: None

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

**Error Responses**:

*Missing Authentication* (401 Unauthorized):
```json
{
  "success": false,
  "error": "Authentication required",
  "code": "AUTH_REQUIRED"
}
```

*Invalid Token* (401 Unauthorized):
```json
{
  "success": false,
  "error": "Invalid or expired token",
  "code": "INVALID_TOKEN"
}
```

**Example Usage**:
```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
```

---

### 3. Get Current User

Retrieve information about the currently authenticated user.

**Endpoint**: `GET /api/auth/me/`

**Authentication Required**: Yes

**Request Headers**:
```
Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

**Success Response** (200 OK):
```json
{
  "success": true,
  "user": {
    "id": 1,
    "phone_number": "09123456789",
    "role": "user",
    "created_at": "2024-12-01 10:30:00",
    "is_active": true
  },
  "wallet": {
    "id": 1,
    "user_id": 1,
    "balance": 500000,
    "last_updated": "2024-12-01 15:45:00"
  }
}
```

**Error Responses**:

*Missing Authentication* (401 Unauthorized):
```json
{
  "success": false,
  "error": "Authentication required",
  "code": "AUTH_REQUIRED"
}
```

*Invalid Token* (401 Unauthorized):
```json
{
  "success": false,
  "error": "Invalid or expired token",
  "code": "INVALID_TOKEN"
}
```

**Example Usage**:
```bash
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
```

---

## Wallet Management Endpoints

### 4. Get Wallet Balance

Retrieve the current balance of the authenticated user's wallet.

**Endpoint**: `GET /api/wallet/balance/`

**Authentication Required**: Yes

**Request Headers**:
```
Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

**Success Response** (200 OK):
```json
{
  "balance": 500000,
  "last_updated": "2024-12-01 15:45:00"
}
```

**Error Responses**:

*Missing Authentication* (401 Unauthorized):
```json
{
  "success": false,
  "error": "Authentication required",
  "code": "AUTH_REQUIRED"
}
```

*Wallet Not Found* (404 Not Found):
```json
{
  "success": false,
  "error": "Wallet not found for user",
  "code": "WALLET_NOT_FOUND"
}
```

**Example Usage**:
```bash
curl -X GET http://localhost:8000/api/wallet/balance/ \
  -H "Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
```

---

### 5. Charge Wallet

Add funds to the authenticated user's wallet.

**Endpoint**: `POST /api/wallet/charge/`

**Authentication Required**: Yes

**Request Headers**:
```
Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

**Request Body**:
```json
{
  "amount": 100000
}
```

**Request Fields**:
- `amount` (integer, required): Amount to add to wallet in Rials (must be positive)

**Success Response** (200 OK):
```json
{
  "success": true,
  "new_balance": 600000,
  "transaction_id": 123
}
```

**Error Responses**:

*Invalid Amount* (400 Bad Request):
```json
{
  "success": false,
  "error": "Charge amount must be positive",
  "code": "INVALID_CHARGE_AMOUNT"
}
```

*Invalid Request Data* (400 Bad Request):
```json
{
  "success": false,
  "error": "Invalid request data",
  "code": "INVALID_REQUEST",
  "details": {
    "amount": ["Ensure this value is greater than or equal to 1."]
  }
}
```

*Missing Authentication* (401 Unauthorized):
```json
{
  "success": false,
  "error": "Authentication required",
  "code": "AUTH_REQUIRED"
}
```

**Example Usage**:
```bash
curl -X POST http://localhost:8000/api/wallet/charge/ \
  -H "Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6" \
  -H "Content-Type: application/json" \
  -d '{"amount": 100000}'
```

---

### 6. Get Transaction History

Retrieve the transaction history for the authenticated user's wallet.

**Endpoint**: `GET /api/wallet/transactions/`

**Authentication Required**: Yes

**Request Headers**:
```
Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

**Query Parameters**:
- `limit` (integer, optional): Number of transactions to return (default: 50, max: 100)
- `offset` (integer, optional): Number of transactions to skip (default: 0)

**Success Response** (200 OK):
```json
{
  "count": 150,
  "results": [
    {
      "id": 123,
      "wallet_id": 1,
      "transaction_type": "charge",
      "amount": 100000,
      "timestamp": "2024-12-01 15:45:00",
      "description": "Wallet charge",
      "exit_id": null
    },
    {
      "id": 122,
      "wallet_id": 1,
      "transaction_type": "payment",
      "amount": 40000,
      "timestamp": "2024-12-01 14:30:00",
      "description": "Automatic parking payment",
      "exit_id": 456
    }
  ]
}
```

**Response Fields**:
- `count` (integer): Total number of transactions
- `results` (array): Array of transaction objects
  - `id` (integer): Transaction ID
  - `wallet_id` (integer): Associated wallet ID
  - `transaction_type` (string): Type of transaction (`charge`, `payment`, `refund`)
  - `amount` (integer): Transaction amount in Rials
  - `timestamp` (string): Transaction timestamp
  - `description` (string): Transaction description
  - `exit_id` (integer, nullable): Associated exit ID for payment transactions

**Error Responses**:

*Missing Authentication* (401 Unauthorized):
```json
{
  "success": false,
  "error": "Authentication required",
  "code": "AUTH_REQUIRED"
}
```

**Example Usage**:
```bash
# Get first 50 transactions
curl -X GET http://localhost:8000/api/wallet/transactions/ \
  -H "Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"

# Get next 50 transactions with pagination
curl -X GET "http://localhost:8000/api/wallet/transactions/?limit=50&offset=50" \
  -H "Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
```

---

## Plate Management Endpoints

### 7. Get User Plates

Retrieve all license plates registered to the authenticated user.

**Endpoint**: `GET /api/plates/`

**Authentication Required**: Yes

**Request Headers**:
```
Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

**Success Response** (200 OK):
```json
[
  {
    "id": 1,
    "user_id": 1,
    "plate": "12ب345-67",
    "registered_at": "2024-12-01 10:30:00",
    "is_active": true
  },
  {
    "id": 2,
    "user_id": 1,
    "plate": "88الف123-45",
    "registered_at": "2024-12-01 11:15:00",
    "is_active": true
  }
]
```

**Response Fields**:
- `id` (integer): Plate registration ID
- `user_id` (integer): Owner user ID
- `plate` (string): License plate number in Iranian format
- `registered_at` (string): Registration timestamp
- `is_active` (boolean): Whether the plate is active

**Error Responses**:

*Missing Authentication* (401 Unauthorized):
```json
{
  "success": false,
  "error": "Authentication required",
  "code": "AUTH_REQUIRED"
}
```

**Example Usage**:
```bash
curl -X GET http://localhost:8000/api/plates/ \
  -H "Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
```

---

### 8. Add Plate

Register a new license plate to the authenticated user's account.

**Endpoint**: `POST /api/plates/`

**Authentication Required**: Yes

**Request Headers**:
```
Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

**Request Body**:
```json
{
  "plate": "12ب345-67"
}
```

**Request Fields**:
- `plate` (string, required): License plate number in Iranian format

**Success Response** (201 Created):
```json
{
  "id": 1,
  "user_id": 1,
  "plate": "12ب345-67",
  "registered_at": "2024-12-01 10:30:00",
  "is_active": true
}
```

**Error Responses**:

*Invalid Plate Format* (400 Bad Request):
```json
{
  "success": false,
  "error": "Invalid license plate format",
  "code": "INVALID_PLATE_FORMAT"
}
```

*Duplicate Plate* (400 Bad Request):
```json
{
  "success": false,
  "error": "Plate already registered to this user",
  "code": "DUPLICATE_PLATE"
}
```

*Invalid Request Data* (400 Bad Request):
```json
{
  "success": false,
  "error": "Invalid request data",
  "code": "INVALID_REQUEST",
  "details": {
    "plate": ["This field is required."]
  }
}
```

*Missing Authentication* (401 Unauthorized):
```json
{
  "success": false,
  "error": "Authentication required",
  "code": "AUTH_REQUIRED"
}
```

**Example Usage**:
```bash
curl -X POST http://localhost:8000/api/plates/ \
  -H "Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6" \
  -H "Content-Type: application/json" \
  -d '{"plate": "12ب345-67"}'
```

---

### 9. Delete Plate

Remove a license plate from the authenticated user's account.

**Endpoint**: `DELETE /api/plates/{plate_id}/`

**Authentication Required**: Yes

**Request Headers**:
```
Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

**URL Parameters**:
- `plate_id` (integer): ID of the plate to delete

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Plate deleted successfully"
}
```

**Error Responses**:

*Plate Not Found* (404 Not Found):
```json
{
  "success": false,
  "error": "Plate not found",
  "code": "PLATE_NOT_FOUND"
}
```

*Unauthorized Access* (403 Forbidden):
```json
{
  "success": false,
  "error": "Plate does not belong to this user",
  "code": "PLATE_UNAUTHORIZED"
}
```

*Missing Authentication* (401 Unauthorized):
```json
{
  "success": false,
  "error": "Authentication required",
  "code": "AUTH_REQUIRED"
}
```

**Example Usage**:
```bash
curl -X DELETE http://localhost:8000/api/plates/1/ \
  -H "Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
```

---

## Admin Endpoints

### 10. Get All Users

Retrieve a list of all users in the system. Requires Admin or SuperUser role.

**Endpoint**: `GET /api/admin/users/`

**Authentication Required**: Yes (Admin or SuperUser role)

**Request Headers**:
```
Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

**Query Parameters**:
- `limit` (integer, optional): Number of users to return (default: 100, max: 500)
- `offset` (integer, optional): Number of users to skip (default: 0)

**Success Response** (200 OK):
```json
{
  "count": 250,
  "results": [
    {
      "id": 1,
      "phone_number": "09123456789",
      "role": "user",
      "created_at": "2024-12-01 10:30:00",
      "is_active": true
    },
    {
      "id": 2,
      "phone_number": "09987654321",
      "role": "admin",
      "created_at": "2024-11-15 08:20:00",
      "is_active": true
    }
  ]
}
```

**Error Responses**:

*Missing Authentication* (401 Unauthorized):
```json
{
  "success": false,
  "error": "Authentication required",
  "code": "AUTH_REQUIRED"
}
```

*Insufficient Permissions* (403 Forbidden):
```json
{
  "success": false,
  "error": "Insufficient permissions",
  "code": "FORBIDDEN"
}
```

**Example Usage**:
```bash
# Get first 100 users
curl -X GET http://localhost:8000/api/admin/users/ \
  -H "Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"

# Get next 100 users with pagination
curl -X GET "http://localhost:8000/api/admin/users/?limit=100&offset=100" \
  -H "Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
```

---

### 11. Update User Role

Update a user's role. Requires SuperUser role.

**Endpoint**: `PUT /api/admin/users/{user_id}/role/`

**Authentication Required**: Yes (SuperUser role only)

**Request Headers**:
```
Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

**URL Parameters**:
- `user_id` (integer): ID of the user to update

**Request Body**:
```json
{
  "role": "admin"
}
```

**Request Fields**:
- `role` (string, required): New role for the user (`user`, `admin`, or `superuser`)

**Success Response** (200 OK):
```json
{
  "success": true,
  "user": {
    "id": 1,
    "phone_number": "09123456789",
    "role": "admin",
    "created_at": "2024-12-01 10:30:00",
    "is_active": true
  }
}
```

**Error Responses**:

*Role Required* (400 Bad Request):
```json
{
  "success": false,
  "error": "Role is required",
  "code": "ROLE_REQUIRED"
}
```

*Invalid Role* (400 Bad Request):
```json
{
  "success": false,
  "error": "Invalid role: must be user, admin, or superuser",
  "code": "INVALID_ROLE"
}
```

*User Not Found* (404 Not Found):
```json
{
  "success": false,
  "error": "User not found",
  "code": "USER_NOT_FOUND"
}
```

*Missing Authentication* (401 Unauthorized):
```json
{
  "success": false,
  "error": "Authentication required",
  "code": "AUTH_REQUIRED"
}
```

*Insufficient Permissions* (403 Forbidden):
```json
{
  "success": false,
  "error": "Insufficient permissions",
  "code": "FORBIDDEN"
}
```

**Example Usage**:
```bash
curl -X PUT http://localhost:8000/api/admin/users/1/role/ \
  -H "Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6" \
  -H "Content-Type: application/json" \
  -d '{"role": "admin"}'
```

---

## Error Codes Reference

### Authentication Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `INVALID_PHONE_FORMAT` | Phone number doesn't match required format | 400 |
| `AUTH_REQUIRED` | Authentication token is missing | 401 |
| `INVALID_TOKEN` | Authentication token is invalid or expired | 401 |
| `FORBIDDEN` | User doesn't have required permissions | 403 |
| `LOGIN_FAILED` | Login process failed due to server error | 500 |

### Wallet Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `INVALID_CHARGE_AMOUNT` | Charge amount must be positive | 400 |
| `INSUFFICIENT_BALANCE` | Wallet balance is insufficient for operation | 400 |
| `WALLET_NOT_FOUND` | Wallet not found for user | 404 |
| `WALLET_OPERATION_FAILED` | Wallet operation failed due to server error | 500 |

### Plate Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `INVALID_PLATE_FORMAT` | License plate format is invalid | 400 |
| `DUPLICATE_PLATE` | Plate already registered to this user | 400 |
| `PLATE_NOT_FOUND` | Plate not found | 404 |
| `PLATE_UNAUTHORIZED` | User doesn't have permission to access this plate | 403 |
| `PLATE_OPERATION_FAILED` | Plate operation failed due to server error | 500 |

### Admin Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `USER_NOT_FOUND` | User not found | 404 |
| `ROLE_REQUIRED` | Role field is required | 400 |
| `INVALID_ROLE` | Invalid role value | 400 |

### General Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `INVALID_REQUEST` | Request data is invalid or malformed | 400 |
| `DATABASE_ERROR` | Database operation failed | 500 |
| `INTERNAL_ERROR` | Internal server error | 500 |

---

## Common Error Responses

### 400 Bad Request

Returned when the request data is invalid or doesn't meet validation requirements.

**Example - Missing Required Field**:
```json
{
  "success": false,
  "error": "Invalid request data",
  "code": "INVALID_REQUEST",
  "details": {
    "phone_number": ["This field is required."]
  }
}
```

**Example - Invalid Format**:
```json
{
  "success": false,
  "error": "Invalid phone number format",
  "code": "INVALID_PHONE_FORMAT"
}
```

**Example - Business Logic Violation**:
```json
{
  "success": false,
  "error": "Charge amount must be positive",
  "code": "INVALID_CHARGE_AMOUNT"
}
```

---

### 401 Unauthorized

Returned when authentication is required but not provided, or when the provided token is invalid.

**Example - Missing Token**:
```json
{
  "success": false,
  "error": "Authentication required",
  "code": "AUTH_REQUIRED"
}
```

**Example - Invalid Token**:
```json
{
  "success": false,
  "error": "Invalid or expired token",
  "code": "INVALID_TOKEN"
}
```

---

### 403 Forbidden

Returned when the authenticated user doesn't have permission to perform the requested action.

**Example - Insufficient Role**:
```json
{
  "success": false,
  "error": "Insufficient permissions",
  "code": "FORBIDDEN"
}
```

**Example - Resource Ownership**:
```json
{
  "success": false,
  "error": "Plate does not belong to this user",
  "code": "PLATE_UNAUTHORIZED"
}
```

---

### 404 Not Found

Returned when the requested resource doesn't exist.

**Example - User Not Found**:
```json
{
  "success": false,
  "error": "User not found",
  "code": "USER_NOT_FOUND"
}
```

**Example - Plate Not Found**:
```json
{
  "success": false,
  "error": "Plate not found",
  "code": "PLATE_NOT_FOUND"
}
```

---

### 500 Internal Server Error

Returned when an unexpected server error occurs.

**Example - Database Error**:
```json
{
  "success": false,
  "error": "Database connection failed",
  "code": "DATABASE_ERROR"
}
```

**Example - Generic Error**:
```json
{
  "success": false,
  "error": "An unexpected error occurred",
  "code": "INTERNAL_ERROR"
}
```

---

### 503 Service Unavailable

Returned when the service is temporarily unavailable.

**Example - Database Unavailable**:
```json
{
  "success": false,
  "error": "Database temporarily unavailable",
  "code": "DATABASE_ERROR"
}
```

---

## Authentication Flow

### Complete Authentication Flow Example

1. **User Login**:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "09123456789"}'
```

Response:
```json
{
  "success": true,
  "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "user": {
    "id": 1,
    "phone_number": "09123456789",
    "role": "user",
    "created_at": "2024-12-01 10:30:00",
    "is_active": true
  },
  "wallet": {
    "id": 1,
    "user_id": 1,
    "balance": 0,
    "last_updated": "2024-12-01 10:30:00"
  }
}
```

2. **Store Token**: Save the token securely on the client side (e.g., in secure storage)

3. **Make Authenticated Requests**: Include the token in the Authorization header for all subsequent requests:
```bash
curl -X GET http://localhost:8000/api/wallet/balance/ \
  -H "Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
```

4. **Logout** (optional):
```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
```

---

## Complete User Journey Examples

### Example 1: New User Registration and First Wallet Charge

**Step 1: Login (creates new user)**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "09123456789"}'
```

**Step 2: Charge Wallet**
```bash
curl -X POST http://localhost:8000/api/wallet/charge/ \
  -H "Authorization: Token <token>" \
  -H "Content-Type: application/json" \
  -d '{"amount": 500000}'
```

**Step 3: Verify Balance**
```bash
curl -X GET http://localhost:8000/api/wallet/balance/ \
  -H "Authorization: Token <token>"
```

---

### Example 2: Register Plate and Automatic Payment

**Step 1: Add Plate**
```bash
curl -X POST http://localhost:8000/api/plates/ \
  -H "Authorization: Token <token>" \
  -H "Content-Type: application/json" \
  -d '{"plate": "12ب345-67"}'
```

**Step 2: Verify Plate Registration**
```bash
curl -X GET http://localhost:8000/api/plates/ \
  -H "Authorization: Token <token>"
```

**Step 3: Park Vehicle** (automatic - plate detected at entry)

**Step 4: Exit Parking** (automatic payment processed)

**Step 5: Check Transaction History**
```bash
curl -X GET http://localhost:8000/api/wallet/transactions/ \
  -H "Authorization: Token <token>"
```

---

### Example 3: Admin Managing Users

**Step 1: Login as SuperUser**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "09999999999"}'
```

**Step 2: Get All Users**
```bash
curl -X GET http://localhost:8000/api/admin/users/ \
  -H "Authorization: Token <superuser-token>"
```

**Step 3: Promote User to Admin**
```bash
curl -X PUT http://localhost:8000/api/admin/users/5/role/ \
  -H "Authorization: Token <superuser-token>" \
  -H "Content-Type: application/json" \
  -d '{"role": "admin"}'
```

---

## Rate Limiting

To prevent abuse, the following rate limits are recommended for production:

- **Login Endpoint**: 5 requests per minute per IP address
- **Wallet Charge**: 10 requests per minute per user
- **Plate Operations**: 20 requests per minute per user
- **Admin Endpoints**: 100 requests per minute per admin user

Rate limit responses return HTTP 429 (Too Many Requests):
```json
{
  "success": false,
  "error": "Rate limit exceeded. Please try again later.",
  "code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60
}
```

---

## Security Best Practices

### For API Consumers

1. **Store Tokens Securely**: Use secure storage mechanisms (e.g., flutter_secure_storage for Flutter apps)
2. **Use HTTPS**: Always use HTTPS in production to encrypt data in transit
3. **Validate Input**: Validate all user input on the client side before sending to the API
4. **Handle Errors Gracefully**: Display user-friendly error messages and log detailed errors for debugging
5. **Implement Timeout**: Set reasonable timeout values for API requests
6. **Logout on Inactivity**: Implement automatic logout after a period of inactivity

### For API Administrators

1. **Enable HTTPS**: Configure SSL/TLS certificates for production
2. **Implement Rate Limiting**: Use rate limiting to prevent abuse
3. **Monitor Logs**: Regularly review API access logs for suspicious activity
4. **Keep Dependencies Updated**: Regularly update Django and other dependencies
5. **Use Environment Variables**: Store sensitive configuration in environment variables
6. **Backup Database**: Implement regular database backups
7. **Implement CORS**: Configure CORS properly for web clients

---

## Testing the API

### Using cURL

All examples in this documentation use cURL. Replace `<token>` with your actual authentication token.

### Using Postman

1. Import the API endpoints into Postman
2. Set up an environment variable for the base URL: `http://localhost:8000/api/`
3. Set up an environment variable for the token after login
4. Use `{{base_url}}` and `{{token}}` in your requests

### Using Python Requests

```python
import requests

# Login
response = requests.post(
    'http://localhost:8000/api/auth/login/',
    json={'phone_number': '09123456789'}
)
data = response.json()
token = data['token']

# Make authenticated request
headers = {'Authorization': f'Token {token}'}
response = requests.get(
    'http://localhost:8000/api/wallet/balance/',
    headers=headers
)
print(response.json())
```

---

## Changelog

### Version 1.0.0 (2024-12-01)

- Initial release of User Wallet System API
- Authentication endpoints (login, logout, get current user)
- Wallet management endpoints (balance, charge, transactions)
- Plate management endpoints (list, add, delete)
- Admin endpoints (list users, update user role)
- Comprehensive error handling and response formatting

---

## Support and Contact

For API support, bug reports, or feature requests, please contact the development team or create an issue in the project repository.

**API Version**: 1.0.0  
**Last Updated**: December 1, 2024