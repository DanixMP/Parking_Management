import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:parking/widgets/plate_list_item.dart';
import 'package:parking/models/user_plate.dart';

void main() {
  group('PlateListItem Widget Tests', () {
    testWidgets('PlateListItem displays plate correctly',
        (WidgetTester tester) async {
      // Create a test user plate
      final userPlate = UserPlate(
        id: 1,
        userId: 1,
        plate: '12ب345-67',
        registeredAt: DateTime(2024, 1, 15, 10, 30),
        isActive: true,
      );

      bool deletePressed = false;

      // Build the widget
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: PlateListItem(
              userPlate: userPlate,
              onDelete: () {
                deletePressed = true;
              },
            ),
          ),
        ),
      );

      // Verify the widget renders
      expect(find.byType(PlateListItem), findsOneWidget);

      // Verify delete button is present
      expect(find.byIcon(Icons.delete_outline), findsOneWidget);

      // Verify registration date label
      expect(find.text('تاریخ ثبت:'), findsOneWidget);

      // Verify calendar icon
      expect(find.byIcon(Icons.calendar_today), findsOneWidget);
    });

    testWidgets('PlateListItem shows inactive status',
        (WidgetTester tester) async {
      final userPlate = UserPlate(
        id: 1,
        userId: 1,
        plate: '12ب345-67',
        registeredAt: DateTime.now(),
        isActive: false,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: PlateListItem(
              userPlate: userPlate,
              onDelete: () {},
            ),
          ),
        ),
      );

      // Verify inactive status is shown
      expect(find.text('غیرفعال'), findsOneWidget);
      expect(find.byIcon(Icons.warning_amber_rounded), findsOneWidget);
    });

    testWidgets(
        'PlateListItem hides delete button when showDeleteButton is false',
        (WidgetTester tester) async {
      final userPlate = UserPlate(
        id: 1,
        userId: 1,
        plate: '12ب345-67',
        registeredAt: DateTime.now(),
        isActive: true,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: PlateListItem(
              userPlate: userPlate,
              onDelete: () {},
              showDeleteButton: false,
            ),
          ),
        ),
      );

      // Verify delete button is not present
      expect(find.byIcon(Icons.delete_outline), findsNothing);
    });

    testWidgets('PlateListItem shows confirmation dialog on delete',
        (WidgetTester tester) async {
      final userPlate = UserPlate(
        id: 1,
        userId: 1,
        plate: '12ب345-67',
        registeredAt: DateTime.now(),
        isActive: true,
      );

      bool deletePressed = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: PlateListItem(
              userPlate: userPlate,
              onDelete: () {
                deletePressed = true;
              },
            ),
          ),
        ),
      );

      // Tap delete button
      await tester.tap(find.byIcon(Icons.delete_outline));
      await tester.pumpAndSettle();

      // Verify confirmation dialog appears
      expect(find.text('حذف پلاک'), findsOneWidget);
      expect(find.text('آیا از حذف این پلاک اطمینان دارید؟'), findsOneWidget);
      expect(find.text('این عملیات قابل بازگشت نیست.'), findsOneWidget);

      // Verify dialog buttons
      expect(find.text('انصراف'), findsOneWidget);
      expect(find.widgetWithText(ElevatedButton, 'حذف'), findsOneWidget);

      // Verify delete has not been called yet
      expect(deletePressed, false);
    });

    testWidgets('PlateListItem confirmation dialog cancel works',
        (WidgetTester tester) async {
      final userPlate = UserPlate(
        id: 1,
        userId: 1,
        plate: '12ب345-67',
        registeredAt: DateTime.now(),
        isActive: true,
      );

      bool deletePressed = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: PlateListItem(
              userPlate: userPlate,
              onDelete: () {
                deletePressed = true;
              },
            ),
          ),
        ),
      );

      // Tap delete button
      await tester.tap(find.byIcon(Icons.delete_outline));
      await tester.pumpAndSettle();

      // Tap cancel button
      await tester.tap(find.text('انصراف'));
      await tester.pumpAndSettle();

      // Verify dialog is closed
      expect(find.text('حذف پلاک'), findsNothing);

      // Verify delete was not called
      expect(deletePressed, false);
    });

    testWidgets('PlateListItem confirmation dialog delete works',
        (WidgetTester tester) async {
      final userPlate = UserPlate(
        id: 1,
        userId: 1,
        plate: '12ب345-67',
        registeredAt: DateTime.now(),
        isActive: true,
      );

      bool deletePressed = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: PlateListItem(
              userPlate: userPlate,
              onDelete: () {
                deletePressed = true;
              },
            ),
          ),
        ),
      );

      // Tap delete button
      await tester.tap(find.byIcon(Icons.delete_outline));
      await tester.pumpAndSettle();

      // Tap confirm delete button
      await tester.tap(find.widgetWithText(ElevatedButton, 'حذف'));
      await tester.pumpAndSettle();

      // Verify dialog is closed
      expect(find.text('حذف پلاک'), findsNothing);

      // Verify delete was called
      expect(deletePressed, true);
    });

    testWidgets('CompactPlateListItem displays correctly',
        (WidgetTester tester) async {
      final userPlate = UserPlate(
        id: 1,
        userId: 1,
        plate: '12ب345-67',
        registeredAt: DateTime(2024, 1, 15),
        isActive: true,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CompactPlateListItem(
              userPlate: userPlate,
            ),
          ),
        ),
      );

      // Verify the widget renders
      expect(find.byType(CompactPlateListItem), findsOneWidget);

      // Verify car icon is present
      expect(find.byIcon(Icons.directions_car), findsOneWidget);
    });

    testWidgets(
        'CompactPlateListItem shows delete button when onDelete provided',
        (WidgetTester tester) async {
      final userPlate = UserPlate(
        id: 1,
        userId: 1,
        plate: '12ب345-67',
        registeredAt: DateTime.now(),
        isActive: true,
      );

      bool deletePressed = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CompactPlateListItem(
              userPlate: userPlate,
              onDelete: () {
                deletePressed = true;
              },
            ),
          ),
        ),
      );

      // Verify delete button is present
      expect(find.byIcon(Icons.delete_outline), findsOneWidget);

      // Tap delete button
      await tester.tap(find.byIcon(Icons.delete_outline));
      await tester.pump();

      // Verify delete was called
      expect(deletePressed, true);
    });

    testWidgets(
        'CompactPlateListItem hides delete button when onDelete not provided',
        (WidgetTester tester) async {
      final userPlate = UserPlate(
        id: 1,
        userId: 1,
        plate: '12ب345-67',
        registeredAt: DateTime.now(),
        isActive: true,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CompactPlateListItem(
              userPlate: userPlate,
            ),
          ),
        ),
      );

      // Verify delete button is not present
      expect(find.byIcon(Icons.delete_outline), findsNothing);
    });

    testWidgets('CompactPlateListItem onTap works',
        (WidgetTester tester) async {
      final userPlate = UserPlate(
        id: 1,
        userId: 1,
        plate: '12ب345-67',
        registeredAt: DateTime.now(),
        isActive: true,
      );

      bool tapped = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CompactPlateListItem(
              userPlate: userPlate,
              onTap: () {
                tapped = true;
              },
            ),
          ),
        ),
      );

      // Tap the list tile
      await tester.tap(find.byType(ListTile));
      await tester.pump();

      // Verify onTap was called
      expect(tapped, true);
    });

    testWidgets('CompactPlateListItem shows inactive status with grey icon',
        (WidgetTester tester) async {
      final userPlate = UserPlate(
        id: 1,
        userId: 1,
        plate: '12ب345-67',
        registeredAt: DateTime.now(),
        isActive: false,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CompactPlateListItem(
              userPlate: userPlate,
            ),
          ),
        ),
      );

      // Find the car icon
      final iconFinder = find.byIcon(Icons.directions_car);
      expect(iconFinder, findsOneWidget);

      // Verify icon color is grey for inactive plates
      final icon = tester.widget<Icon>(iconFinder);
      expect(icon.color, Colors.grey);
    });
  });
}
