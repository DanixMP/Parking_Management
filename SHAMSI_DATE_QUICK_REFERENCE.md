# Shamsi Date Quick Reference Card

## Import Statement
```dart
import 'package:parking/utils/date_utils.dart';
```

## Common Usage Patterns

### Display Current Date
```dart
// Simple date: 1403/09/10
String date = PersianDateUtils.getCurrentShamsiDate();

// With time: 14:30 - 1403/09/10
String dateTime = PersianDateUtils.getCurrentShamsiDateTime();
```

### Convert DateTime to Shamsi
```dart
DateTime now = DateTime.now();

// Basic: 1403/09/10
String shamsi = PersianDateUtils.toShamsiDate(now);

// With time: 14:30 - 1403/09/10
String shamsiTime = PersianDateUtils.toShamsiDateTime(now);

// Full: 1403 آذر 10
String full = PersianDateUtils.toShamsiFullDate(now);

// With day name: یکشنبه، 10 آذر 1403
String withDay = PersianDateUtils.toShamsiWithDayName(now);
```

### Format Time Only
```dart
DateTime now = DateTime.now();

// 14:30
String time = PersianDateUtils.formatTime(now);

// 14:30:45
String timeSeconds = PersianDateUtils.formatTimeWithSeconds(now);
```

### Parse String to DateTime
```dart
String isoString = "2024-11-30T14:30:00";
DateTime? dt = PersianDateUtils.parseDateTime(isoString);
```

### Format Duration
```dart
// 45 دقیقه
String duration1 = PersianDateUtils.formatDuration(45);

// 2 ساعت
String duration2 = PersianDateUtils.formatDuration(120);

// 2 ساعت و 30 دقیقه
String duration3 = PersianDateUtils.formatDuration(150);
```

### Format Currency
```dart
// 15,000 تومان
String price = PersianDateUtils.formatCurrency(15000);

// 1,250,000 تومان
String bigPrice = PersianDateUtils.formatCurrency(1250000);
```

### Date Comparisons
```dart
DateTime date1 = DateTime.now();
DateTime date2 = DateTime.now().subtract(Duration(days: 1));

// Check if same Shamsi day
bool same = PersianDateUtils.isSameDay(date1, date2);

// Check if today
bool today = PersianDateUtils.isToday(date1);
```

### Get Jalali Object
```dart
DateTime now = DateTime.now();
Jalali jalali = PersianDateUtils.toJalali(now);

print(jalali.year);   // 1403
print(jalali.month);  // 9
print(jalali.day);    // 10
```

## Widget Usage Examples

### Text Widget
```dart
Text(
  PersianDateUtils.toShamsiDate(entry.timestampIn),
  style: TextStyle(fontSize: 14),
)
```

### ListTile
```dart
ListTile(
  title: Text(entry.plate),
  subtitle: Text(
    'زمان: ${PersianDateUtils.toShamsiDateTime(entry.timestampIn)}',
  ),
)
```

### Card with Date
```dart
Card(
  child: Column(
    children: [
      Text(PersianDateUtils.toShamsiWithDayName(DateTime.now())),
      Text(PersianDateUtils.formatTime(DateTime.now())),
    ],
  ),
)
```

## Export Usage Examples

### Excel Export
```dart
final exportService = ExportService();

// Export entries
String? path = await exportService.exportEntriesToExcel(entries);

// Export exits
String? path = await exportService.exportExitsToExcel(exits);
```

### CSV Export
```dart
// Export entries to CSV
String? path = await exportService.exportEntriesToCSV(entries);

// Export exits to CSV
String? path = await exportService.exportExitsToCSV(exits);
```

### PDF Generation
```dart
// Generate entries PDF
await exportService.generateEntriesPDF(entries);

// Generate exits PDF with income
await exportService.generateExitsPDF(exits);

// Generate full report
await exportService.generateFullReportPDF(
  entries,
  exits,
  activeCars,
  capacity,
);
```

## Persian Month Names
```
1  = فروردین (Farvardin)
2  = اردیبهشت (Ordibehesht)
3  = خرداد (Khordad)
4  = تیر (Tir)
5  = مرداد (Mordad)
6  = شهریور (Shahrivar)
7  = مهر (Mehr)
8  = آبان (Aban)
9  = آذر (Azar)
10 = دی (Dey)
11 = بهمن (Bahman)
12 = اسفند (Esfand)
```

## Persian Day Names
```
1 = دوشنبه (Monday)
2 = سه‌شنبه (Tuesday)
3 = چهارشنبه (Wednesday)
4 = پنج‌شنبه (Thursday)
5 = جمعه (Friday)
6 = شنبه (Saturday)
7 = یکشنبه (Sunday)
```

## Date Format Patterns

### Standard Formats
```
1403/09/10              // Basic date
14:30 - 1403/09/10      // Date with time
1403 آذر 10             // Full date
یکشنبه، 10 آذر 1403     // With day name
```

### Time Formats
```
14:30                   // Time only
14:30:45                // Time with seconds
```

### Duration Formats
```
45 دقیقه                // Minutes only
2 ساعت                  // Hours only
2 ساعت و 30 دقیقه       // Hours and minutes
```

### Currency Format
```
15,000 تومان            // With thousand separator
1,250,000 تومان         // Large amounts
```

## Common Scenarios

### Display Entry Time
```dart
Text(
  'ورود: ${PersianDateUtils.toShamsiDateTime(entry.timestampIn)}',
)
```

### Display Exit with Duration
```dart
Column(
  children: [
    Text('خروج: ${PersianDateUtils.toShamsiDateTime(exit.timestampOut)}'),
    Text('مدت: ${PersianDateUtils.formatDuration(exit.duration)}'),
    Text('هزینه: ${PersianDateUtils.formatCurrency(exit.cost)}'),
  ],
)
```

### Display Today's Date in AppBar
```dart
AppBar(
  title: Text('گزارشات'),
  subtitle: Text(PersianDateUtils.getCurrentShamsiDate()),
)
```

### Filter by Today
```dart
final todayEntries = entries.where((entry) {
  return PersianDateUtils.isToday(entry.timestampIn);
}).toList();
```

### Sort by Shamsi Date
```dart
entries.sort((a, b) {
  final jalaliA = PersianDateUtils.toJalali(a.timestampIn);
  final jalaliB = PersianDateUtils.toJalali(b.timestampIn);
  return jalaliB.compareTo(jalaliA); // Descending
});
```

## Best Practices

1. **Always use Shamsi dates for display**
   - Store as DateTime in database
   - Convert to Shamsi for UI

2. **Use appropriate format for context**
   - Lists: `toShamsiDateTime()`
   - Cards: `toShamsiWithDayName()`
   - Tables: `toShamsiDate()` + `formatTime()`

3. **Handle null dates**
   ```dart
   String displayDate = date != null 
     ? PersianDateUtils.toShamsiDate(date)
     : 'تاریخ نامشخص';
   ```

4. **Use formatCurrency for all prices**
   ```dart
   Text(PersianDateUtils.formatCurrency(price))
   ```

5. **Use formatDuration for time periods**
   ```dart
   Text(PersianDateUtils.formatDuration(minutes))
   ```

## Testing Dates

### Create Test Dates
```dart
// Today
final today = DateTime.now();

// Yesterday
final yesterday = DateTime.now().subtract(Duration(days: 1));

// Specific date
final specific = DateTime(2024, 11, 30, 14, 30);

// Convert all to Shamsi
print(PersianDateUtils.toShamsiDate(today));
print(PersianDateUtils.toShamsiDate(yesterday));
print(PersianDateUtils.toShamsiDate(specific));
```

## Troubleshooting

### Issue: Date shows as Gregorian
```dart
// ❌ Wrong
Text(DateFormat('yyyy/MM/dd').format(date))

// ✅ Correct
Text(PersianDateUtils.toShamsiDate(date))
```

### Issue: Time not showing
```dart
// ❌ Wrong
Text(PersianDateUtils.toShamsiDate(date))

// ✅ Correct
Text(PersianDateUtils.toShamsiDateTime(date))
```

### Issue: Currency without separator
```dart
// ❌ Wrong
Text('$price تومان')

// ✅ Correct
Text(PersianDateUtils.formatCurrency(price))
```

---

**Quick Tip**: Import once, use everywhere! Add to your base widgets or create a mixin for common date operations.
