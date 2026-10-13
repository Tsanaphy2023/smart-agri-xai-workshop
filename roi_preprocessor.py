"""
Soil Vision & ROI Preprocessing Engine
---------------------------------------
โมดูลการประมวลผลภาพถ่ายดินและพืชขั้นสูง (Two-Stage Precision Agri Vision Pipeline)
ออกแบบตามมาตรฐาน Computer Vision และ Digital Agriphysics:
1. Intelligent ROI Localization (ตรวจจับและตัดเฉพาะพื้นที่เป้าหมาย ป้องกัน Clever Hans Effect)
2. Data Quality & Artifact Gate (ตรวจสอบความเบลอด้วย Laplacian Variance, ตรวจจับแสงจ้าและเงามืด)
3. Illumination & Color Normalization (Gray-World White Balance + CIE L*a*b* CLAHE)
4. Physicochemical Color Feature Extraction (คำนวณดัชนีสีทางฟิสิกส์เกษตร L*, a*, b*, Moisture & Organic Proxies)
"""

import cv2
import numpy as np
from PIL import Image
from typing import Dict, Any, Tuple, Optional


class SoilVisionPreprocessor:
    """
    คลาสสำหรับประมวลผลภาพถ่ายดินและใบพืชก่อนป้อนเข้าโครงข่ายประสาทเทียม
    """

    @staticmethod
    def pil_to_cv2(pil_img: Image.Image) -> np.ndarray:
        """แปลง PIL Image (RGB) เป็น OpenCV BGR ndarray"""
        rgb = np.array(pil_img.convert("RGB"))
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    @staticmethod
    def cv2_to_pil(cv_img: np.ndarray) -> Image.Image:
        """แปลง OpenCV BGR ndarray เป็น PIL Image (RGB)"""
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb)

    @classmethod
    def detect_roi(
        cls, 
        cv_img: np.ndarray, 
        padding_ratio: float = 0.05
    ) -> Tuple[Tuple[int, int, int, int], float, np.ndarray]:
        """
        ตรวจจับกรอบเป้าหมาย (Region of Interest: ROI) ของดินหรือพืช
        ใช้วิธี Color Saliency + Adaptive Otsu + Morphological Energy
        คืนค่า: (x, y, w, h), confidence_score, annotated_image
        """
        h, w = cv_img.shape[:2]
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        
        # 1. ปรับลดสัญญาณรบกวนด้วย Gaussian Blur
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)
        
        # 2. คำนวณ Saliency / Gradient Energy
        sobelx = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
        grad_mag = np.sqrt(sobelx**2 + sobely**2)
        grad_norm = cv2.normalize(grad_mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        
        # 3. รวมค่า Gradient กับ Otsu Thresholding
        _, thresh = cv2.threshold(grad_norm, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological Closing เพื่อเชื่อมโยงพื้นที่เนื้อเดียวกัน
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        best_bbox = (0, 0, w, h)
        best_score = 0.85
        
        if contours:
            # คัดเลือก Contour ที่มีพื้นที่และสมดุลตรงกลางภาพมากที่สุด
            center_x, center_y = w / 2, h / 2
            max_val = 0.0
            
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < (w * h * 0.04):  # ข้ามจุดรบกวนขนาดเล็ก (<4% ของภาพ)
                    continue
                
                bx, by, bw, bh = cv2.boundingRect(cnt)
                cnt_cx = bx + bw / 2
                cnt_cy = by + bh / 2
                
                # คิดคะแนนจากขนาดพื้นที่ + ความใกล้จุดกึ่งกลางเลนส์กล้อง
                dist_from_center = np.sqrt((cnt_cx - center_x)**2 + (cnt_cy - center_y)**2)
                norm_dist = dist_from_center / np.sqrt(center_x**2 + center_y**2)
                area_ratio = area / (w * h)
                
                score = area_ratio * 0.6 + (1.0 - norm_dist) * 0.4
                if score > max_val:
                    max_val = score
                    # เพิ่ม Padding รอบกรอบ
                    pad_w = int(bw * padding_ratio)
                    pad_h = int(bh * padding_ratio)
                    x1 = max(0, bx - pad_w)
                    y1 = max(0, by - pad_h)
                    x2 = min(w, bx + bw + pad_w)
                    y2 = min(h, by + bh + pad_h)
                    best_bbox = (x1, y1, x2 - x1, y2 - y1)
                    best_score = min(0.99, 0.70 + float(score) * 0.3)

        # วาดกรอบ Bounding Box พร้อมเป้าเล็งเชิงวิศวกรรม
        annotated = cv_img.copy()
        bx, by, bw, bh = best_bbox
        
        # วาดกรอบสีเขียวมรกต (BGR: 16, 185, 129 -> [129, 185, 16])
        cv2.rectangle(annotated, (bx, by), (bx + bw, by + bh), (129, 185, 16), 2)
        
        # วาดมุมเล็งไฮเทค (Corner Brackets)
        c_len = min(25, int(min(bw, bh) * 0.15))
        # มุมบนซ้าย
        cv2.line(annotated, (bx, by), (bx + c_len, by), (212, 182, 6), 4)
        cv2.line(annotated, (bx, by), (bx, by + c_len), (212, 182, 6), 4)
        # มุมบนขวา
        cv2.line(annotated, (bx + bw, by), (bx + bw - c_len, by), (212, 182, 6), 4)
        cv2.line(annotated, (bx + bw, by), (bx + bw, by + c_len), (212, 182, 6), 4)
        # มุมล่างซ้าย
        cv2.line(annotated, (bx, by + bh), (bx + c_len, by + bh), (212, 182, 6), 4)
        cv2.line(annotated, (bx, by + bh), (bx, by + bh - c_len), (212, 182, 6), 4)
        # มุมล่างขวา
        cv2.line(annotated, (bx + bw, by + bh), (bx + bw - c_len, by + bh), (212, 182, 6), 4)
        cv2.line(annotated, (bx + bw, by + bh), (bx + bw, by + bh - c_len), (212, 182, 6), 4)
        
        # ป้ายระบุข้อมูล ROI
        label_text = f"TARGET ROI [{bw}x{bh}] Conf: {best_score*100:.1f}%"
        cv2.putText(
            annotated, label_text, (bx + 8, max(25, by - 10)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (129, 185, 16), 2, cv2.LINE_AA
        )
        
        return best_bbox, best_score, annotated

    @classmethod
    def assess_quality(cls, roi_bgr: np.ndarray) -> Dict[str, Any]:
        """
        ตรวจสอบเกณฑ์คุณภาพของภาพถ่าย (Quality Gate):
        - ความคมชัด (Blur metric ด้วย Laplacian Variance)
        - แสงสะท้อนจ้า (Specular Glare / Overexposure)
        - เงามืดรบกวน (Underexposure / Shadow Ratio)
        """
        gray = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
        
        # 1. คำนวณความคมชัด
        lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        if lap_var >= 120.0:
            blur_status = "PASSED (คมชัดสูง)"
            blur_pass = True
        elif lap_var >= 60.0:
            blur_status = "WARNING (คมชัดปานกลาง ยอมรับได้)"
            blur_pass = True
        else:
            blur_status = "FAILED (ภาพเบลอ ไม่แนะนำ)"
            blur_pass = False

        # 2. คำนวณแสงจ้าเกิน (Specular reflection > 250 ในช่อง R,G,B)
        total_pixels = roi_bgr.shape[0] * roi_bgr.shape[1]
        glare_pixels = np.sum(np.all(roi_bgr >= 248, axis=2))
        glare_ratio = float(glare_pixels / total_pixels) * 100.0

        # 3. คำนวณเงามืดรบกวน (Underexposure: ความสว่างเฉลี่ย < 25)
        shadow_pixels = np.sum(gray <= 28)
        shadow_ratio = float(shadow_pixels / total_pixels) * 100.0

        # 4. คำนวณ Quality Score รวม (0 - 100%)
        q_score = 100.0
        if lap_var < 100:
            q_score -= max(0, (100 - lap_var) * 0.4)
        q_score -= min(30.0, glare_ratio * 3.0)
        q_score -= min(30.0, shadow_ratio * 1.5)
        q_score = max(10.0, min(100.0, q_score))

        # สรุปคำแนะนำเชิงคุณภาพ
        recs = []
        if not blur_pass:
            recs.append("กล้องสั่นไหว: ถือกล้องให้นิ่งขึ้น หรือแตะหน้าจอเพื่อปรับโฟกัส")
        if glare_ratio > 4.0:
            recs.append("พบแสงสะท้อนจ้า: บังแสงแดดทางตรง หรือปรับมุมกล้องเฉียง 30 องศา")
        if shadow_ratio > 15.0:
            recs.append("พบเงามืดบังวัตถุ: จัดตำแหน่งแสงให้สว่างสม่ำเสมอทั่วหน้าดิน")
        if not recs:
            recs.append("คุณภาพภาพยอดเยี่ยม พร้อมสำหรับการจำแนกและวิเคราะห์คุณสมบัติ")

        return {
            "laplacian_variance": lap_var,
            "blur_status": blur_status,
            "blur_pass": blur_pass,
            "glare_ratio_pct": glare_ratio,
            "shadow_ratio_pct": shadow_ratio,
            "quality_score_pct": q_score,
            "is_acceptable": blur_pass and glare_ratio < 12.0,
            "recommendations": recs
        }

    @classmethod
    def normalize_illumination_and_color(
        cls, 
        roi_bgr: np.ndarray,
        clahe_clip: float = 2.5,
        clahe_grid: Tuple[int, int] = (8, 8)
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        ปรับสมดุลแสงและสีเพื่อขจัดผลกระทบจากแสงแดดกลางแจ้ง:
        1. Gray-World White Balance (ปรับสมดุลสมการแสงสีเทา)
        2. CIE L*a*b* Separation (แยกค่าความสว่าง L* ออกจากเนื้อสีแท้ a*, b*)
        3. CLAHE บนช่อง L* เพื่อกระจายแสงเงาให้เรียบสม่ำเสมอ โดยคงเม็ดสีดั้งเดิม 100%
        """
        # Step 1: Gray-World White Balance
        b, g, r = cv2.split(roi_bgr.astype(np.float32))
        mean_b, mean_g, mean_r = np.mean(b), np.mean(g), np.mean(r)
        mean_gray = (mean_b + mean_g + mean_r) / 3.0
        
        # ป้องกัน division by zero
        scale_b = mean_gray / (mean_b + 1e-5)
        scale_g = mean_gray / (mean_g + 1e-5)
        scale_r = mean_gray / (mean_r + 1e-5)
        
        balanced_b = np.clip(b * scale_b, 0, 255).astype(np.uint8)
        balanced_g = np.clip(g * scale_g, 0, 255).astype(np.uint8)
        balanced_r = np.clip(r * scale_r, 0, 255).astype(np.uint8)
        balanced_bgr = cv2.merge([balanced_b, balanced_g, balanced_r])

        # Step 2: CIE L*a*b* Transformation & CLAHE
        lab = cv2.cvtColor(balanced_bgr, cv2.COLOR_BGR2LAB)
        l, a, b_ch = cv2.split(lab)
        
        clahe = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=clahe_grid)
        l_equalized = clahe.apply(l)
        
        # รวมช่องกลับเข้าด้วยกัน (โดยไม่แตะต้องช่อง a และ b ทำให้สีแท้ของดินคงเดิม)
        lab_normalized = cv2.merge([l_equalized, a, b_ch])
        final_bgr = cv2.cvtColor(lab_normalized, cv2.COLOR_LAB2BGR)

        stats = {
            "orig_mean_rgb": [float(mean_r), float(mean_g), float(mean_b)],
            "balanced_scales": [float(scale_r), float(scale_g), float(scale_b)],
            "l_mean_before": float(np.mean(l)),
            "l_mean_after": float(np.mean(l_equalized)),
            "l_std_before": float(np.std(l)),
            "l_std_after": float(np.std(l_equalized)),
        }

        return final_bgr, stats

    @classmethod
    def extract_physicochemical_indices(
        cls, 
        normalized_bgr: np.ndarray
    ) -> Dict[str, Any]:
        """
        สกัดดัชนีสีเชิงฟิสิกส์เกษตร (Agri-physics Color Indices):
        - CIE L*, a*, b* (Luminance, Red-Green, Yellow-Blue)
        - Moisture Index Proxy: MI = (R - B) / (R + B)
        - Soil Redness Index (RI)
        - Soil Organic Matter Proxy (SOM index based on dark absorption)
        """
        rgb = cv2.cvtColor(normalized_bgr, cv2.COLOR_BGR2RGB).astype(np.float32)
        r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
        
        lab = cv2.cvtColor(normalized_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
        l_ch, a_ch, b_ch = lab[:, :, 0], lab[:, :, 1], lab[:, :, 2]
        
        # สเกล L* ให้อยู่ในช่วง 0-100, a* และ b* ในช่วง -128 ถึง 127 ตามมาตรฐาน CIE
        l_std = np.mean(l_ch) * (100.0 / 255.0)
        a_std = np.mean(a_ch) - 128.0
        b_std = np.mean(b_ch) - 128.0

        mean_r, mean_g, mean_b = np.mean(r), np.mean(g), np.mean(b)

        # 1. Moisture Index Proxy: ดินชื้นจะดูดกลืนแสงสีแดงมากกว่าดินแห้ง
        moisture_proxy = float((mean_r - mean_b) / (mean_r + mean_b + 1e-5))

        # 2. Redness Index (RI) สำหรับดินลูกรัง/ดินตะกอน (Laterite / Clay)
        redness_index = float((mean_r**2) / ((mean_b * (mean_g**3)) + 1e-5) * 1e5)

        # 3. Organic Matter Proxy (ดินฮิวมัสสูง L* จะต่ำ)
        som_proxy_score = float(max(0.0, min(100.0, (100.0 - l_std) * 1.4)))

        # ประมาณการประเภทดินจากพิกัดสี
        if som_proxy_score >= 65.0:
            soil_est = "ดินดำอินทรีย์วัตถุสูง (High Organic Loam)"
        elif a_std > 8.0 and b_std > 12.0:
            soil_est = "ดินลูกรังแดง / ดินเหนียวสีแดง (Laterite Red Soil)"
        elif b_std > 15.0 and l_std > 55.0:
            soil_est = "ดินทรายสีเหลือง / ดินร่วนปนทราย (Sandy Loam)"
        else:
            soil_est = "ดินร่วนธรรมดา (Typical Field Soil)"

        return {
            "l_star": float(l_std),
            "a_star": float(a_std),
            "b_star": float(b_std),
            "mean_rgb": [float(mean_r), float(mean_g), float(mean_b)],
            "moisture_proxy": moisture_proxy,
            "redness_index": redness_index,
            "organic_matter_proxy_pct": som_proxy_score,
            "estimated_soil_family": soil_est
        }

    @classmethod
    def process_full_pipeline(
        cls, 
        pil_img: Image.Image,
        auto_crop: bool = True
    ) -> Dict[str, Any]:
        """
        รันระบบประมวลผล Two-Stage เต็มรูปแบบ:
        Raw -> ROI Detect -> Quality Gate -> Illumination Normalization -> Physics Indices
        """
        orig_cv = cls.pil_to_cv2(pil_img)
        h, w = orig_cv.shape[:2]

        # 1. Detect ROI
        bbox, roi_conf, annotated_cv = cls.detect_roi(orig_cv)
        bx, by, bw, bh = bbox

        if auto_crop and bw > 30 and bh > 30:
            roi_cv = orig_cv[by:by+bh, bx:bx+bw].copy()
        else:
            roi_cv = orig_cv.copy()
            bbox = (0, 0, w, h)

        # 2. Quality Gate
        quality = cls.assess_quality(roi_cv)

        # 3. Normalization (Gray-World + CLAHE)
        norm_cv, norm_stats = cls.normalize_illumination_and_color(roi_cv)

        # 4. Physicochemical Indices
        indices = cls.extract_physicochemical_indices(norm_cv)

        return {
            "original_size": (w, h),
            "roi_bbox": bbox,
            "roi_confidence": roi_conf,
            "annotated_pil": cls.cv2_to_pil(annotated_cv),
            "cropped_roi_pil": cls.cv2_to_pil(roi_cv),
            "normalized_roi_pil": cls.cv2_to_pil(norm_cv),
            "quality": quality,
            "norm_stats": norm_stats,
            "indices": indices
        }
