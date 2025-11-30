# Export & Shamsi Date Testing Guide

## Quick Test Steps

### 1. Install Dependencies
```bash
cd frontend/parking
flutter pub get
```

### 2. Test Shamsi Date Display

#### Home Screen
1. Launch the app
2. Check "Recent Activity" table
3. Verify dates show as: `14:30 - 1403/09/10`

#### Reports Screen
1. Navigate to Reports
2. Check Dashboard tab - verify Shamsi dates
3. Check Entries tab - verify timestamps
4. Check Exits tab - verify timestamps
5. Check Archive tab - verify date selector shows Shamsi

### 3. Test Excel Export

#### Export Entries
1. Go to Reports → Entries tab
2. Click download icon (top right)
3. Check notification: "X ورودی به Excel ذخیره شد"
4. File saved to: `Documents/entries_[timestamp].xlsx`

#### Export Exits
1. Go to Reports → Exits tab
2. Click download icon
3. Check notification: "X خروجی به Excel ذخیره شد"
4. File saved to: `Documents/exits_[timestamp].xlsx`

#### Verify Excel Content
- Open generated Excel file
- Check headers are in Persian
- Verify dates are in Shamsi format (1403/09/10)
- Verify times are in 24-hour format (14:30)
- Check exit file has total income row

### 4. Test CSV Export

#### From Archive Tab
1. Go to Reports → Archive tab
2. Click "خروجی ورودی‌های امروز"
3. Select "CSV" from dialog
4. Check notification
5. File saved to: `Documents/entries_[timestamp].csv`

#### Verify CSV Content
- Open with text editor or Excel
- Check UTF-8 encoding (Persian text readable)
- Verify comma-separated values
- Check Shamsi dates present

### 5. Test PDF Generation

#### Full Report
1. Go to Reports → Archive tab
2. Click "گزارش کامل امروز"
3. Select "PDF" from dialog
4. PDF preview should open
5. Verify:
   - Title: "گزارش کامل روزانه"
   - Date in Shamsi: "تاریخ: 1403/09/10"
   - Statistics section
   - Entry/Exit tables
   - RTL text alignment

#### Income Report
1. Go to Reports → Archive tab
2. Click "گزارش درآمد"
3. PDF preview opens
4. Verify:
   - Title: "گزارش خروجی‌ها و درآمد"
   - Total income highlighted
   - Duration in minutes
   - Cost in Toman

### 6. Test Date Utilities

#### Create Test File
```dart
// test_dates.dart
import 'package:parking/utils/date_utils.dart';

void main() {
  final now = DateTime.now();
  
  print('Shamsi Date: ${PersianDateUtils.toShamsiDate(now)}');
  print('Shamsi DateTime: ${PersianDateUtils.toShamsiDateTime(now)}');
  print('Full Date: ${PersianDateUtils.toShamsiFullDate(now)}');
  print('With Day: ${PersianDateUtils.toShamsiWithDayName(now)}');
  print('Duration: ${PersianDateUtils.formatDuration(150)}');
  print('Currency: ${PersianDateUtils.formatCurrency(15000)}');
}
```

Expected Output:
```
Shamsi Date: 1403/09/10
Shamsi DateTime: 14:30 - 1403/09/10
Full Date: 1403 آذر 10
With Day: یکشنبه، 10 آذر 1403
Duration: 2 ساعت و 30 دقیقه
Currency: 15,000 تومان
```

### 7. Test Export Dialog

#### Format Selection
1. Go to Reports → Dashboard
2. Click "خروجی امروز" button
3. Dialog should show 3 options:
   - Excel (green icon)
   - CSV (blue icon)
   - PDF (red icon)
4. Select each and verify export works

### 8. Test Error Handling

#### No Data Export
1. Reset database (if available)
2. Try to export with no entries
3. Should handle gracefully (empty file or notification)

#### File Permission
1. Check app has storage permissions
2. Verify files are saved to accessible location

## Expected File Locations

### Windows
```
C:\Users\[Username]\Documents\
  - entries_[timestamp].xlsx
  - exits_[timestamp].xlsx
  - entries_[timestamp].csv
  - exits_[timestamp].csv
```

### Android
```
/storage/emulated/0/Documents/
  - entries_[timestamp].xlsx
  - exits_[timestamp].xlsx
  - entries_[timestamp].csv
  - exits_[timestamp].csv
```

## Verification Checklist

### Shamsi Dates
- [ ] Home screen shows Shamsi dates
- [ ] Reports dashboard shows Shamsi dates
- [ ] Entries list shows Shamsi timestamps
- [ ] Exits list shows Shamsi timestamps
- [ ] Archive date selector uses Shamsi
- [ ] PDF reports have Shamsi dates

### Excel Export
- [ ] Entries export creates .xlsx file
- [ ] Exits export creates .xlsx file
- [ ] Files open in Excel/LibreOffice
- [ ] Persian text displays correctly
- [ ] Shamsi dates in correct format
- [ ] Exit file has total income

### CSV Export
- [ ] Entries export creates .csv file
- [ ] Exits export creates .csv file
- [ ] UTF-8 encoding works
- [ ] Persian text readable
- [ ] Can import to Excel

### PDF Export
- [ ] Entry PDF generates
- [ ] Exit PDF generates
- [ ] Full report PDF generates
- [ ] Income report PDF generates
- [ ] RTL text alignment correct
- [ ] Persian text displays properly
- [ ] Tables formatted correctly

### UI/UX
- [ ] Export buttons visible
- [ ] Format selection dialog works
- [ ] Success notifications show
- [ ] Error notifications show
- [ ] Loading states work
- [ ] File paths shown (if applicable)

## Common Issues & Solutions

### Issue: Persian text shows as boxes
**Solution**: Ensure UTF-8 encoding in CSV exports

### Issue: PDF text alignment wrong
**Solution**: Already handled with TableHelper and RTL support

### Issue: Files not found
**Solution**: Check path_provider returns correct directory

### Issue: Excel file won't open
**Solution**: Verify excel package version and encoding

### Issue: Dates show as Gregorian
**Solution**: Check PersianDateUtils is imported and used

## Performance Notes

- Excel export: ~100ms for 100 entries
- CSV export: ~50ms for 100 entries
- PDF generation: ~200ms for full report
- Date conversion: <1ms per date

## Next Steps After Testing

1. Fix any bugs found
2. Optimize export performance if needed
3. Add export progress indicators
4. Implement file sharing options
5. Add export scheduling/automation
6. Create export templates
7. Add custom date range selection

---

**Test Date**: 1403/09/10 (2024-11-30)
**Tester**: [Your Name]
**Status**: Ready for Testing
