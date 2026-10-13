#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
สคริปต์ดาวน์โหลดและจัดระเบียบชุดข้อมูลเปิดระดับโลกสำหรับ Workshop เกษตรอัจฉริยะ (Smart Agri & AI)
- PlantDoc-Dataset (In-the-wild Plant Disease Detection & Classification)
- Kaggle Soil Types Dataset (prasanshasatpathy/soil-types)
- IP102 Insect Pest Dataset (Agricultural Pests)
- Durian Leaf Disease & Pests (ชุดข้อมูลทุเรียนไทย/เอเชียตะวันออกเฉียงใต้)
- Rice Leaf Disease & Nutrient Deficiencies

ผศ.ดร.ชีวะ ทัศนา | มหาวิทยาลัยราชภัฏรำไพพรรณี
"""

import os
import sys
import argparse
import subprocess
import shutil

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATASET_INFO = {
    "plantdoc": {
        "title": "PlantDoc Dataset (Cornell / IIT Kanpur)",
        "type": "git",
        "url": "https://github.com/pratikkayal/PlantDoc-Dataset.git",
        "dest": os.path.join(BASE_DIR, "downloads", "PlantDoc-Dataset"),
        "desc": "ภาพถ่ายโรคพืชในสภาพแวดล้อมจริง (In-the-wild) 2,569 ภาพ ครอบคลุม 13 ชนิดพืช 27 คลาสโรค",
        "target_sync": os.path.join(BASE_DIR, "Plant", "PlantDiseases", "Tomato_มะเขือเทศ")
    },
    "soil": {
        "title": "Kaggle Soil Types Dataset (5 Classes, CycleGAN Augmented)",
        "type": "kagglehub",
        "dataset_name": "prasanshasatpathy/soil-types",
        "dest": os.path.join(BASE_DIR, "Soil", "SoilType"),
        "desc": "ภาพดิน 5 ชนิดหลัก: Black, Cinder, Laterite, Peat, Yellow จัดโครงสร้าง train/val เรียบร้อย"
    },
    "durian": {
        "title": "Durian Leaf Disease Dataset (โรคใบและแมลงศัตรูทุเรียน)",
        "type": "git",
        "url": "https://github.com/gianguyen14/durian-leaf-disease-detection.git",
        "dest": os.path.join(BASE_DIR, "downloads", "durian-disease-dataset"),
        "desc": "ชุดข้อมูลโรคใบจุดสาหร่าย (Algal spot), รากเน่าโคนเน่า (Phytophthora), แอนแทรคโนส (Anthracnose)"
    },
    "ip102": {
        "title": "IP102 Insect Pest Benchmark Dataset (CVPR 2019)",
        "type": "info",
        "url": "https://github.com/xpwu95/IP102",
        "desc": "ชุดข้อมูลแมลงศัตรูพืชทางการเกษตรขนาดใหญ่ 75,000+ ภาพ 102 ชนิดแมลง (เพลี้ยกระโดด, หนอนกอ, หนอนกระทู้ ฯลฯ)"
    },
    "rice": {
        "title": "Rice Leaf Disease and Nutrient Deficiency Dataset",
        "type": "info",
        "url": "https://www.kaggle.com/datasets (ค้นหา: rice leaf disease and nutrient deficiency)",
        "desc": "ภาพโรคข้าว (ขอบใบแห้ง, ใบไหม้, ใบจุด) และการขาดธาตุอาหาร N, P, K"
    }
}

def print_catalog():
    print("\n" + "=" * 70)
    print("🌾 แหล่งชุดข้อมูลเปิดระดับโลกที่รองรับในระบบ (Open Datasets Catalog)")
    print("=" * 70)
    for key, info in DATASET_INFO.items():
        print(f"\n🔹 [{key.upper()}] {info['title']}")
        print(f"   คำอธิบาย: {info['desc']}")
        print(f"   ลิงก์อ้างอิง: {info.get('url', info.get('dataset_name'))}")
    print("\n" + "=" * 70)
    print("💡 ตัวอย่างการใช้งาน:")
    print("   python3 datasets/download_plant_datasets.py --list")
    print("   python3 datasets/download_plant_datasets.py --dataset plantdoc")
    print("   python3 datasets/download_plant_datasets.py --dataset soil")
    print("   python3 datasets/download_plant_datasets.py --dataset durian")
    print("=" * 70 + "\n")

def download_git(url, dest_dir, title):
    print(f"\n📦 กำลังดาวน์โหลด {title} ผ่าน Git Clone...")
    print(f"📍 ปลายทาง: {dest_dir}")
    if os.path.exists(dest_dir):
        print(f"✅ โฟลเดอร์ {dest_dir} มีอยู่แล้ว ข้ามขั้นตอนการ clone")
        return True
    os.makedirs(os.path.dirname(dest_dir), exist_ok=True)
    cmd = ["git", "clone", "--depth", "1", url, dest_dir]
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ ดาวน์โหลด {title} เสร็จสมบูรณ์!")
        return True
    except Exception as e:
        print(f"⚠️ เกิดข้อผิดพลาดในการรัน git clone: {e}")
        print("💡 คุณสามารถ clone ด้วยตนเองได้โดยรันคำสั่ง:")
        print(f"   git clone {url} {dest_dir}")
        return False

def download_soil_kaggle():
    print("\n📦 กำลังดาวน์โหลด Kaggle Soil Types...")
    try:
        import kagglehub
        path = kagglehub.dataset_download("prasanshasatpathy/soil-types")
        print(f"✅ ดาวน์โหลดสำเร็จ! พิกัดแคช: {path}")
        target_dir = os.path.join(BASE_DIR, "Soil", "SoilType")
        print(f"📂 จัดเตรียมไฟล์เข้าสู่: {target_dir}")
        return True
    except ImportError:
        print("⚠️ ไม่พบไลบรารี kagglehub (กรุณาติดตั้งด้วย: pip install kagglehub)")
        return False
    except Exception as e:
        print(f"⚠️ ไม่สามารถดาวน์โหลดผ่าน kagglehub ได้: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="สคริปต์ดาวน์โหลดชุดข้อมูลเปิด Smart Agri AI")
    parser.add_argument("--dataset", choices=["plantdoc", "soil", "durian", "ip102", "rice", "all"], help="เลือกชุดข้อมูลที่ต้องการดาวน์โหลด")
    parser.add_argument("--list", action="store_true", help="แสดงรายการชุดข้อมูลทั้งหมด")

    args = parser.parse_args()

    if args.list or not args.dataset:
        print_catalog()
        return

    if args.dataset == "plantdoc" or args.dataset == "all":
        info = DATASET_INFO["plantdoc"]
        download_git(info["url"], info["dest"], info["title"])

    if args.dataset == "soil" or args.dataset == "all":
        download_soil_kaggle()

    if args.dataset == "durian" or args.dataset == "all":
        info = DATASET_INFO["durian"]
        download_git(info["url"], info["dest"], info["title"])

    if args.dataset in ["ip102", "rice"]:
        info = DATASET_INFO[args.dataset]
        print(f"\nℹ️ คำแนะนำสำหรับ {info['title']}:")
        print(f"   {info['desc']}")
        print(f"   🔗 ดาวน์โหลดได้ที่: {info['url']}")
        print("   เนื่องจากชุดข้อมูลมีขนาดใหญ่ (หลายสิบ GB) แนะนำให้ดาวน์โหลดเฉพาะโฟลเดอร์พืชที่ต้องการใช้ในการอบรม")

if __name__ == "__main__":
    main()
