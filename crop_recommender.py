#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Soil & Plant AI — Crop & Fertilizer Recommender Engine
โมดูลแนะนำพืชและวิเคราะห์ความอุดมสมบูรณ์ของดินจากค่าเซนเซอร์เคมีและกายภาพ
ใช้ฐานข้อมูลมาตรฐาน 2,200 แปลงตัวอย่าง (22 ชนิดพืช)
พัฒนาโดย ผศ.ดร.ชีวะ ทัศนา | มหาวิทยาลัยราชภัฏรำไพพรรณี
"""

import os
import numpy as np
import pandas as pd

# พจนานุกรมชื่อภาษาไทยและข้อมูลทางปฐพีวิทยา
CROP_THAI_METADATA = {
    "rice": {"name": "ข้าว (Rice)", "icon": "🌾", "desc": "ต้องการน้ำและไนโตรเจนสูง สภาพดินร่วนเหนียวหรือดินเหนียว pH 5.5-7.0"},
    "maize": {"name": "ข้าวโพด (Maize)", "icon": "🌽", "desc": "พืชไร่เศรษฐกิจ ต้องการไนโตรเจนและฟอสฟอรัสสูง ดินระบายน้ำดี pH 6.0-7.2"},
    "chickpea": {"name": "ถั่วชิกพี (Chickpea)", "icon": "🫘", "desc": "พืชตระกูลถั่ว ทนแล้ง ตรึงไนโตรเจนได้ดี ต้องการฟอสฟอรัสสูง pH 6.0-7.5"},
    "kidneybeans": {"name": "ถั่วแดงหลวง (Kidney Beans)", "icon": "🫘", "desc": "ชอบอากาศเย็นปานกลาง ดินร่วนโปร่ง ต้องการโพแทสเซียมสูง pH 5.5-6.5"},
    "pigeonpeas": {"name": "ถั่วมะแฮะ (Pigeon Peas)", "icon": "🌿", "desc": "ระบบรากลึก ช่วยฟื้นฟูโครงสร้างดินดานและตรึงไนโตรเจน pH 5.0-7.0"},
    "mothbeans": {"name": "ถั่วพุ่มทนแล้ง (Moth Beans)", "icon": "🌱", "desc": "ทนแล้งสูงมาก ใช้น้ำน้อย เหมาะกับดินทรายหรือดินลูกรัง pH 6.0-8.0"},
    "mungbean": {"name": "ถั่วเขียว (Mungbean)", "icon": "🌱", "desc": "พืชอายุสั้น ใช้น้ำน้อย ปลูกสลับตัดวงจรโรคและบำรุงดิน pH 6.2-7.2"},
    "blackgram": {"name": "ถั่วดำ (Blackgram)", "icon": "🫘", "desc": "ช่วยปรับปรุงหน้าดิน ตรึงไนโตรเจนในดิน ต้องการความชื้นพอเหมาะ pH 6.0-7.0"},
    "lentil": {"name": "ถั่วเลนทิล (Lentil)", "icon": "🥣", "desc": "พืชโปรตีนสูง เจริญเติบโตได้ดีในดินร่วนระบายน้ำดี pH 6.0-7.0"},
    "pomegranate": {"name": "ทับทิม (Pomegranate)", "icon": "🍎", "desc": "ไม้ผลทนแล้ง ต้องการโพแทสเซียมและฟอสฟอรัสสูง pH 6.5-7.5"},
    "banana": {"name": "กล้วย (Banana)", "icon": "🍌", "desc": "ต้องการโพแทสเซียมและไนโตรเจนสูงมาก ให้น้ำสม่ำเสมอ pH 6.0-6.8"},
    "mango": {"name": "มะม่วง (Mango)", "icon": "🥭", "desc": "ทนแล้งได้ดี รากลึก ต้องการโพแทสเซียมช่วงติดดอกและสร้างผล pH 5.5-7.5"},
    "grapes": {"name": "องุ่น (Grapes)", "icon": "🍇", "desc": "ต้องการโพแทสเซียมและฟอสฟอรัสสูงมาก ดินระบายน้ำคล่อง pH 6.0-7.0"},
    "watermelon": {"name": "แตงโม (Watermelon)", "icon": "🍉", "desc": "ชอบดินร่วนปนทราย อุณหภูมิอบอุ่น ไนโตรเจนและโพแทสเซียมสมดุล pH 6.0-6.8"},
    "muskmelon": {"name": "เมล่อน (Muskmelon)", "icon": "🍈", "desc": "ต้องการความอบอุ่นและการระบายน้ำดี โพแทสเซียมช่วยเพิ่มความหวาน pH 6.0-6.8"},
    "apple": {"name": "แอปเปิ้ล (Apple)", "icon": "🍏", "desc": "ไม้ผลเมืองหนาว ต้องการธาตุอาหารสมดุล ดินระบายน้ำดีเลิศ pH 6.0-7.0"},
    "orange": {"name": "ส้ม (Orange)", "icon": "🍊", "desc": "ต้องการการระบายน้ำดี ไนโตรเจนและโพแทสเซียมสูง pH 5.5-6.5"},
    "papaya": {"name": "มะละกอ (Papaya)", "icon": "🪴", "desc": "โตเร็ว ดินต้องไม่แฉะน้ำขัง โพแทสเซียมสูงช่วยเนื้อแน่นหวาน pH 6.0-6.5"},
    "coconut": {"name": "มะพร้าว (Coconut)", "icon": "🥥", "desc": "ชอบความชื้นสูง ทนดินเค็มและดินทรายชายฝั่ง ต้องการโพแทสเซียมสูง pH 5.2-8.0"},
    "cotton": {"name": "ฝ้าย (Cotton)", "icon": "☁️", "desc": "พืชเส้นใย ทนแดดจัด ต้องการไนโตรเจนและฟอสฟอรัสสูง pH 6.0-7.5"},
    "jute": {"name": "ปอกระเจา (Jute)", "icon": "🌾", "desc": "ชอบน้ำและความชื้นสูง ดินตะกอนน้ำพา pH 6.0-7.0"},
    "coffee": {"name": "กาแฟ (Coffee)", "icon": "☕", "desc": "ชอบร่มเงา ดินร่วนภูเขาสูง ฮิวมัสสูง ต้องการโพแทสเซียมและไนโตรเจน pH 5.0-6.0"}
}

class CropRecommenderEngine:
    def __init__(self, csv_path: str = None):
        if csv_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            csv_path = os.path.join(
                base_dir, 
                "datasets", "Soil", "SoilNutrient", "01_Real_Data", "Crop_recommendation.csv"
            )
        
        self.csv_path = csv_path
        self.df = None
        self.features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        self.class_profiles = {}
        self.feature_means = None
        self.feature_stds = None
        self._load_and_train()

    def _load_and_train(self):
        """โหลดข้อมูลและคำนวณ Normalization & Class Centroids (Gaussian Nearest Centroid)"""
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"ไม่พบไฟล์ฐานข้อมูล: {self.csv_path}")

        self.df = pd.read_csv(self.csv_path)
        
        # คำนวณ Standard Scale parameters
        self.feature_means = self.df[self.features].mean().values
        self.feature_stds = self.df[self.features].std().values + 1e-6

        # คำนวณ Mean และ Covariance ของแต่ละพืช
        for crop in self.df['label'].unique():
            subset = self.df[self.df['label'] == crop][self.features].values
            crop_mean = np.mean(subset, axis=0)
            crop_std = np.std(subset, axis=0) + 1e-4
            self.class_profiles[crop] = {
                "mean": crop_mean,
                "std": crop_std
            }

    def predict(self, n: float, p: float, k: float, temp: float, hum: float, ph: float, rain: float, top_k: int = 3):
        """
        ทำนายความเหมาะสมของพืช top_k อันดับ พร้อมเปอร์เซ็นต์ความเหมาะสม (Score %)
        """
        user_vec = np.array([n, p, k, temp, hum, ph, rain], dtype=np.float32)
        
        distances = []
        for crop, prof in self.class_profiles.items():
            # Normalized Euclidean distance
            diff = (user_vec - prof["mean"]) / self.feature_stds
            dist = np.linalg.norm(diff)
            distances.append((crop, dist))
        
        distances.sort(key=lambda x: x[1])
        
        # แปลงระยะห่างเป็น Similarity Score (0 - 100%)
        min_dist = distances[0][1]
        results = []
        for crop, dist in distances[:top_k]:
            meta = CROP_THAI_METADATA.get(crop, {"name": crop, "icon": "🌱", "desc": ""})
            similarity = max(50.0, min(99.0, 100.0 - (dist * 7.5)))
            results.append({
                "label": crop,
                "name": meta["name"],
                "icon": meta["icon"],
                "desc": meta["desc"],
                "similarity_score": round(similarity, 1),
                "distance": round(dist, 2),
                "ideal_n": round(float(self.class_profiles[crop]["mean"][0]), 1),
                "ideal_p": round(float(self.class_profiles[crop]["mean"][1]), 1),
                "ideal_k": round(float(self.class_profiles[crop]["mean"][2]), 1),
                "ideal_ph": round(float(self.class_profiles[crop]["mean"][5]), 2),
            })
        
        # วิเคราะห์การจัดการปุ๋ย (Fertilizer Action Plan)
        top_crop = results[0]
        n_diff = top_crop["ideal_n"] - n
        p_diff = top_crop["ideal_p"] - p
        k_diff = top_crop["ideal_k"] - k
        
        fertilizer_advice = []
        if n_diff > 15:
            fertilizer_advice.append(f"ธาตุไนโตรเจน (N) ต่ำกว่าระดับแนะนำ {n_diff:.0f} mg/kg: ควรใส่ปุ๋ยยูเรีย (46-0-0) หรือปุ๋ยหมักมูลสัตว์")
        elif n_diff < -25:
            fertilizer_advice.append(f"ธาตุไนโตรเจน (N) สูงเกินความต้องการ: ชะลอการให้ปุ๋ย N เพื่อลดการบ้าใบและป้องกันโรคระบาด")
            
        if p_diff > 15:
            fertilizer_advice.append(f"ธาตุฟอสฟอรัส (P) ต่ำกว่าระดับแนะนำ {p_diff:.0f} mg/kg: ควรใส่ปุ๋ยไดแอมโมเนียมฟอสเฟต (18-46-0) หรือกระดูกป่น")
            
        if k_diff > 15:
            fertilizer_advice.append(f"ธาตุโพแทสเซียม (K) ต่ำกว่าระดับแนะนำ {k_diff:.0f} mg/kg: ควรเติมโพแทสเซียมคลอไรด์ (0-0-60) หรือขี้เถ้าแกลบ")

        if ph < 5.5:
            fertilizer_advice.append(f"ดินมีความเป็นกรด (pH {ph:.1f}): ควรหว่านปูนโดโลไมต์ปรับค่ากรด-ด่างก่อนใส่ปุ๋ย")
        elif ph > 7.5:
            fertilizer_advice.append(f"ดินมีความเป็นด่าง (pH {ph:.1f}): หลีกเลี่ยงปูน ใส่ยิปซัมหรือกำมะถันผงเพื่อลดด่าง")

        if not fertilizer_advice:
            fertilizer_advice.append("ระดับธาตุอาหาร N-P-K และค่า pH อยู่ในเกณฑ์สมดุลดีเยี่ยมตามธรรมชาติของพืช")

        return {
            "top_crops": results,
            "fertilizer_recommendations": fertilizer_advice
        }
