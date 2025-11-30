import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:parking/widgets/add_plate_dialog.dart';
import 'package:parking/providers/user_provider.dart';
import 'package:provider/provider.dart';

void main() {
  group('AddPlateDialog Widget Tests', () {
    testWidgets('AddPlateDialog displays correctly',
        (WidgetTester tester) async {
      // Create a mock user provider
      final userProvider = UserProvider();

      // Build the widget
      await tester.pumpWidget(
        MaterialApp(
          home: ChangeNotifierProvider<UserProvider>.value(
            value: userProvider,
            child: const Scaffold(
              body: AddPlateDialog(),
            ),
          ),
        ),
      );

      // Verify the dialog renders
      expect(find.byType(AddPlateDialog), findsOneWidget);

      // Verify title
      expect(find.text('افزودن پلاک'), findsOneWidget);

      // Verify instruction text
      expect(
          find.text('لطفا اطلاعات پلاک خودرو را وارد کنید:'), findsOneWidget);

      // Verify input fields (3 TextFormFields for series, serial, region)
      expect(find.byType(TextFormField), findsNWidgets(3));

      // Verify letter dropdown
      expect(find.byType(DropdownButton<String>), findsOneWidget);

      // Verify action buttons
      expect(find.text('انصراف'), findsOneWidget);
      expect(find.widgetWithText(ElevatedButton, 'افزودن'), findsOneWidget);
    });

    testWidgets('AddPlateDialog validates empty series',
        (WidgetTester tester) async {
      final userProvider = UserProvider();

      await tester.pumpWidget(
        MaterialApp(
          home: ChangeNotifierProvider<UserProvider>.value(
            value: userProvider,
            child: const Scaffold(
              body: AddPlateDialog(),
            ),
          ),
        ),
      );

      // Find and tap the add button without entering series
      final addButton = find.widgetWithText(ElevatedButton, 'افزودن');
      await tester.tap(addButton);
      await tester.pump();

      // Verify validation error appears
      expect(find.text('الزامی'), findsAtLeastNWidgets(1));
    });

    testWidgets('AddPlateDialog validates series length',
        (WidgetTester tester) async {
      final userProvider = UserProvider();

      await tester.pumpWidget(
        MaterialApp(
          home: ChangeNotifierProvider<UserProvider>.value(
            value: userProvider,
            child: const Scaffold(
              body: AddPlateDialog(),
            ),
          ),
        ),
      );

      // Find series field (first TextFormField)
      final seriesField = find.byType(TextFormField).first;

      // Enter only 1 digit
      await tester.enterText(seriesField, '1');
      await tester.pump();

      // Tap add button
      final addButton = find.widgetWithText(ElevatedButton, 'افزودن');
      await tester.tap(addButton);
      await tester.pump();

      // Verify validation error
      expect(find.text('۲ رقم'), findsOneWidget);
    });

    testWidgets('AddPlateDialog validates serial length',
        (WidgetTester tester) async {
      final userProvider = UserProvider();

      await tester.pumpWidget(
        MaterialApp(
          home: ChangeNotifierProvider<UserProvider>.value(
            value: userProvider,
            child: const Scaffold(
              body: AddPlateDialog(),
            ),
          ),
        ),
      );

      // Find serial field (second TextFormField)
      final serialField = find.byType(TextFormField).at(1);

      // Enter only 2 digits
      await tester.enterText(serialField, '12');
      await tester.pump();

      // Tap add button
      final addButton = find.widgetWithText(ElevatedButton, 'افزودن');
      await tester.tap(addButton);
      await tester.pump();

      // Verify validation error
      expect(find.text('۳ رقم'), findsOneWidget);
    });

    testWidgets('AddPlateDialog validates region length',
        (WidgetTester tester) async {
      final userProvider = UserProvider();

      await tester.pumpWidget(
        MaterialApp(
          home: ChangeNotifierProvider<UserProvider>.value(
            value: userProvider,
            child: const Scaffold(
              body: AddPlateDialog(),
            ),
          ),
        ),
      );

      // Find region field (third TextFormField)
      final regionField = find.byType(TextFormField).at(2);

      // Enter only 1 digit
      await tester.enterText(regionField, '1');
      await tester.pump();

      // Tap add button
      final addButton = find.widgetWithText(ElevatedButton, 'افزودن');
      await tester.tap(addButton);
      await tester.pump();

      // Verify validation error
      expect(find.text('۲ رقم'), findsOneWidget);
    });

    testWidgets('AddPlateDialog shows preview when fields are filled',
        (WidgetTester tester) async {
      final userProvider = UserProvider();

      await tester.pumpWidget(
        MaterialApp(
          home: ChangeNotifierProvider<UserProvider>.value(
            value: userProvider,
            child: const Scaffold(
              body: AddPlateDialog(),
            ),
          ),
        ),
      );

      // Enter series
      await tester.enterText(find.byType(TextFormField).first, '12');
      await tester.pump();

      // Verify preview appears
      expect(find.text('پیش‌نمایش:'), findsOneWidget);

      // Enter serial
      await tester.enterText(find.byType(TextFormField).at(1), '345');
      await tester.pump();

      // Enter region
      await tester.enterText(find.byType(TextFormField).at(2), '67');
      await tester.pump();

      // Verify preview is updated
      expect(find.text('پیش‌نمایش:'), findsOneWidget);
    });

    testWidgets('AddPlateDialog letter dropdown works',
        (WidgetTester tester) async {
      final userProvider = UserProvider();

      await tester.pumpWidget(
        MaterialApp(
          home: ChangeNotifierProvider<UserProvider>.value(
            value: userProvider,
            child: const Scaffold(
              body: AddPlateDialog(),
            ),
          ),
        ),
      );

      // Verify default letter is 'الف'
      expect(find.text('الف'), findsOneWidget);

      // Tap dropdown to open it
      await tester.tap(find.byType(DropdownButton<String>));
      await tester.pumpAndSettle();

      // Select a different letter (ب)
      await tester.tap(find.text('ب').last);
      await tester.pumpAndSettle();

      // Verify the letter changed
      expect(find.text('ب'), findsOneWidget);
    });

    testWidgets('AddPlateDialog cancel button works',
        (WidgetTester tester) async {
      final userProvider = UserProvider();

      await tester.pumpWidget(
        MaterialApp(
          home: ChangeNotifierProvider<UserProvider>.value(
            value: userProvider,
            child: Builder(
              builder: (context) => Scaffold(
                body: Center(
                  child: ElevatedButton(
                    onPressed: () {
                      showDialog(
                        context: context,
                        builder: (context) => const AddPlateDialog(),
                      );
                    },
                    child: const Text('Show Dialog'),
                  ),
                ),
              ),
            ),
          ),
        ),
      );

      // Open the dialog
      await tester.tap(find.text('Show Dialog'));
      await tester.pumpAndSettle();

      // Verify dialog is shown
      expect(find.byType(AddPlateDialog), findsOneWidget);

      // Tap cancel button
      await tester.tap(find.text('انصراف'));
      await tester.pumpAndSettle();

      // Verify dialog is closed
      expect(find.byType(AddPlateDialog), findsNothing);
    });

    testWidgets('AddPlateDialog only accepts digits in number fields',
        (WidgetTester tester) async {
      final userProvider = UserProvider();

      await tester.pumpWidget(
        MaterialApp(
          home: ChangeNotifierProvider<UserProvider>.value(
            value: userProvider,
            child: const Scaffold(
              body: AddPlateDialog(),
            ),
          ),
        ),
      );

      // Try to enter non-digit characters in series field
      await tester.enterText(find.byType(TextFormField).first, 'abc');
      await tester.pump();

      // Verify the field is empty (non-digits filtered out)
      final seriesField =
          tester.widget<TextFormField>(find.byType(TextFormField).first);
      expect(seriesField.controller?.text, '');
    });
  });
}
