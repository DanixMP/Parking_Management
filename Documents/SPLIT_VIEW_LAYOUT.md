# 📐 Split View Layout - Camera & Activity

## New Layout Design

```
┌──────────────────────────────────────────────────────────────┐
│  [Capacity] [Active] [Free] [Price]  ← Compact Stats (1 Row) │
├──────────────────────────────────────────────────────────────┤
│ ┌────────────────────┬─────────────────────────────────────┐ │
│ │  Camera Zone       │  Activity Table                     │ │
│ │  (40% width)       │  (60% width)                        │ │
│ │                    │                                     │ │
│ │ 🎥 دوربین ورودی    │  📋 فعالیت‌های اخیر      [ریست]   │ │
│ │ [ورود][خروج] ●فعال│                                     │ │
│ │ ┌────────────────┐ │  ┌─────────────────────────────┐   │ │
│ │ │                │ │  │ Time  │ Plate  │ Type      │   │ │
│ │ │  Live Camera   │ │  ├───────┼────────┼───────────┤   │ │
│ │ │  Feed          │ │  │ 12:30 │ 12ب345 │ Entry ✓   │   │ │
│ │ │  (400px)       │ │  │ 12:45 │ 34د567 │ Exit 20K  │   │ │
│ │ │  YOLO AI       │ │  │ 13:00 │ 56ج789 │ Entry ✓   │   │ │
│ │ │                │ │  │ ...   │ ...    │ ...       │   │ │
│ │ └────────────────┘ │  └─────────────────────────────┘   │ │
│ │                    │                                     │ │
│ │ آخرین: 12ب345-67   │                                     │ │
│ │ اطمینان: 95%       │                                     │ │
│ │ تعداد: 5           │                                     │ │
│ │ وضعیت: آماده       │                                     │ │
│ └────────────────────┴─────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## Layout Breakdown

### Top Row: Compact Stats (Full Width)
- 4 stat cards in one row
- Capacity, Active, Free, Price
- Color-coded
- 80px height

### Main Content: Split View (2 Columns)

#### Left Column: Camera Zone (40%)
**Components:**
- Header with mode toggle
  - Title: "دوربین ورودی" or "دوربین خروجی"
  - Toggle buttons: [ورود] [خروج]
  - Status badge: ● فعال
- Camera preview (400px height)
  - Live webcam feed
  - YOLO AI overlay
  - Detection status
- Statistics panel
  - Last detected plate
  - Confidence percentage
  - Daily count
  - Camera status

#### Right Column: Activity Table (60%)
**Components:**
- Header with reset button
  - Icon + Title
  - Reset system button
- Activity table
  - Timestamps
  - Plate numbers
  - Entry/Exit type
  - Status/Cost
  - Scrollable list

## Features

### Camera Zone Features
✅ **Live Preview**: 400px height camera feed
✅ **Mode Toggle**: Switch Entry/Exit with one click
✅ **Status Indicator**: Green "فعال" badge
✅ **YOLO Overlay**: AI detection indicator
✅ **Real-time Stats**: Updates with each detection
✅ **Camera Status**: Shows initialization state

### Activity Table Features
✅ **Real-time Updates**: Auto-refreshes on detection
✅ **Scrollable**: Shows all recent activities
✅ **Color-coded**: Entry (green), Exit (red)
✅ **Detailed Info**: Time, plate, type, cost
✅ **Quick Reset**: One-click system reset

## Responsive Behavior

### Desktop (Wide Screen)
- Split view: 40% camera, 60% activity
- Camera: 400px height
- Table: Full height with scroll

### Tablet (Medium Screen)
- Split view maintained
- Slightly adjusted ratios
- Compact layout preserved

### Mobile (Future)
- Stack vertically
- Camera on top
- Activity below

## Benefits

### 1. Better Space Utilization
- Camera and activity visible simultaneously
- No scrolling needed
- All info at a glance

### 2. Improved Workflow
- Monitor camera while checking activity
- See detections appear in real-time
- Quick mode switching

### 3. Professional Look
- Clean, organized layout
- Balanced proportions
- Modern design

### 4. Efficient Monitoring
- Camera status always visible
- Activity log always accessible
- Quick actions available

## Color Scheme

**Camera Zone:**
- Entry mode: Green (#2E7D32)
- Exit mode: Red (#D32F2F)
- Background: Dark blue (#1E3A5F)
- Border: Mode color

**Activity Table:**
- Background: Dark blue (#1E3A5F)
- Text: White
- Icons: White70
- Reset button: Purple (#7B1FA2)

## Interaction Flow

### 1. Monitor Camera
- Watch live feed
- See YOLO AI indicator
- Check detection status

### 2. Switch Modes
- Click "ورود" for Entry mode
- Click "خروج" for Exit mode
- Camera stays active

### 3. View Activity
- See detections appear
- Check timestamps
- Verify plate numbers

### 4. Quick Actions
- Reset system if needed
- Refresh data
- Check statistics

## Technical Details

### Layout Structure
```dart
Row(
  children: [
    Expanded(flex: 2, child: CameraZone),  // 40%
    SizedBox(width: 12),
    Expanded(flex: 3, child: ActivityTable), // 60%
  ],
)
```

### Camera Zone Height
- Preview: 400px
- Stats panel: Auto
- Total: ~550px

### Activity Table
- Header: 60px
- Content: Remaining height
- Scrollable: Yes

## Advantages Over Previous Design

### Before (Full Width Camera)
- ❌ Had to scroll to see activity
- ❌ Camera took too much space
- ❌ Less efficient monitoring

### After (Split View)
- ✅ Everything visible at once
- ✅ Better space utilization
- ✅ Professional layout
- ✅ Easier monitoring

## Usage Tips

### For Monitoring
1. Keep app open on split view
2. Watch camera feed on left
3. Monitor activity on right
4. Toggle modes as needed

### For Testing
1. Entry mode: Show plate to camera
2. Wait for detection
3. See entry in activity table
4. Switch to Exit mode
5. Show same plate
6. See exit with cost

### For Operations
1. Monitor both zones
2. Quick mode switching
3. Real-time updates
4. Easy system reset

---

**Status**: ✅ Split view layout implemented
**Camera**: 40% width, 400px height
**Activity**: 60% width, full height
**Toggle**: Entry/Exit mode switching
**Ready**: For testing with live camera
