import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/app_theme.dart';
import '../../providers/sensor_provider.dart';

class SoilSensorScreen extends StatelessWidget {
  const SoilSensorScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final sensor = context.watch<SensorProvider>();
    final data = sensor.currentData;

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('🧪 เซนเซอร์ดิน NPK & pH (BLE)'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => sensor.refreshSensor(),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 1. Connection Status Bar
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: AppTheme.surface,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.white12),
              ),
              child: Row(
                children: [
                  Container(
                    width: 10,
                    height: 10,
                    decoration: const BoxDecoration(
                      shape: BoxShape.circle,
                      color: AppTheme.primaryEmerald,
                    ),
                  ),
                  const SizedBox(width: 10),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'RS485 SOIL PROBE: CONNECTED (BLE)',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: AppTheme.primaryEmerald,
                            letterSpacing: 0.5,
                          ),
                        ),
                        Text(
                          'MAC: C4:5B:BE:88:12:FA | RSSI: -62 dBm',
                          style: TextStyle(fontSize: 10.5, color: AppTheme.textMuted),
                        ),
                      ],
                    ),
                  ),
                  ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.surfaceCard,
                      foregroundColor: AppTheme.secondaryCyan,
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      textStyle: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                    ),
                    onPressed: sensor.isScanning ? null : () => sensor.scanAndConnect(),
                    child: Text(sensor.isScanning ? 'ค้นหา...' : 'สแกนซ้ำ'),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 18),

            // 2. Telemetry Grid (N, P, K, pH)
            Row(
              children: [
                Expanded(
                  child: _buildMetricCard(
                    title: 'ไนโตรเจน (N)',
                    value: '${data.nitrogen.toStringAsFixed(1)} mg/kg',
                    status: data.nitrogen < 50 ? 'ต่ำกว่าเกณฑ์' : 'เหมาะสม',
                    accentColor: AppTheme.primaryEmerald,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildMetricCard(
                    title: 'ฟอสฟอรัส (P)',
                    value: '${data.phosphorus.toStringAsFixed(1)} mg/kg',
                    status: data.phosphorus < 20 ? 'ค่อนข้างต่ำ' : 'เหมาะสม',
                    accentColor: AppTheme.secondaryCyan,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildMetricCard(
                    title: 'โพแทสเซียม (K)',
                    value: '${data.potassium.toStringAsFixed(1)} mg/kg',
                    status: data.potassium > 100 ? 'อุดมสมบูรณ์' : 'ปานกลาง',
                    accentColor: AppTheme.accentAmber,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildMetricCard(
                    title: 'ความเป็นกรด-ด่าง (pH)',
                    value: data.ph.toStringAsFixed(2),
                    status: data.ph < 6.0 ? 'กรดอ่อน' : 'ปานกลาง',
                    accentColor: const Color(0xFFA855F7),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),

            // 3. Environmental Bar (Moisture & Temperature)
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: AppTheme.surface,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.white10),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.water_drop, color: AppTheme.secondaryCyan, size: 20),
                      const SizedBox(width: 6),
                      Text(
                        'ความชื้น: ${data.moisture.toStringAsFixed(1)}%',
                        style: const TextStyle(fontSize: 13, color: Colors.white),
                      ),
                    ],
                  ),
                  Row(
                    children: [
                      const Icon(Icons.thermostat, color: AppTheme.accentAmber, size: 20),
                      const SizedBox(width: 6),
                      Text(
                        'อุณหภูมิดิน: ${data.temperature.toStringAsFixed(1)}°C',
                        style: const TextStyle(fontSize: 13, color: Colors.white),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // 4. Tailored Fertilizer Recommendation Card
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    AppTheme.primaryEmerald.withOpacity(0.15),
                    AppTheme.surfaceCard,
                  ],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: AppTheme.primaryEmerald.withOpacity(0.3)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.psychology, color: AppTheme.primaryEmerald, size: 22),
                      SizedBox(width: 8),
                      Text(
                        'แผนคำนวณปุ๋ยสั่งตัดรายแปลง (xAI Tailored Plan)',
                        style: TextStyle(
                          fontSize: 14.5,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Text(
                    data.tailoredFertilizerRecommendation,
                    style: const TextStyle(
                      fontSize: 13,
                      color: AppTheme.textMain,
                      height: 1.45,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetricCard({
    required String title,
    required String value,
    required String status,
    required Color accentColor,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surfaceCard,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: accentColor.withOpacity(0.25)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(fontSize: 12, color: AppTheme.textMuted),
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: accentColor,
            ),
          ),
          const SizedBox(height: 6),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
            decoration: BoxDecoration(
              color: accentColor.withOpacity(0.12),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              status,
              style: TextStyle(fontSize: 10.5, color: accentColor, fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
    );
  }
}
