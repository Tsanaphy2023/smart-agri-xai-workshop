# 🖥️ Prompt: สร้าง Web App Dashboard ด้วย Streamlit
> **เครื่องมือ:** VS Code, Cursor, Google Antigravity, Claude Code

```markdown
ช่วยออกแบบและเขียนโค้ดเว็บแอปพลิเคชัน Dashboard สำหรับเกษตรแม่นยำ (Smart Agriculture) ด้วย Streamlit โดยมีข้อกำหนดดังนี้:

1. **ธีมและการออกแบบ (UI/UX):**
   - ธีม Glassmorphism ทันสมัย โทนสีมรกต (#10B981) และฟ้าไฮเทค (#06B6D4)
   - แถบสถานะระบบสด (Telemetry HUD Bar) ด้านบน มีไฟกระพริบ Online Beacon
   - รองรับการแสดงผล Responsive บนสมาร์ทโฟนและแท็บเล็ต

2. **ฟังก์ชันที่ต้องมี (Features):**
   - **แท็บ 1: Real-time Telemetry:** แสดงเกจวัด N-P-K (mg/kg), pH ดิน, ความชื้น และอุณหภูมิ พร้อมปุ่มโหลดพรีเซ็ตแปลงจริง (นาข้าว, สวนทุเรียนจันทบุรี, ข้าวโพด)
   - **แท็บ 2: AI Visual Diagnosis:** ลากวางภาพถ่ายดินหรือใบพืช แล้วส่งเข้าโมเดล `smart_agri_model.onnx` (ใช้ onnxruntime) หรือ mock inference แสดงค่าความมั่นใจ (%) ป้ายผลการวินิจฉัย และแผนคำแนะนำการปรับปรุงดิน
   - **แท็บ 3: Crop Recommender:** คำนวณพืชที่เหมาะสม 3 อันดับแรกตามค่า N-P-K และ pH พร้อมแผนปุ๋ยสั่งตัด
   - **แท็บ 4: Data Export:** ปุ่มดาวน์โหลดรายงานสรุปเป็น JSON และ Markdown

3. **คุณภาพโค้ด:**
   - เขียนโค้ดในไฟล์เดียว `app.py` ให้ทำงานได้ทันที
   - มีการจัดการข้อผิดพลาด (Exception Handling) ครบถ้วน
```
