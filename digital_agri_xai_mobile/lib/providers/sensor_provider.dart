import 'dart:math';
import 'package:flutter/material.dart';
import '../models/soil_sensor_data.dart';

class SensorProvider extends ChangeNotifier {
  bool _isScanning = false;
  bool _isConnected = true;
  SoilSensorData _currentData = SoilSensorData(
    nitrogen: 68.5,
    phosphorus: 18.2,
    potassium: 142.0,
    ph: 5.85,
    moisture: 32.4,
    temperature: 28.6,
    timestamp: DateTime.now(),
    isConnected: true,
  );

  bool get isScanning => _isScanning;
  bool get isConnected => _isConnected;
  SoilSensorData get currentData => _currentData;

  Future<void> scanAndConnect() async {
    _isScanning = true;
    notifyListeners();
    await Future.delayed(const Duration(seconds: 1));
    _isConnected = true;
    _isScanning = false;
    _simulateNewReading();
    notifyListeners();
  }

  void _simulateNewReading() {
    final rand = Random();
    _currentData = SoilSensorData(
      nitrogen: 50 + rand.nextDouble() * 35,
      phosphorus: 15 + rand.nextDouble() * 20,
      potassium: 120 + rand.nextDouble() * 50,
      ph: 5.4 + rand.nextDouble() * 1.5,
      moisture: 25 + rand.nextDouble() * 20,
      temperature: 26 + rand.nextDouble() * 5,
      timestamp: DateTime.now(),
      isConnected: true,
    );
    notifyListeners();
  }

  void refreshSensor() {
    _simulateNewReading();
  }
}
