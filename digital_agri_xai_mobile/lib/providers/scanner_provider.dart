import 'package:flutter/material.dart';
import '../models/diagnostic_result.dart';

class ScannerProvider extends ChangeNotifier {
  bool _isAnalyzing = false;
  DiagnosticResult? _lastResult;
  final List<DiagnosticResult> _history = [];

  bool get isAnalyzing => _isAnalyzing;
  DiagnosticResult? get lastResult => _lastResult;
  List<DiagnosticResult> get history => List.unmodifiable(_history);

  // Simulated In-Device TFLite Edge Inference
  Future<void> runDiagnostics({String? mockType}) async {
    _isAnalyzing = true;
    notifyListeners();

    await Future.delayed(const Duration(milliseconds: 650));

    final result = DiagnosticResult(
      domain: 'Plant Diseases (ทุเรียนจันทบุรี)',
      className: 'durian_anthracnose_leaf_blight',
      thaiLabel: 'โรคแอนแทรคโนสใบไหม้ (Colletotrichum)',
      confidence: 0.968,
      status: 'ตรวจพบโรคระดับปานกลาง',
      actionPlan: 'ตัดแต่งกิ่งที่เป็นโรค เผาทำลายนอกแปลง และฉีดพ่นสารคอปเปอร์ออกซีคลอไรด์หรืออะซอกซีสโตรบิน',
      timestamp: DateTime.now(),
      latitude: 12.6114,
      longitude: 102.1039,
    );

    _lastResult = result;
    _history.insert(0, result);
    _isAnalyzing = false;
    notifyListeners();
  }

  void clearCurrent() {
    _lastResult = null;
    notifyListeners();
  }
}
