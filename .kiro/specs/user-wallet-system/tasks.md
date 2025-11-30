# Implementation Plan

- [x] 1. Set up database schema and core user models





  - Create database tables for users, wallets, transactions, user_plates, and auth_tokens in `backend/src/database.py`
  - Extend `init_db()` function to initialize new tables with proper foreign keys and constraints
  - Create Django models in `backend/api/models.py` for User, Wallet, Transaction, UserPlate, and AuthToken
  - Set up model relationships and Meta options
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

- [x] 1.1 Write property test for phone number uniqueness






  - **Property 23: Phone number uniqueness enforcement**
  - **Validates: Requirements 7.5**

- [x] 1.2 Write property test for database persistence






  - **Property 20: Database persistence completeness**
  - **Property 21: Transaction persistence completeness**
  - **Property 22: Plate persistence completeness**
  - **Validates: Requirements 7.1, 7.2, 7.3**

- [x] 2. Implement authentication system





  - Create authentication helper functions in `backend/src/database.py` for user CRUD operations
  - Implement token generation and validation logic
  - Create authentication serializers in `backend/api/serializers.py`
  - Implement login endpoint (`POST /api/auth/login/`) in `backend/api/views.py`
  - Implement logout endpoint (`POST /api/auth/logout/`)
  - Implement get current user endpoint (`GET /api/auth/me/`)
  - Create authentication middleware for token validation
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 4.1_

- [x] 2.1 Write property test for phone validation
  - **Property 1: Phone number validation consistency**
  - **Validates: Requirements 1.1**

- [x] 2.2 Write property test for login idempotency

  - **Property 2: Login idempotency**
  - **Validates: Requirements 1.2**

- [x] 2.3 Write property test for default role assignment






  - **Property 3: Default role assignment**
  - **Validates: Requirements 1.3**

- [x] 2.4 Write property test for token generation






  - **Property 4: Authentication token generation**
  - **Validates: Requirements 1.4**

- [x] 2.5 Write property test for authentication requirement






  - **Property 14: Authentication requirement for protected endpoints**
  - **Validates: Requirements 4.2**

- [x] 3. Implement wallet management system





  - Create wallet helper functions in `backend/src/database.py` for balance operations
  - Implement transaction recording logic
  - Create wallet serializers in `backend/api/serializers.py`
  - Implement get wallet balance endpoint (`GET /api/wallet/balance/`)
  - Implement charge wallet endpoint (`POST /api/wallet/charge/`)
  - Implement get transactions endpoint (`GET /api/wallet/transactions/`)
  - Add wallet creation on user registration
  - _Requirements: 2.2, 2.3, 2.6, 4.2_

- [x] 3.1 Write property test for wallet balance updates





  - **Property 6: Wallet balance update correctness**
  - **Validates: Requirements 2.2**

- [x] 3.2 Write property test for transaction record creation






  - **Property 7: Transaction record creation**
  - **Validates: Requirements 2.3**

- [x] 3.3 Write property test for transaction ordering






  - **Property 9: Transaction chronological ordering**
  - **Validates: Requirements 2.6**

- [x] 3.4 Write property test for financial precision






  - **Property 24: Financial precision preservation**
  - **Validates: Requirements 7.6**

- [x] 4. Implement plate management system





  - Create plate validation function for Iranian license plate format
  - Create plate helper functions in `backend/src/database.py` for CRUD operations
  - Create plate serializers in `backend/api/serializers.py`
  - Implement get user plates endpoint (`GET /api/plates/`)
  - Implement add plate endpoint (`POST /api/plates/`)
  - Implement delete plate endpoint (`DELETE /api/plates/{id}/`)
  - _Requirements: 3.1, 3.2, 3.3, 3.6, 4.3_

- [x] 4.1 Write property test for plate format validation



  - **Property 10: Plate format validation**
  - **Validates: Requirements 3.1**

- [x] 4.2 Write property test for plate association



  - **Property 11: Plate association correctness**
  - **Validates: Requirements 3.2, 3.6**

- [x] 4.3 Write property test for multiple plates support



  - **Property 12: Multiple plates support**
  - **Validates: Requirements 3.3**

- [x] 5. Integrate automatic payment processing with existing parking system





  - Modify `register_exit()` in `backend/src/database.py` to check for registered plates
  - Implement automatic wallet deduction logic for registered plates
  - Create transaction records linking exits to wallet payments
  - Handle insufficient balance scenarios
  - Ensure backward compatibility with non-registered users
  - _Requirements: 2.4, 3.4, 3.5, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

- [x] 5.1 Write property test for automatic payment processing



  - **Property 8: Automatic payment processing**
  - **Validates: Requirements 2.4, 3.5, 8.2**


- [x] 5.2 Write property test for entry-user linkage



  - **Property 13: Entry-user linkage**
  - **Validates: Requirements 3.4**

- [x] 5.3 Write property test for plate registration check



  - **Property 25: Plate registration check on exit**
  - **Validates: Requirements 8.1**

- [x] 5.4 Write property test for payment atomicity



  - **Property 26: Automatic payment atomicity**
  - **Validates: Requirements 8.4, 8.5**

- [x] 5.5 Write property test for backward compatibility



  - **Property 27: Backward compatibility with non-registered users**
  - **Validates: Requirements 8.6**

- [x] 6. Implement role-based access control and admin endpoints





  - Create permission checking middleware for role-based access
  - Implement get all users endpoint (`GET /api/admin/users/`) for Admin/SuperUser
  - Implement update user role endpoint (`PUT /api/admin/users/{id}/role/`) for SuperUser
  - Add role checks to existing endpoints where appropriate
  - _Requirements: 1.5, 1.6_

- [x] 6.1 Write property test for role-based access control



  - **Property 5: Role-based access control**
  - **Validates: Requirements 1.5, 1.6**

- [x] 7. Implement API error handling and response formatting





  - Create standardized error response format
  - Add error handling to all endpoints
  - Implement appropriate HTTP status codes for different error types
  - Add sensitive data filtering to user data responses
  - _Requirements: 4.5, 4.6_

- [x] 7.1 Write property test for sensitive data exclusion



  - **Property 15: Sensitive data exclusion**
  - **Validates: Requirements 4.5**


- [x] 7.2 Write property test for error response consistency



  - **Property 16: Error response consistency**
  - **Validates: Requirements 4.6**

- [x] 8. Update API URL configuration




  - Add new URL patterns to `backend/api/urls.py` for authentication, wallet, plates, and admin endpoints
  - Ensure proper URL namespacing
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 9. Create Flutter data models for user system





  - Create `User` model in `frontend/parking/lib/models/user.dart`
  - Create `Wallet` model in `frontend/parking/lib/models/wallet.dart`
  - Create `Transaction` model in `frontend/parking/lib/models/transaction.dart`
  - Create `UserPlate` model in `frontend/parking/lib/models/user_plate.dart`
  - Implement JSON serialization/deserialization for all models
  - _Requirements: 5.1, 5.2, 5.7, 5.8_

- [x] 10. Implement Flutter API service for user endpoints





  - Extend `ApiService` in `frontend/parking/lib/services/api_service.dart` with authentication methods
  - Add wallet management methods (getBalance, chargeWallet, getTransactions)
  - Add plate management methods (getPlates, addPlate, deletePlate)
  - Implement token storage and retrieval using flutter_secure_storage
  - Add authentication headers to all protected requests
  - _Requirements: 4.1, 4.2, 4.3, 6.4_

- [x] 10.1 Write property test for cross-platform API consistency






  - **Property 19: Cross-platform API consistency**
  - **Validates: Requirements 6.1, 6.4**

- [x] 11. Create UserProvider for state management





  - Create `UserProvider` in `frontend/parking/lib/providers/user_provider.dart`
  - Implement login/logout methods
  - Implement wallet charge method with state updates
  - Implement plate add/remove methods with state updates
  - Implement transaction history loading
  - Add error handling and loading states
  - _Requirements: 5.1, 5.2, 5.7, 5.8_

- [x] 11.1 Write property test for UI state consistency after wallet charge



  - **Property 17: UI state consistency after wallet charge**
  - **Validates: Requirements 5.7**

- [x] 11.2 Write property test for UI state consistency after plate addition



  - **Property 18: UI state consistency after plate addition**
  - **Validates: Requirements 5.8**

- [x] 12. Create login screen UI




  - Create `LoginScreen` in `frontend/parking/lib/screens/login_screen.dart`
  - Implement phone number input field with validation
  - Add login button with loading state
  - Implement navigation to home screen on successful login
  - Add error message display
  - _Requirements: 5.1, 5.2_

- [x] 13. Create user home screen UI





  - Create `UserHomeScreen` in `frontend/parking/lib/screens/user_home_screen.dart`
  - Implement main screen layout with wallet card at top
  - Add "Charge Wallet" and "Add Plate" action buttons
  - Display list of registered plates
  - Add navigation to transaction history
  - Implement pull-to-refresh functionality
  - _Requirements: 5.2, 5.3, 5.4_

- [x] 14. Create wallet card widget





  - Create `WalletCard` widget in `frontend/parking/lib/widgets/wallet_card.dart`
  - Design credit card-sized widget displaying balance
  - Add visual styling (gradient, shadows, card-like appearance)
  - Display balance in formatted Rial currency
  - Add last updated timestamp
  - _Requirements: 2.1, 5.3_
- [x] 15. Create wallet charge dialog









- [ ] 15. Create wallet charge dialog

  - Create `WalletChargeDialog` in `frontend/parking/lib/widgets/wallet_charge_dialog.dart`
  - Implement amount input field with numeric keyboard
  - Add validation for positive amounts
  - Implement submit button with loading state
  - Show success/error feedback
  - _Requirements: 5.5, 5.7_
-

- [x] 16. Create add plate dialog




  - Create `AddPlateDialog` in `frontend/parking/lib/widgets/add_plate_dialog.dart`
  - Implement plate input fields (numbers and letters)
  - Add Iranian plate format validation
  - Implement submit button with loading state
  - Show success/error feedback
  - _Requirements: 5.6, 5.8_
-

- [x] 17. Create plate list widget




  - Create `PlateListItem` widget in `frontend/parking/lib/widgets/plate_list_item.dart`
  - Display plate in Iranian format with proper styling
  - Add delete button with confirmation dialog
  - Show registration date
  - _Requirements: 3.6, 5.8_
- [x] 18. Create transaction history screen













- [ ] 18. Create transaction history screen

  - Create `TransactionHistoryScreen` in `frontend/parking/lib/screens/transaction_history_screen.dart`
  - Display list of transactions in chronological order
  - Show transaction type, amount, and timestamp
  - Implement pagination or infinite scroll
  - Add filtering options (charges vs payments)
  - _Requirements: 2.6_
- [x] 19. Update main app structure for user authentication




- [ ] 19. Update main app structure for user authentication

  - Modify `main.dart` to add `UserProvider` to provider tree
  - Implement authentication check on app startup
  - Add routing logic to show login screen or home screen based on auth state
  - Update existing admin interface to coexist with user interface
  - _Requirements: 5.1, 5.2_

- [x] 20. Add flutter_secure_storage dependency




  - Update `pubspec.yaml` to include flutter_secure_storage package
  - Run flutter pub get
  - _Requirements: 4.2_

- [x] 21. Implement web-specific responsive layouts





  - Add responsive breakpoints for desktop web layout
  - Adjust wallet card size for larger screens
  - Optimize button layouts for mouse interaction
  - Ensure all functionality works identically on web
  - _Requirements: 6.1, 6.2, 6.4_
-

- [x] 22. Add Persian/Farsi localization for user interface








  - Add Persian translations for all user-facing text
  - Implement RTL layout support for Persian text
  - Format currency amounts with Persian number formatting
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_
- [x] 23. Checkpoint - Ensure all tests pass










- [ ] 23. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.
-

- [x] 24. Create API documentation







  - Document all new API endpoints with request/response examples
  - Add authentication requirements to endpoint documentation
  - Include error response examples
- [x] 25. Final integration testing and bug fixes




- [ ] 25. Final integration testing and bug fixes


- [ ] 25. Final integration testing and bug fixes

  - Test complete user journey from registration to automatic payment
  - Verify backward compatibility with existing parking system
  - Test edge cases (insufficient balance, duplicate plates, etc.)
  - Fix any discovered bugs
  - _Requirements: All_
-

- [x] 26. Final Checkpoint - Ensure all tests pass







  - Ensure all tests pass, ask the user if questions arise.
