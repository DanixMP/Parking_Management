# Design Document

## Overview

The User Wallet System extends the existing parking management application with user authentication, digital wallet functionality, and automatic payment processing. The system introduces three user roles (Admin, User, SuperUser) with phone-based authentication, allowing users to pre-load funds into digital wallets and register vehicle plates for seamless automatic transactions.

The design integrates with the existing Django backend and Flutter frontend, adding new database tables, API endpoints, and UI screens while maintaining compatibility with the current parking entry/exit flow. The architecture follows the existing patterns: Django REST Framework for the backend, Provider pattern for state management in Flutter, and SQLite for data persistence.

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Flutter Frontend                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Login Screen │  │  User Home   │  │ Admin Panel  │      │
│  │              │  │   Screen     │  │   (existing) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                   ┌────────▼────────┐                        │
│                   │  UserProvider   │                        │
│                   │  (State Mgmt)   │                        │
│                   └────────┬────────┘                        │
│                            │                                 │
│                   ┌────────▼────────┐                        │
│                   │   ApiService    │                        │
│                   │  (HTTP Client)  │                        │
│                   └────────┬────────┘                        │
└────────────────────────────┼────────────────────────────────┘
                             │ HTTP/JSON
┌────────────────────────────▼────────────────────────────────┐
│                   Django REST Backend                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API Endpoints (views.py)                 │   │
│  │  /auth/login  /wallet/*  /plates/*  /users/*        │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │           Business Logic Layer                        │   │
│  │  - Authentication  - Wallet Operations                │   │
│  │  - Plate Management - Auto Payment Processing        │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │         Database Layer (database.py)                  │   │
│  │  - User CRUD  - Wallet CRUD  - Transaction CRUD      │   │
│  └──────────────────┬───────────────────────────────────┘   │
└─────────────────────┼──────────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────────┐
│                   SQLite Database                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐            │
│  │  users   │  │  wallets │  │ transactions │            │
│  └──────────┘  └──────────┘  └──────────────┘            │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐            │
│  │user_plates│ │  entries │  │    exits     │            │
│  └──────────┘  └──────────┘  └──────────────┘            │
└────────────────────────────────────────────────────────────┘
```

### Integration Points

1. **Existing Entry/Exit Flow**: The system hooks into the existing `register_exit` function to check for registered plates and process automatic payments
2. **Authentication Layer**: New middleware validates user tokens for protected endpoints
3. **Database Extension**: New tables coexist with existing parking tables
4. **Frontend Navigation**: New user screens integrate with existing admin interface

## Components and Interfaces

### Backend Components

#### 1. User Model (`backend/api/models.py`)

```python
class User(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    role = models.CharField(max_length=20, choices=[
        ('user', 'User'),
        ('admin', 'Admin'),
        ('superuser', 'SuperUser')
    ], default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
```

#### 2. Wallet Model

```python
class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=0)
    last_updated = models.DateTimeField(auto_now=True)
```

#### 3. Transaction Model

```python
class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=[
        ('charge', 'Charge'),
        ('payment', 'Payment'),
        ('refund', 'Refund')
    ])
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    exit_id = models.IntegerField(null=True, blank=True)
```

#### 4. UserPlate Model

```python
class UserPlate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plate = models.CharField(max_length=20)
    registered_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('user', 'plate')
```

### API Endpoints

#### Authentication Endpoints

```
POST /api/auth/login/
Request: { "phone_number": "09123456789" }
Response: { "token": "...", "user": {...}, "wallet": {...} }

POST /api/auth/logout/
Headers: Authorization: Token <token>
Response: { "success": true }

GET /api/auth/me/
Headers: Authorization: Token <token>
Response: { "user": {...}, "wallet": {...}, "plates": [...] }
```

#### Wallet Endpoints

```
GET /api/wallet/balance/
Headers: Authorization: Token <token>
Response: { "balance": 500000, "last_updated": "..." }

POST /api/wallet/charge/
Headers: Authorization: Token <token>
Request: { "amount": 100000 }
Response: { "success": true, "new_balance": 600000, "transaction_id": 123 }

GET /api/wallet/transactions/
Headers: Authorization: Token <token>
Query: ?limit=50&offset=0
Response: { "count": 150, "results": [...] }
```

#### Plate Endpoints

```
GET /api/plates/
Headers: Authorization: Token <token>
Response: [{ "id": 1, "plate": "12ب345-67", "registered_at": "..." }, ...]

POST /api/plates/
Headers: Authorization: Token <token>
Request: { "plate": "12ب345-67" }
Response: { "id": 1, "plate": "12ب345-67", "registered_at": "..." }

DELETE /api/plates/{id}/
Headers: Authorization: Token <token>
Response: { "success": true }
```

#### Admin Endpoints

```
GET /api/admin/users/
Headers: Authorization: Token <token> (Admin/SuperUser only)
Response: [{ "id": 1, "phone_number": "...", "role": "user", ... }, ...]

PUT /api/admin/users/{id}/role/
Headers: Authorization: Token <token> (SuperUser only)
Request: { "role": "admin" }
Response: { "success": true, "user": {...} }
```

### Frontend Components

#### 1. User Provider (`lib/providers/user_provider.dart`)

```dart
class UserProvider with ChangeNotifier {
  User? _currentUser;
  Wallet? _wallet;
  List<UserPlate> _plates = [];
  String? _authToken;
  
  Future<bool> login(String phoneNumber);
  Future<void> logout();
  Future<void> loadUserData();
  Future<bool> chargeWallet(int amount);
  Future<bool> addPlate(String plate);
  Future<bool> removePlate(int plateId);
  Future<List<Transaction>> getTransactions();
}
```

#### 2. Screens

- **LoginScreen**: Phone number input with validation
- **UserHomeScreen**: Wallet card, action buttons, plate list
- **WalletChargeDialog**: Amount input for wallet charging
- **AddPlateDialog**: Plate input with format validation
- **TransactionHistoryScreen**: List of wallet transactions

#### 3. Widgets

- **WalletCard**: Credit card-sized widget displaying balance
- **PlateListItem**: Individual plate display with delete option
- **TransactionListItem**: Transaction history item
- **ActionButton**: Reusable button for main actions

## Data Models

### Database Schema

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    created_at TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1
);

-- Wallets table
CREATE TABLE wallets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    balance INTEGER NOT NULL DEFAULT 0,
    last_updated TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Transactions table
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet_id INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,
    amount INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    description TEXT,
    exit_id INTEGER,
    FOREIGN KEY(wallet_id) REFERENCES wallets(id),
    FOREIGN KEY(exit_id) REFERENCES exits(id)
);

-- User plates table
CREATE TABLE user_plates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    plate TEXT NOT NULL,
    registered_at TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY(user_id) REFERENCES users(id),
    UNIQUE(user_id, plate)
);

-- Auth tokens table
CREATE TABLE auth_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
```

### Flutter Data Models

```dart
class User {
  final int id;
  final String phoneNumber;
  final String role;
  final DateTime createdAt;
  final bool isActive;
}

class Wallet {
  final int id;
  final int userId;
  final int balance;
  final DateTime lastUpdated;
}

class Transaction {
  final int id;
  final int walletId;
  final String transactionType;
  final int amount;
  final DateTime timestamp;
  final String? description;
  final int? exitId;
}

class UserPlate {
  final int id;
  final int userId;
  final String plate;
  final DateTime registeredAt;
  final bool isActive;
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Phone number validation consistency
*For any* string input to the authentication system, the system should accept it if and only if it matches the valid phone number format (Iranian format: 09XXXXXXXXX).
**Validates: Requirements 1.1**

### Property 2: Login idempotency
*For any* valid phone number, calling the login endpoint multiple times should always return the same user ID and user data.
**Validates: Requirements 1.2**

### Property 3: Default role assignment
*For any* newly created user account, the assigned role should be "user" unless explicitly specified otherwise.
**Validates: Requirements 1.3**

### Property 4: Authentication token generation
*For any* successful authentication, the response should contain a valid authentication token that can be used for subsequent requests.
**Validates: Requirements 1.4**

### Property 5: Role-based access control
*For any* API endpoint marked as requiring specific roles, users with insufficient roles should receive 403 Forbidden responses, while users with sufficient roles should be able to access the endpoint.
**Validates: Requirements 1.5, 1.6**

### Property 6: Wallet balance update correctness
*For any* wallet with balance B and any positive charge amount A, after charging the wallet, the new balance should equal B + A.
**Validates: Requirements 2.2**

### Property 7: Transaction record creation
*For any* wallet operation (charge or payment), a corresponding transaction record should be created with the correct amount, type, and timestamp.
**Validates: Requirements 2.3**

### Property 8: Automatic payment processing
*For any* registered plate that exits parking, if the associated user's wallet balance is greater than or equal to the parking cost, the wallet balance should be reduced by exactly the parking cost.
**Validates: Requirements 2.4, 3.5, 8.2**

### Property 9: Transaction chronological ordering
*For any* user's transaction history, the transactions should be ordered by timestamp in descending order (most recent first).
**Validates: Requirements 2.6**

### Property 10: Plate format validation
*For any* string input to the plate registration system, the system should accept it if and only if it matches the valid Iranian license plate format.
**Validates: Requirements 3.1**

### Property 11: Plate association correctness
*For any* valid plate added by a user, querying that user's plates should include the newly added plate.
**Validates: Requirements 3.2, 3.6**

### Property 12: Multiple plates support
*For any* user, the system should allow adding multiple distinct plates, and all added plates should be retrievable.
**Validates: Requirements 3.3**

### Property 13: Entry-user linkage
*For any* registered plate that enters parking, the created entry record should be linkable to the plate's owner through the user_plates table.
**Validates: Requirements 3.4**

### Property 14: Authentication requirement for protected endpoints
*For any* wallet or plate management endpoint, requests without valid authentication tokens should receive 401 Unauthorized responses.
**Validates: Requirements 4.2**

### Property 15: Sensitive data exclusion
*For any* API response containing user data, the response should not include internal fields such as password hashes or raw token values.
**Validates: Requirements 4.5**

### Property 16: Error response consistency
*For any* API error condition, the response should include an appropriate HTTP status code (4xx for client errors, 5xx for server errors) and a JSON body with an error message.
**Validates: Requirements 4.6**

### Property 17: UI state consistency after wallet charge
*For any* successful wallet charge operation in the mobile or web interface, the displayed balance should match the balance returned by the backend API.
**Validates: Requirements 5.7**

### Property 18: UI state consistency after plate addition
*For any* successful plate addition in the mobile or web interface, the displayed plate list should include the newly added plate.
**Validates: Requirements 5.8**

### Property 19: Cross-platform API consistency
*For any* API endpoint, both the mobile and web interfaces should use the same URL, HTTP method, and request/response format.
**Validates: Requirements 6.1, 6.4**

### Property 20: Database persistence completeness
*For any* user creation, the database should contain a record with phone_number, role, and created_at fields populated.
**Validates: Requirements 7.1**

### Property 21: Transaction persistence completeness
*For any* wallet transaction, the database should contain a transaction record with transaction_type, amount, timestamp, and wallet_id fields populated.
**Validates: Requirements 7.2**

### Property 22: Plate persistence completeness
*For any* plate registration, the database should contain a user_plates record with plate, user_id, and registered_at fields populated.
**Validates: Requirements 7.3**

### Property 23: Phone number uniqueness enforcement
*For any* attempt to create a user with a phone number that already exists, the system should reject the operation with an appropriate error.
**Validates: Requirements 7.5**

### Property 24: Financial precision preservation
*For any* sequence of wallet operations, the final balance should equal the initial balance plus all charges minus all payments, with no rounding errors.
**Validates: Requirements 7.6**

### Property 25: Plate registration check on exit
*For any* vehicle exit, the system should query the user_plates table to determine if the plate is registered before processing payment.
**Validates: Requirements 8.1**

### Property 26: Automatic payment atomicity
*For any* automatic payment, either both the wallet balance update and the transaction record creation should succeed, or neither should occur (atomic operation).
**Validates: Requirements 8.4, 8.5**

### Property 27: Backward compatibility with non-registered users
*For any* vehicle exit where the plate is not registered to any user, the exit should be processed successfully using the existing manual payment flow.
**Validates: Requirements 8.6**

## Error Handling

### Authentication Errors

1. **Invalid Phone Format**: Return 400 Bad Request with message "Invalid phone number format"
2. **Missing Auth Token**: Return 401 Unauthorized with message "Authentication required"
3. **Invalid/Expired Token**: Return 401 Unauthorized with message "Invalid or expired token"
4. **Insufficient Permissions**: Return 403 Forbidden with message "Insufficient permissions"

### Wallet Errors

1. **Insufficient Balance**: Return 400 Bad Request with message "Insufficient wallet balance"
2. **Invalid Charge Amount**: Return 400 Bad Request with message "Charge amount must be positive"
3. **Wallet Not Found**: Return 404 Not Found with message "Wallet not found for user"

### Plate Errors

1. **Invalid Plate Format**: Return 400 Bad Request with message "Invalid license plate format"
2. **Duplicate Plate**: Return 400 Bad Request with message "Plate already registered to this user"
3. **Plate Not Found**: Return 404 Not Found with message "Plate not found"
4. **Plate Belongs to Another User**: Return 403 Forbidden with message "Cannot modify another user's plate"

### Database Errors

1. **Connection Failure**: Return 503 Service Unavailable with message "Database temporarily unavailable"
2. **Constraint Violation**: Return 409 Conflict with message describing the constraint
3. **Transaction Rollback**: Log error and return 500 Internal Server Error with generic message

### Error Response Format

All errors follow this JSON structure:
```json
{
  "success": false,
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": {} // Optional additional context
}
```

## Testing Strategy

### Unit Testing

The system will use Python's `unittest` framework for backend testing and Flutter's built-in test framework for frontend testing.

**Backend Unit Tests:**
- User model CRUD operations
- Wallet balance calculations
- Plate format validation
- Authentication token generation and validation
- Transaction record creation
- API endpoint request/response handling

**Frontend Unit Tests:**
- Model serialization/deserialization
- Phone number format validation
- Plate format validation
- API service method calls
- Provider state updates

### Property-Based Testing

The system will use **Hypothesis** for Python property-based testing. Each property test will run a minimum of 100 iterations with randomly generated inputs.

**Property Test Configuration:**
```python
from hypothesis import given, settings
import hypothesis.strategies as st

@settings(max_examples=100)
@given(phone_number=st.text())
def test_phone_validation_property(phone_number):
    # Test implementation
    pass
```

**Property Test Tagging:**
Each property-based test must include a comment explicitly referencing the correctness property from this design document using the format:
```python
# Feature: user-wallet-system, Property 1: Phone number validation consistency
```

**Key Property Tests:**
- Phone number and plate format validation across random inputs
- Wallet balance arithmetic across sequences of operations
- Transaction ordering across random transaction sets
- Role-based access control across all role combinations
- Automatic payment processing across various balance/cost scenarios
- Database uniqueness constraints across duplicate attempts
- API authentication across valid/invalid token scenarios

### Integration Testing

**Backend Integration Tests:**
- Full authentication flow (login → token → authenticated request)
- Wallet charge flow (charge → balance update → transaction record)
- Plate registration flow (add plate → verify in database → retrieve via API)
- Automatic payment flow (register plate → park → exit → verify payment)
- Cross-table queries (user → wallet → transactions)

**Frontend Integration Tests:**
- Login flow (enter phone → authenticate → navigate to home)
- Wallet charge flow (tap button → enter amount → submit → verify UI update)
- Plate management flow (add plate → verify in list → delete plate)
- API integration (make request → handle response → update state)

### End-to-End Testing

**User Journey Tests:**
1. New user registration and first wallet charge
2. Plate registration and automatic payment on first parking
3. Multiple parking sessions with balance depletion
4. Admin user managing other users
5. Cross-platform consistency (same actions on mobile and web)

**Test Data:**
- Use realistic Iranian phone numbers and license plates
- Test with various balance amounts (0, small, large)
- Test with edge cases (exactly sufficient balance, insufficient by 1 Rial)
- Test with multiple concurrent users

### Testing Tools

- **Backend**: pytest, Hypothesis, Django test client
- **Frontend**: flutter_test, mockito for mocking
- **API Testing**: Postman collections for manual testing
- **Database**: SQLite in-memory database for test isolation

## Implementation Notes

### Database Migration Strategy

Since the existing system uses `managed = False` in Django models, we'll need to manually create the new tables using SQL scripts in `backend/src/database.py`. The `init_db()` function will be extended to create user-related tables.

### Authentication Implementation

We'll use Django REST Framework's token authentication with custom token generation. Tokens will be stored in the database with expiration timestamps.

### Automatic Payment Integration

The existing `register_exit()` function in `database.py` will be modified to:
1. Check if the plate is registered (query `user_plates`)
2. If registered, get the user's wallet
3. If balance is sufficient, deduct cost and create transaction
4. Return payment status along with exit data

### Frontend State Management

The existing `ParkingProvider` will be complemented with a new `UserProvider` for user-specific state. Both providers will be available at the app root level.

### Phone Number Format

Iranian mobile numbers follow the format: `09XXXXXXXXX` (11 digits starting with 09). Validation regex: `^09\d{9}$`

### License Plate Format

Iranian plates follow formats like: `12ب345-67` or `12الف345-67`. The system will validate against the existing plate parsing logic in the Flutter app.

### Currency

All amounts are in Iranian Rials (IRR) stored as integers to avoid floating-point precision issues.

### Security Considerations

1. **Token Storage**: Tokens stored securely in Flutter secure storage
2. **HTTPS**: All API communication should use HTTPS in production
3. **Rate Limiting**: Implement rate limiting on authentication endpoints
4. **Input Validation**: All user inputs validated on both client and server
5. **SQL Injection**: Use parameterized queries (already implemented)
6. **XSS Prevention**: Sanitize any user-generated content before display
