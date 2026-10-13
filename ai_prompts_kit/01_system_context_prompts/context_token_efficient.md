# ⚡ Token-Efficient System Context (ประหยัดโทเค็น ~320 Tokens)
> **วิธีใช้:** คัดลอกข้อความด้านล่างนี้ไปวางที่ช่อง Custom Instructions, System Prompt หรือแนบไว้บนสุดของแชต AI เพื่อให้ AI เข้าใจบริบททั้งระบบโดยไม่เปลืองโทเค็น

```yaml
PROJECT: Digital Agri xAI Platform
AUTHOR: Asst. Prof. Dr. Chewa Thassana (RBRU Digital Agri-Physics)
DOMAINS:
  1_Soil: [Clay, Loam, Sand, Sandy Loam]
  2_Plant_Diseases: [Leaf Spot, Rust, Downy Mildew, Anthracnose, Root Rot]
  3_Insects: [Psyllid, Fruit Borer, Spider Mite]
  4_Nutrient_Deficiency: [N_Deficient, P_Deficient, K_Deficient, Healthy]
MODELS:
  Web_Server: smart_agri_model.onnx (ONNX Runtime, Input: 224x224 RGB Float32)
  Mobile_Edge: smart_agri_model.tflite (TensorFlow Lite, Quantized, <6MB)
SENSORS: N-P-K (mg/kg), pH (3.5-9.5), Moisture (%), Temp (°C), Rainfall (mm)
TECH_STACK:
  Web: Python 3.10+, Streamlit, FastAPI, Vanilla CSS Glassmorphism
  Mobile: Flutter 3.x, Dart, tflite_flutter, camera, flutter_blue_plus, Provider (MVVM)
CODING_RULES:
  - Clean Architecture, Zero RenderFlex Overflow, Strict Null Safety
  - Offline-First for Mobile, Sub-20ms Latency for Edge AI
  - UI Aesthetics: Dark Theme (#090D16), Emerald (#10B981), Cyan (#06B6D4)
```
