# 🎨 Prompt: สร้างภาพปก 3D Pixar และโค้ด TikZ ปกหน้าแบบ Full-Bleed
> **เครื่องมือ:** AI Image Generator (Midjourney / DALL-E / Imagen) + XeLaTeX / TikZ  
> **มาตรฐาน:** 6 × 9 นิ้ว, Aspect Ratio 2:3, Transparent Text Overlay ไร้กล่องทึบ

---

### 🖼️ ตอนที่ 1: พรอมพ์สั่งวาดภาพปกสไตล์ 3D Pixar (สำหรับ AI Image Generator)

คัดลอกพรอมพ์ภาษาอังกฤษด้านล่างนี้ไปสั่งใน Midjourney, DALL-E 3 หรือฟังก์ชัน `generate_image`:

```text
A stunning 3D Pixar and DreamWorks animation style textbook cover illustration for digital precision agriculture and soil AI diagnostics. 
In the center, a friendly young Thai scientist/agronomist and a sleek glowing cyber-leaf AI companion holding a high-tech smart soil probe with glowing LED sensors. 
Beneath them is a translucent cutaway of fertile agricultural soil showing rich layers, moisture, and root networks. 
Background features rolling green high-tech agricultural fields under a warm, glowing sunrise with soft golden hour light and cinematic studio rim lighting. 
The top one-third of the image has an open, clean sky with ample negative space specifically composed for typography overlay. 
The bottom area is grounded in deep, rich soil layers with clean space for author credits. 
Vibrant colors, rich emerald green, cyan glow, and warm sunlight. Ultra-detailed, 8k resolution, cinematic lighting, masterpiece, no text, no watermark, 2:3 aspect ratio.
```

---

### 💻 ตอนที่ 2: โค้ดแม่แบบ TikZ ปกนอก (`frontmatter/cover.tex`)

เมื่อได้ไฟล์ภาพปกแล้ว บันทึกเป็น `figures/cover_art.jpg` แล้วใช้โค้ดด้านล่างนี้ในไฟล์ `frontmatter/cover.tex`:

```latex
% frontmatter/cover.tex - High-Aesthetic Full-Bleed 3D Illustrated Cover
\begin{titlepage}
\thispagestyle{empty}
\begin{tikzpicture}[remember picture, overlay]

    % 1. ภาพพื้นหลังเต็มผืนกระดาษ ไร้ขอบ (Full-bleed 6x9 inch)
    \node[anchor=center, inner sep=0pt] at (current page.center) {
        \includegraphics[width=\paperwidth, height=\paperheight]{figures/cover_art.jpg}
    };

    % 2. ส่วนหัวเรื่องด้านบน (Transparent Text + Layered Drop Shadows บนท้องฟ้า)
    \begingroup
    \setlength{\XeTeXlinebreakskip}{0pt} % ป้องกันการกระจายพยางค์ผิดพลาด
    
    % แถบ Badge หมวดหมู่
    \node[anchor=north, align=center, text width=5.2in] at ([yshift=-0.45in]current page.north) {
        {\fontsize{8.5pt}{11pt}\selectfont\textbf{\textsf{HANDS-ON WORKSHOP HANDBOOK \textbullet\ เอกสารประกอบการอบรม}}}
    };
    
    % ชื่อเรื่องภาษาไทย บรรทัดที่ 1 (ซ้อนเงาสีขาวบางเพื่อความคมชัดบนฟ้าสว่าง)
    \node[anchor=north, align=center, text width=5.2in] at ([xshift=0.6pt, yshift=-0.74in]current page.north) {
        {\fontsize{18pt}{24pt}\selectfont\textbf{\textcolor{white}{คู่มือการจัดเตรียมชุดข้อมูลและการฝึกอบรม}}}
    };
    \node[anchor=north, align=center, text width=5.2in] at ([yshift=-0.75in]current page.north) {
        {\fontsize{18pt}{24pt}\selectfont\textbf{\textcolor{darkgray}{คู่มือการจัดเตรียมชุดข้อมูลและการฝึกอบรม}}}
    };

    % ชื่อเรื่องภาษาไทย บรรทัดที่ 2 (เน้นสีเขียวมรกตเข้ม / น้ำเงินเข้ม)
    \node[anchor=north, align=center, text width=5.2in] at ([xshift=0.6pt, yshift=-1.14in]current page.north) {
        {\fontsize{21pt}{28pt}\selectfont\textbf{\textcolor{white}{ปัญญาประดิษฐ์เพื่อเกษตรดิจิทัลและสิ่งแวดล้อม}}}
    };
    \node[anchor=north, align=center, text width=5.2in] at ([yshift=-1.15in]current page.north) {
        {\fontsize{21pt}{28pt}\selectfont\textbf{\textcolor{ForestGreen!85!black}{ปัญญาประดิษฐ์เพื่อเกษตรดิจิทัลและสิ่งแวดล้อม}}}
    };

    % ชื่อเรื่องภาษาอังกฤษ
    \node[anchor=north, align=center, text width=5.2in] at ([yshift=-1.55in]current page.north) {
        {\fontsize{8.5pt}{12pt}\selectfont\textbf{\textcolor{black!75}{DIGITAL AGRI xAI: SOIL \& CROP HEALTH DIAGNOSTICS}}}
    };
    \endgroup

    % 3. ข้อมูลผู้แต่งและสังกัดด้านล่าง (บนชั้นผิวดินเข้ม ใช้ตัวหนังสือสีขาว)
    \begingroup
    \setlength{\XeTeXlinebreakskip}{0pt}
    
    % ชื่อผู้แต่ง (สีขาวคมชัด)
    \node[anchor=south, align=center, text width=5.2in] at ([yshift=1.20in]current page.south) {
        {\fontsize{13pt}{17pt}\selectfont\textbf{\textcolor{white}{ผู้ช่วยศาสตราจารย์ ดร.ชีวะ ทัศนา}}}
    };

    % ตำแหน่งและสังกัด
    \node[anchor=south, align=center, text width=5.2in] at ([yshift=0.85in]current page.south) {
        {\fontsize{9pt}{13pt}\selectfont\textbf{\textcolor{white!90}{สาขาวิชาปัญญาประดิษฐ์เพื่อเกษตรดิจิทัลและสิ่งแวดล้อม คณะวิทยาศาสตร์และเทคโนโลยี}}}
    };
    
    % มหาวิทยาลัยและปี
    \node[anchor=south, align=center, text width=5.2in] at ([yshift=0.55in]current page.south) {
        {\fontsize{9pt}{13pt}\selectfont\textbf{\textcolor{white!85}{มหาวิทยาลัยราชภัฏรำไพพรรณี}}}
    };
    \node[anchor=south, align=center, text width=5.2in] at ([yshift=0.30in]current page.south) {
        {\fontsize{8pt}{11pt}\selectfont\textbf{\textcolor{amber!40!yellow}{โครงการบริการวิชาการ ประจำปีงบประมาณ ๒๕๖๗}}}
    };
    \endgroup

\end{tikzpicture}
\end{titlepage}
```
