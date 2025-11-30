import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:parking/widgets/wallet_card.dart';
import 'package:parking/models/wallet.dart';

void main() {
  group('WalletCard Widget Tests', () {
    testWidgets('WalletCard displays balance correctly',
        (WidgetTester tester) async {
      // Create a test wallet
      final wallet = Wallet(
        id: 1,
        userId: 1,
        balance: 1500000,
        lastUpdated: DateTime(2024, 1, 15, 10, 30),
      );

      // Build the widget with proper sizing
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Center(
              child: SizedBox(
                width: 340,
                height: 200,
                child: WalletCard(wallet: wallet),
              ),
            ),
          ),
        ),
      );

      // Verify the widget renders
      expect(find.byType(WalletCard), findsOneWidget);

      // Verify balance is displayed with formatting
      expect(find.text('1,500,000'), findsOneWidget);

      // Verify currency label
      expect(find.text('ریال'), findsOneWidget);

      // Verify wallet title
      expect(find.text('کیف پول'), findsOneWidget);
    });

    testWidgets('WalletCard displays zero balance correctly',
        (WidgetTester tester) async {
      final wallet = Wallet(
        id: 1,
        userId: 1,
        balance: 0,
        lastUpdated: DateTime.now(),
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Center(
              child: SizedBox(
                width: 340,
                height: 200,
                child: WalletCard(wallet: wallet),
              ),
            ),
          ),
        ),
      );

      expect(find.text('0'), findsOneWidget);
    });

    testWidgets('WalletCard displays large balance with proper formatting',
        (WidgetTester tester) async {
      final wallet = Wallet(
        id: 1,
        userId: 1,
        balance: 123456789,
        lastUpdated: DateTime.now(),
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Center(
              child: SizedBox(
                width: 340,
                height: 200,
                child: WalletCard(wallet: wallet),
              ),
            ),
          ),
        ),
      );

      // Verify large number formatting
      expect(find.text('123,456,789'), findsOneWidget);
    });

    testWidgets('CompactWalletCard displays correctly',
        (WidgetTester tester) async {
      final wallet = Wallet(
        id: 1,
        userId: 1,
        balance: 500000,
        lastUpdated: DateTime.now(),
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Center(
              child: SizedBox(
                width: 280,
                height: 120,
                child: CompactWalletCard(wallet: wallet),
              ),
            ),
          ),
        ),
      );

      expect(find.byType(CompactWalletCard), findsOneWidget);
      expect(find.text('500,000'), findsOneWidget);
      expect(find.text('موجودی کیف پول'), findsOneWidget);
    });

    testWidgets('WalletCard has proper styling elements',
        (WidgetTester tester) async {
      final wallet = Wallet(
        id: 1,
        userId: 1,
        balance: 1000000,
        lastUpdated: DateTime.now(),
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Center(
              child: SizedBox(
                width: 340,
                height: 200,
                child: WalletCard(wallet: wallet),
              ),
            ),
          ),
        ),
      );

      // Verify wallet icon is present
      expect(find.byIcon(Icons.account_balance_wallet), findsOneWidget);

      // Verify credit card icon is present
      expect(find.byIcon(Icons.credit_card), findsOneWidget);

      // Verify last updated label
      expect(find.text('آخرین بروزرسانی'), findsOneWidget);
    });
  });
}
