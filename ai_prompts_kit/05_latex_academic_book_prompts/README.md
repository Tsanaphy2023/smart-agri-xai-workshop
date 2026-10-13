# 📖 คู่มือการออกแบบและจัดทำตำราวิชาการ LaTeX ภาษาไทย
## Thai Academic LaTeX Book & Cover Architecture Guide (6 × 9 นิ้ว)
**อ้างอิงมาตรฐาน:** `thai-academic-latex-formatting` | **พัฒนาโดย:** ผศ.ดร.ชีวะ ทัศนา (RBRU Digital Agri-Physics)

---

### 🎯 วัตถุประสงค์
คู่มือและชุดคำสั่ง AI Prompt ชุดนี้ออกแบบมาเพื่อให้นักวิจัย คณาจารย์ และผู้เข้าร่วมกิจกรรมการอบรม สามารถใช้ AI (เช่น Cursor, Google Antigravity, VS Code Copilot, Claude Code) ออกแบบ จัดทำรูปเล่ม และจัดพิมพ์หนังสือตำราวิชาการ คู่มือปฏิบัติการ และรายงานวิจัยในรูปแบบ **XeLaTeX ภาษาไทย** คุณภาพระดับโรงพิมพ์สากล (Springer / MIT Press / Cambridge Standard)

---

### 📐 1. มาตรฐานกายภาพรูปเล่ม (Physical Book Profile)

| พารามิเตอร์ | ค่ามาตรฐานที่กำหนด | คำอธิบายและคำสั่ง LaTeX |
| :--- | :--- | :--- |
| **ขนาดรูปเล่ม (Trim Size)** | **6 × 9 นิ้ว** (Royal Octavo) | `\geometry{paperwidth=6in, paperheight=9in}` |
| **สัดส่วนภาพปก (Cover Ratio)** | **2:3 Aspect Ratio** | อัตราส่วนกว้างต่อยาวตรงกับขนาด 6 × 9 นิ้ว 100% |
| **ระยะขอบกระดาษ (Margins)** | Inner=1.0", Outer=0.75", Top/Bottom=0.85" | เว้นขอบในสำหรับเย็บเล่ม (Gutter/Binding) |
| **แบบอักษรหลัก (Font)** | **Sarabun** (หรือ TH Sarabun New) | ฟอนต์มาตรฐานสากล อ่านง่ายทั้งบนจอและกระดาษพิมพ์ |
| **ระยะห่างบรรทัด (Line Spacing)**| **1.18 เท่า** (`\setstretch{1.18}`) | ระยะห่างพอเหมาะกับวรรณยุกต์และสระภาษาไทย 4 ระดับ |
| **ระยะย่อหน้าแรก (Indent)** | **3em** (ไม่มีเว้นวรรคระหว่างย่อหน้า) | `\setlength{\parindent}{3em}`, `\parskip=0pt` |
| **ย่อหน้าแรกหลังหัวข้อ** | ย่อหน้า 3em เสมอ | ใช้แพ็กเกจ `indentfirst` และปรับแต่ง `\@afterheading` |
| **การขึ้นบทใหม่ (Chapter Open)**| **เริ่มหน้าคี่เสมอ (Odd / Right-hand page)** | ใช้ตัวเลือกคลาส `openright, twoside` |
| **หัวข้อบท (Chapter Heading)** | **ชิดขวา (Right-aligned)** | ตัวเลขบทตัวหนาเด่นชัด `\raggedleft` |

---

### 🎨 2. สถาปัตยกรรมปกคู่ (Dual-Cover Architecture)

หนังสือวิชาการสมัยใหม่ใช้ระบบปกคู่เพื่อแยกภาพลักษณ์ที่ดึงดูดใจออกจากข้อมูลทางการ:

1. **ปกนอก (Outer Cover - `frontmatter/cover.tex`):**
   * **ภาพประกอบ 3D Pixar / High-Aesthetic:** ตัวละครนักวิจัยน่ารัก เป็นมิตร ทันสมัย ร่วมกับระบบ AI และเกษตรดิจิทัล
   * **การวางตัวหนังสือแบบโปร่งใส (Transparent Text Overlay):** ไม่ใช้กล่องสี่เหลี่ยมทึบบดบังภาพวาด ใช้การซ้อนเงาตัวอักษร (Micro Drop-Shadow) เพื่อให้อ่านออกชัดเจน 100%
   * **การแก้ปัญหาสระลอยภาษาไทยบนปก:** ครอบหัวเรื่องด้วย `\begingroup\setlength{\XeTeXlinebreakskip}{0pt} ... \endgroup` ป้องกัน XeLaTeX กระจายพยางค์ในข้อความกึ่งกลาง
2. **ปกในวิชาการ (Inner Title Page - `frontmatter/titlepage.tex`):**
   * บันทึกข้อมูลวิชาการครบถ้วน: ชื่อหนังสือภาษาไทย-อังกฤษ, ชื่อผู้แต่งพร้อมตำแหน่งทางวิชาการ, สาขาวิชา, คณะ, มหาวิทยาลัย, ปีงบประมาณ, และตราสัญลักษณ์เวกเตอร์

---

### 🏷️ 3. การจัดรูปแบบคำบรรยายภาพและตาราง (Captions)

* **ภาพประกอบ:** ใช้ป้าย `ภาพที่ X.Y` คั่นด้วยเว้นวรรค (space) **ไม่มีเครื่องหมายโคลอน (:)**
* **ตาราง:** ใช้ป้าย `ตารางที่ X.Y` คั่นด้วยเว้นวรรค **ไม่มีโคลอน (:)** และ **จัดชิดซ้าย (Left-aligned) ทั้งเล่ม**
* **คำสั่งตั้งค่าส่วนกลาง:**
```latex
\DeclareCaptionLabelSeparator{space}{ }
\captionsetup{labelsep=space, labelfont=bf}
\captionsetup[table]{singlelinecheck=false, justification=raggedright, position=top}
\captionsetup[figure]{justification=centering, position=bottom}
\renewcommand{\figurename}{ภาพที่}
\renewcommand{\tablename}{ตารางที่}
```

---

### 📁 4. โครงสร้างโปรเจกต์แบบโมดูลาร์ (Modular Project Tree)

```text
my_academic_book/
├── main.tex                    # จุดรวมและคลาสารบัญหลัก
├── build.sh                    # สคริปต์คอมไพล์ XeLaTeX อัตโนมัติ (2-pass)
├── fonts/                      # ไฟล์ฟอนต์ Sarabun.ttf (Self-contained 100%)
│   ├── Sarabun-Regular.ttf
│   ├── Sarabun-Bold.ttf
│   ├── Sarabun-Italic.ttf
│   └── Sarabun-BoldItalic.ttf
├── preamble/                   # โมดูลตั้งค่าและแพ็กเกจ
│   ├── packages.tex            # โหลดแพ็กเกจ
│   ├── typography.tex          # ตั้งค่าฟอนต์ ตัดคำไทย และย่อหน้า 3em
│   ├── headings.tex            # รูปแบบบท หัวข้อ และ needspace
│   └── captions.tex            # ตั้งค่า ภาพที่ / ตารางที่ ไร้โคลอน
├── frontmatter/                # ส่วนนำ
│   ├── cover.tex               # ปกนอก 3D Pixar Full-bleed TikZ
│   ├── titlepage.tex           # ปกในทางการวิชาการ
│   └── preface.tex             # คำนิยม / คำนำ
├── chapters/                   # เนื้อหาแต่ละบท
│   ├── ch01_introduction.tex
│   ├── ch02_datasets.tex
│   └── ch03_edge_ai.tex
├── appendices/                 # ภาคผนวก
│   └── app_a_code_ref.tex
└── figures/                    # ภาพประกอบความละเอียดสูง
    ├── cover_art.jpg           # ภาพปกขนาด 2:3 (1600x2400 px)
    └── diagrams/
```
