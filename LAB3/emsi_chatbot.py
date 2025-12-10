"""
🎓 EMSI-Bot PRO - Interface Moderne Ultra Avancée
✨ Design System professionnel avec animations fluides
🚀 Lazy Loading optimisé - Pas de blocage au démarrage
"""

import streamlit as st
import ollama
from typing import List, Dict, Any
import logging
import sys
import os
import time
import asyncio

sys.path.insert(0, os.path.dirname(__file__))
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== MCP INTEGRATION ====================
try:
    from mcp_client import mcp_client
    MCP_AVAILABLE = True
    logger.info("✅ MCP Client chargé avec succès")
except Exception as e:
    MCP_AVAILABLE = False
    logger.warning(f"⚠️ MCP Client non disponible: {e}")

# ==================== CSS 3D PREMIUM ====================
MODERN_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    * { 
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -0.02em;
    }
    
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    /* ANIMATIONS 3D */
    @keyframes fadeIn3D {
        from { 
            opacity: 0; 
            transform: perspective(1000px) translateZ(-50px) rotateX(10deg);
        }
        to { 
            opacity: 1; 
            transform: perspective(1000px) translateZ(0) rotateX(0deg);
        }
    }
    
    @keyframes slideIn3D {
        from { 
            opacity: 0; 
            transform: perspective(1000px) translateX(-50px) rotateY(-15deg);
        }
        to { 
            opacity: 1; 
            transform: perspective(1000px) translateX(0) rotateY(0deg);
        }
    }
    
    @keyframes float3D {
        0%, 100% { transform: perspective(1000px) translateY(0) rotateX(0deg); }
        50% { transform: perspective(1000px) translateY(-10px) rotateX(5deg); }
    }
    
    @keyframes rotate3D {
        0% { transform: perspective(1000px) rotateY(0deg); }
        100% { transform: perspective(1000px) rotateY(360deg); }
    }
    
    @keyframes pulse3D {
        0%, 100% { 
            transform: perspective(1000px) scale(1) translateZ(0);
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        }
        50% { 
            transform: perspective(1000px) scale(1.05) translateZ(10px);
            box-shadow: 0 20px 60px rgba(102, 126, 234, 0.6);
        }
    }
    
    @keyframes shimmer3D {
        0% { 
            background-position: -1000px 0;
            transform: perspective(1000px) translateZ(0);
        }
        50% { transform: perspective(1000px) translateZ(5px); }
        100% { 
            background-position: 1000px 0;
            transform: perspective(1000px) translateZ(0);
        }
    }
    
    @keyframes hologram {
        0%, 100% { opacity: 0.8; filter: hue-rotate(0deg); }
        50% { opacity: 1; filter: hue-rotate(90deg); }
    }
    
    /* MAIN CONTAINER 3D */
    .main {
        animation: fadeIn3D 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        background: 
            radial-gradient(circle at 20% 80%, rgba(102, 126, 234, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(118, 75, 162, 0.15) 0%, transparent 50%),
            linear-gradient(135deg, #0a0a14 0%, #12121f 50%, #1a1a2e 100%);
        position: relative;
        transform-style: preserve-3d;
    }
    
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            repeating-linear-gradient(0deg, rgba(102, 126, 234, 0.03) 0px, transparent 2px, transparent 4px),
            repeating-linear-gradient(90deg, rgba(118, 75, 162, 0.03) 0px, transparent 2px, transparent 4px);
        pointer-events: none;
        animation: hologram 10s ease-in-out infinite;
    }
    
    /* HEADER 3D GRADIENT */
    .stApp header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        backdrop-filter: blur(20px) saturate(180%);
        box-shadow: 
            0 4px 30px rgba(102, 126, 234, 0.3),
            inset 0 -2px 20px rgba(255, 255, 255, 0.1);
        transform: perspective(1000px) translateZ(10px);
        animation: float3D 6s ease-in-out infinite;
    }
    
    /* SIDEBAR 3D PREMIUM */
    section[data-testid="stSidebar"] {
        background: 
            linear-gradient(180deg, 
                rgba(10, 10, 20, 0.95) 0%, 
                rgba(18, 18, 31, 0.98) 50%,
                rgba(26, 26, 46, 0.95) 100%
            ),
            radial-gradient(circle at 50% 0%, rgba(102, 126, 234, 0.15) 0%, transparent 70%);
        border-right: 2px solid;
        border-image: linear-gradient(180deg, 
            rgba(102, 126, 234, 0.8) 0%, 
            rgba(0, 201, 255, 0.6) 50%,
            rgba(118, 75, 162, 0.8) 100%
        ) 1;
        box-shadow: 
            4px 0 50px rgba(102, 126, 234, 0.3),
            inset -2px 0 30px rgba(102, 126, 234, 0.15);
        backdrop-filter: blur(20px) saturate(180%);
        transform-style: preserve-3d;
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #00c9ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 2px 20px rgba(102, 126, 234, 0.6);
        letter-spacing: 0.5px;
        animation: pulse3D 3s ease-in-out infinite;
    }
    
    section[data-testid="stSidebar"] label {
        color: #e0e0ff !important;
        font-weight: 500;
        font-size: 0.95rem;
        letter-spacing: 0.3px;
        transition: all 0.3s ease;
    }
    
    section[data-testid="stSidebar"] label:hover {
        color: #ffffff !important;
        text-shadow: 0 0 15px rgba(102, 126, 234, 0.6);
    }
    
    /* Image logo sidebar */
    section[data-testid="stSidebar"] img {
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    section[data-testid="stSidebar"] img:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 30px rgba(102, 126, 234, 0.5);
    }
    
    /* Colonnes pour les valeurs des sliders */
    section[data-testid="stSidebar"] [data-testid="column"] {
        padding: 0 !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="column"] p {
        margin: 0 !important;
        padding: 0.25rem 0.5rem !important;
        text-align: right !important;
    }
    
    /* MESSAGES 3D */
    .stChatMessage {
        background: rgba(255,255,255,0.03);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(15px) saturate(180%);
        border: 1px solid rgba(255,255,255,0.1);
        animation: slideIn3D 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        transform-style: preserve-3d;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1),
            inset 0 -1px 0 rgba(0, 0, 0, 0.2);
    }
    
    .stChatMessage:hover {
        transform: perspective(1000px) translateY(-5px) translateZ(20px) rotateX(2deg);
        box-shadow: 
            0 20px 50px rgba(102, 126, 234, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    /* USER MESSAGE */
    div[data-testid="stChatMessage"]:has(div.user) {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-left: 3px solid #667eea;
    }
    
    /* ASSISTANT MESSAGE */
    div[data-testid="stChatMessage"]:has(div.assistant) {
        background: linear-gradient(135deg, #00c9ff15 0%, #92fe9d15 100%);
        border-left: 3px solid #00c9ff;
    }
    
    /* BUTTONS MODERNES FLUIDES */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #00c9ff 100%);
        background-size: 200% 200%;
        color: white;
        border: none;
        border-radius: 16px;
        padding: 0.85rem 1.75rem;
        font-weight: 600;
        font-size: 0.95rem;
        letter-spacing: 0.5px;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            0 6px 25px rgba(102, 126, 234, 0.4),
            0 2px 10px rgba(0, 201, 255, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
        animation: gradient-shift 3s ease infinite;
    }
    
    @keyframes gradient-shift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .stButton button:before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, 
            transparent, 
            rgba(255,255,255,0.4), 
            transparent
        );
        transition: left 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stButton button:hover:before {
        left: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 
            0 12px 40px rgba(102, 126, 234, 0.6),
            0 6px 20px rgba(0, 201, 255, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }
    
    .stButton button:active {
        transform: translateY(-1px) scale(0.98);
        box-shadow: 
            0 4px 15px rgba(102, 126, 234, 0.5),
            inset 0 2px 10px rgba(0, 0, 0, 0.2);
    }
    
    /* SLIDERS FLUIDES COLORÉS */
    .stSlider {
        padding: 1.5rem 1rem;
        background: rgba(102, 126, 234, 0.05);
        border-radius: 12px;
        margin: 0.5rem 0;
    }
    
    .stSlider > div > div > div > div[data-baseweb="slider"] {
        background: linear-gradient(90deg, 
            #667eea 0%, 
            #764ba2 35%,
            #00c9ff 70%,
            #92fe9d 100%
        ) !important;
        background-size: 300% 100% !important;
        height: 8px !important;
        border-radius: 10px !important;
        box-shadow: 
            0 2px 15px rgba(102, 126, 234, 0.4),
            0 0 30px rgba(0, 201, 255, 0.2) !important;
        animation: slider-glow 3s ease-in-out infinite;
    }
    
    @keyframes slider-glow {
        0%, 100% { 
            box-shadow: 0 2px 15px rgba(102, 126, 234, 0.4), 0 0 30px rgba(0, 201, 255, 0.2);
            background-position: 0% 50%;
        }
        50% { 
            box-shadow: 0 2px 20px rgba(0, 201, 255, 0.6), 0 0 40px rgba(102, 126, 234, 0.4);
            background-position: 100% 50%;
        }
    }
    
    .stSlider div[role="slider"] {
        background: linear-gradient(135deg, #ffffff 0%, #e0e7ff 100%) !important;
        border: 3px solid rgba(102, 126, 234, 0.6) !important;
        box-shadow: 
            0 4px 20px rgba(102, 126, 234, 0.5),
            0 0 15px rgba(255, 255, 255, 0.6),
            inset 0 1px 3px rgba(255, 255, 255, 0.8) !important;
        width: 22px !important;
        height: 22px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: grab !important;
    }
    
    .stSlider div[role="slider"]:hover {
        transform: scale(1.4) !important;
        box-shadow: 
            0 6px 30px rgba(102, 126, 234, 0.7),
            0 0 25px rgba(255, 255, 255, 0.8),
            inset 0 1px 5px rgba(255, 255, 255, 1) !important;
        border-color: rgba(0, 201, 255, 0.9) !important;
        cursor: grabbing !important;
    }
    
    .stSlider div[role="slider"]:active {
        transform: scale(1.2) !important;
        cursor: grabbing !important;
    }
    
    /* Labels et valeurs des sliders */
    .stSlider label {
        color: #e0e7ff !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .stSlider [data-testid="stTickBar"] {
        color: rgba(224, 231, 255, 0.6) !important;
    }
    
    /* RADIO BUTTONS PERSONA - DESIGN MODERNE CARDS */
    .stRadio > label {
        color: #e0e7ff !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        margin-bottom: 1rem !important;
        text-shadow: 0 2px 10px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Container des options radio */
    .stRadio > div {
        gap: 0.75rem !important;
        display: flex !important;
        flex-direction: column !important;
    }
    
    /* Chaque option radio comme une card */
    .stRadio > div > label {
        background: linear-gradient(135deg, 
            rgba(102, 126, 234, 0.12) 0%, 
            rgba(0, 201, 255, 0.08) 100%
        ) !important;
        backdrop-filter: blur(15px) saturate(180%) !important;
        border-radius: 14px !important;
        border: 2px solid rgba(102, 126, 234, 0.25) !important;
        padding: 0.9rem 1.2rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        box-shadow: 
            0 4px 15px rgba(102, 126, 234, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
    }
    
    /* Hover sur option */
    .stRadio > div > label:hover {
        background: linear-gradient(135deg, 
            rgba(102, 126, 234, 0.25) 0%, 
            rgba(0, 201, 255, 0.18) 100%
        ) !important;
        border-color: rgba(102, 126, 234, 0.6) !important;
        box-shadow: 
            0 0 25px rgba(102, 126, 234, 0.4),
            0 5px 20px rgba(0, 201, 255, 0.25),
            inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
        transform: translateX(4px) !important;
    }
    
    /* Option sélectionnée */
    .stRadio > div > label:has(input:checked) {
        background: linear-gradient(135deg, 
            rgba(102, 126, 234, 0.35) 0%, 
            rgba(0, 201, 255, 0.25) 100%
        ) !important;
        border-color: rgba(0, 201, 255, 0.8) !important;
        box-shadow: 
            0 0 35px rgba(0, 201, 255, 0.6),
            0 6px 25px rgba(102, 126, 234, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        transform: translateX(6px) scale(1.02) !important;
    }
    
    /* Texte de l'option */
    .stRadio > div > label > div {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        padding-left: 0.5rem !important;
    }
    
    /* Option sélectionnée - texte */
    .stRadio > div > label:has(input:checked) > div {
        color: #00c9ff !important;
        font-weight: 700 !important;
        text-shadow: 0 0 15px rgba(0, 201, 255, 0.5) !important;
    }
    
    /* Radio button lui-même */
    .stRadio input[type="radio"] {
        width: 20px !important;
        height: 20px !important;
        border: 2px solid rgba(102, 126, 234, 0.6) !important;
        transition: all 0.3s ease !important;
    }
    
    .stRadio input[type="radio"]:checked {
        background: linear-gradient(135deg, #667eea 0%, #00c9ff 100%) !important;
        border-color: rgba(0, 201, 255, 0.9) !important;
        box-shadow: 0 0 15px rgba(0, 201, 255, 0.6) !important;
    }
    
    /* LOADING SPINNER */
    .stSpinner > div {
        border-color: #667eea !important;
        border-right-color: transparent !important;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    /* SUCCESS/INFO/WARNING */
    .stSuccess {
        background: linear-gradient(135deg, #00c9ff15 0%, #92fe9d15 100%);
        border-left: 4px solid #00c9ff;
        border-radius: 12px;
        animation: slideIn 0.5s ease-out;
        padding: 1rem 1.5rem;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-left: 4px solid #667eea;
        border-radius: 12px;
        padding: 1rem 1.5rem;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #f093fb15 0%, #f5576c15 100%);
        border-left: 4px solid #f093fb;
        border-radius: 12px;
        padding: 1rem 1.5rem;
    }
    
    /* CHECKBOX TOGGLE MODERNE */
    .stCheckbox {
        padding: 1.2rem 1.5rem !important;
        background: linear-gradient(135deg, 
            rgba(102, 126, 234, 0.1) 0%, 
            rgba(118, 75, 162, 0.08) 100%
        ) !important;
        border-radius: 16px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 2px solid rgba(102, 126, 234, 0.25) !important;
        backdrop-filter: blur(10px) saturate(150%) !important;
        box-shadow: 
            0 4px 15px rgba(102, 126, 234, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
    }
    
    .stCheckbox:hover {
        background: linear-gradient(135deg, 
            rgba(102, 126, 234, 0.2) 0%, 
            rgba(0, 201, 255, 0.15) 100%
        ) !important;
        border-color: rgba(102, 126, 234, 0.5) !important;
        box-shadow: 
            0 0 25px rgba(102, 126, 234, 0.4),
            0 6px 20px rgba(0, 201, 255, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
        transform: translateY(-2px) !important;
    }
    
    .stCheckbox label {
        color: #e0e7ff !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stCheckbox:hover label {
        color: #ffffff !important;
        text-shadow: 0 0 10px rgba(102, 126, 234, 0.6) !important;
    }
    
    /* Style de la checkbox elle-même */
    .stCheckbox input[type="checkbox"] {
        width: 22px !important;
        height: 22px !important;
        border-radius: 6px !important;
        border: 2px solid rgba(102, 126, 234, 0.6) !important;
        transition: all 0.3s ease !important;
    }
    
    .stCheckbox input[type="checkbox"]:checked {
        background: linear-gradient(135deg, #667eea 0%, #00c9ff 100%) !important;
        border-color: rgba(0, 201, 255, 0.9) !important;
        box-shadow: 0 0 15px rgba(0, 201, 255, 0.6) !important;
    }
    
    /* DIVIDER */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, 
            transparent 0%, 
            rgba(102,126,234,0.5) 25%, 
            rgba(118,75,162,0.5) 50%, 
            rgba(102,126,234,0.5) 75%, 
            transparent 100%
        );
    }
    
    /* METRIC CARDS */
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.05);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* EXPANDER */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        transition: all 0.3s ease;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(102, 126, 234, 0.1);
        border-color: #667eea;
    }
    
    /* INPUT FIELDS */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1);
        color: white;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
    }
    
    /* LOADING SKELETON */
    .loading-skeleton {
        background: linear-gradient(90deg, 
            rgba(255,255,255,0.05) 0%, 
            rgba(255,255,255,0.1) 50%, 
            rgba(255,255,255,0.05) 100%
        );
        background-size: 1000px 100%;
        animation: shimmer 2s infinite;
        border-radius: 12px;
        height: 60px;
        margin: 0.5rem 0;
    }
</style>
"""

# ==================== CONFIGURATION ====================
st.set_page_config(
    page_title="🎓 EMSI-Bot PRO",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(MODERN_CSS, unsafe_allow_html=True)

# ✨ Modèle Fine-Tuné EMSI (créé avec run_finetuning.py)
MODEL_NAME = "emsi-bot"  # Fine-tuned sur données EMSI (ancien: "llama3.2:1b")
EMSI_PERSONAS = {
    "academic_advisor": "👨‍🎓 Conseiller Académique",
    "recruiter": "🎯 Responsable Admissions",
    "technical_expert": "⚙️ Expert Technique",
    "general_expert": "🤖 Expert Général EMSI"
}

# ==================== UTILITY FUNCTIONS ====================
import base64

def get_base64_image(image_path):
    """Encode image to base64 for inline display"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        logger.error(f"Error encoding image: {e}")
        return ""

# ==================== SESSION STATE ====================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "rag_loaded" not in st.session_state:
    st.session_state.rag_loaded = False
if "rag_instance" not in st.session_state:
    st.session_state.rag_instance = None
if "mcp_initialized" not in st.session_state:
    st.session_state.mcp_initialized = False
if "mcp_tools" not in st.session_state:
    st.session_state.mcp_tools = []

# ==================== MCP INITIALIZATION ====================
async def initialize_mcp_async():
    """Initialise MCP de manière asynchrone"""
    if MCP_AVAILABLE and not st.session_state.mcp_initialized:
        try:
            await mcp_client.initialize()
            st.session_state.mcp_tools = mcp_client.available_tools
            st.session_state.mcp_initialized = True
            logger.info(f"✅ MCP initialisé avec {len(st.session_state.mcp_tools)} outils")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur initialisation MCP: {e}")
            return False
    return st.session_state.mcp_initialized

def initialize_mcp():
    """Wrapper synchrone pour Streamlit"""
    return asyncio.run(initialize_mcp_async())

# ==================== LAZY RAG LOADING ====================
def initialize_rag_system_lazy():
    """Charge le RAG uniquement quand nécessaire (LAZY)"""
    if st.session_state.rag_loaded:
        return st.session_state.rag_instance
    
    with st.spinner("🔄 Chargement RAG (~30s)..."):
        try:
            from rag_core.rag_orchestrator import RAGOrchestrator
            from rag_core.pdf_ingestion import PDFIngestionManager
            
            # ✅ FIX: Initialiser l'orchestrateur ET ses composants
            rag = RAGOrchestrator()
            rag.initialize_components()
            
            # ✅ FIX: Extraire les PDFs PUIS ingérer
            pdf_dir = os.path.join(os.path.dirname(__file__), "entrainement_chatbot_emsi")
            if os.path.exists(pdf_dir):
                ingestion = PDFIngestionManager()
                documents = ingestion.extract_from_multiple_pdfs(pdf_dir)
                if documents:
                    rag.ingest_documents(documents)
                    logger.info(f"✅ {len(documents)} documents ingérés")
            
            st.session_state.rag_instance = rag
            st.session_state.rag_loaded = True
            st.success("✅ RAG prêt!")
            return rag
        except Exception as e:
            logger.error(f"❌ Erreur RAG: {e}", exc_info=True)
            st.error(f"❌ Erreur RAG: {e}")
            return None

# ==================== OLLAMA CALLS ====================
async def call_mcp_tool_async(tool_name: str, **kwargs) -> Dict[str, Any]:
    """Appel asynchrone d'un outil MCP"""
    if MCP_AVAILABLE and st.session_state.mcp_initialized:
        try:
            result = await mcp_client.call_tool(tool_name, **kwargs)
            return result
        except Exception as e:
            logger.error(f"❌ Erreur outil MCP {tool_name}: {e}")
            return {"error": str(e)}
    return {"error": "MCP non disponible"}

def call_mcp_tool(tool_name: str, **kwargs) -> Dict[str, Any]:
    """Wrapper synchrone pour appel outil MCP"""
    return asyncio.run(call_mcp_tool_async(tool_name, **kwargs))

def call_ollama_with_rag(
    user_message: str,
    persona: str,
    temperature: float,
    max_tokens: int,
    top_p: float,
    top_k: int,
    use_rag: bool,
    use_mcp: bool = False
) -> str:
    """Appel Ollama avec RAG optionnel et outils MCP"""
    
    context = ""
    mcp_context = ""
    
    # RAG Context
    if use_rag:
        rag = initialize_rag_system_lazy()
        if rag:
            try:
                # ✅ FIX: Utiliser build_augmented_prompt() au lieu de query()
                augmented = rag.build_augmented_prompt(
                    user_message, 
                    persona=persona, 
                    include_context=True
                )
                context = augmented.get("system", "")
            except Exception as e:
                logger.warning(f"⚠️ RAG skip: {e}")
                st.warning(f"⚠️ RAG skip: {e}")
    
    # MCP Tools Context
    if use_mcp and st.session_state.mcp_initialized:
        mcp_context = f"\n\n🤖 **Outils Disponibles:**\n{mcp_client.get_tools_description()}"
    
    # Construction prompt
    system_prompt = f"""Tu es {EMSI_PERSONAS[persona]} de l'EMSI.
Rôle: Réponds avec expertise et précision.
Ton: Professionnel et bienveillant.

{f'Contexte RAG:{context}' if context else ''}
{mcp_context if mcp_context else ''}
"""
    
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend([
        {"role": msg["role"], "content": msg["content"]}
        for msg in st.session_state.messages
    ])
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=messages,
            options={"temperature": temperature, "num_predict": max_tokens, "top_p": top_p, "top_k": top_k}
        )
        return response['message']['content']
    except Exception as e:
        return f"❌ Erreur Ollama: {e}"

# ==================== SIDEBAR ====================
with st.sidebar:
    # Logo EMSI - Design Expert Moderne Centré
    logo_path = os.path.join(os.path.dirname(__file__), "logo_emsi", "logo_emsi.jpg")
    if os.path.exists(logo_path):
        st.markdown("""
        <style>
        .logo-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 1.5rem 0;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, 
                rgba(102, 126, 234, 0.1) 0%, 
                rgba(118, 75, 162, 0.08) 50%,
                rgba(0, 201, 255, 0.1) 100%);
            border-radius: 20px;
            backdrop-filter: blur(20px) saturate(180%);
            border: 2px solid rgba(102, 126, 234, 0.2);
            box-shadow: 
                0 8px 32px rgba(102, 126, 234, 0.2),
                0 0 60px rgba(0, 201, 255, 0.1),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .logo-container:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 
                0 15px 50px rgba(102, 126, 234, 0.35),
                0 0 80px rgba(0, 201, 255, 0.2),
                inset 0 1px 0 rgba(255, 255, 255, 0.2);
            border-color: rgba(0, 201, 255, 0.5);
        }
        .logo-wrapper {
            width: 100%;
            max-width: 280px;
            border-radius: 20px;
            overflow: hidden;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(0, 201, 255, 0.15));
            padding: 8px;
            box-shadow: 
                0 10px 40px rgba(102, 126, 234, 0.3),
                0 0 60px rgba(0, 201, 255, 0.2),
                0 0 0 3px rgba(255, 255, 255, 0.1);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            animation: float3D 6s ease-in-out infinite;
        }
        .logo-wrapper:hover {
            transform: scale(1.05) translateY(-5px);
            box-shadow: 
                0 15px 60px rgba(102, 126, 234, 0.5),
                0 0 80px rgba(0, 201, 255, 0.4),
                0 0 0 4px rgba(0, 201, 255, 0.4);
        }
        .logo-inner {
            width: 100%;
            border-radius: 16px;
            overflow: hidden;
            background: #ffffff;
        }
        .logo-wrapper img {
            width: 100%;
            height: auto;
            display: block;
            filter: drop-shadow(0 5px 15px rgba(0, 0, 0, 0.3));
            transition: filter 0.3s ease;
        }
        .logo-wrapper:hover img {
            filter: drop-shadow(0 8px 25px rgba(102, 126, 234, 0.5));
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="logo-container">
            <div class="logo-wrapper">
                <div class="logo-inner">
                    <img src="data:image/jpeg;base64,{get_base64_image(logo_path)}" alt="EMSI Logo"/>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin: 1.5rem 0 1rem 0;">
        <h1 style="
            font-size: 2rem; 
            background: linear-gradient(135deg, #667eea 0%, #00c9ff 100%); 
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent; 
            font-weight: 800; 
            letter-spacing: 0.5px;
            text-shadow: 0 0 30px rgba(102, 126, 234, 0.3);
            margin-bottom: 0.3rem;
        ">
            🎓 EMSI-Bot PRO
        </h1>
        <p style="
            color: rgba(224, 231, 255, 0.85); 
            font-size: 0.9rem; 
            font-weight: 500;
            letter-spacing: 0.3px;
        ">
            ✨ Votre assistant intelligent
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ⚙️ Configuration")
    st.markdown("---")
    
    # Persona - RADIO BUTTONS MODERNE
    st.markdown("**🎭 Choisissez votre Persona**")
    persona_display = st.radio(
        "Persona",
        options=list(EMSI_PERSONAS.values()),
        index=3,  # Par défaut: "🤖 Expert Général EMSI"
        label_visibility="collapsed"
    )
    
    # Récupérer la clé correspondante pour l'API
    persona_key = [k for k, v in EMSI_PERSONAS.items() if v == persona_display][0]
    
    st.markdown("---")
    
    # RAG Toggle avec animation
    use_rag = st.checkbox(
        "✨ Activer Augmentation RAG",
        value=False,
        help="Charge le système RAG (~30s au 1er usage)"
    )
    
    if use_rag and st.session_state.rag_loaded:
        st.success("🟢 RAG Actif")
    
    st.markdown("---")
    
    # LLM Parameters
    st.markdown("### 🎚️ Paramètres LLM")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**🌡️ Température**")
    with col2:
        st.markdown(f"<span style='color: #00c9ff; font-weight: 600;'>{st.session_state.get('temp_val', 0.7):.2f}</span>", unsafe_allow_html=True)
    
    temperature = st.slider(
        "temp_slider",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.01,
        help="Créativité du modèle (0=déterministe, 1=créatif)",
        label_visibility="collapsed",
        key="temperature_slider"
    )
    st.session_state.temp_val = temperature
    
    st.markdown("")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**📏 Max Tokens**")
    with col2:
        st.markdown(f"<span style='color: #00c9ff; font-weight: 600;'>{st.session_state.get('tokens_val', 512)}</span>", unsafe_allow_html=True)
    
    max_tokens = st.slider(
        "tokens_slider",
        min_value=256,
        max_value=2048,
        value=512,
        step=64,
        help="Longueur maximale de la réponse",
        label_visibility="collapsed",
        key="max_tokens_slider"
    )
    st.session_state.tokens_val = max_tokens
    
    st.markdown("")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**🎲 Top P (Nucleus)**")
    with col2:
        st.markdown(f"<span style='color: #00c9ff; font-weight: 600;'>{st.session_state.get('topp_val', 0.9):.2f}</span>", unsafe_allow_html=True)
    
    top_p = st.slider(
        "topp_slider",
        min_value=0.1,
        max_value=1.0,
        value=0.9,
        step=0.01,
        help="Probabilité cumulée pour échantillonnage nucleus",
        label_visibility="collapsed",
        key="top_p_slider"
    )
    st.session_state.topp_val = top_p
    
    st.markdown("")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**🔢 Top K**")
    with col2:
        st.markdown(f"<span style='color: #00c9ff; font-weight: 600;'>{st.session_state.get('topk_val', 40)}</span>", unsafe_allow_html=True)
    
    top_k = st.slider(
        "topk_slider",
        min_value=1,
        max_value=100,
        value=40,
        step=1,
        help="Nombre de tokens considérés à chaque étape",
        label_visibility="collapsed",
        key="top_k_slider"
    )
    st.session_state.topk_val = top_k
    
    st.markdown("---")
    
    # ==================== MCP TOOLS SECTION ====================
    if MCP_AVAILABLE:
        st.markdown("### 🤖 Outils Agentiques MCP")
        
        # Initialisation MCP
        if not st.session_state.mcp_initialized:
            if st.button("🔄 Activer MCP", use_container_width=True):
                with st.spinner("Initialisation MCP..."):
                    if initialize_mcp():
                        st.success(f"✅ {len(st.session_state.mcp_tools)} outils activés")
                        st.rerun()
                    else:
                        st.error("❌ Erreur initialisation MCP")
        else:
            st.success(f"✅ MCP Actif ({len(st.session_state.mcp_tools)} outils)")
            
            # Affichage des outils disponibles
            with st.expander("📦 Outils Disponibles", expanded=False):
                for tool in st.session_state.mcp_tools:
                    st.markdown(f"""
                    **{tool.name}** ({tool.server})  
                    {tool.description}
                    """)
            
            # Désactiver MCP
            if st.button("⏸️ Désactiver MCP", use_container_width=True):
                st.session_state.mcp_initialized = False
                st.session_state.mcp_tools = []
                st.rerun()
    
    st.markdown("---")
    
    # Actions
    if st.button("🗑️ Réinitialiser Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 Stats")
    st.metric("💬 Messages", len(st.session_state.messages))
    if st.session_state.mcp_initialized:
        st.metric("🤖 Outils MCP", len(st.session_state.mcp_tools))
    st.metric("🎭 Persona", persona_display)

# ==================== MAIN ====================
# Logo centré en haut de la page principale
logo_path_main = os.path.join(os.path.dirname(__file__), "logo_emsi", "logo_emsi.jpg")
if os.path.exists(logo_path_main):
    st.markdown("""
    <style>
    .main-logo-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem 0 1rem 0;
        margin-bottom: 1.5rem;
    }
    .main-logo-wrapper {
        width: 100%;
        max-width: 400px;
        border-radius: 24px;
        overflow: hidden;
        background: linear-gradient(135deg, 
            rgba(102, 126, 234, 0.2) 0%, 
            rgba(0, 201, 255, 0.2) 100%);
        padding: 12px;
        box-shadow: 
            0 15px 60px rgba(102, 126, 234, 0.4),
            0 0 80px rgba(0, 201, 255, 0.3),
            inset 0 2px 0 rgba(255, 255, 255, 0.2);
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        animation: float3D 6s ease-in-out infinite;
    }
    .main-logo-wrapper:hover {
        transform: scale(1.08) translateY(-8px);
        box-shadow: 
            0 20px 80px rgba(102, 126, 234, 0.6),
            0 0 120px rgba(0, 201, 255, 0.5),
            inset 0 3px 0 rgba(255, 255, 255, 0.3);
    }
    .main-logo-inner {
        width: 100%;
        border-radius: 20px;
        overflow: hidden;
        background: #ffffff;
    }
    .main-logo-inner img {
        width: 100%;
        height: auto;
        display: block;
        filter: drop-shadow(0 5px 20px rgba(0, 0, 0, 0.5));
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="main-logo-container">
        <div class="main-logo-wrapper">
            <div class="main-logo-inner">
                <img src="data:image/jpeg;base64,{get_base64_image(logo_path_main)}" alt="EMSI Logo"/>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center; padding: 0.5rem 0 2rem 0;'>
    <h1 style='
        font-size: 3.5rem; 
        font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #00c9ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.8rem;
        letter-spacing: -0.02em;
        text-shadow: 0 0 40px rgba(102, 126, 234, 0.4);
        animation: pulse3D 3s ease-in-out infinite;
    '>
        🎓 EMSI-Bot PRO
    </h1>
    <p style='
        color: rgba(255,255,255,0.8); 
        font-size: 1.3rem;
        font-weight: 500;
        letter-spacing: 0.5px;
    '>
        ✨ Votre assistant intelligent avec IA avancée
    </p>
</div>
""", unsafe_allow_html=True)

# Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input
if prompt := st.chat_input("💭 Posez votre question..."):
    # 🔔 NOTIFICATION DISCORD (Gratuit et illimité!)
    try:
        import asyncio
        from mcp_tools_advanced import DiscordTool
        
        notification_message = f"**Question reçue:**\n\n{prompt[:300]}"
        
        # Envoi asynchrone Discord
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        discord_result = loop.run_until_complete(
            DiscordTool.send_notification(notification_message, "🤖 Nouvelle Question EMSI-Bot")
        )
        loop.close()
        
        if discord_result.get('success'):
            logger.info(f"✅ Notification Discord envoyée")
        else:
            logger.debug(f"ℹ️ Discord non configuré: {discord_result.get('note', '')}")
            
    except Exception as e:
        logger.debug(f"Discord notification skipped: {e}")
    
    # Ajout message user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Réponse assistant avec loading animation
    with st.chat_message("assistant"):
        with st.spinner("✨ Génération de la réponse..."):
            response = call_ollama_with_rag(
                prompt, persona_key, temperature, max_tokens, top_p, top_k, use_rag,
                use_mcp=st.session_state.mcp_initialized
            )
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
