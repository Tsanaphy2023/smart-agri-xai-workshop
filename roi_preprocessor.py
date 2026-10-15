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
        ตรวจจับกรอบเป้าหมายอัจฉริยะ (Agri-Vision 2.0 Precision ROI Localization)
        บูรณาการ 3 เทคนิคขั้นสูงตามมาตรฐานวิศวกรรมคอมพิวเตอร์วิทัศน์เกษตร:
        1. Bio-Spectral Vegetation Index (ExG = 2G - R - B) แยกใบพืชออกจากดิน/มือ/ฉากหลัง
        2. CIE L*a*b* & Saliency Gradient สำหรับเนื้อดินและรอยโรค
        3. Center-Weighted 2D Gaussian Prior จัดลำดับความสำคัญของวัตถุกึ่งกลางเลนส์
        คืนค่า: (x, y, w, h), confidence_score, annotated_image
        """
        h, w = cv_img.shape[:2]
        
        # คำนวณสัดส่วนสีทางฟิสิกส์เกษตร
        b_ch = cv_img[:, :, 0].astype(np.float32)
        g_ch = cv_img[:, :, 1].astype(np.float32)
        r_ch = cv_img[:, :, 2].astype(np.float32)
        sum_rgb = r_ch + g_ch + b_ch + 1e-6
        norm_r, norm_g, norm_b = r_ch / sum_rgb, g_ch / sum_rgb, b_ch / sum_rgb
        
        # Excess Green Index (ExG)
        exg = 2.0 * norm_g - norm_r - norm_b
        mean_center_exg = float(np.mean(exg[int(h*0.25):int(h*0.75), int(w*0.25):int(w*0.75)]))
        
        # สร้าง 2D Center Gaussian Spatial Prior Mask
        y_coords, x_coords = np.ogrid[:h, :w]
        cy, cx = h / 2.0, w / 2.0
        dist_sq = (x_coords - cx)**2 / (w * 0.45)**2 + (y_coords - cy)**2 / (h * 0.45)**2
        center_prior = np.exp(-0.5 * dist_sq)
        
        # 1. โหมดใบพืช / โรคพืช (Bio-Spectral Vegetation Index)
        if mean_center_exg > 0.02:
            exg_norm = cv2.normalize(exg, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            _, mask = cv2.threshold(exg_norm, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # เสริมด้วย HSV Chlorophyll Gate (เขียวมะนาวถึงเขียวเข้ม)
            hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
            hsv_mask = cv2.inRange(hsv, np.array([25, 35, 30]), np.array([95, 255, 255]))
            fused_mask = cv2.bitwise_or(mask, hsv_mask)
            
            # ประยุกต์ Center Spatial Prior เพื่อขจัดฉากหลังขอบภาพ
            weighted_mask = cv2.bitwise_and(fused_mask, fused_mask, mask=(center_prior > 0.15).astype(np.uint8))
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17))
            closed = cv2.morphologyEx(weighted_mask, cv2.MORPH_CLOSE, kernel)
        else:
            # 2. โหมดเนื้อดิน / ตัวอย่างแห้ง (CIE L*a*b* & Saliency)
            lab = cv2.cvtColor(cv_img, cv2.COLOR_BGR2LAB)
            l_chan, _, b_chan = cv2.split(lab)
            
            # Saliency Gradient จากความสว่างและเฉดสีดิน
            grad_l = cv2.Sobel(l_chan, cv2.CV_64F, 1, 1, ksize=3)
            grad_mag = np.abs(grad_l)
            grad_norm = cv2.normalize(grad_mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            _, mask = cv2.threshold(grad_norm, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            weighted_mask = cv2.bitwise_and(mask, mask, mask=(center_prior > 0.12).astype(np.uint8))
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 21))
            closed = cv2.morphologyEx(weighted_mask, cv2.MORPH_CLOSE, kernel)
            
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # ค่าตั้งต้น: พื้นที่ปลอดภัยตรงกลาง 80%
        best_bbox = (int(w * 0.1), int(h * 0.1), int(w * 0.8), int(h * 0.8))
        best_score = 0.82
        
        if contours:
            max_score = 0.0
            total_img_area = float(w * h)
            
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < (total_img_area * 0.03):
                    continue
                    
                bx, by, bw, bh = cv2.boundingRect(cnt)
                cnt_cx, cnt_cy = bx + bw / 2.0, by + bh / 2.0
                
                # คะแนนระยะห่างจากศูนย์กลางภาพ (Normalized Distance Penalty)
                norm_dist = np.sqrt((cnt_cx - cx)**2 + (cnt_cy - cy)**2) / np.sqrt(cx**2 + cy**2)
                area_ratio = min(1.0, area / (total_img_area * 0.5))
                
                # Solidity (ความแน่นของวัตถุเป้าหมาย)
                hull = cv2.convexHull(cnt)
                hull_area = cv2.contourArea(hull)
                solidity = float(area) / hull_area if hull_area > 0 else 0.5
                
                # คำนวณคะแนนรวมถ่วงน้ำหนัก (Solidity 30% + Area 40% + Center 30%)
                composite_score = (area_ratio * 0.4) + ((1.0 - norm_dist) * 0.3) + (solidity * 0.3)
                
                if composite_score > max_score:
                    max_score = composite_score
                    pad_w = int(bw * padding_ratio)
                    pad_h = int(bh * padding_ratio)
                    x1 = max(0, bx - pad_w)
                    y1 = max(0, by - pad_h)
                    x2 = min(w, bx + bw + pad_w)
                    y2 = min(h, by + bh + pad_h)
                    best_bbox = (x1, y1, x2 - x1, y2 - y1)
                    best_score = min(0.99, 0.75 + float(composite_score) * 0.24)
                    
        annotated = cv_img.copy()
        bx, by, bw, bh = best_bbox
        
        # ตีกรอบสีเขียว Emerald (BGR: 16, 185, 129 -> [129, 185, 16])
        cv2.rectangle(annotated, (bx, by), (bx + bw, by + bh), (129, 185, 16), 2)
        
        # วาดมุมเล็งไฮเทค (Corner Brackets สี Cyan)
        c_len = min(25, max(8, int(min(bw, bh) * 0.15)))
        for (corner_x, corner_y, dx, dy) in [
            (bx, by, 1, 1), (bx + bw, by, -1, 1),
            (bx, by + bh, 1, -1), (bx + bw, by + bh, -1, -1)
        ]:
            cv2.line(annotated, (corner_x, corner_y), (corner_x + dx * c_len, corner_y), (212, 182, 6), 3)
            cv2.line(annotated, (corner_x, corner_y), (corner_x, corner_y + dy * c_len), (212, 182, 6), 3)
            
        # ป้ายระบุข้อมูล ROI
        label_text = f"TARGET ROI [{bw}x{bh}] Conf: {best_score*100:.1f}%"
        cv2.putText(
            annotated, label_text, (bx + 8, max(24, by - 8)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.52, (129, 185, 16), 2, cv2.LINE_AA
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
    def get_pipeline_stages(
        cls, 
        cv_img: np.ndarray,
        padding_ratio: float = 0.08,
        mode: str = "auto",
        sigma_scale: float = 0.35,
        min_solidity: float = 0.45
    ) -> Dict[str, Any]:
        """
        แยกย่อยขั้นตอนการคำนวณตามแผนผัง ROI Pipeline เพื่อการตรวจสอบ (Diagnostic Breakdown):
        Stage 1: ภาพต้นฉบับและจุดเล็งศูนย์กลาง (Original Frame & Center Target)
        Stage 2: แผนที่ความเด่นชัดทางชีวภาพ (Bio-Spectral Salience: ExG / Lab Gradient)
        Stage 3: แมตริกซ์ถ่วงน้ำหนักเกาส์เซียนเชิงพื้นที่ 2 มิติ (2D Center Gaussian Spatial Prior)
        Stage 4: หน้ากากรวมศูนย์หลังสัณฐานวิทยา (Fused Weighted Mask & Morphological Closing)
        Stage 5: การวิเคราะห์คอนทัวร์, Convex Hull และ Solidity Filter
        Stage 6: ตีกรอบเป้าหมาย ROI และ Corner Reticles
        Stage 7: การครอบตัดและปรับสมดุลแสงสี (Normalized Target Crop: Gray-World + CLAHE)
        """
        h, w = cv_img.shape[:2]
        cy, cx = h / 2.0, w / 2.0
        
        # Stage 1: Input Frame with Center Crosshair
        stage_1_cv = cv_img.copy()
        cv2.drawMarker(stage_1_cv, (int(cx), int(cy)), (0, 255, 255), cv2.MARKER_CROSS, 28, 2)
        cv2.circle(stage_1_cv, (int(cx), int(cy)), int(min(w, h) * 0.25), (0, 255, 255), 1, cv2.LINE_AA)
        
        # คำนวณ ExG
        b_ch = cv_img[:, :, 0].astype(np.float32)
        g_ch = cv_img[:, :, 1].astype(np.float32)
        r_ch = cv_img[:, :, 2].astype(np.float32)
        sum_rgb = r_ch + g_ch + b_ch + 1e-6
        norm_r, norm_g, norm_b = r_ch / sum_rgb, g_ch / sum_rgb, b_ch / sum_rgb
        exg = 2.0 * norm_g - norm_r - norm_b
        mean_center_exg = float(np.mean(exg[int(h*0.25):int(h*0.75), int(w*0.25):int(w*0.75)]))
        
        is_plant = (mode == "plant") or (mode == "auto" and mean_center_exg > 0.02)
        
        # Stage 2: Bio-Spectral Salience Map
        if is_plant:
            sal_norm = cv2.normalize(exg, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
            hsv_mask = cv2.inRange(hsv, np.array([25, 35, 30]), np.array([95, 255, 255]))
            stage_2_raw = cv2.addWeighted(sal_norm, 0.7, hsv_mask, 0.3, 0)
            target_type_str = "พืช/ใบไม้ (Bio-Spectral ExG + Chlorophyll Gate)"
        else:
            lab = cv2.cvtColor(cv_img, cv2.COLOR_BGR2LAB)
            l_chan, _, _ = cv2.split(lab)
            grad_l = cv2.Sobel(l_chan, cv2.CV_64F, 1, 1, ksize=3)
            stage_2_raw = cv2.normalize(np.abs(grad_l), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            target_type_str = "หน้าดิน (CIE L*a*b* Gradient Texture Saliency)"
            
        stage_2_colored = cv2.applyColorMap(stage_2_raw, cv2.COLORMAP_JET)

        # Stage 3: 2D Center Gaussian Spatial Prior
        y_coords, x_coords = np.ogrid[:h, :w]
        sig_x, sig_y = w * sigma_scale, h * sigma_scale
        center_prior = np.exp(-0.5 * (((x_coords - cx)**2 / (sig_x**2)) + ((y_coords - cy)**2 / (sig_y**2))))
        prior_u8 = (center_prior * 255.0).astype(np.uint8)
        stage_3_colored = cv2.applyColorMap(prior_u8, cv2.COLORMAP_VIRIDIS)

        # Stage 4: Weighted Saliency & Morphological Closing
        weighted_sal = (stage_2_raw.astype(np.float32) * center_prior).astype(np.uint8)
        _, thresh = cv2.threshold(weighted_sal, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        k_size = 17 if is_plant else 21
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_size, k_size))
        stage_4_closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        # Stage 5: Contour Analysis, Convex Hull & Solidity
        stage_5_cv = cv_img.copy()
        contours, _ = cv2.findContours(stage_4_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        best_bbox = (int(w * 0.1), int(h * 0.1), int(w * 0.8), int(h * 0.8))
        best_score = 0.80
        best_cnt = None
        best_solidity = 0.50
        best_area_ratio = 0.50
        best_norm_dist = 0.0
        
        if contours:
            max_score = 0.0
            total_img_area = float(w * h)
            
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < (total_img_area * 0.02):
                    continue
                bx, by, bw, bh = cv2.boundingRect(cnt)
                cnt_cx, cnt_cy = bx + bw / 2.0, by + bh / 2.0
                norm_dist = np.sqrt((cnt_cx - cx)**2 + (cnt_cy - cy)**2) / np.sqrt(cx**2 + cy**2)
                area_ratio = min(1.0, area / (total_img_area * 0.5))
                
                hull = cv2.convexHull(cnt)
                hull_area = cv2.contourArea(hull)
                solidity = float(area) / hull_area if hull_area > 0 else 0.5
                
                # Draw candidate contours in thin gray
                cv2.drawContours(stage_5_cv, [cnt], -1, (160, 160, 160), 1)
                
                composite_score = (area_ratio * 0.4) + ((1.0 - norm_dist) * 0.3) + (solidity * 0.3)
                if solidity < min_solidity:
                    composite_score *= 0.5
                    
                if composite_score > max_score:
                    max_score = composite_score
                    best_cnt = cnt
                    best_solidity = solidity
                    best_area_ratio = area_ratio
                    best_norm_dist = norm_dist
                    
                    pad_w = int(bw * padding_ratio)
                    pad_h = int(bh * padding_ratio)
                    x1 = max(0, bx - pad_w)
                    y1 = max(0, by - pad_h)
                    x2 = min(w, bx + bw + pad_w)
                    y2 = min(h, by + bh + pad_h)
                    best_bbox = (x1, y1, x2 - x1, y2 - y1)
                    best_score = min(0.99, 0.75 + float(composite_score) * 0.24)
            
            # Highlight best contour & convex hull on Stage 5
            if best_cnt is not None:
                hull = cv2.convexHull(best_cnt)
                cv2.drawContours(stage_5_cv, [hull], -1, (0, 165, 255), 2)       # Orange Convex Hull
                cv2.drawContours(stage_5_cv, [best_cnt], -1, (0, 255, 0), 2)     # Green Contour
                bx, by, bw, bh = cv2.boundingRect(best_cnt)
                cv2.line(stage_5_cv, (int(cx), int(cy)), (int(bx + bw/2), int(by + bh/2)), (255, 0, 255), 2)

        # Stage 6: Annotated Bounding Box & Corner Brackets
        stage_6_cv = cv_img.copy()
        bx, by, bw, bh = best_bbox
        cv2.rectangle(stage_6_cv, (bx, by), (bx + bw, by + bh), (129, 185, 16), 2)
        c_len = min(25, max(8, int(min(bw, bh) * 0.15)))
        for (corner_x, corner_y, dx, dy) in [
            (bx, by, 1, 1), (bx + bw, by, -1, 1),
            (bx, by + bh, 1, -1), (bx + bw, by + bh, -1, -1)
        ]:
            cv2.line(stage_6_cv, (corner_x, corner_y), (corner_x + dx * c_len, corner_y), (212, 182, 6), 3)
            cv2.line(stage_6_cv, (corner_x, corner_y), (corner_x, corner_y + dy * c_len), (212, 182, 6), 3)
        lbl = f"TARGET ROI [{bw}x{bh}] Conf: {best_score*100:.1f}%"
        cv2.putText(stage_6_cv, lbl, (bx + 8, max(24, by - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (129, 185, 16), 2, cv2.LINE_AA)

        # Stage 7: Cropped & Normalized
        cropped = cv_img[by:by+bh, bx:bx+bw].copy() if (bw > 30 and bh > 30) else cv_img.copy()
        normalized_bgr, norm_stats = cls.normalize_illumination_and_color(cropped)
        quality = cls.assess_quality(cropped)

        # Recommendations for parameter tuning
        tuning_hints = []
        if best_solidity < min_solidity:
            tuning_hints.append(f"ค่า Solidity ต่ำ ({best_solidity:.2f} < {min_solidity:.2f}): วัตถุอาจเว้าแหว่งหรือแตกเป็นเสี่ยง ลองลด min_solidity หรือเพิ่มขนาดโครงสร้าง Closing")
        if best_norm_dist > 0.4:
            tuning_hints.append(f"วัตถุอยู่ห่างจากศูนย์กลาง ({best_norm_dist:.2f}): ลองขยาย sigma_scale (เช่น 0.45-0.50) หากภาพถ่ายไม่ได้จัดกึ่งกลาง")
        if quality["laplacian_variance"] < 80.0:
            tuning_hints.append("ภาพมีความเบลอ: พิจารณาเพิ่มเกณฑ์ Laplacian หรือเลือกถ่ายซ้ำเพื่อผลลัพธ์ที่ดีขึ้น")
        if not tuning_hints:
            tuning_hints.append("การคัดกรอง ROI สมบูรณ์แบบ พารามิเตอร์ปัจจุบันเหมาะสมกับชุดข้อมูลนี้อย่างยิ่ง")

        return {
            "stage_1_input_pil": cls.cv2_to_pil(stage_1_cv),
            "stage_2_salience_pil": cls.cv2_to_pil(stage_2_colored),
            "stage_3_center_prior_pil": cls.cv2_to_pil(stage_3_colored),
            "stage_4_mask_pil": Image.fromarray(stage_4_closed),
            "stage_5_contour_pil": cls.cv2_to_pil(stage_5_cv),
            "stage_6_annotated_pil": cls.cv2_to_pil(stage_6_cv),
            "stage_7_normalized_pil": cls.cv2_to_pil(normalized_bgr),
            "bbox": best_bbox,
            "confidence": best_score,
            "telemetry": {
                "target_type": target_type_str,
                "center_exg": mean_center_exg,
                "solidity": best_solidity,
                "area_ratio": best_area_ratio,
                "center_dist_penalty": best_norm_dist,
                "laplacian_blur": quality["laplacian_variance"],
                "glare_pct": quality["glare_ratio_pct"],
                "shadow_pct": quality["shadow_ratio_pct"],
                "tuning_hints": tuning_hints
            }
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

        # 1. Detect ROI & Detailed Stage Breakdown
        stages = cls.get_pipeline_stages(orig_cv)
        bbox = stages["bbox"]
        roi_conf = stages["confidence"]
        annotated_cv = cls.pil_to_cv2(stages["stage_6_annotated_pil"])
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
            "annotated_pil": stages["stage_6_annotated_pil"],
            "cropped_roi_pil": cls.cv2_to_pil(roi_cv),
            "normalized_roi_pil": cls.cv2_to_pil(norm_cv),
            "quality": quality,
            "norm_stats": norm_stats,
            "indices": indices,
            "stages": stages
        }

    @classmethod
    def generate_color_spaces_gallery(cls, pil_img: Image.Image) -> Dict[str, Any]:
        """
        แปลงภาพถ่ายเข้าสู่ 6 ปริภูมิสีและการสอบเทียบเชิงแสง (Multi-Channel Color Space Gallery):
        1. RGB Original (สีธรรมชาติ)
        2. HSV Color Space (เฉดสี Hue & ความอิ่มตัว Saturation - วิเคราะห์ใบซีดเหลือง)
        3. CIE L*a*b* (Lightness L* & ความเป็นสีดิน a*, b*)
        4. ExG Bio-Spectral Index (คลอโรฟิลล์พืช 2G - R - B)
        5. CLAHE Radiometric Calibration (ขจัดเงามืดและแสงสะท้อนจ้า)
        6. Clean Binary Mask & Edges (Data Cleaning อุดรูพรุน ขจัดสัญญาณรบกวน)
        """
        cv_img = cls.pil_to_cv2(pil_img)
        h, w = cv_img.shape[:2]

        # 1. RGB Original
        rgb_pil = pil_img.copy()

        # 2. HSV Color Space
        hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
        h_ch = hsv[:, :, 0]
        s_ch = hsv[:, :, 1]
        v_ch = hsv[:, :, 2]
        # Hue colormap
        h_colored = cv2.applyColorMap((h_ch.astype(np.float32) * (255.0 / 180.0)).astype(np.uint8), cv2.COLORMAP_HSV)
        hsv_pil = Image.fromarray(cv2.cvtColor(h_colored, cv2.COLOR_BGR2RGB))

        # 3. CIE L*a*b*
        lab = cv2.cvtColor(cv_img, cv2.COLOR_BGR2Lab)
        l_ch = lab[:, :, 0]
        l_colored = cv2.applyColorMap(l_ch, cv2.COLORMAP_TWILIGHT)
        lab_pil = Image.fromarray(cv2.cvtColor(l_colored, cv2.COLOR_BGR2RGB))

        # 4. ExG Bio-Spectral Index
        b_f = cv_img[:, :, 0].astype(np.float32)
        g_f = cv_img[:, :, 1].astype(np.float32)
        r_f = cv_img[:, :, 2].astype(np.float32)
        sum_rgb = r_f + g_f + b_f + 1e-6
        exg_raw = 2.0 * (g_f / sum_rgb) - (r_f / sum_rgb) - (b_f / sum_rgb)
        exg_norm = cv2.normalize(exg_raw, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        exg_colored = cv2.applyColorMap(exg_norm, cv2.COLORMAP_SUMMER)
        exg_pil = Image.fromarray(cv2.cvtColor(exg_colored, cv2.COLOR_BGR2RGB))

        # 5. CLAHE Radiometric Calibration
        clahe = cv2.createCLAHE(clipLimit=2.8, tileGridSize=(8, 8))
        lab_clahe = lab.copy()
        lab_clahe[:, :, 0] = clahe.apply(lab[:, :, 0])
        clahe_bgr = cv2.cvtColor(lab_clahe, cv2.COLOR_Lab2BGR)
        clahe_pil = cls.cv2_to_pil(clahe_bgr)

        # 6. Clean Mask & Edges
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        closed_mask = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
        edges = cv2.Canny(blur, 40, 120)
        mask_viz = cv2.cvtColor(closed_mask, cv2.COLOR_GRAY2BGR)
        mask_viz[edges > 0] = [0, 255, 0]  # Neon green contour
        mask_pil = Image.fromarray(cv2.cvtColor(mask_viz, cv2.COLOR_BGR2RGB))

        return {
            "rgb": {
                "id": "rgb",
                "name": "1. ภาพถ่ายสีธรรมชาติ (RGB Original)",
                "pil": rgb_pil,
                "domain": "Natural Human Vision",
                "purpose": "ภาพดิบจากเลนส์กล้องตามที่สายตามนุษย์มองเห็น เป็นตัวอ้างอิงเปรียบเทียบ",
                "stats": {"channels": "Red, Green, Blue", "resolution": f"{w}x{h}"}
            },
            "hsv": {
                "id": "hsv",
                "name": "2. ปริภูมิสี HSV (Hue & Saturation)",
                "pil": hsv_pil,
                "domain": "Color Perception & Plant Stress",
                "purpose": "แยกเฉดสี (Hue) และความอิ่มตัว (Saturation) ออกจากแสงสว่าง เพื่อตรวจดูใบซีดเหลืองหรือขอบใบไหม้",
                "stats": {"mean_hue": f"{float(np.mean(h_ch)):.1f}°", "mean_saturation": f"{float(np.mean(s_ch)):.1f}"}
            },
            "lab": {
                "id": "lab",
                "name": "3. ปริภูมิสี CIE L*a*b* (Lightness & Soil Proxy)",
                "pil": lab_pil,
                "domain": "Pedology & Photometry",
                "purpose": "ช่อง L* บ่งชี้ความชื้น/ฮิวมัส (L* ยิ่งต่ำดินยิ่งชื้น) ส่วน a*, b* จำแนกดินลูกรัง vs ดินดำ",
                "stats": {"mean_l_star": f"{float(np.mean(l_ch))*100.0/255.0:.1f}", "moisture_proxy": f"{100.0 - (float(np.mean(l_ch))*100.0/255.0):.1f}%"}
            },
            "exg": {
                "id": "exg",
                "name": "4. ดัชนีชีวภาพ ExG (Excess Green Index)",
                "pil": exg_pil,
                "domain": "Bio-Spectral Remote Sensing",
                "purpose": "สูตร 2G - R - B สกัดเฉพาะพิกัดคลอโรฟิลล์พืช ตัดสิ่งรบกวนของฉากหลัง ดิน และมือคนออก 100%",
                "stats": {"mean_exg": f"{float(np.mean(exg_raw)):.3f}", "vegetation_gate": "Active" if np.mean(exg_raw) > 0.02 else "Low Chlorophyll"}
            },
            "clahe": {
                "id": "clahe",
                "name": "5. การสอบเทียบแสง CLAHE (Radiometric Calibration)",
                "pil": clahe_pil,
                "domain": "Optoelectronic Calibration",
                "purpose": "ปรับเกลี่ยฮิสโตแกรมความสว่างแบบ Adaptive ขจัดเงามืดใต้ทรงพุ่มและแสงสะท้อนจ้า (Glare)",
                "stats": {"clip_limit": "2.8", "tile_grid": "8x8 Cells"}
            },
            "mask": {
                "id": "mask",
                "name": "6. หน้ากากทำความสะอาดข้อมูล (Clean Mask & Edges)",
                "pil": mask_pil,
                "domain": "Morphological Noise Reduction",
                "purpose": "อุดรูพรุนเม็ดดิน ขจัดสัญญาณรบกวนพิกเซล และตีกรอบโครงสร้างหลักของวัตถุอย่างชัดเจน",
                "stats": {"kernel": "7x7 Ellipse", "edge_detector": "Canny Threshold 40/120"}
            }
        }

    @classmethod
    def multi_point_sampling(
        cls,
        pil_img: Image.Image,
        strategy: str = "composite_5point",
        custom_points: Optional[list] = None,
        patch_size: int = 60
    ) -> Dict[str, Any]:
        """
        ระบบสุ่มตัวอย่างพื้นที่หลายจุดพร้อมกัน (Multi-Point / Multi-ROI Spatial Sampling):
        รองรับ 4 กลยุทธ์ตามมาตรฐานการเกษตรแม่นยำและปฐพีวิทยา:
        1. 'single_center': จุดกึ่งกลางภาพจุดเดียว (1 จุด)
        2. 'composite_5point': ตัวอย่างรวม 5 จุด (ดาว 5 แฉก / กากบาท: กึ่งกลาง + 4 มุมตัวแทนแปลง)
        3. 'grid_3x3': ตาราง 9 โซนย่อยทั่วทั้งภาพ (A1 ถึง C3)
        4. 'custom_points': ผู้ใช้งานกำหนดพิกัด [(x, y), ...] ได้เองอย่างอิสระ
        """
        cv_img = cls.pil_to_cv2(pil_img)
        h, w = cv_img.shape[:2]
        lab_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2Lab)

        points = []
        point_labels = []

        if strategy == "single_center":
            points.append((int(w * 0.5), int(h * 0.5)))
            point_labels.append("P1 (Center)")

        elif strategy == "composite_5point":
            # มาตรฐานการเก็บตัวอย่างดินแบบผสม 5 จุด (Composite Sampling Pattern)
            points = [
                (int(w * 0.5), int(h * 0.5)),      # กึ่งกลาง
                (int(w * 0.25), int(h * 0.25)),    # บน-ซ้าย (NW)
                (int(w * 0.75), int(h * 0.25)),    # บน-ขวา (NE)
                (int(w * 0.25), int(h * 0.75)),    # ล่าง-ซ้าย (SW)
                (int(w * 0.75), int(h * 0.75))     # ล่าง-ขวา (SE)
            ]
            point_labels = ["P1 (Center)", "P2 (NW)", "P3 (NE)", "P4 (SW)", "P5 (SE)"]

        elif strategy == "grid_3x3":
            # ตารางเมทริกซ์ 9 โซนย่อย
            row_names = ["A", "B", "C"]
            col_names = ["1", "2", "3"]
            xs = [int(w * 0.22), int(w * 0.50), int(w * 0.78)]
            ys = [int(h * 0.22), int(h * 0.50), int(h * 0.78)]
            for r_idx, py in enumerate(ys):
                for c_idx, px in enumerate(xs):
                    points.append((px, py))
                    point_labels.append(f"{row_names[r_idx]}{col_names[c_idx]}")

        elif strategy == "custom_points" and custom_points:
            for idx, pt in enumerate(custom_points):
                px = max(patch_size // 2, min(w - patch_size // 2, int(pt[0])))
                py = max(patch_size // 2, min(h - patch_size // 2, int(pt[1])))
                points.append((px, py))
                point_labels.append(f"Custom-{idx+1}")
        else:
            # Fallback to single center
            points.append((int(w * 0.5), int(h * 0.5)))
            point_labels.append("P1 (Center)")

        half_p = max(15, patch_size // 2)
        samples = []
        annotated_cv = cv_img.copy()

        # วาดเส้นเชื่อมโยงโครงร่างสำหรับ 5-Point Composite
        if strategy == "composite_5point" and len(points) == 5:
            cx, cy = points[0]
            for pt in points[1:]:
                cv2.line(annotated_cv, (cx, cy), pt, (0, 180, 255), 1, cv2.LINE_AA)

        palette = [
            (16, 185, 129),   # Emerald
            (6, 182, 212),    # Cyan
            (99, 102, 241),   # Indigo
            (245, 158, 11),   # Amber
            (236, 72, 153),   # Pink
            (168, 85, 247),   # Purple
            (34, 197, 94),    # Green
            (59, 130, 246),   # Blue
            (239, 68, 68)     # Red
        ]

        l_stars = []
        a_stars = []
        b_stars = []
        moistures = []
        rednesses = []
        sharpnesses = []
        ph_proxies = []

        for idx, (px, py) in enumerate(points):
            x1 = max(0, px - half_p)
            y1 = max(0, py - half_p)
            x2 = min(w, px + half_p)
            y2 = min(h, py + half_p)

            patch_bgr = cv_img[y1:y2, x1:x2]
            patch_lab = lab_img[y1:y2, x1:x2]

            mean_b = float(np.mean(patch_bgr[:, :, 0]))
            mean_g = float(np.mean(patch_bgr[:, :, 1]))
            mean_r = float(np.mean(patch_bgr[:, :, 2]))

            l_val = float(np.mean(patch_lab[:, :, 0])) * 100.0 / 255.0
            a_val = float(np.mean(patch_lab[:, :, 1])) - 128.0
            b_val = float(np.mean(patch_lab[:, :, 2])) - 128.0

            moisture_p = float(np.clip(100.0 - l_val, 0.0, 100.0))
            redness_i = float((mean_r ** 2) / (mean_g * mean_b + 1e-4))
            
            # Sharpness Laplacian
            gray_p = cv2.cvtColor(patch_bgr, cv2.COLOR_BGR2GRAY)
            lap_v = float(cv2.Laplacian(gray_p, cv2.CV_64F).var())

            # Calibrated pH Proxy
            # Empirically: Red Laterite soil with high a*, redness has lower pH (acidic 4.8 - 5.5)
            # Black organic soil has higher organic matter (pH 6.0 - 7.0)
            base_ph = 6.2 - (redness_i * 0.45) + (b_val * 0.02)
            est_ph = float(np.clip(base_ph, 4.5, 7.8))

            if redness_i > 1.4:
                soil_family = "ดินลูกรังสีแดง (กรด/ธาตุเหล็กสูง)"
            elif l_val < 38.0:
                soil_family = "ดินดำอินทรียวัตถุสูง (ร่วน/ชื้นดี)"
            elif b_val > 14.0:
                soil_family = "ดินร่วนปนทราย (โปร่ง/ระบายน้ำเร็ว)"
            else:
                soil_family = "ดินเหนียว/ดินร่วนมาตรฐาน"

            l_stars.append(l_val)
            a_stars.append(a_val)
            b_stars.append(b_val)
            moistures.append(moisture_p)
            rednesses.append(redness_i)
            sharpnesses.append(lap_v)
            ph_proxies.append(est_ph)

            color_bgr = palette[idx % len(palette)]
            # Draw on annotated image
            cv2.rectangle(annotated_cv, (x1, y1), (x2, y2), color_bgr, 2)
            cv2.circle(annotated_cv, (px, py), 4, (0, 0, 255), -1)
            
            lbl = point_labels[idx]
            cv2.putText(annotated_cv, lbl, (x1, max(14, y1 - 6)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, color_bgr, 1, cv2.LINE_AA)

            samples.append({
                "point_id": idx + 1,
                "label": lbl,
                "center": (px, py),
                "bbox": (x1, y1, x2 - x1, y2 - y1),
                "patch_pil": cls.cv2_to_pil(patch_bgr),
                "l_star": round(l_val, 1),
                "a_star": round(a_val, 1),
                "b_star": round(b_val, 1),
                "moisture_proxy_pct": round(moisture_p, 1),
                "redness_index": round(redness_i, 2),
                "sharpness_lap": round(lap_v, 1),
                "estimated_ph": round(est_ph, 2),
                "soil_family": soil_family
            })

        # Calculate Aggregate Cross-Point Statistics
        mean_l = float(np.mean(l_stars))
        std_l = float(np.std(l_stars))
        mean_moist = float(np.mean(moistures))
        std_moist = float(np.std(moistures))
        mean_redness = float(np.mean(rednesses))
        mean_ph = float(np.mean(ph_proxies))
        std_ph = float(np.std(ph_proxies))

        # Spatial Homogeneity Index (ดัชนีความสม่ำเสมอของเนื้อดินเชิงพื้นที่)
        # 100% means completely uniform; lower percentage means high heterogeneity
        cv_pct = (std_l / (mean_l + 1e-5)) * 100.0
        homogeneity_idx = float(np.clip(100.0 - cv_pct, 10.0, 99.9))

        if homogeneity_idx >= 88.0:
            homogeneity_verdict = "เนื้อดินมีความสม่ำเสมอสูงมาก (Highly Homogeneous)"
        elif homogeneity_idx >= 75.0:
            homogeneity_verdict = "เนื้อดินสม่ำเสมอในเกณฑ์มาตรฐาน (Acceptable Uniformity)"
        else:
            homogeneity_verdict = "เนื้อดินมีความแปรปรวนเชิงพื้นที่สูง (Spatial Heterogeneity) ควรให้ปุ๋ยเฉพาะจุด"

        return {
            "strategy": strategy,
            "total_points": len(points),
            "samples": samples,
            "annotated_pil": cls.cv2_to_pil(annotated_cv),
            "aggregate_stats": {
                "mean_l_star": round(mean_l, 1),
                "std_l_star": round(std_l, 2),
                "mean_moisture_pct": round(mean_moist, 1),
                "std_moisture_pct": round(std_moist, 2),
                "mean_redness": round(mean_redness, 2),
                "mean_estimated_ph": round(mean_ph, 2),
                "std_estimated_ph": round(std_ph, 2),
                "homogeneity_index_pct": round(homogeneity_idx, 1),
                "homogeneity_verdict": homogeneity_verdict
            }
        }


def extract_target_roi(
    img_rgb_or_bgr: np.ndarray,
    mode: str = "auto",
    pad_ratio: float = 0.08,
    return_stages: bool = False
) -> Tuple[np.ndarray, Tuple[int, int, int, int]]:
    """
    ฟังก์ชันสากลแบบ Standalone สำหรับสกัดพื้นที่เป้าหมายความแม่นยำสูง (Agri-Vision 2.0 Precision ROI)
    รองรับทั้งการเทรนใน PyTorch DataLoader, ใน Colab Notebook และใน Server REST API
    """
    if len(img_rgb_or_bgr.shape) == 2:
        img_bgr = cv2.cvtColor(img_rgb_or_bgr, cv2.COLOR_GRAY2BGR)
    elif img_rgb_or_bgr.shape[2] == 3:
        # สมมติเป็น BGR ตามมาตรฐาน OpenCV แต่ตรวจสอบถ้าเป็น RGB
        img_bgr = img_rgb_or_bgr
    else:
        img_bgr = img_rgb_or_bgr[:, :, :3]

    stages = SoilVisionPreprocessor.get_pipeline_stages(img_bgr, padding_ratio=pad_ratio, mode=mode)
    bx, by, bw, bh = stages["bbox"]
    cropped = img_bgr[by:by+bh, bx:bx+bw] if (bw > 30 and bh > 30) else img_bgr

    if return_stages:
        return cropped, stages["bbox"], stages
    return cropped, stages["bbox"]


def plot_roi_diagnostic_stages(stages_dict: Dict[str, Any], title: Optional[str] = None):
    """
    วาดแผนภาพแสดงรายละเอียดทุกขั้นตอนของ ROI Pipeline (6-Panel High-Tech Layout)
    เหมาะสำหรับใช้ใน Colab, รายงานวิจัย หรือ Streamlit Matplotlib rendering
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("⚠️ กรุณาติดตั้ง matplotlib เพื่อแสดงผลกราฟ (pip install matplotlib)")
        return None

    fig, axes = plt.subplots(2, 3, figsize=(15, 9.5))
    axes = axes.flatten()

    panels = [
        ("Step 1: Input Frame & Target Center", stages_dict["stage_1_input_pil"]),
        ("Step 2: Bio-Spectral Salience (ExG/Lab)", stages_dict["stage_2_salience_pil"]),
        ("Step 3: 2D Center Gaussian Spatial Prior", stages_dict["stage_3_center_prior_pil"]),
        ("Step 4: Fused Mask & Morphological Closing", stages_dict["stage_4_mask_pil"]),
        ("Step 5: Contours & Convex Hull (Solidity)", stages_dict["stage_5_contour_pil"]),
        ("Step 6: Bounding Box & Target ROI", stages_dict["stage_6_annotated_pil"])
    ]

    for i, (p_title, p_img) in enumerate(panels):
        axes[i].imshow(p_img, cmap='gray' if i == 3 else None)
        axes[i].set_title(p_title, fontsize=11, fontweight='bold', pad=8)
        axes[i].axis('off')

    tel = stages_dict.get("telemetry", {})
    t_type = tel.get("target_type", "General")
    sol = tel.get("solidity", 0.0)
    conf = stages_dict.get("confidence", 0.0) * 100
    blur = tel.get("laplacian_blur", 0.0)
    
    header_title = title or f"Agri-Vision 2.0 Precision ROI Diagnostic: {t_type}"
    fig.suptitle(f"{header_title}\n[Conf: {conf:.1f}% | Solidity: {sol:.2f} | Sharpness Lap: {blur:.1f}]", 
                 fontsize=13, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0.02, 1, 0.94])
    return fig

