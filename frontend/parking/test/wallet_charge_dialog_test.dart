import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:parking/widgets/wallet_charge_dialog.dart';
import 'package:parking/providers/user_provider.dart';
import 'package:provider/provider.dart';

void main() {
  group('WalletChargeDialog Widget Tests', () {
    testWidgets('WalletChargeDialog displays correctly',
        (WidgetTester tester) async {
      // Create a mock user provider
      final userProvider = UserProvider();

      // Build the widget
      await tester.pumpWidget(
        MaterialApp(
          home: ChangeNotifierProvider<UserProvider>.value(
            value: userProvider,
            child: const Scaffold(
              body: WalletChargeDialog(),
            ),
          ),
        ),
      );

      // Verify the dialog renders
      expect(find.byType(WalletChargeDialog), findsOneWidget);

      // Verify title (appears twice - in title and button)
      expect(find.text('شارژ کیف پول'), findsNWidgets(2));

      // Verify amount input field
      expect(find.byType(TextFormField), findsOneWidget);

      // Verify quick amount buttons
      expect(find.text('مبالغ پیشنهادی:'), findsOneWidget);

      // Verify action buttons
      expect(find.text('انصراف'), findsOneWidget);
      expect(
          find.widgetWithText(ElevatedButton, 'شارژ کیف پول'), findsOneWidget);
    });

    testWidgets('WalletChargeDialog validates empty input',
        (WidgetTester tester) async {
      final userProvider = UserProvider();

      await tester.pumpWidget(
        MaterialApp(
          home: ChangeNotifierProvider<UserProvider>.value(
            value: userProvider,
            child: const Scaffold(
              body: WalletChargeDialog(),
            ),
          ),
        ),
      );

      // Find and tap the charge button without entering amount
      final chargeButton = find.widgetWithText(ElevatedButton, 'شارژ کیف پول');
      await tester.tap(chargeButton);
      await tester.pump();

      // Verify validation error appears
      expect(find.text('لطفا مبلغ را وارد کنید'), findsOneWidget);
    });

    testWidgets('WalletChargeDialog validates zero amount',
        (WidgetTester tester) async {
      final userProvider = UserProvider();

      await tester.pumpWidget(
        MaterialApp(
          home: ChangeNotifierProvider<UserProvider>.value(
            value: userProvider,
            child: const Scaffold(
              body: WalletChargeDialog(),
            ),
          ),
        ),
      );

      // Enter zero amount
      await tester.enterText(find.byType(TextFormField), '0');
      await tester.pump();

      // Tap charge button
      final chargeButton = find.widgetWithText(ElevatedButton, 'شارژ کیف پول');
      await tester.tap(chargeButton);
      await tester.pump();

      // Verify validation error
      expect(find.text('مبلغ باید بیشتر از صفر باشد'), findsOneWidget);
    });

    testWidgets('WalletChargeDialog validates minimum amount',
        (WidgetTester tester) async {
      final userProvider = UserProvider();

      await tester.pumpWidget(
        MaterialApp(
          home: ChangeNotifierProvider<UserProvider>.value(
            value: userProvider,
            child: const Scaffold(
              body: WalletChargeDialog(),
            ),
          ),
        ),
      );

      // Enter amount below minimum
      await tester.enterText(find.byType(TextFormField), '5000');
      await tester.pump();

      // Tap charge button
      final chargeButton = find.widgetWithText(ElevatedButton, 'شارژ کیف پول');
      await tester.tap(chargeButton);
      await tester.pump();

      // Verify validation error
      expect(find.text('حداقل مبلغ شارژ ۱۰,۰۰۰ ریال است'), findsOneWidget);
    });

    testWidgets('WalletChargeDialog quick amount buttons work',
        (WidgetTester tester) async {
      final userProvider = UserProvider();

      await tester.pumpWidget(
        MaterialApp(
          home: ChangeNotifierProvider<UserProvider>.value(
            value: userProvider,
            child: const Scaffold(
              body: WalletChargeDialog(),
            ),
          ),
        ),
      );

      // Find and tap a quick amount button (100,000 Rials = 10,000 Toman)
      final quickButton = find.text('10,000 تومان').first;
      await tester.tap(quickButton);
      await tester.pump();

      // Verify the amount is filled in the text field
      final textField =
          tester.widget<TextFormField>(find.byType(TextFormField));
      expect(textField.controller?.text, '100000');
    });

    testWidgets('WalletChargeDialog cancel button works',
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
                        builder: (context) => const WalletChargeDialog(),
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
      expect(find.byType(WalletChargeDialog), findsOneWidget);

      // Tap cancel button
      await tester.tap(find.text('انصراف'));
      await tester.pumpAndSettle();

      // Verify dialog is closed
      expect(find.byType(WalletChargeDialog), findsNothing);
    });

    testWidgets('WalletChargeDialog displays info message',
        (WidgetTester tester) async {
      final userProvider = UserProvider();

      await tester.pumpWidget(
        MaterialApp(
          home: ChangeNotifierProvider<UserProvider>.value(
            value: userProvider,
            child: const Scaffold(
              body: WalletChargeDialog(),
            ),
          ),
        ),
      );

      // Verify info message is displayed
      expect(
        find.text(
            'موجودی شارژ شده برای پرداخت خودکار هزینه پارکینگ استفاده می‌شود'),
        findsOneWidget,
      );
    });
  });
}
