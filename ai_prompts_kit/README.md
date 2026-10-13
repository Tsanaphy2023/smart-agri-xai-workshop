# 🤖 Digital Agri xAI Prompt & Context Engineering Kit
คู่มือและคลังชุดคำสั่ง AI Prompt Engineering สำหรับผู้เข้าอบรม เพื่อใช้ออกแบบและสร้าง **Web Dashboard** และ **สมาร์ทโฟนแอปพลิเคชัน (Flutter)** ด้วยตนเอง
พัฒนาโดย: ผศ.ดร.ชีวะ ทัศนา (RBRU Digital Agri-Physics)

---

## 🎯 ปัญหาที่พบบ่อยและแนวทางแก้ไข
เมื่อผู้เรียนต้องการให้ AI (เช่น Cursor, VS Code Copilot, Google Antigravity, Claude Code) เขียนโค้ดให้ มักพบปัญหา:
1. **AI เขียนโค้ดไม่ตรงบริบท:** โมเดลไม่รู้ว่าเรามีโมเดลอะไร มีคลาสอะไรบ้าง
2. **เปลืองโทเค็น (Token Waste):** ก๊อปปี้เนื้อหาทั้งหมดไปแปะ ทำให้เปลืองโควตาและ AI สับสน
3. **โครงสร้างโค้ดไม่เป็นระเบียบ:** โค้ดปนกันในไฟล์เดียว บำรุงรักษายาก

คลังพรอมพ์ชุดนี้ถูกออกแบบตามมาตรฐาน **CLEAR Prompting Framework** และ **Token-Efficient Context Compression** เพื่อให้ผู้เรียนสามารถคัดลอกไปสั่งการ AI ได้ทันที โค้ดที่ได้จะสมบูรณ์ ไร้บั๊ก และนำไปต่อยอดได้จริง

---

## 📁 โครงสร้างชุดคำสั่งในโฟลเดอร์นี้

```text
ai_prompts_kit/
├── 01_system_context_prompts/
│   ├── context_token_efficient.md           # คอนเทกต์ระบบแบบประหยัดโทเค็น (~350 Tokens)
│   └── context_full_architecture.md         # คอนเทกต์ระบบสถาปัตยกรรมเชิงลึก
├── 02_web_dashboard_prompts/
│   ├── prompt_streamlit_dashboard.md        # สั่งสร้าง Streamlit Web Dashboard
│   └── prompt_fastapi_backend.md            # สั่งสร้าง FastAPI ONNX Backend
├── 03_smartphone_flutter_prompts/
│   ├── prompt_flutter_camera_tflite.md      # สั่งสร้างหน้าจอส่องกล้อง Edge AI ออฟไลน์
│   └── prompt_flutter_bluetooth_sensor.md   # สั่งสร้างหน้ารับค่าเซนเซอร์ NPK ผ่าน BLE
├── 04_config_templates/
│   ├── .cursorrules                         # สำหรับ Cursor Editor
│   ├── AGENTS.md                            # สำหรับ Google Antigravity & Agent IDEs
│   └── copilot-instructions.md              # สำหรับ VS Code GitHub Copilot
└── 05_latex_academic_book_prompts/
    ├── README.md                            # คู่มือการออกแบบและจัดทำตำราวิชาการ LaTeX (6x9 นิ้ว)
    ├── prompt_latex_book_full_architecture.md # พรอมพ์สั่งสร้างโครงสร้างโปรเจกต์ตำรา LaTeX ทั้งเล่ม
    ├── prompt_latex_cover_art_and_tikz.md   # พรอมพ์สั่งเจนภาพ 3D Pixar และโค้ด TikZ ปกโปร่งใส
    └── preamble_template_quickref.tex       # พรีแอมเบิลมาตรฐาน XeLaTeX ภาษาไทย (ย่อหน้า 3em ไร้โคลอน)
```
