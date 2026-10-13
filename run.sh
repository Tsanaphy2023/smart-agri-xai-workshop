#!/bin/bash
cd "$(dirname "$0")"

# 1. สร้าง Virtual Environment ถ้ายังไม่มี
if [ ! -d ".venv" ]; then
    echo "📦 กำลังสร้าง Virtual Environment (.venv)..."
    python3 -m venv .venv
fi

# 2. เปิดใช้งาน Virtual Environment
source .venv/bin/activate

# 3. ตรวจสอบและติดตั้ง Dependencies
if ! command -v streamlit &> /dev/null; then
    echo "📥 กำลังติดตั้ง Dependencies (streamlit, google-genai, pillow, python-dotenv)..."
    python3 -m pip install -r requirements.txt
fi

# 4. สั่งรันแอปพลิเคชัน
echo "🚀 กำลังเปิด Smart Soil AI Analyzer..."
streamlit run app.py
