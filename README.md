# 🌱 Smart Soil & Plant AI Analyzer (Fullstack Edition)
**พัฒนาโดย:** ผศ.ดร.ชีวะ ทัศนา | มหาวิทยาลัยราชภัฏรำไพพรรณี

ระบบวิเคราะห์คุณภาพดิน สภาพแวดล้อม และสุขภาวะพืชอัจฉริยะ (Smart Agriculture Diagnostic Platform) รองรับทั้งการประมวลผลผ่าน Cloud AI, Local On-Device (Ollama) และโมเดลวิจัยเฉพาะทางแบบ In-Process Edge AI พร้อมระบบแนะนำพืชและวิเคราะห์ธาตุอาหารจากเซนเซอร์เคมีดิน

---

## 🚀 สรุปฟังก์ชันการทำงานหลัก (System Architecture)

### แท็บ 1: 📸 วิเคราะห์ภาพถ่ายดินและใบพืช (Visual Diagnostic AI)
1. **Quick Demo Presets:** ปุ่มเลือกภาพตัวอย่างด่วน (ใบพืชสมบูรณ์, ขาด N, ขาด P, ขาด K, ดินดำ, ดินลูกรัง, ดินเหนียว, ดินร่วนปนทราย) โหลดภาพและบริบทพื้นที่ทันทีโดยไม่ต้องค้นหาไฟล์
2. **Hybrid AI Engine Selector:**
   - ☁️ **Cloud API:** Google Gemini 2.5 Flash / 1.5 Flash (ฉลาดรอบด้าน ภาษาไทยสละสลวย)
   - 💻 **Local Runtime:** Ollama API (`localhost:11434`) ออฟไลน์ 100% บน Apple Silicon (แนะนำโมเดล `llava`)
   - 🎯 **Custom Edge AI:**
     - **In-Process Offline Engine (แนะนำ):** รันตรงในตัวแอป 100% ออฟไลน์ ไม่ต้องเปิดเซิร์ฟเวอร์ภายนอก ไร้ปัญหา Connection Refused
     - **External REST API:** เชื่อมต่อพอร์ต 8000 (มี Auto-fallback สลับมา In-Process ทันทีหากเซิร์ฟเวอร์ปิดอยู่)
3. **Structured Diagnostic Output:** แสดงผลสถานะปัญหา, อาการที่พบ, คำแนะนำเชิงปฏิบัติ, และค่าความมั่นใจ (Confidence Score)
4. **Export Diagnostic Report:** ปุ่มดาวน์โหลดรายงานผลเป็น **JSON** และ **Markdown Summary Card**

### แท็บ 2: 🧪 วิเคราะห์ธาตุอาหารเคมีและแนะนำพืช (Soil Sensor & Crop AI)
1. **Field Sensor Inputs:** รับค่า ไนโตรเจน (N), ฟอสฟอรัส (P), โพแทสเซียม (K), ค่าความเป็นกรด-ด่าง (pH), อุณหภูมิ, ความชื้น, ปริมาณน้ำฝน
2. **Sensor Presets:** ทางลัดจำลองค่าจากแปลงจริง เช่น นาข้าวชลประทาน, สวนไม้ผล/ทุเรียนจันทบุรี, ไร่ข้าวโพด, แปลงถั่วบำรุงดิน, สวนกาแฟ
3. **Crop Recommender Engine:** คำนวณความเหมาะสมของพืช 22 ชนิด (2,200 แปลงตัวอย่าง) แสดงผล 3 อันดับแรก พร้อมค่าความเหมาะสม (%) และค่า N-P-K-pH ที่เหมาะสมตามหลักวิชาการ
4. **Fertilizer Action Plan:** แนะนำการจัดการปุ๋ยสั่งตัดและปรับปรุงโครงสร้างดินอย่างแม่นยำ

### แท็บ 3: 🎓 สตูดิโอฝึกสอน AI ด้วยตัวเอง (No-Code AI Trainer Studio)
1. **No-Code 4-Step Pipeline:** ผู้เข้าอบรมที่ไม่มีพื้นฐานโปรแกรมสามารถเลือกชุดข้อมูล (ดิน 5 ชนิด, อาการขาด N-P-K, โรคทุเรียนจันทบุรี)
2. **Interactive Hyperparameters:** เลื่อนสไลเดอร์ปรับจำนวนรอบ Epochs (3-20), Batch Size และเปิดระบบ Data Augmentation
3. **Live Training Visualization:** กราฟเส้นความแม่นยำ (Validation Accuracy) และค่า Loss แบบ Real-time
4. **Instant Export & In-App Testing:** ดาวน์โหลดโมเดล `.onnx` และมีปุ่มคลิกเดียวส่งโมเดลใหม่ไปทดสอบในแท็บที่ 1 ทันที

---

## 🎓 สมุดงานสำหรับจัดอบรม (Workshop Notebook)
ผู้เข้าอบรมสามารถเปิดไฟล์สมุดงาน [Smart_Agri_AI_LowCode_Workshop.ipynb](file:///Users/chewathassana/Desktop/6_My_Business/6.2_Products_Services/smart-soil-ai/Smart_Agri_AI_LowCode_Workshop.ipynb) บน Google Colab ได้โดยตรง:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Tsanaphy2023/smart-agri-xai-workshop/blob/main/Smart_Agri_AI_LowCode_Workshop.ipynb)
- **โหมด Interactive Form:** ซ่อนโค้ด 100% มีเฉพาะฟอร์มภาษาไทยให้เลือก
- **เร่งความเร็วด้วย Free GPU (T4):** เทรนโมเดล MobileNetV3 เสร็จใน 1-2 นาที
- **ดาวน์โหลดไฟล์อัตโนมัติ:** เมื่อเทรนเสร็จ ระบบจะส่งออกไฟล์ `.onnx` ลงเครื่องทันที

---

## 🛠️ วิธีการรันใช้งาน

### 1. รันเว็บแอปพลิเคชัน (Streamlit Web App)
```bash
cd "/Users/chewathassana/Desktop/6_My_Business/6.2_Products_Services/smart-soil-ai"
./run.sh
```
หรือรันผ่าน Virtual Environment โดยตรง:
```bash
source .venv/bin/activate
streamlit run app.py
```
เปิดใช้งานที่: `http://localhost:8501` (หรือ `8502`)

### 2. (ทางเลือก) รัน REST API Microservice สำหรับอุปกรณ์ Edge / Flutter
หากต้องการเปิด REST Endpoint บนพอร์ต 8000 ให้กับแอปมือถือหรืออุปกรณ์ภายนอก:
```bash
source .venv/bin/activate
python server.py
```
- Endpoint ตรวจสอบสถานะ: `GET http://localhost:8000/health`
- Endpoint วิเคราะห์ภาพ: `POST http://localhost:8000/predict`
- Endpoint แนะนำพืช: `POST http://localhost:8000/recommend_crops`

---

## 💡 แนวทางการแก้ปัญหาข้อผิดพลาดที่พบบ่อย (Troubleshooting)

| ข้อผิดพลาดที่พบ | สาเหตุ | วิธีการแก้ไข |
| :--- | :--- | :--- |
| **`Errno 61 Connection refused` (พอร์ต 8000)** | เลือกโหมด Custom Model แต่ไม่ได้เปิดเซิร์ฟเวอร์ภายนอกไว้ | ในแอปใหม่นี้ ระบบมี **In-Process Engine** ในตัวเป็นค่าเริ่มต้น ซึ่งรันได้ทันทีโดยไม่ต้องเปิดเซิร์ฟเวอร์ หรือหากเลือก REST API ระบบจะ Auto-fallback ให้ทันที |
| **`unknown model architecture: 'mllama'` (Ollama HTTP 500)** | เลือกโมเดล `llama3.2-vision` แต่ Ollama ในเครื่องยังเป็นเวอร์ชันเก่า | 1. สลับไปใช้โมเดล **`llava`** ในแถบด้านซ้าย (รองรับ 100% ทุกเวอร์ชัน)<br>2. หรืออัปเดต Ollama ด้วยคำสั่ง `brew upgrade ollama` ใน Terminal |
