class SoilSensorData {
  final double nitrogen; // mg/kg
  final double phosphorus; // mg/kg
  final double potassium; // mg/kg
  final double ph;
  final double moisture; // %
  final double temperature; // °C
  final DateTime timestamp;
  final bool isConnected;

  SoilSensorData({
    required this.nitrogen,
    required this.phosphorus,
    required this.potassium,
    required this.ph,
    required this.moisture,
    required this.temperature,
    required this.timestamp,
    this.isConnected = false,
  });

  // Tailored Fertilizer Recommendation based on Centroid Logic
  String get tailoredFertilizerRecommendation {
    if (ph < 5.5) {
      return 'ดินมีความเป็นกรดรุนแรง (pH ${ph.toStringAsFixed(1)}): ควรหว่านโดโลไมต์ 100-150 กก./ไร่ และงดปุ๋ยเคมีที่มีแอมโมเนียม';
    } else if (ph > 7.5) {
      return 'ดินด่างจัด (pH ${ph.toStringAsFixed(1)}): ควรใส่ยิปซัมการเกษตรหรือกำมะถันผงเพื่อลดค่า pH';
    }

    if (nitrogen < 50) {
      return 'ขาดไนโตรเจน (N): แนะนำปุ๋ยสูตร 46-0-0 หรือมูลค้างคาวเพื่อเร่งการแตกใบ';
    } else if (phosphorus < 20) {
      return 'ขาดฟอสฟอรัส (P): แนะนำปุ๋ยสูตร 18-46-0 เพื่อเสริมสร้างระบบรากและการออกดอก';
    } else if (potassium < 80) {
      return 'ขาดโพแทสเซียม (K): แนะนำปุ๋ยสูตร 0-0-60 เสริมสร้างเนื้อผลและความหวาน';
    } else {
      return 'ธาตุอาหารสมดุลดี: แนะนำปุ๋ยสูตรเสมอ 15-15-15 หรือ 16-16-16 ในอัตราปกติ';
    }
  }
}
