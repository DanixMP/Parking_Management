# 🎥🎥 Dual Camera Layout - Entry & Exit

## New Layout Design

```
┌──────────────────────────────────────────────────────────────┐
│  [Capacity] [Active] [Free] [Price]  ← Stats (1 Row)         │
├──────────────────────────────────────────────────────────────┤
│ ┌────────────────────────┬────────────────────────────────┐  │
│ │  Entry Camera          │  Exit Camera                   │  │
│ │  🎥 دوربین ورودی        │  🎥 دوربین خروجی               │  │
│ │  ● فعال  [▶]           │  ○ غیرفعال  [▶]               │  │
│ │ ┌────────────────────┐ │ ┌────────────────────────┐     │  │
│ │ │                    │ │ │                        │     │  │
│ │ │  Live Camera Feed  │ │ │  Dimmed Camera Feed    │     │  │
│ │ │  (Active)          │ │ │  (Inactive)            │     │  │
│ │ │  YOLO AI           │ │ │  [Paused Overlay]      │     │  │
│ │ │                    │ │ │                        │     │  │
│ │ └────────────────────┘ │ └────────────────────────┘     │  │
│ │ آخرین: 12ب345-67       │ آخرین: 34د567-89              │  │
│ │ اطمینان: 95%           │ اطمینان: 0%                   │  │
│ │ تعداد: 5               │ تعداد: 3                      │  │
│ └────────────────────────┴────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────┤
│  📋 فعالیت‌های اخیر (تشخیص خودکار)          [ریست سیستم]   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Time  │ Plate      │ Type        │ Status/Cost        │  │
│  ├───────┼────────────┼─────────────┼────────────────────┤  │
│  │ 12:30 │ 12ب345-67  │ Entry       │ ✓ Registered       │  │
│  │ 12:45 │ 34د567-89  │ Exit        │ ✓ Cost: 20,000     │  │
│  │ 13:00 │ 56ج789-01  │ Entry       │ ✓ Registered       │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## Layout Structure

### Top Row: Compact Stats
- 4 stat cards in one row
- Real-time updates

### Middle Row: Dual Camera View (50/50 Split)

#### Left: Entry Camera (Green Theme)
- **Header**: "دوربین ورودی" with entry icon
- **Status**: ● فعال (when active) or ○ غیرفعال (when inactive)
- **Activate Button**: [▶] to switch to this mode
- **Camera Feed**: 
  - Full brightness when active
  - 30% opacity when inactive
  - Overlay: "غیرفعال" when not active
- **Stats Panel**:
  - Last detected plate
  - Confidence percentage
  - Daily entry count

#### Right: Exit Camera (Red Theme)
- **Header**: "دوربین خروجی" with exit icon
- **Status**: ● فعال (when active) or ○ غیرفعال (when inactive)
- **Activate Button**: [▶] to switch to this mode
- **Camera Feed**:
  - Full brightness when active
  - 30% opacity when inactive
  - Overlay: "غیرفعال" when not active
- **Stats Panel**:
  - Last detected plate
  - Confidence percentage
  - Daily exit count

### Bottom: Activity Table (Full Width)
- Recent detections from both cameras
- Entry/Exit indicators
- Timestamps and costs
- Reset system button

## Key Features

### 1. Visual Mode Indication
- **Active Camera**: 
  - ● Filled radio button
  - Full brightness feed
  - Bold "فعال" text
  - Colored border (green/red)
  - YOLO AI overlay visible

- **Inactive Camera**:
  - ○ Empty radio button
  - 30% opacity feed
  - Regular "غیرفعال" text
  - Gray border
  - Pause overlay

### 2. Quick Mode Switching
- Click [▶] button on inactive camera
- Instantly switches detection mode
- Camera feed stays active
- Only detection mode changes

### 3. Same Webcam, Dual Display
- Uses single webcam
- Shows feed in both zones
- Active zone: full detection
- Inactive zone: preview only

### 4. Independent Statistics
- Entry camera: tracks entry count
- Exit camera: tracks exit count
- Last detected plate per mode
- Confidence per mode

## How It Works

### Detection Flow

**When Entry Camera is Active:**
1. Camera captures frame every 3 seconds
2. Sends to `/api/detect-entry/`
3. Registers entry automatically
4. Updates entry camera stats
5. Shows notification
6. Adds to activity table

**When Exit Camera is Active:**
1. Camera captures frame every 3 seconds
2. Sends to `/api/detect-exit/`
3. Calculates cost automatically
4. Updates exit camera stats
5. Shows notification with cost
6. Adds to activity table

### Mode Switching

**To Switch from Entry to Exit:**
1. Click [▶] button on Exit camera
2. Entry camera dims (30% opacity)
3. Exit camera brightens (100% opacity)
4. Detection switches to exit mode
5. Stats update for exit mode

**To Switch from Exit to Entry:**
1. Click [▶] button on Entry camera
2. Exit camera dims (30% opacity)
3. Entry camera brightens (100% opacity)
4. Detection switches to entry mode
5. Stats update for entry mode

## Visual States

### Active Camera
```
┌─────────────────────────┐
│ 🎥 دوربین ورودی          │
│ ● فعال                  │
├─────────────────────────┤
│                         │
│   [Live Feed 100%]      │
│   YOLO AI Active        │
│                         │
├─────────────────────────┤
│ آخرین: 12ب345-67        │
│ اطمینان: 95%            │
│ تعداد: 5                │
└─────────────────────────┘
```

### Inactive Camera
```
┌─────────────────────────┐
│ 🎥 دوربین خروجی    [▶]  │
│ ○ غیرفعال               │
├─────────────────────────┤
│  ╔═══════════════════╗  │
│  ║ [Dimmed Feed 30%] ║  │
│  ║   ⏸ غیرفعال       ║  │
│  ║ برای فعال‌سازی کلیک║  │
│  ╚═══════════════════╝  │
├─────────────────────────┤
│ آخرین: 34د567-89        │
│ اطمینان: 0%             │
│ تعداد: 3                │
└─────────────────────────┘
```

## Benefits

### 1. Professional Monitoring
- See both entry and exit zones
- Clear visual indication of active mode
- Quick mode switching
- Professional layout

### 2. Better Context
- See what both cameras would see
- Preview inactive camera
- Understand traffic flow
- Monitor both zones

### 3. Efficient Operation
- One-click mode switching
- No camera restart needed
- Instant mode change
- Continuous monitoring

### 4. Clear Status
- Always know which mode is active
- Visual feedback on both cameras
- Independent statistics
- Easy to understand

## User Interaction

### Monitoring
1. Watch both camera feeds
2. Active camera shows full brightness
3. Inactive camera shows preview
4. Check statistics on both

### Switching Modes
1. See vehicle approaching exit
2. Click [▶] on Exit camera
3. Exit camera activates
4. Entry camera dims
5. Detection switches to exit mode

### Verification
1. Check activity table
2. See entries and exits
3. Verify plate numbers
4. Check costs

## Technical Details

### Layout Ratios
- Entry Camera: 50% width
- Exit Camera: 50% width
- Gap: 12px
- Camera Height: 300px

### Opacity Levels
- Active camera: 100% opacity
- Inactive camera: 30% opacity
- Overlay: 54% black

### Border Styling
- Active: 2px colored border (green/red)
- Inactive: 1px gray border

### Status Indicators
- Active: ● (filled circle) + bold text
- Inactive: ○ (empty circle) + regular text

## Color Coding

**Entry Camera (Active):**
- Border: Green (#2E7D32)
- Status: Green background
- Icon: Green

**Exit Camera (Active):**
- Border: Red (#D32F2F)
- Status: Red background
- Icon: Red

**Inactive:**
- Border: Gray (#FFFFFF12)
- Status: Dark background
- Icon: Gray

## Advantages

### vs. Single Camera with Toggle
- ✅ See both zones simultaneously
- ✅ Preview inactive camera
- ✅ Better spatial awareness
- ✅ Professional appearance

### vs. Separate Physical Cameras
- ✅ Uses single webcam
- ✅ Lower cost
- ✅ Easier setup
- ✅ Same quality for both

## Use Cases

### Scenario 1: Entry Detection
1. Entry camera active (green, bright)
2. Exit camera inactive (gray, dimmed)
3. Vehicle approaches entry
4. Entry camera detects plate
5. Registers entry automatically

### Scenario 2: Exit Detection
1. Click [▶] on Exit camera
2. Exit camera active (red, bright)
3. Entry camera inactive (gray, dimmed)
4. Vehicle approaches exit
5. Exit camera detects plate
6. Calculates cost, registers exit

### Scenario 3: Monitoring Both
1. Watch both camera feeds
2. See entry and exit zones
3. Switch modes as needed
4. Monitor traffic flow

---

**Status**: ✅ Dual camera layout implemented
**Cameras**: Entry (left) + Exit (right)
**Mode**: Click [▶] to switch active camera
**Display**: Same webcam shown in both zones
**Detection**: Only active camera processes frames
**Ready**: For testing with live webcam
