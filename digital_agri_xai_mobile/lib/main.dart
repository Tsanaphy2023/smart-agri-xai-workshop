import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/theme/app_theme.dart';
import 'providers/scanner_provider.dart';
import 'providers/sensor_provider.dart';
import 'ui/screens/camera_scanner_screen.dart';
import 'ui/screens/soil_sensor_screen.dart';
import 'ui/screens/field_history_screen.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ScannerProvider()),
        ChangeNotifierProvider(create: (_) => SensorProvider()),
      ],
      child: const DigitalAgriApp(),
    ),
  );
}

class DigitalAgriApp extends StatelessWidget {
  const DigitalAgriApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Digital Agri xAI Mobile',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: const MainNavigationScreen(),
    );
  }
}

class MainNavigationScreen extends StatefulWidget {
  const MainNavigationScreen({super.key});

  @override
  State<MainNavigationScreen> createState() => _MainNavigationScreenState();
}

class _MainNavigationScreenState extends State<MainNavigationScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = const [
    CameraScannerScreen(),
    SoilSensorScreen(),
    FieldHistoryScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.camera_alt),
            label: 'สแกน AI กล้อง',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.sensors),
            label: 'เซนเซอร์ NPK',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.history),
            label: 'ประวัติแปลง',
          ),
        ],
      ),
    );
  }
}
