# Flutter Frontend Integration Guide

## Overview
The Flutter frontend is fully integrated with the Django REST API backend, providing a modern, responsive UI for the parking management system.

## Project Structure

```
frontend/parking/
├── lib/
│   ├── main.dart                    # App entry point
│   ├── models/                      # Data models
│   │   ├── parking_status.dart      # Parking status model
│   │   ├── entry.dart               # Entry record model
│   │   ├── exit.dart                # Exit record model
│   │   └── active_car.dart          # Active car model
│   ├── providers/                   # State management
│   │   └── parking_provider.dart    # Main provider
│   ├── services/                    # API services
│   │   └── api_service.dart         # Django API client
│   ├── screens/                     # UI screens
│   │   └── home_screen.dart         # Main dashboard
│   └── widgets/                     # Reusable widgets
│       ├── status_card.dart         # Status display cards
│       ├── action_button.dart       # Action buttons
│       ├── recent_activity_table.dart # Activity table
│       └── settings_dialog.dart     # Settings dialog
├── pubspec.yaml                     # Dependencies
└── run_flutter_*.bat                # Launch scripts
```

## Features

### ✅ Implemented Features

1. **Real-time Status Dashboard**
   - Total capacity display
   - Active cars count
   - Free slots calculation
   - Hourly pricing display

2. **Vehicle Management**
   - Manual entry registration
   - Manual exit registration with cost calculation
   - Active cars list

3. **Settings Management**
   - Update parking capacity
   - Update hourly pricing
   - Database reset functionality

4. **Recent Activity**
   - Entry records table
   - Timestamp display
   - Plate number tracking

5. **Persian/RTL Support**
   - Right-to-left layout
   - Persian text support
   - Jalali date formatting

## Running the Application

### Option 1: Full System (Recommended)
From the project root:
```bash
start_full_system.bat
```
This starts both Django backend and Flutter frontend automatically.

### Option 2: Manual Start

#### Start Backend First
```bash
cd backend
start_django.bat
```

#### Then Start Frontend
```bash
cd frontend/parking
flutter run -d windows
```

Or use the batch files:
- `run_flutter_windows.bat` - Run on Windows
- `run_flutter_web.bat` - Run in Chrome browser

## API Integration

### API Service Configuration
The API base URL is configured in `lib/services/api_service.dart`:
```dart
static const String baseUrl = 'http://localhost:8000/api';
```

### Available API Methods

```dart
// Status
await apiService.getParkingStatus();

// Entries
await apiService.getEntries();
await apiService.registerEntry(plate, imagePath);

// Exits
await apiService.getExits();
await apiService.registerExit(plate, imagePath);

// Active Cars
await apiService.getActiveCars();

// Settings
await apiService.getSettings();
await apiService.updateSettings(capacity, pricePerHour);

// Reset
await apiService.resetDatabase();
```

## State Management

The app uses Provider for state management:

```dart
// Access provider in widgets
final provider = Provider.of<ParkingProvider>(context);

// Load data
await provider.loadParkingStatus();
await provider.loadActiveCars();
await provider.loadEntries();

// Register entry
bool success = await provider.registerEntry(plate, imagePath);

// Register exit
Map<String, dynamic>? result = await provider.registerExit(plate, imagePath);
```

## UI Components

### Status Cards
Display key metrics with icons and colors:
```dart
StatusCard(
  title: 'کل ظرفیت',
  value: '200',
  subtitle: 'جای پارکینگ',
  color: Color(0xFF1E3A5F),
  icon: Icons.local_parking,
)
```

### Action Buttons
Large, prominent buttons for main actions:
```dart
ActionButton(
  label: 'ثبت ورود خودرو',
  subtitle: '(تشخیص ورودی)',
  color: Color(0xFF2E7D32),
  icon: Icons.login,
  onPressed: () => _showEntryDialog(),
)
```

## Error Handling

The app includes comprehensive error handling:

1. **Connection Errors**
   - Displays error message if Django server is not running
   - Provides retry button
   - Shows helpful message to start the server

2. **API Errors**
   - Catches and displays API errors
   - Shows user-friendly Persian error messages
   - Maintains app stability

3. **Validation**
   - Validates plate numbers before submission
   - Checks for empty fields
   - Provides feedback on invalid inputs

## Customization

### Changing Colors
Edit the color scheme in `lib/main.dart`:
```dart
colorScheme: ColorScheme.fromSeed(
  seedColor: const Color(0xFF1E3A5F),
  brightness: Brightness.dark,
),
```

### Changing API URL
For production or different server:
```dart
// In lib/services/api_service.dart
static const String baseUrl = 'http://your-server:port/api';
```

### Adding New Features

1. **Add Model** (if needed)
   ```dart
   // lib/models/your_model.dart
   class YourModel {
     factory YourModel.fromJson(Map<String, dynamic> json) { ... }
   }
   ```

2. **Add API Method**
   ```dart
   // lib/services/api_service.dart
   Future<YourModel> getYourData() async {
     final response = await http.get(Uri.parse('$baseUrl/your-endpoint/'));
     return YourModel.fromJson(json.decode(response.body));
   }
   ```

3. **Add Provider Method**
   ```dart
   // lib/providers/parking_provider.dart
   Future<void> loadYourData() async {
     final data = await _apiService.getYourData();
     notifyListeners();
   }
   ```

4. **Update UI**
   ```dart
   // Use in widgets
   Consumer<ParkingProvider>(
     builder: (context, provider, child) {
       return YourWidget(data: provider.yourData);
     },
   )
   ```

## Dependencies

Current dependencies in `pubspec.yaml`:
- `http: ^1.1.0` - HTTP requests
- `provider: ^6.1.1` - State management
- `shamsi_date: ^1.0.1` - Persian/Jalali dates
- `intl: ^0.19.0` - Number formatting

## Building for Production

### Windows Desktop
```bash
flutter build windows --release
```
Output: `build/windows/runner/Release/`

### Web
```bash
flutter build web --release
```
Output: `build/web/`

### Android
```bash
flutter build apk --release
```
Output: `build/app/outputs/flutter-apk/`

## Troubleshooting

### Flutter Not Found
Install Flutter SDK: https://flutter.dev/docs/get-started/install

### Dependencies Error
```bash
cd frontend/parking
flutter pub get
```

### Connection Refused
Make sure Django backend is running on port 8000:
```bash
cd backend
python manage.py runserver 8000
```

### CORS Error
Verify your frontend URL is in Django's `CORS_ALLOWED_ORIGINS` in `backend/parking_api/settings.py`

### Hot Reload Not Working
Press `r` in the terminal or `R` for hot restart

## Next Steps

### Recommended Enhancements

1. **Camera Integration**
   - Add camera capture for entry/exit
   - Integrate with YOLO detection
   - Automatic plate recognition

2. **Reports & Analytics**
   - Daily/monthly reports
   - Revenue charts
   - Peak hours analysis

3. **User Authentication**
   - Admin login
   - Role-based access
   - Operator accounts

4. **Notifications**
   - Push notifications
   - Email alerts
   - SMS integration

5. **Advanced Features**
   - Reservation system
   - Monthly passes
   - Payment integration
   - Receipt printing

## Support

For issues or questions:
1. Check Django backend is running
2. Verify API endpoints in browser
3. Check Flutter console for errors
4. Review API_DOCUMENTATION.md for endpoint details

---

**Status**: ✅ Fully Integrated
**Last Updated**: November 30, 2025
