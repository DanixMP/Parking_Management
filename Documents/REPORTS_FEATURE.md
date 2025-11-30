# 📊 Reports & Analytics Feature

## Overview
Complete reports and analytics system with 4 tabs: Dashboard, Entries, Exits, and Archive.

## Features

### 1. Dashboard Tab
**Summary Cards:**
- Total Entries
- Total Exits  
- Active Cars
- Total Income

**Today's Statistics:**
- Entries today
- Exits today
- Income today
- Average parking duration

**Quick Actions:**
- Export today's data
- Go to archive

### 2. Entries Tab
**Features:**
- List all vehicle entries
- Entry ID, plate number, timestamp
- Export to Excel button
- Total count display

**Entry Card Shows:**
- Plate number (large, bold)
- Entry timestamp
- Entry ID
- Green theme

### 3. Exits Tab
**Features:**
- List all vehicle exits
- Exit details with cost
- Total income display
- Export to Excel button

**Exit Card Shows:**
- Plate number
- Exit timestamp
- Duration (minutes)
- Cost (IQD)
- Exit ID
- Red theme

### 4. Archive Tab
**Features:**
- Date selector
- Export options:
  - Today's entries
  - Today's exits
  - Full report
  - Income report

## Access

**From Home Screen:**
- Click the 📊 (assessment) icon in app bar
- Opens Reports screen

## UI Design

```
┌──────────────────────────────────────────────┐
│ گزارشات و آمار                    [🔄]      │
├──────────────────────────────────────────────┤
│ [داشبورد] [ورودی‌ها] [خروجی‌ها] [آرشیو]    │
├──────────────────────────────────────────────┤
│                                              │
│  Tab Content Here                            │
│                                              │
└──────────────────────────────────────────────┘
```

### Dashboard Layout
```
┌────────────┬────────────┐
│ Entries    │ Exits      │
│ 150        │ 145        │
└────────────┴────────────┘
┌────────────┬────────────┐
│ Active     │ Income     │
│ 5          │ 2,900,000  │
└────────────┴────────────┘

Today's Statistics:
- Entries: 150
- Exits: 145
- Income: 2,900,000 IQD
- Avg Duration: 120 min

[Export Today] [Archive]
```

### Entries List
```
┌─────────────────────────────────┐
│ 🟢 12ب345-67          #123      │
│ Entry: 12:30 - 2025/11/30       │
└─────────────────────────────────┘
┌─────────────────────────────────┐
│ 🟢 34د567-89          #124      │
│ Entry: 12:45 - 2025/11/30       │
└─────────────────────────────────┘
```

### Exits List
```
┌─────────────────────────────────┐
│ 🔴 12ب345-67          #123      │
│ Exit: 14:30 - 2025/11/30        │
│ ┌─────────────┬───────────────┐ │
│ │ Duration    │ Cost          │ │
│ │ 120 min     │ 40,000 IQD    │ │
│ └─────────────┴───────────────┘ │
└─────────────────────────────────┘
```

### Archive Options
```
┌─────────────────────────────────┐
│ 🟢 Export Today's Entries       │
│ All registered entries today    │
└─────────────────────────────────┘
┌─────────────────────────────────┐
│ 🔴 Export Today's Exits         │
│ All exits and income today      │
└─────────────────────────────────┘
┌─────────────────────────────────┐
│ 📄 Full Report                  │
│ Complete statistics             │
└─────────────────────────────────┘
┌─────────────────────────────────┐
│ 💰 Income Report                │
│ Financial details               │
└─────────────────────────────────┘
```

## Color Scheme

**Dashboard:**
- Entries: Green (#2E7D32)
- Exits: Red (#D32F2F)
- Active: Blue (#1976D2)
- Income: Orange (#FF9800)

**Cards:**
- Background: Dark Blue (#1E3A5F)
- Text: White
- Borders: Theme colors

## Calculations

### Total Income
```dart
Sum of all exit costs
```

### Average Duration
```dart
Total duration / Number of exits
```

### Today's Stats
```dart
Filter by today's date
Count entries, exits
Sum income
```

## Export Functionality

**Planned Features:**
- Export to Excel/CSV
- PDF reports
- Email reports
- Date range selection
- Custom filters

**Current Status:**
- UI complete
- Shows notifications
- TODO: Implement actual export

## Data Flow

```
Reports Screen
    ↓
ParkingProvider
    ↓
ApiService
    ↓
Django API
    ↓
Database
```

## API Endpoints Used

- `GET /api/entries/` - All entries
- `GET /api/exits/` - All exits
- `GET /api/active-cars/` - Active vehicles
- `GET /api/status/` - Current status

## Usage Examples

### View Dashboard
1. Open app
2. Click 📊 icon
3. See summary statistics

### View Entries
1. Go to Reports
2. Click "ورودی‌ها" tab
3. Scroll through entries
4. Click download to export

### View Exits
1. Go to Reports
2. Click "خروجی‌ها" tab
3. See exits with costs
4. Total income at top

### Export Data
1. Go to Reports
2. Click "آرشیو" tab
3. Select date (optional)
4. Choose export type
5. Click to download

## Future Enhancements

### Phase 1 (Current)
- ✅ Dashboard with statistics
- ✅ Entries list
- ✅ Exits list with costs
- ✅ Archive tab UI
- ⏳ Export functionality

### Phase 2
- [ ] Actual Excel export
- [ ] PDF generation
- [ ] Date range filters
- [ ] Search functionality
- [ ] Sort options

### Phase 3
- [ ] Charts and graphs
- [ ] Monthly reports
- [ ] Yearly statistics
- [ ] Revenue trends
- [ ] Peak hours analysis

### Phase 4
- [ ] Email reports
- [ ] Scheduled exports
- [ ] Custom report builder
- [ ] Advanced analytics
- [ ] Predictive insights

## Technical Details

### File Structure
```
lib/
├── screens/
│   ├── home_screen.dart
│   └── reports_screen.dart  ← New
├── providers/
│   └── parking_provider.dart (updated)
└── services/
    └── api_service.dart
```

### State Management
- Uses Provider pattern
- Loads data on tab open
- Refresh button available
- Real-time updates

### Performance
- Lazy loading
- Efficient list rendering
- Cached data
- Minimal rebuilds

## Testing Checklist

- [ ] Dashboard shows correct stats
- [ ] Entries list displays all entries
- [ ] Exits list shows costs
- [ ] Income calculation correct
- [ ] Average duration accurate
- [ ] Date selector works
- [ ] Export buttons show notifications
- [ ] Navigation works
- [ ] Refresh updates data
- [ ] Tabs switch smoothly

---

**Status**: ✅ UI Complete, Export TODO
**Access**: 📊 icon in home screen
**Tabs**: 4 (Dashboard, Entries, Exits, Archive)
**Features**: Statistics, Lists, Export options
**Ready**: For testing and data viewing
