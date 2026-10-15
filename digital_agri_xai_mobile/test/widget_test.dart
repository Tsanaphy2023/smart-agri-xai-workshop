import 'package:flutter_test/flutter_test.dart';
import 'package:digital_agri_xai_mobile/main.dart';
import 'package:provider/provider.dart';
import 'package:digital_agri_xai_mobile/providers/scanner_provider.dart';
import 'package:digital_agri_xai_mobile/providers/sensor_provider.dart';

void main() {
  testWidgets('Digital Agri app initializes without crash', (WidgetTester tester) async {
    await tester.pumpWidget(
      MultiProvider(
        providers: [
          ChangeNotifierProvider(create: (_) => ScannerProvider()),
          ChangeNotifierProvider(create: (_) => SensorProvider()),
        ],
        child: const DigitalAgriApp(),
      ),
    );

    expect(find.byType(DigitalAgriApp), findsOneWidget);
  });
}
