#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
สคริปต์ดาวน์โหลดชุดข้อมูล Kaggle Soil Types อัตโนมัติด้วย kagglehub
และจัดระเบียบเข้าสู่ datasets/01_Soil_Types_Image_Dataset/ ทันที
ผศ.ดร.ชีวะ ทัศนา | มหาวิทยาลัยราชภัฏรำไพพรรณี
"""

import os
import shutil
import sys

def main():
    print("🚀 กำลังตรวจสอบและดาวน์โหลดชุดข้อมูลจาก Kaggle...")
    try:
        import kagglehub
    except ImportError:
        print("⚠️ ไม่พบโมดูล kagglehub ในสภาพแวดล้อมปัจจุบัน")
        print("💡 กรุณาติดตั้งด้วยคำสั่ง: python3 -m pip install kagglehub")
        sys.exit(1)

    dataset_name = "prasanshasatpathy/soil-types"
    print(f"📦 กำลังดาวน์โหลดชุดข้อมูล: {dataset_name} (ผ่าน kagglehub)")
    
    try:
        downloaded_path = kagglehub.dataset_download(dataset_name)
        print(f"✅ ดาวน์โหลดสำเร็จเรียบร้อย!")
        print(f"📍 พิกัดแคชของ Kaggle: {downloaded_path}")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการดาวน์โหลด: {e}")
        sys.exit(1)

    target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "01_Soil_Types_Image_Dataset"))
    print(f"\n📂 กำลังจัดระเบียบไฟล์เข้าสู่: {target_dir} ...")

    # Inspect downloaded directory
    items = os.listdir(downloaded_path)
    print(f"🔎 รายการในชุดข้อมูลที่ดาวน์โหลดมา: {items}")

    # Copy files/folders to target dataset directory
    copied_classes = []
    for item in items:
        item_path = os.path.join(downloaded_path, item)
        if os.path.isdir(item_path):
            dst = os.path.join(target_dir, item)
            if not os.path.exists(dst):
                shutil.copytree(item_path, dst)
            else:
                for subf in os.listdir(item_path):
                    s_src = os.path.join(item_path, subf)
                    s_dst = os.path.join(dst, subf)
                    if not os.path.exists(s_dst):
                        if os.path.isdir(s_src):
                            shutil.copytree(s_src, s_dst)
                        else:
                            shutil.copy2(s_src, s_dst)
            copied_classes.append(item)

    print(f"\n🎉 จัดระเบียบชุดข้อมูลเสร็จสมบูรณ์! ({len(copied_classes)} คลาสหลัก)")
    for c in copied_classes:
        c_path = os.path.join(target_dir, c)
        num_files = len([f for r, d, files in os.walk(c_path) for f in files if not f.startswith('.')])
        print(f"  • {c}: {num_files} ไฟล์")

    print("\n👉 สามารถสั่งรันเทรนโมเดลต่อได้ทันทีด้วย: python3 datasets/train_custom_soil_model.py")

if __name__ == "__main__":
    main()
