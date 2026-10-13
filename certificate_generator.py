import os
import subprocess
import tempfile
import qrcode
from PIL import Image

CERT_LATEX_TEMPLATE = r"""\documentclass[landscape,a4paper]{article}
\usepackage[margin=1.5cm]{geometry}
\usepackage{fontspec}
\usepackage{xcolor}
\usepackage{tikz}
\usepackage{graphicx}

\setmainfont[
    Path = fonts/,
    BoldFont = THSarabun-Bold.ttf,
    ItalicFont = THSarabun-Italic.ttf,
    BoldItalicFont = THSarabun-BoldItalic.ttf
]{THSarabun.ttf}

\definecolor{golddark}{RGB}{180, 130, 20}
\definecolor{emeralddeep}{RGB}{6, 78, 59}
\definecolor{obsidian}{RGB}{15, 23, 42}
\definecolor{cybercyan}{RGB}{8, 145, 178}

\pagestyle{empty}

\begin{document}

\begin{tikzpicture}[remember picture, overlay]
    % Outer Frame
    \draw[line width=4.5pt, color=emeralddeep] 
        ([xshift=0.9cm,yshift=-0.9cm]current page.north west) 
        rectangle 
        ([xshift=-0.9cm,yshift=0.9cm]current page.south east);
        
    % Inner Gold Accent Frame
    \draw[line width=1.6pt, color=golddark] 
        ([xshift=1.15cm,yshift=-1.15cm]current page.north west) 
        rectangle 
        ([xshift=-1.15cm,yshift=1.15cm]current page.south east);

    % Thin Inner Border
    \draw[line width=0.6pt, color=emeralddeep!50] 
        ([xshift=1.35cm,yshift=-1.35cm]current page.north west) 
        rectangle 
        ([xshift=-1.35cm,yshift=1.35cm]current page.south east);

    % Corner Dots
    \fill[golddark] ([xshift=1.15cm,yshift=-1.15cm]current page.north west) circle (3.5pt);
    \fill[golddark] ([xshift=-1.15cm,yshift=-1.15cm]current page.north east) circle (3.5pt);
    \fill[golddark] ([xshift=1.15cm,yshift=1.15cm]current page.south west) circle (3.5pt);
    \fill[golddark] ([xshift=-1.15cm,yshift=1.15cm]current page.south east) circle (3.5pt);
\end{tikzpicture}

\begin{center}
    \vspace*{0.3cm}
    
    {\fontsize{22}{26}\selectfont\bfseries\color{obsidian} มหาวิทยาลัยราชภัฏรำไพพรรณี}\par
    \vspace{0.15cm}
    {\fontsize{16}{20}\selectfont\color{emeralddeep} ศูนย์วิจัยและบริการวิชาการเกษตรดิจิทัลและปัญญาประดิษฐ์ (Digital Agri xAI Center)}\par
    \vspace{0.5cm}
    
    {\fontsize{34}{40}\selectfont\bfseries\color{emeralddeep} เกียรติบัตรรับรองการฝึกอบรม}\par
    \vspace{0.15cm}
    {\fontsize{15}{18}\selectfont\color{golddark}\bfseries CERTIFICATE OF PROFESSIONAL TRAINING ACHIEVEMENT}\par
    \vspace{0.5cm}
    
    {\fontsize{18}{22}\selectfont ขอมอบเกียรติบัตรฉบับนี้เพื่อแสดงว่า}\par
    \vspace{0.4cm}
    
    {\fontsize{32}{36}\selectfont\bfseries\color{obsidian} __NAME__}\par
    \vspace{0.15cm}
    {\fontsize{16}{20}\selectfont\color{cybercyan}\bfseries __ORG__}\par
    \vspace{0.45cm}
    
    {\fontsize{17}{21}\selectfont ได้สำเร็จการฝึกอบรมเชิงปฏิบัติการหลักสูตรวิชาชีพขั้นสูง}\par
    \vspace{0.25cm}
    {\fontsize{22}{26}\selectfont\bfseries\color{emeralddeep} ``การพัฒนาปัญญาประดิษฐ์ตรวจวิเคราะห์ดินและสุขภาวะพืช (Digital Agri xAI)''}\par
    \vspace{0.2cm}
    {\fontsize{15}{19}\selectfont ครอบคลุมการสร้างโมเดล Machine Learning ใน Google Colab, สถาปัตยกรรม Edge AI ออฟไลน์บนมือถือ,\\และการเชื่อมต่อโทรมาตรเซนเซอร์ดิน NPK/pH ผ่าน Bluetooth Low Energy (BLE)}\par
    
\end{center}

\vfill

\noindent
\begin{minipage}[b]{0.30\textwidth}
    \begin{center}
        \includegraphics[width=2.5cm]{__QR_PATH__}\par
        \vspace{0.1cm}
        {\fontsize{11}{13}\selectfont รหัสตรวจสอบ: \textbf{__CERT_ID__}}\par
        {\fontsize{10}{12}\selectfont สแกน QR เพื่อตรวจสอบความถูกต้อง}
    \end{center}
\end{minipage}
\hfill
\begin{minipage}[b]{0.42\textwidth}
    \begin{center}
        {\fontsize{14}{17}\selectfont ออกให้ ณ วันที่ __DATE__}\par
        \vspace{0.8cm}
        \rule{5.5cm}{0.8pt}\par
        \vspace{0.15cm}
        {\fontsize{16}{19}\selectfont\bfseries (ผู้ช่วยศาสตราจารย์ ดร.ชีวะ ทัศนา)}\par
        {\fontsize{13}{16}\selectfont หัวหน้าโครงการวิจัยและผู้เชี่ยวชาญ Digital Agri-Physics}\par
        {\fontsize{12}{15}\selectfont มหาวิทยาลัยราชภัฏรำไพพรรณี}
    \end{center}
\end{minipage}

\end{document}
"""

def generate_certificate(name: str, org: str, cert_id: str, date_str: str = "13 ตุลาคม พ.ศ. 2569"):
    """
    Generates a high-quality printable PDF certificate and a PNG preview.
    Returns: (pdf_bytes, png_bytes or None)
    """
    # 1. Generate QR Code
    qr_dir = os.path.join(os.path.dirname(__file__), "docs", "certs")
    os.makedirs(qr_dir, exist_ok=True)
    qr_path = os.path.join(qr_dir, f"qr_{cert_id}.png")
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=6,
        border=1,
    )
    qr.add_data(f"https://github.com/Tsanaphy2023/smart-agri-xai-workshop/verify?id={cert_id}")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#0f172a", back_color="white")
    qr_img.save(qr_path)

    # 2. Populate LaTeX template
    content = (CERT_LATEX_TEMPLATE
        .replace("__NAME__", name)
        .replace("__ORG__", org)
        .replace("__CERT_ID__", cert_id)
        .replace("__DATE__", date_str)
        .replace("__QR_PATH__", qr_path)
    )

    tex_path = os.path.join(qr_dir, f"{cert_id}.tex")
    pdf_path = os.path.join(qr_dir, f"{cert_id}.pdf")
    png_prefix = os.path.join(qr_dir, f"preview_{cert_id}")

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(content)

    # 3. Compile with XeLaTeX
    try:
        subprocess.run(
            ["xelatex", "-interaction=nonstopmode", f"-output-directory={qr_dir}", tex_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except Exception as e:
        print(f"XeLaTeX compilation error: {e}")
        return None, None

    # Read PDF
    pdf_bytes = None
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

    # 4. Render PNG preview with pdftoppm
    png_bytes = None
    try:
        subprocess.run(["pdftoppm", "-png", "-r", "150", pdf_path, png_prefix], check=True)
        rendered_png = f"{png_prefix}-1.png"
        if os.path.exists(rendered_png):
            with open(rendered_png, "rb") as f:
                png_bytes = f.read()
    except Exception as e:
        print(f"pdftoppm rendering error: {e}")

    return pdf_bytes, png_bytes


if __name__ == "__main__":
    pdf_b, png_b = generate_certificate(
        name="นายพงศธร เกษตรก้าวหน้า",
        org="วิสาหกิจชุมชนเกษตรแปลงใหญ่ทุเรียนจันทบุรี",
        cert_id="RBRU-xAI-2026-0042",
        date_str="13 ตุลาคม พ.ศ. 2569"
    )
    print("PDF bytes:", len(pdf_b) if pdf_b else 0)
    print("PNG bytes:", len(png_b) if png_b else 0)
