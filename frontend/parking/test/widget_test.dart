// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter_test/flutter_test.dart';

import 'package:parking/main.dart';
import 'package:parking/services/camera_service.dart';

void main() {
  testWidgets('App initialization test', (WidgetTester tester) async {
    // Create a mock camera service for testing
    final cameraService = CameraService();

    // Build our app and trigger a frame.
    await tester.pumpWidget(MyApp(cameraService: cameraService));

    // Verify that the app loads with authentication wrapper
    expect(find.byType(AuthenticationWrapper), findsOneWidget);
  });
}
