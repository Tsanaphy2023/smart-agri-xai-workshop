# 📦 แคตตาล็อกชุดข้อมูลและการจัดระเบียบโครงสร้าง (Smart Agri Dataset Catalog)
**ระบบ:** Smart Soil & Plant Environmental AI Analyzer  
**ผู้ออกแบบหลักสูตรและระบบ:** ผศ.ดร.ชีวะ ทัศนา (มหาวิทยาลัยราชภัฏรำไพพรรณี)  
**ตำแหน่งจัดเก็บ:** [`6_My_Business/6.2_Products_Services/smart-soil-ai/datasets/`](file:///Users/chewathassana/Desktop/6_My_Business/6.2_Products_Services/smart-soil-ai/datasets)

---

## 1. ผังโครงสร้างการจัดหมวดหมู่ข้อมูล (Hierarchical Dataset Architecture)

เพื่อรองรับการอบรมเชิงปฏิบัติการ (Workshop Hands-on) และงานวิจัยที่ผู้เรียนสามารถเลือกฝึกโมเดลได้ตามโจทย์จริง โครงสร้างข้อมูลถูกจัดแบ่งออกเป็น 2 เสาหลักตามมาตรฐานของ ผศ.ดร.ชีวะ ทัศนา:

```text
datasets/
├── 📁 1. ระบบอัจฉริยะด้านดิน (Soil Analysis) - 4 กลุ่มย่อย
│   ├── 📁 1.1 SoilType/                           # จำแนกชนิดเนื้อดิน 5 คลาส (ภาพจริง 156 ภาพ)
│   │   └── 📁 01_Real_Data/ (train/ และ val/)
│   ├── 📁 1.2 SoilNutrient (Thai Local)/          # ธาตุอาหารและปุ๋ยดินไทย
│   │   └── thai_soil_crop_recommendation.csv      # N, P, K, pH, พืชไทย (ทุเรียน, ข้าวหอมมะลิ) & โดโลไมต์
│   ├── 📁 1.3 SoilNutrient (Global ML)/           # ฐานข้อมูลทำนายพืชสากล
│   │   └── 01_Real_Data/Crop_recommendation.csv   # 2,200 แถว / 22 พืช (Nearest Centroid Engine)
│   └── 📁 1.4 OSSL Soil Spectroscopy/             # สเปกโตรสโกปีดินขั้นสูง
│       └── 01_Real_Data/OSSL_Soil_Spectroscopy/   # sample_visnir, sample_mir, neospectra, ASD files
│
└── 📁 2. ระบบอัจฉริยะด้านพืช (Plant)
    ├── 📁 2.1 โรคพืช (Plant Diseases) - 5 กลุ่มย่อย (1,347 ภาพ)
    │   ├── 📁 Durian_ทุเรียน/                      # 380 ภาพ (แอนแทรคโนส, รากเน่าโคนเน่า, จุดสนิมสาหร่าย, ปกติ)
    │   ├── 📁 Maize_ข้าวโพด/                      # 360 ภาพ (ราสนิมข้าวโพด, ใบจุดสีเทา, ใบไหม้, ปกติ)
    │   ├── 📁 Tomato_มะเขือเทศ/                   # 360 ภาพ (Early blight, Late blight, Leaf mold, ปกติ)
    │   ├── 📁 Rice_ข้าว/                          # 186 ภาพ (ขอบใบแห้ง BLB, ใบจุดสีน้ำตาล, โรคไหม้, ปกติ)
    │   └── 📁 Cassava_มันสำปะหลัง/                # 61 ภาพ (CMD, CBB, CBSD, ปกติ)
    │
    ├── 📁 2.2 แมลงศัตรูพืช (Plant Insect Pests) - 3 กลุ่ม (761 ภาพ)
    │   ├── 📁 Durian_ทุเรียน/                      # 220 ภาพ (เพลี้ยไก่แจ้, หนอนเจาะต้น, ไรแดง, ใบสมบูรณ์)
    │   ├── 📁 General_Crops_พืชทั่วไป/            # 300 ภาพ (หนอนกระทู้, เพลี้ยอ่อน, หนอนใยผัก, แมลงหวี่ขาว)
    │   └── 📁 Rice_ข้าว/                          # 241 ภาพ (เพลี้ยกระโดดสีน้ำตาล, หนอนกอข้าว, หนอนห่อใบ)
    │
    └── 📁 2.3 การขาดธาตุอาหารหลัก (Plant Nutrient Deficiencies) - 4 กลุ่ม (305 ภาพ)
        ├── 📁 General_พืชทั่วไป/                  # 124 ภาพ (ขาด N, ขาด P, ขาด K, ปกติ)
        ├── 📁 Durian_ทุเรียน/                      # 60 ภาพ (ขาด N, ขาด K, ขาด Mg, ปกติ)
        ├── 📁 Maize_ข้าวโพด/                      # 60 ภาพ (ขาด N, ขาด P, ขาด K, ปกติ)
        └── 📁 Rice_ข้าว/                          # 61 ภาพ (ขาด N, ขาด P, ขาด K, ปกติ)
```

> [!NOTE]
> **การแยกข้อมูลจริงและข้อมูลจำลองอย่างชัดเจน (Real vs Synthetic Separation):**  
> ในแต่ละโฟลเดอร์พืชและดิน ได้จัดแบ่งโครงสร้างออกเป็น 2 หมวดย่อยเพื่อความโปร่งใสทางวิชาการและการเปรียบเทียบผลลัพธ์ (Ablation Study):
> - **`01_Real_Data/`**: รวบรวมภาพถ่ายและข้อมูลจริง 100% จากฐานข้อมูลวิจัยระดับโลก (Kaggle, PlantVillage, Durian Dataset, Rice Dataset, Corn Dataset, Pest24, OSSL Spectroscopy, Crop Recommendation) รวมกว่า **1,795 ไฟล์จริง**
> - **`02_Synthetic_Data/`**: รวบรวมภาพจำลองเสมือนจริงที่จัดทำขึ้นสำหรับการทดสอบระบบและ Starter Kit รวม **840 ภาพ**
> รวมทั้งสิ้น **2,875 ไฟล์** ทุกโฟลเดอร์ย่อยแบ่งสัดส่วน `train/` และ `val/` สมบูรณ์ รองรับ PyTorch `ImageFolder` โดยตรง 100%

---

## 2. ฐานข้อมูลเปิดระดับโลกที่แนะนำสำหรับการอบรม (Open Benchmark Repositories)

สำหรับการฝึกอบรมเชิงลึกหรือโครงการวิจัยขนาดใหญ่ สามารถดาวน์โหลดชุดข้อมูลเปิดระดับโลกมาขยายผลเพิ่มเติมได้ดังนี้:

### 1. PlantDoc Dataset (Cornell University & IIT Kanpur)
* **จุดเด่น:** ภาพถ่ายโรคพืชในสภาพแวดล้อมจริงตามธรรมชาติ (**In-The-Wild**) มีแสงเงา มุมกล้อง และฉากหลังที่ท้าทาย แตกต่างจากภาพถ่ายในห้องแล็บ
* **ขนาด:** 2,569 ภาพ ความละเอียดสูง ครอบคลุม 13 ชนิดพืช และ 27 คลาสโรค
* **พืชที่มี:** มะเขือเทศ (Tomato), ข้าวโพด (Corn), แอปเปิ้ล, พริกหยวก, มันฝรั่ง, ถั่วเหลือง ฯลฯ
* **Repository:** [github.com/pratikkayal/PlantDoc-Dataset](https://github.com/pratikkayal/PlantDoc-Dataset)
* **วิธีดาวน์โหลด:**
  ```bash
  git clone --depth 1 https://github.com/pratikkayal/PlantDoc-Dataset.git
  ```

### 2. IP102: A Large-Scale Benchmark Dataset for Insect Pest Recognition (CVPR 2019)
* **จุดเด่น:** ชุดข้อมูลภาพแมลงศัตรูพืชทางการเกษตรที่ใหญ่ที่สุดในโลก ครอบคลุมการจำแนกระดับอนุกรมวิธาน (Taxonomic Hierarchy)
* **ขนาด:** 75,222 ภาพ แบ่งเป็น 102 ชนิดแมลง
* **แมลงที่เกี่ยวข้องกับไทย:** เพลี้ยกระโดดสีน้ำตาล (Brown Planthopper), หนอนกอข้าว (Rice Stem Borer), หนอนกระทู้ข้าวโพดลายจุด (Fall Armyworm), เพลี้ยอ่อน (Aphids)
* **Repository:** [github.com/xpwu95/IP102](https://github.com/xpwu95/IP102)

### 3. PlantVillage Dataset (Penn State University & EPFL)
* **จุดเด่น:** ชุดข้อมูลคลาสสิกมาตรฐานทองคำสำหรับการเริ่มต้นศึกษา Deep Learning ด้านโรคพืช
* **ขนาด:** 54,306 ภาพ แบ่งเป็น 38 คลาสโรคพืชในสภาวะควบคุม
* **Repository / Kaggle:** [kaggle.com/datasets/abdallahalidev/plantvillage-dataset](https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset)

### 4. Durian Leaf Disease & Pest Datasets (ชุดข้อมูลโรคทุเรียนไทยและอาเซียน)
* **จุดเด่น:** รวบรวมโรคใบสำคัญของทุเรียนหมอนทอง ชะนี ก้านยาว เช่น ใบจุดสนิมสาหร่าย (Algal Leaf Spot), รากเน่าโคนเน่า (Phytophthora), ใบไหม้แอนแทรคโนส (Colletotrichum)
* **Repository:** [github.com/gianguyen14/durian-leaf-disease-detection](https://github.com/gianguyen14/durian-leaf-disease-detection)
* **Mendeley Data:** *Durian Leaf Disease Dataset* (DOI: 10.17632/db47d33rmm.1)

### 5. Cassava Leaf Disease Dataset (Kaggle & Makerere AI Lab)
* **จุดเด่น:** ชุดข้อมูลโรคใบมันสำปะหลังที่จัดแข่งขันระดับโลกโดย Google Research & Kaggle
* **ขนาด:** 21,367 ภาพ (คัดแยกโรค CMD, CBB, CBSD, CGM และ Healthy)
* **Kaggle:** [kaggle.com/c/cassava-leaf-disease-classification](https://www.kaggle.com/c/cassava-leaf-disease-classification)

### 6. Rice Leaf Disease & Nutrient Deficiencies (IRRI & Kaggle)
* **จุดเด่น:** ภาพวิเคราะห์อาการขาดธาตุอาหาร N-P-K เทียบกับแผ่นเทียบสีใบข้าว (Leaf Color Chart: LCC) และโรคขอบใบแห้ง โรคไหม้
* **Kaggle:** [kaggle.com/datasets](https://www.kaggle.com) ค้นหา `Nutrient-Deficiency-Symptoms-in-Rice`

### 7. Kaggle Soil Types Dataset (5 Classes, CycleGAN Augmented)
* **จุดเด่น:** ภาพดิน 5 ประเภทสำหรับการจำแนกกายภาพ (Black, Cinder, Laterite, Peat, Yellow)
* **คำสั่งดาวน์โหลดอัตโนมัติ:**
  ```python
  import kagglehub
  path = kagglehub.dataset_download("prasanshasatpathy/soil-types")
  ```

### 8. OSSL — Open Soil Spectral Library (ระดับโลกด้านธาตุอาหารและสเปกโทรสโกปีของดิน)
* **องค์กรผู้พัฒนา:** Soil Spectroscopy for the Global Good (Woodwell Climate, OpenGeoHub, University of Florida)
* **จุดเด่น:** คลังข้อมูลสเปกตรัมดินที่ใหญ่ที่สุดในโลก ครอบคลุม Vis-NIR (Visible-Near Infrared) และ MIR (Mid-Infrared) จับคู่กับผลวิเคราะห์เคมีเปียกในห้องปฏิบัติการ (N, P, K, pH, Organic Carbon, Cation Exchange Capacity: CEC, Texture)
* **การนำไปใช้:** พัฒนา Machine Learning ทำนายธาตุอาหารและคุณสมบัติดินจากคลื่นแสงสะท้อนโดยไม่ต้องใช้สารเคมี
* **เว็บไซต์/พอร์ทัล:** [soilspectroscopy.org](https://soilspectroscopy.org) | OSSL Explorer

### 9. WoSIS & SoilGrids (ISRIC — World Soil Information)
* **WoSIS (World Soil Information Service):** ฐานข้อมูลหน้าตัดดิน (Soil Profiles) มาตรฐานสากลจากกรมพัฒนาที่ดินและหน่วยงานสำรวจดินทั่วโลก
* **SoilGrids:** แผนที่ดิจิทัลทำนายค่าคุณสมบัติดิน 3 มิติทั่วโลก ความละเอียด 250 เมตร (pH, Organic Carbon, Nitrogen, Bulk Density, Clay/Sand/Silt)
* **พอร์ทัลดาวน์โหลดและ REST API:** [isric.org/explore/soilgrids](https://www.isric.org/explore/soilgrids) | [soilgrids.org](https://www.soilgrids.org)

### 10. LUCAS Topsoil Database (สหภาพยุโรป — European Commission JRC)
* **จุดเด่น:** ตัวอย่างดินผิวดินนับหมื่นจุดทั่วทวีปยุโรป วิเคราะห์คุณสมบัติทางเคมี-กายภาพครบถ้วน พร้อมข้อมูล Vis-NIR Spectral Library
* **พอร์ทัล:** [esdac.jrc.ec.europa.eu](https://esdac.jrc.ec.europa.eu) (European Soil Data Centre)

### 11. CoLeaf-DB — Coffee Leaf Nutrition Deficiency Dataset (Mendeley Data)
* **จุดเด่น:** ชุดข้อมูลเบนช์มาร์กมาตรฐานสำหรับตรวจวัดการขาดธาตุอาหารพืชโดยเฉพาะ (Macronutrients: N, P, K, Ca, Mg และ Micronutrients: B, Fe, Mn รวมถึง Multi-deficiency และ Healthy)
* **ขนาด:** 1,006 ภาพความละเอียดสูงในสภาวะแสงควบคุม
* **DOI / แหล่งดาวน์โหลด:** `10.17632/brfgw46wzb.1` ([data.mendeley.com](https://data.mendeley.com))

### 12. AgriPest & Pest24 Datasets (ฐานข้อมูลภาพแมลงศัตรูพืชแปลงจริง)
* **AgriPest (2021):** 49,700 ภาพ พร้อม Bounding Boxes 264,700 จุด ครอบคลุม 14 แมลงศัตรูพืชในสภาพแปลงธรรมชาติจริง ([github.com/liuliu66/AgriPest](https://github.com/liuliu66/AgriPest))
* **Pest24:** 25,378 ภาพแมลง 24 ชนิดจากกับดักจับแมลงอัตโนมัติ (Chinese Academy of Sciences) รองรับโมเดล YOLO และ Object Detection ([kaggle.com/datasets/boatshuai/pest24](https://www.kaggle.com/datasets/boatshuai/pest24))

### 13. Corn/Maize Leaf Disease Dataset (Kaggle & Global Benchmark)
* **จุดเด่น:** ภาพใบข้าวโพด 4,188 ภาพ แบ่งเป็น 4 คลาสหลัก (Common Rust, Gray Leaf Spot, Northern Leaf Blight, Healthy)
* **ดาวน์โหลด:** `kagglehub.dataset_download("smaranjitghose/corn-or-maize-leaf-disease-dataset")`

---

## 3. สคริปต์ดาวน์โหลดและจัดระเบียบอัตโนมัติ (Automated Downloader Tool)

ในโฟลเดอร์นี้มีสคริปต์ [**`download_plant_datasets.py`**](file:///Users/chewathassana/Desktop/6_My_Business/6.2_Products_Services/smart-soil-ai/datasets/download_plant_datasets.py) สำหรับอำนวยความสะดวกให้ผู้เรียนดาวน์โหลดชุดข้อมูลโดยตรง:

```bash
# 1. แสดงรายการชุดข้อมูลทั้งหมดที่รองรับ
python3 datasets/download_plant_datasets.py --list

# 2. ดาวน์โหลด PlantDoc Dataset
python3 datasets/download_plant_datasets.py --dataset plantdoc

# 3. ดาวน์โหลดชุดข้อมูลโรคใบและแมลงทุเรียน
python3 datasets/download_plant_datasets.py --dataset durian

# 4. ดาวน์โหลดภาพชนิดดินจาก Kaggle
python3 datasets/download_plant_datasets.py --dataset soil
```

---

## 4. ขั้นตอนการนำไปฝึกโมเดลใน Workshop (PyTorch MobileNetV3 Transfer Learning)

สคริปต์ [**`train_custom_soil_model.py`**](file:///Users/chewathassana/Desktop/6_My_Business/6.2_Products_Services/smart-soil-ai/datasets/train_custom_soil_model.py) รองรับการเทรนโฟลเดอร์ใดก็ได้ในระบบ เพียงระบุพารามิเตอร์ `--data_dir`:

```bash
# เทรนโมเดลจำแนกชนิดดิน
python3 datasets/train_custom_soil_model.py \
  --data_dir datasets/Soil/SoilType \
  --epochs 10 \
  --output soil_mobilenet_model

# เทรนโมเดลจำแนกโรคทุเรียน
python3 datasets/train_custom_soil_model.py \
  --data_dir datasets/Plant/PlantDiseases/Durian_ทุเรียน \
  --epochs 15 \
  --output durian_disease_model

# เทรนโมเดลจำแนกอาการขาดธาตุอาหารในข้าว
python3 datasets/train_custom_soil_model.py \
  --data_dir datasets/Plant/PlantNutrient/Rice_ข้าว \
  --epochs 10 \
  --output rice_nutrient_model
```

โมเดลจะถูกบันทึกเป็นทั้งไฟล์น้ำหนัก PyTorch (`.pt`) และส่งออกเป็นมาตรฐานเปิด **ONNX (`.onnx`)** นำไปต่อยอดบนเว็บแอปพลิเคชันหรือบอร์ด MicroPython / Edge AI ได้ทันที
