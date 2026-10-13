#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Soil & Plant AI — REST API Microservice (Port 8000)
เซิร์ฟเวอร์ REST API น้ำหนักเบา สำหรับให้บริการ Inference แก่ Edge AIoT / Flutter / Streamlit
สร้างด้วย Starlette & Uvicorn (Zero-dependency เพิ่มเติม)
ผศ.ดร.ชีวะ ทัศนา | มหาวิทยาลัยราชภัฏรำไพพรรณี
"""

import io
import base64
import json
import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from PIL import Image

from edge_classifier import EdgeAgronomyClassifier
from crop_recommender import CropRecommenderEngine

crop_engine = CropRecommenderEngine()

async def health_check(request):
    return JSONResponse({
        "status": "healthy",
        "service": "Smart Soil & Plant AI Microservice",
        "author": "ผศ.ดร.ชีวะ ทัศนา | มหาวิทยาลัยราชภัฏรำไพพรรณี",
        "version": "1.0.0",
        "endpoints": ["/predict", "/recommend_crops", "/health"]
    })

async def predict_image(request):
    """
    Endpoint รับคำขอวิเคราะห์ภาพถ่าย (Base64)
    POST /predict
    Body: {"image_base64": "...", "location": "...", "model_name": "..."}
    """
    try:
        data = await request.json()
        img_b64 = data.get("image_base64", "")
        location_info = data.get("location", "")
        model_name = data.get("model_name", "Soil-MobileNetV3-Edge")
        
        if not img_b64:
            return JSONResponse({"error": "ไม่พบฟิลด์ image_base64 ในคำขอ"}, status_code=400)
            
        # ถอดรหัส base64 เป็น PIL Image
        img_bytes = base64.b64decode(img_b64)
        image = Image.open(io.BytesIO(img_bytes))
        
        # รันการวิเคราะห์ผ่าน EdgeAgronomyClassifier
        result = EdgeAgronomyClassifier.classify(image, location_info=location_info)
        result["engine"] = f"Custom Microservice ({model_name})"
        
        return JSONResponse(result)
        
    except Exception as e:
        return JSONResponse({"error": f"Internal Server Error: {str(e)}"}, status_code=500)

async def recommend_crops(request):
    """
    Endpoint รับค่าเคมีและกายภาพดินเพื่อแนะนำพืช
    POST /recommend_crops
    Body: {"N": 90, "P": 42, "K": 43, "temperature": 25, "humidity": 80, "ph": 6.5, "rainfall": 200}
    """
    try:
        data = await request.json()
        n = float(data.get("N", 50))
        p = float(data.get("P", 50))
        k = float(data.get("K", 50))
        temp = float(data.get("temperature", 28))
        hum = float(data.get("humidity", 70))
        ph = float(data.get("ph", 6.5))
        rain = float(data.get("rainfall", 100))
        
        rec = crop_engine.predict(n, p, k, temp, hum, ph, rain)
        return JSONResponse(rec)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

app = Starlette(debug=True, routes=[
    Route("/health", health_check, methods=["GET"]),
    Route("/predict", predict_image, methods=["POST"]),
    Route("/recommend_crops", recommend_crops, methods=["POST"]),
])

if __name__ == "__main__":
    print("=" * 65)
    print("🚀 เริ่มต้น Smart Soil & Plant AI REST Microservice บนพอร์ต 8000")
    print("🌐 Endpoint: http://localhost:8000/predict")
    print("=" * 65)
    uvicorn.run(app, host="0.0.0.0", port=8000)
