#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OnnxClassifier — ตัวจำแนกภาพออฟไลน์จากโมเดลที่เทรนใน Workshop (smart_agri_model.onnx + labels.json)
ใช้แทนการประเมินด้วยเกณฑ์สี (edge_classifier.py) โดยคืนค่ารูปแบบ JSON เดียวกับระบบเดิม

ความแตกต่างสำคัญ:
- ค่า confidence มาจากการคำนวณจริง (softmax ที่ปรับเทียบด้วย temperature) ไม่ใช่ข้อความตายตัว
- ถ้าความมั่นใจต่ำกว่าเกณฑ์ใน labels.json จะตอบ "ไม่แน่ใจ" แทนการฟันธง
- แนบค่าประเมินของโมเดล (ความแม่นยำบนชุดทดสอบ, จำนวนภาพทดสอบ) ไว้ในผลลัพธ์

การใช้งาน:
    clf = OnnxClassifier("smart_agri_model.onnx", "labels.json")
    result = clf.classify(PIL.Image.open("soil.jpg"))
ต้องติดตั้ง: pip install onnxruntime pillow numpy
"""
import json
import numpy as np
from PIL import Image

# (ไม่บังคับ) ชื่อไทยของคลาส — เพิ่ม/แก้ได้ตามชุดข้อมูลที่ใช้ ถ้าไม่มีจะแสดงชื่อโฟลเดอร์เดิม
DISPLAY_NAMES = {
    "black_soil": "ดินดำ",
    "cinder_soil": "ดินตะกรัน/ขี้เถ้าภูเขาไฟ",
    "laterite_soil": "ดินลูกรัง",
    "peat_soil": "ดินพีต",
    "yellow_soil": "ดินเหลือง",
}


class OnnxClassifier:
    def __init__(self, model_path="smart_agri_model.onnx", labels_path="labels.json", display_names=None):
        import onnxruntime as ort
        with open(labels_path, encoding="utf-8") as f:
            self.meta = json.load(f)
        self.sess = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
        self.classes = self.meta["classes"]
        self.pp = self.meta["preprocess"]
        self.temperature = float(self.meta.get("temperature", 1.0))
        self.threshold = float(self.meta.get("unsure_threshold", 0.6))
        self.names = {**DISPLAY_NAMES, **(display_names or {})}

    def _preprocess(self, img: Image.Image):
        im = img.convert("RGB")
        w, h = im.size
        s = self.pp["resize_shorter_side"] / min(w, h)
        im = im.resize((max(1, round(w * s)), max(1, round(h * s))), Image.BILINEAR)
        w, h = im.size
        c = self.pp["center_crop"]
        l, t = (w - c) // 2, (h - c) // 2
        im = im.crop((l, t, l + c, t + c))
        x = (np.asarray(im, dtype=np.float32) / 255.0 - np.array(self.pp["mean"], np.float32)) / np.array(self.pp["std"], np.float32)
        return x.transpose(2, 0, 1)[None].astype(np.float32)

    def probabilities(self, img: Image.Image):
        z = self.sess.run(None, {self.meta["input"]["name"]: self._preprocess(img)})[0][0] / self.temperature
        p = np.exp(z - z.max())
        return p / p.sum()

    def classify(self, img: Image.Image, location_info: str = "") -> dict:
        prob = self.probabilities(img)
        order = prob.argsort()[::-1]
        top = int(order[0])
        top_p = float(prob[top])
        name = lambda i: self.names.get(self.classes[i], self.classes[i])
        ev = self.meta.get("evaluation", {})
        ci = ev.get("test_ci95", ["?", "?"])
        eval_line = (f"โมเดลนี้มีความแม่นยำบนชุดทดสอบ {ev.get('test_acc', '?')}% "
                     f"(ช่วงเชื่อมั่น 95%: {ci[0]}–{ci[1]}%, n={ev.get('n_test', '?')}) — ใช้ได้เฉพาะภาพที่คล้ายชุดฝึก")
        observations = [f"อันดับ {r}: {name(int(i))} {100*prob[i]:.1f}%" for r, i in enumerate(order[:3], 1)]
        unsure = top_p < self.threshold

        if unsure:
            status = "ไม่แน่ใจ (ความมั่นใจต่ำกว่าเกณฑ์)"
            details = (f"ความมั่นใจสูงสุด {100*top_p:.0f}% ต่ำกว่าเกณฑ์ {100*self.threshold:.0f}% "
                       f"จึงไม่สรุปผล ภาพอาจต่างจากข้อมูลที่โมเดลเรียนมา (แสง มุม หรือชนิดที่ไม่มีในชุดฝึก). บริบท: {location_info or 'ไม่ระบุ'}")
            recs = ["ถ่ายภาพใหม่ในแสงธรรมชาติสม่ำเสมอ ไม่มีเงาหรือแดดจ้า และให้ตัวอย่างเต็มกรอบ",
                    "ส่งตัวอย่างตรวจยืนยันด้วยการวัดจริงหรือผู้เชี่ยวชาญ"]
        else:
            status = f"คัดกรองเบื้องต้น: {name(top)}"
            details = (f"โมเดลจำแนกเป็น {name(top)} ด้วยความมั่นใจ {100*top_p:.0f}% (ปรับเทียบแล้ว). {eval_line}. "
                       f"บริบท: {location_info or 'ไม่ระบุ'}")
            recs = ["ใช้ผลนี้เป็นข้อมูลประกอบ ไม่ใช่ข้อสรุปสุดท้าย",
                    "ยืนยันด้วยการวัดจริง เช่น pH, N-P-K หรือการตรวจทางห้องปฏิบัติการก่อนตัดสินใจจัดการแปลง"]
        return {
            "target_type": self.meta.get("task", "soil"),
            "predicted_class": None if unsure else self.classes[top],
            "confidence_score": f"{100*top_p:.0f}%",
            "confidence_value": round(top_p, 4),
            "is_uncertain": unsure,
            "visual_observations": observations,
            "diagnosis": {"status": status, "details": details},
            "recommendations": recs,
            "disclaimer": "ผลจากปัญญาประดิษฐ์เป็นการคัดกรองเบื้องต้นเท่านั้น ต้องยืนยันด้วยการตรวจวัดจริงหรือผู้เชี่ยวชาญ",
        }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        sys.exit("ใช้งาน: python 2026-10-15-onnx_classifier.py <ภาพ.jpg> [model.onnx] [labels.json]")
    clf = OnnxClassifier(*(sys.argv[2:4] if len(sys.argv) >= 4 else []))
    print(json.dumps(clf.classify(Image.open(sys.argv[1])), ensure_ascii=False, indent=2))
