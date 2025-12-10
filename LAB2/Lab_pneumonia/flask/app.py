"""
🌐 Flask Advanced - AI Pneumonia Detector API
✨ Features: 
- RESTful API with Blueprint architecture
- Image Classification + GradCAM
- Request validation & error handling
- File upload management
- JSON/Image responses
- CORS enabled
- Logging system
"""

import os
import io
import time
import base64
import logging
from pathlib import Path
from functools import wraps
from typing import Dict, Any, Tuple

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

from flask import (
    Flask,
    request,
    jsonify,
    send_file,
    Blueprint,
    make_response
)
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

# ==================== CONFIGURATION ====================
MODEL_PATH = "../streamlit/model/pneumonia_classifier.h5"
CLASS_NAMES = ["NORMAL", "PNEUMONIA"]
TARGET_SIZE = (224, 224)
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "tiff"}

# ==================== LOGGING ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== FLASK APP ====================
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_IMAGE_SIZE
app.config['JSON_SORT_KEYS'] = False

CORS(app, resources={r"/*": {"origins": "*"}})

# ==================== GLOBAL STATE ====================
model = None

# ==================== MODEL LOADING ====================
def load_model():
    """Chargement du modèle TensorFlow"""
    global model
    try:
        model_path = Path(__file__).parent / MODEL_PATH
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        # Charger avec tf_keras (compatible TF 2.16.2)
        import tf_keras as keras
        model = keras.models.load_model(str(model_path), compile=False)
        logger.info(f"✅ Model loaded successfully from {model_path}")
    except Exception as e:
        logger.error(f"❌ Error loading model: {e}")
        raise

# ==================== UTILITY FUNCTIONS ====================
def allowed_file(filename: str) -> bool:
    """Vérification extension fichier"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image: Image.Image) -> np.ndarray:
    """Prétraitement image"""
    img = image.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
    img = img.convert("RGB")
    
    arr = np.asarray(img).astype("float32")
    arr = (arr / 127.5) - 1.0
    arr = np.expand_dims(arr, axis=0)
    return arr

def analyze_quality(image: Image.Image) -> Dict[str, Any]:
    """Analyse qualité d'image"""
    img_gray = image.convert("L")
    arr = np.asarray(img_gray).astype("float32") / 255.0
    
    brightness = float(np.mean(arr))
    contrast = float(np.std(arr))
    h, w = arr.shape
    aspect_ratio = float(w / h) if h > 0 else 0.0
    
    warnings = []
    if brightness < 0.15:
        warnings.append("Image très sombre")
    elif brightness > 0.85:
        warnings.append("Image très claire")
    
    if contrast < 0.05:
        warnings.append("Contraste très faible")
    
    if aspect_ratio < 0.6 or aspect_ratio > 1.8:
        warnings.append("Ratio inhabituel")
    
    return {
        "brightness": round(brightness, 4),
        "contrast": round(contrast, 4),
        "aspect_ratio": round(aspect_ratio, 4),
        "warnings": warnings,
    }

def generate_heatmap(image: Image.Image, alpha: float = 0.45) -> np.ndarray:
    """Génération heatmap GradCAM"""
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

# ==================== DECORATORS ====================
def require_model(f):
    """Decorator pour vérifier que le modèle est chargé"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if model is None:
            return jsonify({
                "error": "Model not loaded",
                "message": "Service unavailable"
            }), 503
        return f(*args, **kwargs)
    return decorated_function

def validate_image(f):
    """Decorator pour valider l'image uploadée"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                "error": "Invalid file type",
                "allowed": list(ALLOWED_EXTENSIONS)
            }), 400
        
        return f(*args, **kwargs)
    return decorated_function

# ==================== API BLUEPRINT ====================
api = Blueprint('api', __name__, url_prefix='/api/v1')

@api.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy" if model is not None else "unhealthy",
        "model_loaded": model is not None,
        "version": "2.0.0",
        "timestamp": time.time()
    })

@api.route('/predict', methods=['POST'])
@require_model
@validate_image
def predict():
    """
    Prédiction NORMAL/PNEUMONIA
    ---
    POST /api/v1/predict
    Content-Type: multipart/form-data
    Body: file=<image>
    """
    start_time = time.time()
    
    try:
        file = request.files['file']
        image = Image.open(file.stream)
        
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
        
        return jsonify({
            "success": True,
            "class_name": class_name,
            "confidence": round(confidence, 4),
            "probabilities": {
                "NORMAL": round(normal_prob, 4),
                "PNEUMONIA": round(pneumonia_prob, 4)
            },
            "processing_time_ms": round(processing_time, 2)
        })
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/analyze/quality', methods=['POST'])
@validate_image
def analyze_quality_endpoint():
    """Analyse qualité d'image"""
    try:
        file = request.files['file']
        image = Image.open(file.stream)
        
        quality = analyze_quality(image)
        
        return jsonify({
            "success": True,
            "quality": quality
        })
    
    except Exception as e:
        logger.error(f"Quality analysis error: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/analyze/full', methods=['POST'])
@require_model
@validate_image
def full_analysis():
    """Analyse complète: Prédiction + Qualité + Heatmap"""
    start_time = time.time()
    include_heatmap = request.args.get('include_heatmap', 'true').lower() == 'true'
    
    try:
        file = request.files['file']
        image = Image.open(file.stream)
        
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
            "confidence": round(confidence, 4),
            "probabilities": {
                "NORMAL": round(normal_prob, 4),
                "PNEUMONIA": round(pneumonia_prob, 4)
            },
            "processing_time_ms": round(processing_time, 2)
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
                logger.warning(f"Heatmap generation failed: {e}")
        
        return jsonify({
            "prediction": prediction_data,
            "quality": quality_data,
            "heatmap_base64": heatmap_base64
        })
    
    except Exception as e:
        logger.error(f"Full analysis error: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/heatmap', methods=['POST'])
@require_model
@validate_image
def get_heatmap():
    """Génération heatmap seul (retourne PNG)"""
    alpha = float(request.args.get('alpha', 0.45))
    
    try:
        file = request.files['file']
        image = Image.open(file.stream)
        
        heatmap_img = generate_heatmap(image, alpha=alpha)
        heatmap_pil = Image.fromarray(heatmap_img)
        
        buffer = io.BytesIO()
        heatmap_pil.save(buffer, format="PNG")
        buffer.seek(0)
        
        return send_file(buffer, mimetype='image/png')
    
    except Exception as e:
        logger.error(f"Heatmap error: {e}")
        return jsonify({"error": str(e)}), 500

# ==================== ROOT ROUTES ====================
@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        "name": "AI Pneumonia Detector API",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "health": "/api/v1/health",
            "predict": "/api/v1/predict",
            "quality": "/api/v1/analyze/quality",
            "full_analysis": "/api/v1/analyze/full",
            "heatmap": "/api/v1/heatmap"
        }
    })

# ==================== ERROR HANDLERS ====================
@app.errorhandler(413)
def request_entity_too_large(error):
    """Fichier trop volumineux"""
    return jsonify({
        "error": "File too large",
        "max_size_mb": MAX_IMAGE_SIZE / (1024 * 1024)
    }), 413

@app.errorhandler(404)
def not_found(error):
    """Route non trouvée"""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Erreur interne"""
    logger.error(f"Internal error: {error}")
    return jsonify({"error": "Internal server error"}), 500

# ==================== REGISTER BLUEPRINT ====================
app.register_blueprint(api)

# ==================== MAIN ====================
if __name__ == '__main__':
    load_model()
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,  # ⚠️ Debug=True cause des crashes TensorFlow
        threaded=False  # Single thread pour TensorFlow
    )
