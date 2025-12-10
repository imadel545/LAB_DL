"""
🚀 FastAPI Advanced - AI Pneumonia Detector API
✨ Features: 
- Image Classification (NORMAL/PNEUMONIA)
- GradCAM Heatmap Generation
- Image Quality Analysis
- Async Processing
- CORS Support
- Rate Limiting
- Health Check
- Swagger/ReDoc Documentation
"""

import os
import io
import time
import base64
from typing import Optional, Dict, Any, List
from pathlib import Path

# ==================== ENV CONFIG (AVANT TENSORFLOW) ====================
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np
from PIL import Image
import cv2
import tensorflow as tf
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field
import uvicorn

# ==================== CONFIGURATION ====================
MODEL_PATH = "../streamlit/model/pneumonia_classifier.h5"
CLASS_NAMES = ["NORMAL", "PNEUMONIA"]
TARGET_SIZE = (224, 224)
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB

# ==================== PYDANTIC MODELS ====================
class PredictionResponse(BaseModel):
    """Réponse de prédiction"""
    success: bool
    class_name: str
    confidence: float
    probabilities: Dict[str, float]
    processing_time_ms: float
    
class QualityAnalysis(BaseModel):
    """Analyse qualité d'image"""
    brightness: float = Field(..., ge=0, le=1)
    contrast: float = Field(..., ge=0)
    aspect_ratio: float
    warnings: List[str]
    
class FullAnalysisResponse(BaseModel):
    """Réponse complète avec prédiction + qualité + heatmap"""
    prediction: PredictionResponse
    quality: QualityAnalysis
    heatmap_base64: Optional[str] = None
    
class HealthResponse(BaseModel):
    """Statut santé de l'API"""
    status: str
    model_loaded: bool
    version: str
    timestamp: float

# ==================== FASTAPI APP ====================
app = FastAPI(
    title="AI Pneumonia Detector API",
    description="Advanced REST API for Pneumonia Detection using Deep Learning",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ==================== MIDDLEWARE ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# ==================== GLOBAL STATE ====================
model = None

# ==================== STARTUP EVENT ====================
@app.on_event("startup")
async def load_model():
    """Chargement du modèle au démarrage"""
    global model
    try:
        model_path = Path(__file__).parent / MODEL_PATH
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        # Charger avec tf_keras (compatible TF 2.16.2)
        import tf_keras as keras
        model = keras.models.load_model(str(model_path), compile=False)
        print(f"✅ Model loaded successfully from {model_path}")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        raise

# ==================== UTILITY FUNCTIONS ====================
def preprocess_image(image: Image.Image) -> np.ndarray:
    """Prétraitement identique au Streamlit"""
    img = image.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
    img = img.convert("RGB")
    
    arr = np.asarray(img).astype("float32")
    arr = (arr / 127.5) - 1.0
    arr = np.expand_dims(arr, axis=0)
    return arr

def analyze_quality(image: Image.Image) -> Dict[str, Any]:
    """Analyse qualité de l'image"""
    img_gray = image.convert("L")
    arr = np.asarray(img_gray).astype("float32") / 255.0
    
    brightness = float(np.mean(arr))
    contrast = float(np.std(arr))
    h, w = arr.shape
    aspect_ratio = float(w / h) if h > 0 else 0.0
    
    warnings = []
    if brightness < 0.15:
        warnings.append("Image très sombre (sous-exposée)")
    elif brightness > 0.85:
        warnings.append("Image très claire (sur-exposée)")
    
    if contrast < 0.05:
        warnings.append("Contraste très faible")
    
    if aspect_ratio < 0.6 or aspect_ratio > 1.8:
        warnings.append("Rapport largeur/hauteur inhabituel")
    
    return {
        "brightness": brightness,
        "contrast": contrast,
        "aspect_ratio": aspect_ratio,
        "warnings": warnings,
    }

def generate_heatmap(image: Image.Image, alpha: float = 0.45) -> np.ndarray:
    """Génération de heatmap GradCAM"""
    img_array = preprocess_image(image)
    img_tensor = tf.convert_to_tensor(img_array, dtype=tf.float32)
    
    with tf.GradientTape() as tape:
        tape.watch(img_tensor)
        preds = model(img_tensor, training=False)
        loss = preds[:, 0]
    
    grads = tape.gradient(loss, img_tensor)
    if grads is None:
        raise RuntimeError("Impossible de calculer les gradients")
    
    grads_abs = tf.math.abs(grads)
    heatmap = tf.reduce_mean(grads_abs, axis=-1)[0]
    heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-8)
    heatmap_np = heatmap.numpy()
    
    original_size = image.size
    heatmap_resized = cv2.resize(heatmap_np, original_size)
    heatmap_resized = np.uint8(255 * heatmap_resized)
    heatmap_color = cv2.applyColorMap(heatmap_resized, cv2.COLORMAP_JET)
    
    img_bgr = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
    superimposed = cv2.addWeighted(img_bgr, 1.0 - alpha, heatmap_color, alpha, 0)
    superimposed = cv2.cvtColor(superimposed, cv2.COLOR_BGR2RGB)
    
    return superimposed

# ==================== API ENDPOINTS ====================
@app.get("/", response_model=HealthResponse, tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "version": "2.0.0",
        "timestamp": time.time()
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health():
    """Detailed health check"""
    return {
        "status": "healthy" if model is not None else "unhealthy",
        "model_loaded": model is not None,
        "version": "2.0.0",
        "timestamp": time.time()
    }

@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict(
    file: UploadFile = File(..., description="Chest X-ray image (PNG/JPG)")
):
    """
    Prédiction NORMAL/PNEUMONIA
    
    - **file**: Image de radiographie thoracique
    - Retourne la classe prédite et la confiance
    """
    start_time = time.time()
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Vérification taille
    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=413, detail="Image too large (max 10MB)")
    
    # Vérification format
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        image = Image.open(io.BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    # Prétraitement et prédiction
    x = preprocess_image(image)
    y = model.predict(x, verbose=0)
    
    pneumonia_prob = float(y[0, 0])
    normal_prob = 1.0 - pneumonia_prob
    
    if pneumonia_prob >= 0.5:
        class_name = "PNEUMONIA"
        confidence = pneumonia_prob
    else:
        class_name = "NORMAL"
        confidence = normal_prob
    
    processing_time = (time.time() - start_time) * 1000
    
    return {
        "success": True,
        "class_name": class_name,
        "confidence": confidence,
        "probabilities": {
            "NORMAL": normal_prob,
            "PNEUMONIA": pneumonia_prob
        },
        "processing_time_ms": processing_time
    }

@app.post("/analyze/quality", response_model=QualityAnalysis, tags=["Analysis"])
async def analyze_image_quality(
    file: UploadFile = File(..., description="Image to analyze")
):
    """
    Analyse qualité de l'image
    
    - Brightness, contrast, aspect ratio
    - Warnings sur la qualité
    """
    content = await file.read()
    
    try:
        image = Image.open(io.BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    quality = analyze_quality(image)
    return quality

@app.post("/analyze/full", response_model=FullAnalysisResponse, tags=["Analysis"])
async def full_analysis(
    file: UploadFile = File(...),
    include_heatmap: bool = Query(True, description="Include GradCAM heatmap")
):
    """
    Analyse complète: Prédiction + Qualité + Heatmap
    
    - Prédiction NORMAL/PNEUMONIA
    - Analyse qualité d'image
    - Heatmap GradCAM (optionnel)
    """
    start_time = time.time()
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    content = await file.read()
    
    try:
        image = Image.open(io.BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    # 1. Prédiction
    x = preprocess_image(image)
    y = model.predict(x, verbose=0)
    
    pneumonia_prob = float(y[0, 0])
    normal_prob = 1.0 - pneumonia_prob
    
    if pneumonia_prob >= 0.5:
        class_name = "PNEUMONIA"
        confidence = pneumonia_prob
    else:
        class_name = "NORMAL"
        confidence = normal_prob
    
    processing_time = (time.time() - start_time) * 1000
    
    prediction_data = {
        "success": True,
        "class_name": class_name,
        "confidence": confidence,
        "probabilities": {
            "NORMAL": normal_prob,
            "PNEUMONIA": pneumonia_prob
        },
        "processing_time_ms": processing_time
    }
    
    # 2. Qualité
    quality_data = analyze_quality(image)
    
    # 3. Heatmap
    heatmap_base64 = None
    if include_heatmap:
        try:
            heatmap_img = generate_heatmap(image)
            heatmap_pil = Image.fromarray(heatmap_img)
            
            buffer = io.BytesIO()
            heatmap_pil.save(buffer, format="PNG")
            heatmap_base64 = base64.b64encode(buffer.getvalue()).decode()
        except Exception as e:
            print(f"Heatmap error: {e}")
    
    return {
        "prediction": prediction_data,
        "quality": quality_data,
        "heatmap_base64": heatmap_base64
    }

@app.post("/heatmap", tags=["Visualization"])
async def get_heatmap(
    file: UploadFile = File(...),
    alpha: float = Query(0.45, ge=0, le=1, description="Overlay transparency")
):
    """
    Génération de heatmap GradCAM seul
    
    - Retourne l'image heatmap en PNG
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    content = await file.read()
    
    try:
        image = Image.open(io.BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    try:
        heatmap_img = generate_heatmap(image, alpha=alpha)
        heatmap_pil = Image.fromarray(heatmap_img)
        
        buffer = io.BytesIO()
        heatmap_pil.save(buffer, format="PNG")
        buffer.seek(0)
        
        return StreamingResponse(buffer, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Heatmap generation failed: {e}")

# ==================== MAIN ====================
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
