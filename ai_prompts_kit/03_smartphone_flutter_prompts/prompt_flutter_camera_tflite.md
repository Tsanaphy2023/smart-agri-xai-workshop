# 📱 Prompt: สร้าง Flutter Mobile App ส่องกล้องวินิจฉัย Edge AI ออฟไลน์
> **เครื่องมือ:** VS Code, Cursor, Google Antigravity, Claude Code

```markdown
ช่วยออกแบบและเขียนโค้ด Flutter Application สำหรับสมาร์ทโฟน (Android / iOS) ส่องกล้องวินิจฉัยสุขภาพดินและโรคพืชแบบ Offline Edge AI โดยมีข้อกำหนดดังนี้:

1. **สถาปัตยกรรมระบบ (Architecture):**
   - Clean Architecture (MVVM ร่วมกับ Provider State Management)
   - Strict Null Safety, 0 warnings, ปราศจาก RenderFlex Overflow

2. **การทำงานของ Edge AI (Inference Engine):**
   - ใช้แพ็กเกจ `camera` และ `tflite_flutter`
   - โหลดโมเดลไฟล์ `assets/models/smart_agri_model.tflite` (Quantized Float32 [1, 224, 224, 3])
   - สกัดเฟรมภาพจากกล้องแบบเรียลไทม์ และทำนายผลลัพธ์ในเครื่อง 100% ไร้การเชื่อมต่ออินเทอร์เน็ต

3. **หน้าจอผู้ใช้งาน (UI/UX):**
   - ธีม Dark Obsidian (#090D16) ผสานเส้นแสงนีออนมรกต (#10B981)
   - หน้าจอกล้องมีกรอบเล็งเป้าหมาย (Target Reticle) กึ่งกลางหน้าจอ
   - ด้านล่างมีแถบการ์ด Floating Glassmorphic แสดง:
     * ชื่อกลุ่ม/โรคที่ตรวจพบ (เช่น "โรคราสนิม", "ขาดไนโตรเจน", "ดินร่วน")
     * แถบเปอร์เซ็นต์ความมั่นใจ (Confidence Bar)
     * ปุ่ม "บันทึกประวัติแปลงพร้อมพิกัด GPS"

4. **ผลลัพธ์ที่ต้องการ:**
   - โค้ด `pubspec.yaml`
   - โค้ด `lib/services/edge_ai_service.dart` สำหรับประมวลผล TFLite
   - โค้ด `lib/ui/screens/camera_detector_screen.dart` สำหรับแสดงผลหน้ากล้อง
```
