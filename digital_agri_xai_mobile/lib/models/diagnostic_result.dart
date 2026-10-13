class DiagnosticResult {
  final String domain; // Soil, Plant Diseases, Insects, Nutrient Deficiency
  final String className;
  final String thaiLabel;
  final double confidence;
  final String status; // Normal, Alert, Critical
  final String actionPlan;
  final DateTime timestamp;
  final double? latitude;
  final double? longitude;

  DiagnosticResult({
    required this.domain,
    required this.className,
    required this.thaiLabel,
    required this.confidence,
    required this.status,
    required this.actionPlan,
    required this.timestamp,
    this.latitude,
    this.longitude,
  });

  Map<String, dynamic> toMap() {
    return {
      'domain': domain,
      'className': className,
      'thaiLabel': thaiLabel,
      'confidence': confidence,
      'status': status,
      'actionPlan': actionPlan,
      'timestamp': timestamp.toIso8601String(),
      'latitude': latitude,
      'longitude': longitude,
    };
  }
}
