# 🏛️ Masterclass Prompt: วางโครงสร้างและจัดรูปแบบหนังสือตำราวิชาการ LaTeX ทั้งเล่ม
> **เครื่องมือ:** Google Antigravity, Cursor, VS Code, Claude Code  
> **เป้าหมาย:** สร้างโปรเจกต์หนังสือตำราวิชาการ XeLaTeX ภาษาไทย ขนาด 6 × 9 นิ้ว ตามมาตรฐาน `thai-academic-latex-formatting`

---

### 📋 คำสั่งพร้อมใช้ (คัดลอกลงในแชต AI):

```markdown
ช่วยออกแบบและสร้างโปรเจกต์หนังสือตำราวิชาการหรือคู่มือปฏิบัติการฉบับสมบูรณ์ ด้วยภาษา XeLaTeX ภาษาไทย ขนาดเล่ม 6 × 9 นิ้ว (Royal Octavo) ตามมาตรฐานสถาปัตยกรรมทางวิชาการชั้นสูง โดยมีข้อกำหนดทางเทคนิคดังนี้:

1. **โครงสร้างโปรเจกต์แบบโมดูลาร์ (Modular Architecture):**
   - แยกไฟล์เป็นสัดส่วน: `main.tex`, `preamble/packages.tex`, `preamble/typography.tex`, `preamble/headings.tex`, `preamble/captions.tex`
   - โฟลเดอร์ `frontmatter/` (ประกอบด้วย `cover.tex`, `titlepage.tex`, `preface.tex`)
   - โฟลเดอร์ `chapters/` สำหรับเนื้อหาแต่ละบท และ `appendices/` สำหรับภาคผนวก
   - สร้างสคริปต์ `build.sh` สำหรับคอมไพล์ด้วยคำสั่ง `xelatex -interaction=nonstopmode main.tex` 2 รอบ

2. **การตั้งค่าหน้ากระดาษและการจัดพิมพ์ภาษาไทย (Typography & Geometry):**
   - ขนาดกระดาษ: 6 × 9 นิ้ว (`\geometry{paperwidth=6in, paperheight=9in, inner=1.0in, outer=0.75in, top=0.85in, bottom=0.85in}`)
   - แบบอักษร: Sarabun (หรือ TH Sarabun New) กำหนดผ่าน `fontspec` มี Line Spacing 1.18 เท่า
   - ระบบตัดคำภาษาไทย:
     ```latex
     \XeTeXlinebreaklocale "th"
     \XeTeXlinebreakskip = 0pt plus 1pt
     ```
   - ย่อหน้าแรก: กำหนดระยะย่อหน้า 3em (`\setlength{\parindent}{3em}`) ไม่เว้นระยะระหว่างย่อหน้า (`\parskip=0pt`)
   - กำหนดให้ย่อหน้าแรกหลังหัวข้อย่อหน้า 3em เสมอด้วย `indentfirst`

3. **รูปแบบหัวข้อและการขึ้นบทใหม่ (Headings & Chapters):**
   - ใช้ตัวเลือก `openright, twoside` เพื่อให้ทุกบทและภาคผนวกเริ่มต้นที่หน้าคี่ (Odd / Right-hand page) เสมอ
   - ป้ายกำกับบทและชื่อบทจัดชิดขวา (`\raggedleft`) ตัวเลขบทตัวหนาขนาด 18-20pt
   - ใช้คำสั่ง `\needspace{5\baselineskip}` หน้าทุกหัวข้อ `\section` และ `\needspace{4\baselineskip}` หน้า `\subsection` เพื่อป้องกันหัวข้อหลุดไปอยู่บรรทัดสุดท้ายของหน้า

4. **รูปแบบคำบรรยายภาพและตาราง (Captions Specification):**
   - ใช้ป้าย `ภาพที่` และ `ตารางที่` คั่นด้วยเว้นวรรค 1 เคาะ (ห้ามมีเครื่องหมายโคลอน `:`)
   - คำบรรยายตารางทั้งหมดต้อง **จัดชิดซ้าย (Left-aligned)** เสมอ
   - ป้ายกำกับภาพและตารางต้องเป็นตัวหนา (`labelfont=bf`)

5. **สถาปัตยกรรมปกคู่ (Dual-Cover System):**
   - ปกนอก (`frontmatter/cover.tex`): ภาพประกอบ 3D Pixar สัดส่วน 2:3 แบบ Full-bleed TikZ โดยตัวหนังสือเป็นแบบ Transparent Text ซ้อนเงา (Drop Shadow) คมชัด 100% ไร้กล่องทึบบดบังภาพ
   - ปกใน (`frontmatter/titlepage.tex`): หน้าทางการวิชาการระบุชื่อเรื่อง, ชื่อผู้แต่ง (ผศ.ดร.ชีวะ ทัศนา), ภาควิชา, คณะ, มหาวิทยาลัย, และปีงบประมาณ

6. **ระบบการอ้างอิงและบรรณานุกรม (APA 7th Edition):**
   - จัดรูปแบบรายการเอกสารอ้างอิงแบบย่อหน้าแขวน (Hanging Indent 2.5em) ตามมาตรฐาน APA 7

โปรดเขียนโค้ดและสร้างไฟล์ทั้งหมดให้ครบถ้วน 100% ปราศจาก placeholder หรือข้อความย่อ!
```
