# 🧪 Prompt: สร้าง Flutter หน้าเชื่อมต่อเซนเซอร์ดิน NPK ผ่าน Bluetooth LE
> **เครื่องมือ:** VS Code, Cursor, Google Antigravity, Claude Code

```markdown
ช่วยออกแบบและเขียนโค้ด Flutter Screen สำหรับเชื่อมต่อหัวโพรบเซนเซอร์ดิน N-P-K และ pH ผ่าน Bluetooth Low Energy (BLE) โดยมีข้อกำหนดดังนี้:

1. **การเชื่อมต่อฮาร์ดแวร์ (BLE):**
   - ใช้แพ็กเกจ `flutter_blue_plus`
   - มีปุ่ม "ค้นหาอุปกรณ์เซนเซอร์รอบตัว (Scan Devices)"
   - เชื่อมต่อและอ่านค่า Characteristic ที่ส่งข้อมูลพารามิเตอร์ดิน (N, P, K, pH, Moisture, Temp)

2. **หน้าจอแดชบอร์ดเกจวัด (Sensor Telemetry UI):**
   - เกจวัดวงกลมหรือการ์ดสำหรับ:
     * ไนโตรเจน (N: 0-200 mg/kg)
     * ฟอสฟอรัส (P: 0-150 mg/kg)
     * โพแทสเซียม (K: 0-210 mg/kg)
     * ความเป็นกรด-ด่าง (pH: 3.5-9.5)
   - แถบสถานะการเชื่อมต่อ: แสดงไอคอน Bluetooth เขียว (Connected) หรือเทา (Disconnected) พร้อมปุ่ม Reconnect
   - ปุ่ม "คำนวณปุ๋ยสั่งตัดทันที" เมื่อกดจะคำนวณสูตรปุ๋ยที่แปลงต้องการตามค่าปัจจุบัน

3. **คุณภาพโค้ด:**
   - มี Mock Sensor Data สุ่มค่าจำลองให้อัตโนมัติในกรณีที่ยังไม่มีฮาร์ดแวร์จริง เพื่อให้ทดสอบหน้าจอได้ทันที
   - จัดการ Permission Bluetooth (Location, Nearby Devices) อย่างถูกต้อง
```
