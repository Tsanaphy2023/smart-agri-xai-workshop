#!/usr/bin/env bash
# ==============================================================================
# build.sh — สคริปต์คอมไพล์เอกสารตำราวิชาการ XeLaTeX ขนาด 6 x 9 นิ้ว
# ==============================================================================

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

XELATEX="/Library/TeX/texbin/xelatex"
if [ ! -x "$XELATEX" ]; then
    XELATEX="xelatex"
fi

echo "========================================================================"
echo " กำลังคอมไพล์เอกสารตำราวิชาการ: main.tex"
echo " เครื่องมือ: $XELATEX (XeLaTeX)"
echo " มาตรฐาน: thai-academic-latex-formatting (ขนาด 6 x 9 นิ้ว)"
echo "========================================================================"

# Pass 1: สร้างสารบัญและ cross-references
echo ">>> [รอบที่ 1/2] คอมไพล์ XeLaTeX..."
"$XELATEX" -interaction=nonstopmode main.tex

# Pass 2: อัปเดตเลขหน้า สารบัญภาพ สารบัญตาราง
echo ">>> [รอบที่ 2/2] คอมไพล์ XeLaTeX ครั้งที่ 2 เพื่ออัปเดตสารบัญ..."
"$XELATEX" -interaction=nonstopmode main.tex

echo "========================================================================"
if [ -f "main.pdf" ]; then
    echo " คอมไพล์สำเร็จเรียบร้อย! ไฟล์ผลลัพธ์: $DIR/main.pdf"
    ls -lh main.pdf
else
    echo " เกิดข้อผิดพลาด ไม่พบไฟล์ main.pdf"
    exit 1
fi
echo "========================================================================"
