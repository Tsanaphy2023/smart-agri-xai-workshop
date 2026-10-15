#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Soil & Plant AI — Model Training Script (PyTorch MobileNetV3 Transfer Learning)
รองรับทั้งชุดข้อมูลดิน (SoilType) และชุดข้อมูลพืช (PlantNutrient, PlantInsect, PlantDiseases)
ออกแบบสำหรับใช้ใน Workshop หรือรันบน Google Colab (Free GPU) / Apple Silicon (MPS)
ผศ.ดร.ชีวะ ทัศนา | มหาวิทยาลัยราชภัฏรำไพพรรณี
"""

import os
import sys
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader

def train_classifier(data_dir=None, source="auto", num_epochs=10, batch_size=16, lr=0.001, output_name="custom_model", enable_roi_crop=False):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if data_dir is None:
        data_dir = os.path.join(base_dir, "Soil", "SoilType")
    elif not os.path.isabs(data_dir):
        data_dir = os.path.abspath(data_dir)

    # Smart auto-detection of 01_Real_Data
    real_candidate = os.path.join(data_dir, "01_Real_Data")

    if os.path.exists(os.path.join(real_candidate, "train")):
        data_dir = real_candidate
        print("📌 ตรวจพบชุดข้อมูลจริง: โหลดจาก 01_Real_Data เรียบร้อย")
    elif os.path.exists(os.path.join(data_dir, "train")):
        print(f"📌 โหลดชุดข้อมูลจาก: {data_dir}")

    print("=" * 65)
    print(f"🌱 Smart Agri AI Model Trainer — ผศ.ดร.ชีวะ ทัศนา")
    print(f"📂 กำลังโหลดชุดข้อมูลจาก: {data_dir}")
    print("=" * 65)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
    print(f"🚀 กำลังประมวลผลบนฮาร์ดแวร์: {device}")

    # Precision ROI Preprocessing Transform
    def precision_roi_transform(img):
        try:
            import numpy as np
            from PIL import Image
            sys_path_root = os.path.abspath(os.path.join(base_dir, ".."))
            if sys_path_root not in sys.path:
                sys.path.append(sys_path_root)
            from roi_preprocessor import extract_target_roi
            np_img = np.array(img.convert('RGB'))
            roi, _ = extract_target_roi(np_img, mode='auto', pad_ratio=0.10)
            return Image.fromarray(roi)
        except Exception:
            return img

    # Data Augmentation & Preprocessing
    train_transform_list = []
    val_transform_list = []

    # Optional ROI crop toggle (or default auto)
    if enable_roi_crop:
        print("🎯 เปิดใช้งาน Agri-Vision 2.0: Precision Target ROI Cropping ในการเทรน")
        train_transform_list.append(transforms.Lambda(precision_roi_transform))
        val_transform_list.append(transforms.Lambda(precision_roi_transform))

    train_transform_list.extend([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    val_transform_list.extend([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    data_transforms = {
        'train': transforms.Compose(train_transform_list),
        'val': transforms.Compose(val_transform_list),
    }

    train_path = os.path.join(data_dir, 'train')
    val_path = os.path.join(data_dir, 'val')

    if not os.path.exists(train_path):
        print(f"⚠️ ไม่พบโฟลเดอร์ {train_path} กรุณาตรวจสอบชุดข้อมูล")
        return

    val_dataset_exists = os.path.exists(val_path) and len(os.listdir(val_path)) > 0

    image_datasets = {
        'train': datasets.ImageFolder(train_path, data_transforms['train']),
        'val': datasets.ImageFolder(val_path, data_transforms['val']) if val_dataset_exists else datasets.ImageFolder(train_path, data_transforms['val'])
    }

    dataloaders = {
        'train': DataLoader(image_datasets['train'], batch_size=batch_size, shuffle=True, num_workers=0),
        'val': DataLoader(image_datasets['val'], batch_size=batch_size, shuffle=False, num_workers=0)
    }

    class_names = image_datasets['train'].classes
    num_classes = len(class_names)
    print(f"📦 ตรวจพบคลาสข้อมูล ({num_classes} คลาส): {class_names}")
    print(f"📊 จำนวนภาพ Train: {len(image_datasets['train'])} ภาพ | Val: {len(image_datasets['val'])} ภาพ")

    if num_classes < 2:
        print("⚠️ ชุดข้อมูลต้องมีอย่างน้อย 2 คลาสเพื่อทำการจำแนก")
        return

    # Load Pretrained Model (MobileNetV3 Small - น้ำหนักเบา แม่นยำ เหมาะกับ Edge AI / Jetson / Web)
    model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT)
    in_features = model.classifier[3].in_features
    model.classifier[3] = nn.Linear(in_features, num_classes)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)

    best_acc = 0.0
    model_save_path = f"{output_name}.pt"
    onnx_save_path = f"{output_name}.onnx"

    for epoch in range(num_epochs):
        print(f"\n--- Epoch {epoch+1}/{num_epochs} ---")
        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()
            else:
                model.eval()

            running_loss = 0.0
            running_corrects = 0

            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)

                optimizer.zero_grad()
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

            epoch_loss = running_loss / len(image_datasets[phase])
            epoch_acc = running_corrects.double() / len(image_datasets[phase])
            print(f"  [{phase.upper()}] Loss: {epoch_loss:.4f} | Acc: {epoch_acc*100:.2f}%")

            if phase == 'val' and epoch_acc >= best_acc:
                best_acc = epoch_acc
                torch.save({
                    'epoch': epoch + 1,
                    'model_state_dict': model.state_dict(),
                    'class_names': class_names,
                    'val_acc': best_acc.item()
                }, model_save_path)
                print(f"  ⭐ บันทึกโมเดลดีที่สุดลง: {model_save_path}")

        scheduler.step()

    print(f"\n🎉 การฝึกอบรมเสร็จสมบูรณ์! Best Validation Accuracy: {best_acc*100:.2f}%")

    # Export to ONNX for Edge AI / Web deployment
    try:
        dummy_input = torch.randn(1, 3, 224, 224).to(device)
        torch.onnx.export(
            model, dummy_input, onnx_save_path,
            input_names=["input"], output_names=["output"],
            dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}}
        )
        print(f"✅ ส่งออกโมเดลมาตรฐานเปิดสำเร็จ (ONNX): {onnx_save_path}")
    except Exception as e:
        print(f"⚠️ ONNX export warning: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smart Agri PyTorch Model Trainer")
    parser.add_argument("--data_dir", type=str, default=None, help="โฟลเดอร์ชุดข้อมูล เช่น datasets/Soil/SoilType หรือ datasets/Plant/PlantDiseases/Durian_ทุเรียน")
    parser.add_argument("--source", type=str, choices=["real", "synthetic", "auto"], default="auto", help="เลือกประเภทข้อมูล (real: ข้อมูลจริง, synthetic: ข้อมูลจำลอง, auto: ตรวจสอบอัตโนมัติ)")
    parser.add_argument("--epochs", type=int, default=5, help="จำนวนรอบ (epochs) ในการเทรน")
    parser.add_argument("--batch_size", type=int, default=8, help="ขนาด Batch size")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--enable_roi_crop", action="store_true", help="เปิดใช้งาน Agri-Vision 2.0 Precision ROI Cropping อัตโนมัติ")
    parser.add_argument("--output", type=str, default="best_model", help="ชื่อไฟล์โมเดลที่บันทึก")

    args = parser.parse_args()
    train_classifier(data_dir=args.data_dir, source=args.source, num_epochs=args.epochs, batch_size=args.batch_size, lr=args.lr, output_name=args.output, enable_roi_crop=args.enable_roi_crop)
