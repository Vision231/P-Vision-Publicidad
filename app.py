import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import base64
from datetime import datetime
from PIL import Image, ImageOps, ImageFilter
from reportlab.lib.pagesizes import letter, A4, legal
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import streamlit.components.v1 as components


# ==============================================================================
# 1. CONFIGURACIÓN DE PÁGINA STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="VISIÓN Y PUBLICIDAD | Sistema de Gestión & Diseño",
    page_icon="logo.png" if os.path.exists("logo.png") else "🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. INICIALIZACIÓN DE VARIABLES DE SESIÓN (SESSION STATE)
# ==============================================================================
def init_session_state():
    if 'theme_mode' not in st.session_state:
        st.session_state.theme_mode = 'light'
    

    # Catálogo de servicios por medida (Gran Formato) con ortografía corregida (ojales)
    if 'services_by_measure' not in st.session_state:
        st.session_state.services_by_measure = pd.DataFrame([
            {'servicio': 'Pendón con tubo / ojales', 'tarifa_minima': 20000, 'factor': 55.0, 'stock': 1000},
            {'servicio': 'Aviso con estructura sencilla', 'tarifa_minima': 100000, 'factor': 28.0, 'stock': 500},
            {'servicio': 'Aviso Luminoso Panaflex', 'tarifa_minima': 350000, 'factor': 38.0, 'stock': 200},
            {'servicio': 'Adhesivo laminado', 'tarifa_minima': 25000, 'factor': 8.0, 'stock': 800},
            {'servicio': 'Adhesivo troquelado', 'tarifa_minima': 35000, 'factor': 6.0, 'stock': 600}
        ])
    
    # Catálogo de productos fijos según la hoja de precios oficial
    if 'fixed_products' not in st.session_state:
        st.session_state.fixed_products = pd.DataFrame([
            {'producto': 'Tarjetas Mate UV (1.000 un.)', 'precio': 150000, 'stock': 500},
            {'producto': 'Tarjetas Brillantes Full Color (1.000 un.)', 'precio': 100000, 'stock': 500},
            {'producto': 'Factureros Original y 1 Copia (10 talonarios / 50 folios c/u)', 'precio': 150000, 'stock': 200},
            {'producto': 'Volantes 1/2 Carta (1.000 un.)', 'precio': 150000, 'stock': 1000},
            {'producto': 'Volantes 1/4 Carta (2.000 un.)', 'precio': 150000, 'stock': 1000},
            {'producto': 'Letrero Luminoso Redondo en Panaflex (80x80 cm)', 'precio': 500000, 'stock': 50},
            {'producto': 'Rompetráfico 100x70 cm', 'precio': 150000, 'stock': 300},
            {'producto': 'Rompetráfico 80x120 cm', 'precio': 200000, 'stock': 300},
            {'producto': 'Stickers Redondos Adhesivos 5x5 cm (400 un.)', 'precio': 60000, 'stock': 400},
            {'producto': 'Mug Fondo Color', 'precio': 25000, 'stock': 200},
            {'producto': 'Mug Blanco', 'precio': 20000, 'stock': 200},
            {'producto': 'Botilito', 'precio': 25000, 'stock': 150},
            {'producto': 'Cervecero', 'precio': 35000, 'stock': 150},
            {'producto': 'Termo', 'precio': 55000, 'stock': 100},
            {'producto': 'Carnet', 'precio': 25000, 'stock': 500},
            {'producto': 'Botones', 'precio': 5000, 'stock': 1000},
            {'producto': 'Sello 842', 'precio': 45000, 'stock': 100},
            {'producto': 'Sello 843', 'precio': 50000, 'stock': 100},
            {'producto': 'Sello 844', 'precio': 60000, 'stock': 100}
        ])
    
    if 'sales_history' not in st.session_state:
        st.session_state.sales_history = pd.DataFrame(columns=[
            'fecha', 'cliente', 'tipo', 'producto', 'cantidad', 'subtotal', 'iva', 'total'
        ])
    
    if 'receipt_counter' not in st.session_state:
        st.session_state.receipt_counter = 1001

    if 'prefill_converter' not in st.session_state:
        st.session_state.prefill_converter = {'width': 100.0, 'height': 150.0, 'service': ''}

    # Memoria persistente para imágenes subidas
    if 'prepress_img_bytes' not in st.session_state:
        st.session_state.prepress_img_bytes = None
    if 'prepress_img_name' not in st.session_state:
        st.session_state.prepress_img_name = None

    if 'png_editor_bytes' not in st.session_state:
        st.session_state.png_editor_bytes = None
    if 'png_editor_name' not in st.session_state:
        st.session_state.png_editor_name = None

    if 'working_png_img' not in st.session_state:
        st.session_state.working_png_img = None

init_session_state()

# ==============================================================================
# 3. BASE64 DEL LOGO OFICIAL
# ==============================================================================
def get_logo_base64():
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        try:
            with open(logo_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            return ""
    return ""

LOGO_B64 = get_logo_base64()

def pil_to_base64_data_uri(img_pil):
    """Convierte una imagen PIL a Data URI Base64 PNG"""
    buf = io.BytesIO()
    img_pil.save(buf, format="PNG")
    b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64_str}"

# ==============================================================================
# 4. MOTOR DE ESTILOS CSS: MODO PASTEL Y MODO OSCURO CON LETRA NEGRA EN CASILLAS
# ==============================================================================
def apply_theme():
    is_light = st.session_state.theme_mode == 'light'
    
    common_css = """
    <meta name="google" content="notranslate">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
        
        /* Zoom estándar al 100% */
        html, body, .stApp {
            zoom: 1 !important;
            -moz-transform: none !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }
        
        /* Proteger DOM de traducción automática que rompe React */
        .notranslate, [data-testid="stWidgetLabel"] {
            translate: no !important;
        }
    </style>
    """
    st.markdown(common_css, unsafe_allow_html=True)
    
    if is_light:
        theme_css = """
        <style>
            :root {
                --font-heading: 'Outfit', sans-serif;
                --font-body: 'Plus Jakarta Sans', sans-serif;
                --bg-canvas: #f3f4f8;
                --card-bg: #ffffff;
                --card-border: rgba(226, 232, 240, 0.95);
                --text-main: #0f172a;
                --text-secondary: #475569;
                --text-muted: #64748b;
                --brand-blue: #2563eb;
                --brand-blue-hover: #1d4ed8;
            }
            
            .stApp {
                background-color: var(--bg-canvas);
                background-image: 
                    radial-gradient(1200px 600px at 0% -5%, rgba(37, 99, 235, 0.08) 0%, transparent 60%),
                    radial-gradient(900px 500px at 100% 0%, rgba(124, 58, 237, 0.06) 0%, transparent 50%),
                    radial-gradient(1000px 700px at 50% 100%, rgba(16, 185, 129, 0.05) 0%, transparent 55%);
                background-attachment: fixed;
                color: var(--text-main);
            }
            
            [data-testid="stHeader"] {
                background: transparent !important;
            }
            
            [data-testid="stSidebar"] {
                background: #ffffff !important;
                border-right: 1px solid #e2e8f0 !important;
                box-shadow: 4px 0 24px rgba(0, 0, 0, 0.02) !important;
            }
            
            .vp-hero {
                position: relative;
                background: #ffffff;
                border: 1px solid rgba(226, 232, 240, 0.95);
                border-radius: 20px;
                padding: 1.6rem 2.2rem;
                margin-bottom: 1.5rem;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 12px 28px -4px rgba(15, 23, 42, 0.05);
                overflow: hidden;
            }
            
            .vp-hero::before {
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0;
                height: 4px;
                background: linear-gradient(90deg, #2563eb, #7c3aed, #06b6d4, #10b981);
            }
            
            .vp-card {
                background: #ffffff;
                border: 1px solid rgba(226, 232, 240, 0.95);
                border-radius: 18px;
                padding: 1.5rem;
                margin-bottom: 1.3rem;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02), 0 10px 24px -4px rgba(15, 23, 42, 0.04);
            }
            
            .vp-title {
                font-family: var(--font-heading);
                color: #0f172a;
                font-size: 1.65rem;
                font-weight: 800;
                letter-spacing: -0.02em;
                margin: 0;
            }
            
            .vp-subtitle {
                color: #64748b;
                font-size: 0.92rem;
                margin-top: 0.35rem;
                font-weight: 500;
            }
            
            .vp-badge {
                display: inline-flex;
                align-items: center;
                gap: 0.45rem;
                background: #f1f5f9;
                color: #334155;
                padding: 0.4rem 0.95rem;
                border-radius: 9999px;
                font-size: 0.82rem;
                font-weight: 700;
                border: 1px solid #cbd5e1;
            }
            
            .vp-badge-active {
                background: #ecfdf5;
                color: #059669;
                border: 1px solid #a7f3d0;
            }
            
            .vp-stat-box {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
                padding: 1.1rem 1.2rem;
                text-align: center;
            }
            
            .vp-stat-label {
                color: #64748b;
                font-size: 0.78rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.6px;
            }
            
            .vp-stat-val {
                font-family: var(--font-heading);
                color: #0f172a;
                font-size: 1.55rem;
                font-weight: 800;
                margin-top: 0.35rem;
            }
            
            .vp-stat-highlight {
                background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #4338ca 100%);
                color: #ffffff;
                border-radius: 16px;
                padding: 1.4rem;
                text-align: center;
                box-shadow: 0 10px 25px -4px rgba(37, 99, 235, 0.35);
            }
            
            .vp-stat-highlight .vp-stat-label {
                color: rgba(255, 255, 255, 0.85);
                font-size: 0.85rem;
                font-weight: 700;
            }
            
            .vp-stat-highlight .vp-stat-val {
                font-family: var(--font-heading);
                color: #ffffff;
                font-size: 2.1rem;
                font-weight: 900;
                margin-top: 0.25rem;
            }
            
            .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
                background-color: #ffffff !important;
                border: 1px solid #cbd5e1 !important;
                border-radius: 12px !important;
                color: #0f172a !important;
                font-weight: 600 !important;
            }
            
            .stButton > button {
                background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
                color: #ffffff !important;
                border-radius: 12px !important;
                border: none !important;
                font-family: var(--font-heading) !important;
                font-weight: 700 !important;
                padding: 0.75rem 1.6rem !important;
                box-shadow: 0 6px 16px -2px rgba(37, 99, 235, 0.3) !important;
            }
            
            .stDownloadButton > button {
                background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
                color: #ffffff !important;
                border-radius: 12px !important;
                border: none !important;
                font-family: var(--font-heading) !important;
                font-weight: 700 !important;
                box-shadow: 0 6px 16px -2px rgba(16, 185, 129, 0.3) !important;
            }
            
            [data-testid="stTabs"] [role="tablist"] {
                background: #e2e8f0 !important;
                border-radius: 14px !important;
                padding: 0.4rem !important;
                border: 1px solid #cbd5e1 !important;
            }
            
            [data-testid="stTabs"] [role="tab"] {
                font-family: var(--font-heading) !important;
                color: #475569 !important;
                font-weight: 600 !important;
                border-radius: 10px !important;
            }
            
            [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
                background: #ffffff !important;
                color: #0f172a !important;
                font-weight: 800 !important;
                box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08) !important;
            }
            
            [data-testid="stFileUploader"] {
                background: #ffffff !important;
                border: 2px dashed #94a3b8 !important;
                border-radius: 16px !important;
                padding: 1.5rem !important;
            }
            
            .vp-footer {
                margin-top: 3.5rem;
                padding: 1.75rem;
                text-align: center;
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                color: #64748b;
                font-size: 0.88rem;
            }
        </style>
        """
    else:
        # TEMA OSCURO (CYBER NEON) CON CASILLAS DE TEXTO Y SELECCIÓN EN LETRA Y NÚMEROS NEGROS
        theme_css = """
        <style>
            :root {
                --font-heading: 'Outfit', sans-serif;
                --font-body: 'Plus Jakarta Sans', sans-serif;
            }
            
            .stApp {
                background-color: #090a12;
                background-image: 
                    radial-gradient(1000px 500px at 5% 0%, rgba(0, 212, 255, 0.16) 0%, transparent 55%),
                    radial-gradient(900px 600px at 95% 10%, rgba(157, 78, 221, 0.16) 0%, transparent 50%),
                    radial-gradient(1100px 700px at 50% 100%, rgba(0, 255, 136, 0.08) 0%, transparent 60%);
                background-attachment: fixed;
                color: #ffffff !important;
            }
            
            [data-testid="stHeader"] {
                background: transparent !important;
            }
            
            /* TÍTULOS Y TEXTOS GENERALES EN MODO OSCURO */
            h1, h2, h3, h4, h5, h6, p, .stCaption {
                color: #ffffff !important;
            }
            
            /* BARRA LATERAL EN MODO OSCURO */
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0d111e 0%, #070913 100%) !important;
                border-right: 1px solid rgba(0, 212, 255, 0.25) !important;
                color: #ffffff !important;
            }
            
            [data-testid="stSidebar"] [data-testid="stMetric"] {
                background: rgba(255, 255, 255, 0.06) !important;
                border: 1px solid rgba(0, 212, 255, 0.3) !important;
                border-radius: 14px !important;
                padding: 1rem !important;
            }
            
            [data-testid="stSidebar"] [data-testid="stMetric"] label {
                color: #ffffff !important;
                font-weight: 700 !important;
            }
            
            [data-testid="stSidebar"] [data-testid="stMetric"] [data-testid="stMetricValue"] {
                color: #00d4ff !important;
                font-weight: 800 !important;
            }
            
            .vp-hero {
                position: relative;
                background: rgba(18, 22, 38, 0.88);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(0, 212, 255, 0.35);
                border-radius: 20px;
                padding: 1.6rem 2.2rem;
                margin-bottom: 1.5rem;
                box-shadow: 0 10px 32px rgba(0, 0, 0, 0.45);
                overflow: hidden;
            }
            
            .vp-hero::before {
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0;
                height: 4px;
                background: linear-gradient(90deg, #00d4ff, #9d4edd, #00ff88);
            }
            
            .vp-card {
                background: rgba(18, 22, 36, 0.82);
                backdrop-filter: blur(16px);
                border: 1px solid rgba(0, 212, 255, 0.2);
                border-radius: 18px;
                padding: 1.5rem;
                margin-bottom: 1.3rem;
                box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35);
            }
            
            .vp-title {
                font-family: var(--font-heading);
                color: #ffffff !important;
                font-size: 1.65rem;
                font-weight: 800;
                margin: 0;
            }
            
            .vp-subtitle {
                color: #e2e8f0 !important;
                font-size: 0.92rem;
                margin-top: 0.35rem;
            }
            
            .vp-badge {
                display: inline-flex;
                align-items: center;
                gap: 0.45rem;
                background: rgba(0, 212, 255, 0.15);
                color: #00d4ff !important;
                padding: 0.4rem 0.95rem;
                border-radius: 9999px;
                font-size: 0.82rem;
                font-weight: 700;
                border: 1px solid rgba(0, 212, 255, 0.35);
            }
            
            .vp-badge-active {
                background: rgba(0, 255, 136, 0.15);
                color: #00ff88 !important;
                border: 1px solid rgba(0, 255, 136, 0.35);
            }
            
            .vp-stat-box {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(0, 212, 255, 0.25);
                border-radius: 14px;
                padding: 1.1rem 1.2rem;
                text-align: center;
            }
            
            .vp-stat-label {
                color: #e2e8f0 !important;
                font-size: 0.78rem;
                font-weight: 700;
                text-transform: uppercase;
            }
            
            .vp-stat-val {
                font-family: var(--font-heading);
                color: #00d4ff !important;
                font-size: 1.55rem;
                font-weight: 800;
                margin-top: 0.35rem;
            }
            
            .vp-stat-highlight {
                background: linear-gradient(135deg, #00d4ff 0%, #9d4edd 100%);
                color: #ffffff !important;
                border-radius: 16px;
                padding: 1.4rem;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0, 212, 255, 0.35);
            }
            
            .vp-stat-highlight * {
                color: #ffffff !important;
            }

            /* =================================================================
               CORRECCIÓN MODO OSCURO: LETRAS Y NÚMEROS EN COLOR NEGRO PURO
               EN TODAS LAS CASILLAS DE TEXTO, NÚMEROS Y SELECCIÓN
               ================================================================= */
            .stTextInput input, 
            .stNumberInput input, 
            .stTextArea textarea {
                background-color: #ffffff !important;
                color: #000000 !important;
                -webkit-text-fill-color: #000000 !important;
                font-weight: 700 !important;
                font-size: 0.95rem !important;
                border: 2px solid #00d4ff !important;
                border-radius: 12px !important;
                box-shadow: 0 2px 10px rgba(0, 212, 255, 0.2) !important;
            }
            
            .stTextInput input::placeholder, 
            .stNumberInput input::placeholder,
            .stTextArea textarea::placeholder {
                color: #64748b !important;
                -webkit-text-fill-color: #64748b !important;
                font-weight: 500 !important;
            }

            /* Cajas de selección (Selectbox) */
            .stSelectbox [data-baseweb="select"],
            .stSelectbox [data-baseweb="select"] > div {
                background-color: #ffffff !important;
                border: 2px solid #00d4ff !important;
                border-radius: 12px !important;
            }
            
            .stSelectbox [data-baseweb="select"] span,
            .stSelectbox [data-baseweb="select"] div,
            .stSelectbox [data-baseweb="select"] input {
                color: #000000 !important;
                -webkit-text-fill-color: #000000 !important;
                font-weight: 700 !important;
            }

            /* Desplegables de opciones (popover / listbox) */
            [data-baseweb="popover"],
            [data-baseweb="popover"] *,
            [data-baseweb="menu"],
            [data-baseweb="menu"] *,
            div[role="listbox"],
            div[role="listbox"] *,
            ul[role="listbox"],
            ul[role="listbox"] *,
            li[role="option"],
            li[role="option"] * {
                background-color: #ffffff !important;
                color: #000000 !important;
                -webkit-text-fill-color: #000000 !important;
                font-weight: 600 !important;
            }

            li[role="option"]:hover,
            li[role="option"]:hover *,
            li[role="option"][aria-selected="true"],
            li[role="option"][aria-selected="true"] * {
                background-color: #e2e8f0 !important;
                color: #000000 !important;
                -webkit-text-fill-color: #000000 !important;
            }

            /* Botones de incremento y decremento de NumberInput */
            .stNumberInput button {
                background-color: #f1f5f9 !important;
                color: #000000 !important;
                border-radius: 8px !important;
            }

            .stNumberInput button svg {
                fill: #000000 !important;
            }

            /* Celdas del editor de tablas (stDataEditor) */
            [data-testid="stDataEditor"] input,
            [data-testid="stDataEditor"] textarea {
                background-color: #ffffff !important;
                color: #000000 !important;
                -webkit-text-fill-color: #000000 !important;
            }

            /* Etiquetas superiores visibles en blanco nítido */
            .stTextInput label,
            .stNumberInput label,
            .stSelectbox label,
            .stTextArea label,
            .stSlider label,
            .stRadio label,
            [data-testid="stWidgetLabel"] label,
            [data-testid="stWidgetLabel"] p {
                color: #ffffff !important;
                font-weight: 700 !important;
                font-size: 0.92rem !important;
            }
            
            .stButton > button {
                background: linear-gradient(135deg, #00d4ff 0%, #9d4edd 100%) !important;
                color: #ffffff !important;
                border-radius: 12px !important;
                border: none !important;
                font-family: var(--font-heading) !important;
                font-weight: 700 !important;
                padding: 0.75rem 1.6rem !important;
                box-shadow: 0 6px 20px rgba(0, 212, 255, 0.35) !important;
            }
            
            .stDownloadButton > button {
                background: linear-gradient(135deg, #00ff88 0%, #00d4ff 100%) !important;
                color: #090a0f !important;
                border-radius: 12px !important;
                border: none !important;
                font-family: var(--font-heading) !important;
                font-weight: 800 !important;
                box-shadow: 0 6px 20px rgba(0, 255, 136, 0.35) !important;
            }
            
            [data-testid="stTabs"] [role="tablist"] {
                background: rgba(255, 255, 255, 0.06) !important;
                border-radius: 14px !important;
                padding: 0.4rem !important;
                border: 1px solid rgba(0, 212, 255, 0.25) !important;
            }
            
            [data-testid="stTabs"] [role="tab"] {
                font-family: var(--font-heading) !important;
                color: #cbd5e1 !important;
                font-weight: 600 !important;
                border-radius: 10px !important;
            }
            
            [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
                background: linear-gradient(135deg, #00d4ff 0%, #9d4edd 100%) !important;
                color: #ffffff !important;
                font-weight: 800 !important;
            }
            
            [data-testid="stFileUploader"] {
                background: rgba(0, 212, 255, 0.05) !important;
                border: 2px dashed rgba(0, 212, 255, 0.4) !important;
                border-radius: 16px !important;
                padding: 1.5rem !important;
            }
            
            .vp-footer {
                margin-top: 3.5rem;
                padding: 1.75rem;
                text-align: center;
                background: rgba(18, 22, 36, 0.7);
                border: 1px solid rgba(0, 212, 255, 0.2);
                border-radius: 16px;
                color: #e2e8f0 !important;
            }
        </style>
        """
    st.markdown(theme_css, unsafe_allow_html=True)

# ==============================================================================
# 5. FUNCIONES AUXILIARES DE CÁLCULO EN PESOS COLOMBIANOS (COP)
# ==============================================================================
def format_currency(value):
    """Formatea valores en pesos colombianos con etiqueta protegida anti-traductor"""
    return f"${value:,.0f} COP"

def calculate_price(width_cm, height_cm, quantity, tariff_min, factor):
    """
    Cálculo en Pesos Colombianos (COP) para Gran Formato:
    Medidas ingresadas en cm.
    Área en m² = (width_cm * height_cm) / 10000.0
    Fórmula según tabla oficial:
    - Pendón tubo/ojales: Factor 55 -> $55.000 COP/m² (Mín $20.000 COP)
    - Aviso estructura sencilla: Factor 28 -> $280.000 COP/m² (Mín $100.000 COP)
    - Aviso luminoso Panaflex: Factor 38 -> $380.000 COP/m² (Mín $350.000 COP)
    - Adhesivo laminado: Factor 8 -> $80.000 COP/m² (Mín $25.000 COP)
    - Adhesivo troquelado: Factor 6 -> $60.000 COP/m² (Mín $35.000 COP)
    """
    area_m2 = (width_cm * height_cm) / 10000.0
    
    if factor == 55:
        rate_m2 = 55000.0
    elif factor == 28:
        rate_m2 = 280000.0
    elif factor == 38:
        rate_m2 = 380000.0
    elif factor == 8:
        rate_m2 = 80000.0
    elif factor == 6:
        rate_m2 = 60000.0
    else:
        rate_m2 = factor * 1000.0 if factor > 20 else factor * 10000.0
        
    formula_price = area_m2 * rate_m2
    unit_price = max(formula_price, tariff_min)
    total_price = unit_price * quantity
    return unit_price, total_price, area_m2, formula_price, rate_m2

def prepare_rgb_image(image_pil):
    if image_pil.mode in ('RGBA', 'LA') or (image_pil.mode == 'P' and 'transparency' in image_pil.info):
        alpha_img = image_pil.convert('RGBA')
        bg = Image.new('RGB', alpha_img.size, (255, 255, 255))
        bg.paste(alpha_img, mask=alpha_img.split()[3])
        return bg
    elif image_pil.mode != 'RGB':
        return image_pil.convert('RGB')
    return image_pil

# ==============================================================================
# 6. CONVERTIDOR DE IMAGEN A PDF: MODO PREPRENSA GRAN FORMATO CON ORIENTACIÓN ADAPTATIVA
# ==============================================================================
def create_prepress_pdf(image_pil, width_cm, height_cm, bleed_cm=0.5, dpi=150, crop_marks=True, fit_mode='stretch', orientation='auto'):
    """
    Genera un PDF para plotter FPP con orientación inteligente (automática según la forma de la imagen).
    """
    orig_w_px, orig_h_px = image_pil.size
    is_img_horizontal = orig_w_px > orig_h_px
    
    # Adaptar orientación según la forma de la imagen si está en auto
    if orientation == 'auto':
        if is_img_horizontal and width_cm < height_cm:
            width_cm, height_cm = height_cm, width_cm
        elif not is_img_horizontal and width_cm > height_cm:
            width_cm, height_cm = height_cm, width_cm
    elif orientation == 'horizontal':
        if width_cm < height_cm:
            width_cm, height_cm = height_cm, width_cm
    elif orientation == 'vertical':
        if width_cm > height_cm:
            width_cm, height_cm = height_cm, width_cm

    pt_per_cm = 72.0 / 2.54
    slug_cm = 0.6 if crop_marks else 0.0
    slug_pt = slug_cm * pt_per_cm
    bleed_pt = bleed_cm * pt_per_cm
    width_pt = width_cm * pt_per_cm
    height_pt = height_cm * pt_per_cm
    
    total_w_pt = width_pt + 2 * (bleed_pt + slug_pt)
    total_h_pt = height_pt + 2 * (bleed_pt + slug_pt)
    
    rgb_img = prepare_rgb_image(image_pil)
    
    target_w_px = max(10, int((width_cm + 2 * bleed_cm) * dpi / 2.54))
    target_h_px = max(10, int((height_cm + 2 * bleed_cm) * dpi / 2.54))
    
    if fit_mode == 'fit':
        resized_img = ImageOps.pad(rgb_img, (target_w_px, target_h_px), color=(255, 255, 255), method=Image.Resampling.LANCZOS)
    elif fit_mode == 'cover':
        resized_img = ImageOps.fit(rgb_img, (target_w_px, target_h_px), method=Image.Resampling.LANCZOS)
    else:
        resized_img = rgb_img.resize((target_w_px, target_h_px), Image.Resampling.LANCZOS)
    
    img_temp = io.BytesIO()
    resized_img.save(img_temp, format='JPEG', quality=95, dpi=(dpi, dpi))
    img_temp.seek(0)
    
    pdf_buf = io.BytesIO()
    c = canvas.Canvas(pdf_buf, pagesize=(total_w_pt, total_h_pt))
    
    img_x = slug_pt
    img_y = slug_pt
    img_w_pt = width_pt + 2 * bleed_pt
    img_h_pt = height_pt + 2 * bleed_pt
    
    reader = ImageReader(img_temp)
    c.drawImage(reader, img_x, img_y, width=img_w_pt, height=img_h_pt)
    
    # Marcas de corte vectoriales en 4 esquinas
    if crop_marks and slug_pt > 0:
        c.setStrokeColor(colors.black)
        c.setLineWidth(0.6)
        mark_len = slug_pt * 0.75
        
        x1 = slug_pt + bleed_pt
        x2 = x1 + width_pt
        y1 = slug_pt + bleed_pt
        y2 = y1 + height_pt
        gap = 2.0
        
        # Esquinas
        c.line(x1, y1 - gap, x1, y1 - mark_len)
        c.line(x1 - gap, y1, x1 - mark_len, y1)
        
        c.line(x2, y1 - gap, x2, y1 - mark_len)
        c.line(x2 + gap, y1, x2 + mark_len, y1)
        
        c.line(x1, y2 + gap, x1, y2 + mark_len)
        c.line(x1 - gap, y2, x1 - mark_len, y2)
        
        c.line(x2, y2 + gap, x2, y2 + mark_len)
        c.line(x2 + gap, y2, x2 + mark_len, y2)
        
        orient_txt = "Horizontal" if width_cm >= height_cm else "Vertical"
        c.setFont("Helvetica", 6)
        c.setFillColor(colors.HexColor("#555555"))
        c.drawString(x1, total_h_pt - 10, f"Corte: {width_cm:.1f}x{height_cm:.1f} cm ({orient_txt}) | Sangría: {bleed_cm:.1f} cm | DPI: {dpi} | VISIÓN Y PUBLICIDAD")

    c.save()
    pdf_buf.seek(0)
    return pdf_buf.getvalue(), width_cm, height_cm

# ==============================================================================
# 7. CONVERTIDOR DE IMÁGENES A PDF ESTÁNDAR MULTIPÁGINA
# ==============================================================================
def create_standard_multipage_pdf(images_list, page_size_name='Carta', orientation='auto', margin_cm=0.5):
    pdf_buf = io.BytesIO()
    c = None
    
    page_sizes = {
        'Carta': letter,
        'A4': A4,
        'Oficio / Legal': legal,
        'Tabloide (11x17 in)': (792, 1224)
    }
    
    pt_per_cm = 72.0 / 2.54
    margin_pt = margin_cm * pt_per_cm
    
    for raw_img in images_list:
        rgb_img = prepare_rgb_image(raw_img)
        img_w_px, img_h_px = rgb_img.size
        
        if page_size_name == 'Tamaño Original':
            page_w_pt = (img_w_px / 150.0) * 72.0
            page_h_pt = (img_h_px / 150.0) * 72.0
            cur_margin = 0
        else:
            base_w, base_h = page_sizes.get(page_size_name, letter)
            cur_margin = margin_pt
            
            if orientation == 'auto':
                is_landscape = img_w_px > img_h_px
            elif orientation == 'horizontal':
                is_landscape = True
            else:
                is_landscape = False
                
            page_w_pt = max(base_w, base_h) if is_landscape else min(base_w, base_h)
            page_h_pt = min(base_w, base_h) if is_landscape else max(base_w, base_h)
        
        if c is None:
            c = canvas.Canvas(pdf_buf, pagesize=(page_w_pt, page_h_pt))
        else:
            c.setPageSize((page_w_pt, page_h_pt))
            
        avail_w = max(10, page_w_pt - 2 * cur_margin)
        avail_h = max(10, page_h_pt - 2 * cur_margin)
        
        ratio = min(avail_w / img_w_px, avail_h / img_h_px)
        draw_w = img_w_px * ratio
        draw_h = img_h_px * ratio
        
        draw_x = cur_margin + (avail_w - draw_w) / 2.0
        draw_y = cur_margin + (avail_h - draw_h) / 2.0
        
        temp_img_io = io.BytesIO()
        rgb_img.save(temp_img_io, format='JPEG', quality=95)
        temp_img_io.seek(0)
        
        reader = ImageReader(temp_img_io)
        c.drawImage(reader, draw_x, draw_y, width=draw_w, height=draw_h)
        c.showPage()
        
    c.save()
    pdf_buf.seek(0)
    return pdf_buf.getvalue()

# ==============================================================================
# 8. MOTORES DE ELIMINACIÓN DE FONDO & GENERADOR DE ESTUDIO MANUAL CON PINCEL
# ==============================================================================
def remove_background_ai(img_pil):
    """Eliminación de fondo automática con IA (carga diferida para inicio ultra-rápido)"""
    try:
        import rembg
        session = st.session_state.get('rembg_session')
        if session is None:
            session = rembg.new_session('u2netp')
            st.session_state['rembg_session'] = session
        return rembg.remove(img_pil, session=session)
    except Exception:
        # Respaldo automático ultrarrápido si la IA no está disponible o excede la memoria
        return remove_background_numpy(img_pil, target_color_rgb=(255, 255, 255), tolerance=40)


def remove_background_numpy(img_pil, target_color_rgb=(255, 255, 255), tolerance=40, feather_edges=True):
    """Elimina el fondo de una imagen por color clave con aceleración NumPy"""
    img_rgba = img_pil.convert('RGBA')
    arr = np.array(img_rgba)
    
    r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
    tr, tg, tb = target_color_rgb[:3]
    
    # Distancia Euclidiana de color
    dist = np.sqrt((r.astype(float) - tr)**2 + (g.astype(float) - tg)**2 + (b.astype(float) - tb)**2)
    
    # Máscara de transparencia
    mask = dist < tolerance
    
    # Aplicar transparencia
    arr[:, :, 3] = np.where(mask, 0, a)
    result_img = Image.fromarray(arr, mode='RGBA')
    
    if feather_edges:
        alpha = result_img.split()[3]
        alpha_smooth = alpha.filter(ImageFilter.SMOOTH_MORE)
        result_img.putalpha(alpha_smooth)
        
    return result_img

def render_brush_canvas_studio(img_pil, filename_download="imagen_transparente.png"):
    """
    Componente interactivo HTML5 Canvas con pincel/borrador de tamaño regulable,
    deshacer (undo), indicador de grosor y descarga directa en PNG transparente.
    """
    img_data_uri = pil_to_base64_data_uri(img_pil)
    orig_w, orig_h = img_pil.size
    
    # Escalar dimensiones máximas para fluidez de dibujado en pantalla
    display_max_w = 780
    if orig_w > display_max_w:
        ratio = display_max_w / float(orig_w)
        canvas_w = int(orig_w * ratio)
        canvas_h = int(orig_h * ratio)
    else:
        canvas_w = orig_w
        canvas_h = orig_h
        
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        * {{
            box-sizing: border-box;
            user-select: none;
            -webkit-user-select: none;
        }}
        body {{
            margin: 0;
            padding: 12px;
            font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
            background: #111422;
            color: #ffffff;
            border-radius: 16px;
        }}
        .vp-studio-toolbar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 10px;
            background: #1c2136;
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 12px;
            padding: 10px 14px;
            margin-bottom: 12px;
        }}
        .vp-tool-group {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .vp-btn {{
            background: #272f4e;
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.15);
            padding: 6px 12px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        .vp-btn:hover {{
            background: #343e68;
            border-color: #00d4ff;
        }}
        .vp-btn.active {{
            background: linear-gradient(135deg, #00d4ff, #2563eb);
            color: #ffffff;
            border-color: #00d4ff;
            box-shadow: 0 0 10px rgba(0, 212, 255, 0.4);
        }}
        .vp-btn-success {{
            background: linear-gradient(135deg, #10b981, #059669);
            border: none;
            color: white;
            font-weight: 700;
        }}
        .vp-btn-success:hover {{
            box-shadow: 0 0 12px rgba(16, 185, 129, 0.5);
        }}
        .vp-slider-wrap {{
            display: flex;
            align-items: center;
            gap: 8px;
            background: #272f4e;
            padding: 4px 10px;
            border-radius: 8px;
            border: 1px solid rgba(0, 212, 255, 0.2);
        }}
        .vp-slider-wrap input[type=range] {{
            width: 120px;
            accent-color: #00d4ff;
            cursor: pointer;
        }}
        .vp-canvas-stage {{
            position: relative;
            margin: 0 auto;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
            border: 2px solid rgba(0, 212, 255, 0.3);
            /* Patrón de cuadrícula transparente (checkerboard) */
            background-color: #ffffff;
            background-image: linear-gradient(45deg, #e5e7eb 25%, transparent 25%),
                              linear-gradient(-45deg, #e5e7eb 25%, transparent 25%),
                              linear-gradient(45deg, transparent 75%, #e5e7eb 75%),
                              linear-gradient(-45deg, transparent 75%, #e5e7eb 75%);
            background-size: 16px 16px;
            background-position: 0 0, 0 8px, 8px -8px, -8px 0px;
            width: {canvas_w}px;
            height: {canvas_h}px;
            cursor: crosshair;
        }}
        #drawCanvas {{
            display: block;
            width: {canvas_w}px;
            height: {canvas_h}px;
        }}
        #brushCursor {{
            pointer-events: none;
            position: absolute;
            border: 2px solid #ff0055;
            background: rgba(255, 0, 85, 0.2);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            display: none;
            z-index: 99;
        }}
        .vp-info-strip {{
            margin-top: 8px;
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: #94a3b8;
            padding: 0 4px;
        }}
    </style>
    </head>
    <body>
        <div class="vp-studio-toolbar">
            <div class="vp-tool-group">
                <button id="btnEraser" class="vp-btn active">🧹 Pincel Borrador (Fondo)</button>
                <button id="btnRestore" class="vp-btn">🖌️ Pincel Restaurador</button>
            </div>
            
            <div class="vp-slider-wrap">
                <span style="font-size: 12px; font-weight: 700;">Grosor:</span>
                <input type="range" id="sizeSlider" min="3" max="90" value="28">
                <span id="sizeLabel" style="font-size: 12px; font-weight: 800; color: #00d4ff; width: 38px;">28 px</span>
            </div>

            <div class="vp-tool-group">
                <button id="btnUndo" class="vp-btn" title="Deshacer último trazo">↩️ Deshacer</button>
                <button id="btnReset" class="vp-btn" title="Reiniciar imagen">🔄 Restablecer</button>
                <button id="btnBgToggle" class="vp-btn" title="Alternar fondo de verificación">🏁 Fondo</button>
                <button id="btnExport" class="vp-btn vp-btn-success">📥 Descargar PNG</button>
            </div>
        </div>

        <div class="vp-canvas-stage" id="stage">
            <canvas id="drawCanvas" width="{canvas_w}" height="{canvas_h}"></canvas>
            <div id="brushCursor"></div>
        </div>

        <div class="vp-info-strip">
            <span>💡 <strong>Instrucciones:</strong> Pase el pincel sobre las zonas que desea borrar a transparencia total. Use el control deslizante para ajustar el grosor.</span>
            <span>Resolución de trabajo: {orig_w} × {orig_h} px</span>
        </div>

        <script>
            const canvas = document.getElementById('drawCanvas');
            const ctx = canvas.getContext('2d');
            const stage = document.getElementById('stage');
            const brushCursor = document.getElementById('brushCursor');
            const sizeSlider = document.getElementById('sizeSlider');
            const sizeLabel = document.getElementById('sizeLabel');
            const btnEraser = document.getElementById('btnEraser');
            const btnRestore = document.getElementById('btnRestore');
            const btnUndo = document.getElementById('btnUndo');
            const btnReset = document.getElementById('btnReset');
            const btnBgToggle = document.getElementById('btnBgToggle');
            const btnExport = document.getElementById('btnExport');

            let isDrawing = false;
            let brushMode = 'eraser'; // 'eraser' o 'restore'
            let brushSize = parseInt(sizeSlider.value);
            let historyStack = [];
            let maxHistory = 15;

            // Imagen original de referencia
            const origImg = new Image();
            origImg.crossOrigin = 'anonymous';
            origImg.src = "{img_data_uri}";

            origImg.onload = () => {{
                ctx.drawImage(origImg, 0, 0, canvas.width, canvas.height);
                saveState();
            }};

            function saveState() {{
                if (historyStack.length >= maxHistory) {{
                    historyStack.shift();
                }}
                historyStack.push(ctx.getImageData(0, 0, canvas.width, canvas.height));
            }}

            sizeSlider.addEventListener('input', (e) => {{
                brushSize = parseInt(e.target.value);
                sizeLabel.textContent = brushSize + ' px';
                updateCursorSize();
            }});

            function updateCursorSize() {{
                brushCursor.style.width = brushSize + 'px';
                brushCursor.style.height = brushSize + 'px';
                if (brushMode === 'eraser') {{
                    brushCursor.style.borderColor = '#ff0055';
                    brushCursor.style.background = 'rgba(255, 0, 85, 0.2)';
                }} else {{
                    brushCursor.style.borderColor = '#00ff88';
                    brushCursor.style.background = 'rgba(0, 255, 136, 0.2)';
                }}
            }}

            btnEraser.addEventListener('click', () => {{
                brushMode = 'eraser';
                btnEraser.classList.add('active');
                btnRestore.classList.remove('active');
                updateCursorSize();
            }});

            btnRestore.addEventListener('click', () => {{
                brushMode = 'restore';
                btnRestore.classList.add('active');
                btnEraser.classList.remove('active');
                updateCursorSize();
            }});

            btnUndo.addEventListener('click', () => {{
                if (historyStack.length > 1) {{
                    historyStack.pop(); // Quitar el actual
                    const prev = historyStack[historyStack.length - 1];
                    ctx.putImageData(prev, 0, 0);
                }}
            }});

            btnReset.addEventListener('click', () => {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(origImg, 0, 0, canvas.width, canvas.height);
                historyStack = [];
                saveState();
            }});

            let bgState = 0;
            btnBgToggle.addEventListener('click', () => {{
                bgState = (bgState + 1) % 3;
                if (bgState === 0) {{
                    stage.style.backgroundImage = 'linear-gradient(45deg, #e5e7eb 25%, transparent 25%), linear-gradient(-45deg, #e5e7eb 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #e5e7eb 75%), linear-gradient(-45deg, transparent 75%, #e5e7eb 75%)';
                    stage.style.backgroundColor = '#ffffff';
                }} else if (bgState === 1) {{
                    stage.style.backgroundImage = 'none';
                    stage.style.backgroundColor = '#000000';
                }} else {{
                    stage.style.backgroundImage = 'none';
                    stage.style.backgroundColor = '#ffffff';
                }}
            }});

            function getMousePos(evt) {{
                const rect = canvas.getBoundingClientRect();
                const scaleX = canvas.width / rect.width;
                const scaleY = canvas.height / rect.height;
                return {{
                    x: (evt.clientX - rect.left) * scaleX,
                    y: (evt.clientY - rect.top) * scaleY,
                    rawX: evt.clientX - rect.left,
                    rawY: evt.clientY - rect.top
                }};
            }}

            stage.addEventListener('mouseenter', () => {{
                brushCursor.style.display = 'block';
                updateCursorSize();
            }});

            stage.addEventListener('mouseleave', () => {{
                brushCursor.style.display = 'none';
                isDrawing = false;
            }});

            stage.addEventListener('mousemove', (e) => {{
                const pos = getMousePos(e);
                brushCursor.style.left = pos.rawX + 'px';
                brushCursor.style.top = pos.rawY + 'px';
                if (isDrawing) {{
                    draw(pos.x, pos.y);
                }}
            }});

            stage.addEventListener('mousedown', (e) => {{
                isDrawing = true;
                const pos = getMousePos(e);
                ctx.beginPath();
                ctx.moveTo(pos.x, pos.y);
                draw(pos.x, pos.y);
            }});

            window.addEventListener('mouseup', () => {{
                if (isDrawing) {{
                    isDrawing = false;
                    ctx.beginPath();
                    saveState();
                }}
            }});

            function draw(x, y) {{
                ctx.lineWidth = brushSize;
                ctx.lineCap = 'round';
                ctx.lineJoin = 'round';

                if (brushMode === 'eraser') {{
                    ctx.globalCompositeOperation = 'destination-out';
                    ctx.lineTo(x, y);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.moveTo(x, y);
                }} else {{
                    // Restaurador: pintar píxeles desde imagen original usando un canvas temporal de trazo
                    ctx.globalCompositeOperation = 'source-over';
                    const tempC = document.createElement('canvas');
                    tempC.width = canvas.width;
                    tempC.height = canvas.height;
                    const tempCtx = tempC.getContext('2d');
                    tempCtx.lineWidth = brushSize;
                    tempCtx.lineCap = 'round';
                    tempCtx.lineJoin = 'round';
                    tempCtx.beginPath();
                    tempCtx.moveTo(x, y);
                    tempCtx.arc(x, y, brushSize / 2, 0, Math.PI * 2);
                    tempCtx.fill();

                    // Aplicar recorte de la imagen original
                    tempCtx.globalCompositeOperation = 'source-in';
                    tempCtx.drawImage(origImg, 0, 0, canvas.width, canvas.height);

                    ctx.drawImage(tempC, 0, 0);
                }}
            }}

            // Descarga en resolución de salida
            btnExport.addEventListener('click', () => {{
                const link = document.createElement('a');
                link.download = "{filename_download}";
                link.href = canvas.toDataURL('image/png');
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }});
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=canvas_h + 160)

# ==============================================================================
# 9. GENERADOR DE FACTURAS / RECIBOS EN PDF (VISIÓN Y PUBLICIDAD)
# ==============================================================================
def generate_receipt_pdf(client_name, client_doc, items, subtotal, iva, total, receipt_num):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    primary_blue = colors.HexColor('#1E3A8A')
    accent_blue = colors.HexColor('#2563EB')
    gray_bg = colors.HexColor('#F8FAFC')
    gray_border = colors.HexColor('#E2E8F0')
    gray_text = colors.HexColor('#475569')
    dark_text = colors.HexColor('#0F172A')
    
    # Encabezado corporativo
    c.setFillColor(primary_blue)
    c.rect(0, height - 90, width, 90, fill=True, stroke=False)
    
    # Incrustar logo si existe
    if os.path.exists("logo.png"):
        try:
            c.drawImage("logo.png", 40, height - 80, width=55, height=55, mask='auto')
            text_x = 105
        except Exception:
            text_x = 40
    else:
        text_x = 40
        
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(text_x, height - 42, "VISIÓN Y PUBLICIDAD")
    c.setFont("Helvetica", 9)
    c.drawString(text_x, height - 60, "Ingeniería Gráfica & Diseño | PBX: (601) 320-0000")
    
    # Consecutivo
    c.setFillColor(colors.HexColor('#172554'))
    c.roundRect(width - 180, height - 75, 140, 55, 6, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(width - 170, height - 38, "ORDEN / RECIBO")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(width - 170, height - 58, f"N° {receipt_num}")
    
    # Cuadro Cliente
    c.setFillColor(gray_bg)
    c.setStrokeColor(gray_border)
    c.roundRect(40, height - 170, width - 80, 65, 8, fill=True, stroke=True)
    
    c.setFillColor(dark_text)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(55, height - 125, "Cliente / Empresa:")
    c.drawString(55, height - 150, "Documento / NIT:")
    
    c.setFont("Helvetica", 10)
    c.drawString(160, height - 125, str(client_name))
    c.drawString(160, height - 150, str(client_doc if client_doc else "Consumidor Final"))
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(width - 240, height - 125, "Fecha Emisión:")
    c.drawString(width - 240, height - 150, "Estado:")
    
    c.setFont("Helvetica", 10)
    c.drawString(width - 150, height - 125, datetime.now().strftime('%d/%m/%Y %H:%M'))
    c.setFillColor(colors.HexColor('#059669'))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(width - 150, height - 150, "PAGADO / APROBADO")
    
    # Tabla de Items
    y_pos = height - 205
    c.setFillColor(accent_blue)
    c.roundRect(40, y_pos, width - 80, 26, 4, fill=True, stroke=False)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(55, y_pos + 8, "DESCRIPCIÓN DEL PRODUCTO / SERVICIO")
    c.drawString(340, y_pos + 8, "CANT.")
    c.drawString(400, y_pos + 8, "VALOR UNITARIO")
    c.drawString(500, y_pos + 8, "SUBTOTAL")
    
    y_pos -= 24
    row_alt = False
    
    for item in items:
        if row_alt:
            c.setFillColor(gray_bg)
            c.rect(40, y_pos - 4, width - 80, 22, fill=True, stroke=False)
        row_alt = not row_alt
        
        c.setFillColor(dark_text)
        c.setFont("Helvetica", 9)
        c.drawString(55, y_pos + 3, str(item['descripcion'])[:45])
        c.drawString(350, y_pos + 3, str(item['cantidad']))
        c.drawString(400, y_pos + 3, format_currency(item['unitario']))
        c.drawString(500, y_pos + 3, format_currency(item['subtotal']))
        
        c.setStrokeColor(gray_border)
        c.setLineWidth(0.5)
        c.line(40, y_pos - 4, width - 40, y_pos - 4)
        
        y_pos -= 24
        if y_pos < 180:
            break
            
    # Totales
    totals_y = y_pos - 20
    c.setFillColor(gray_bg)
    c.setStrokeColor(gray_border)
    c.roundRect(width - 240, totals_y - 75, 200, 85, 6, fill=True, stroke=True)
    
    c.setFillColor(gray_text)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(width - 225, totals_y - 12, "Subtotal:")
    c.drawString(width - 225, totals_y - 32, "IVA (19%):")
    
    c.setFillColor(dark_text)
    c.setFont("Helvetica", 10)
    c.drawRightString(width - 55, totals_y - 12, format_currency(subtotal))
    c.drawRightString(width - 55, totals_y - 32, format_currency(iva))
    
    c.setStrokeColor(gray_border)
    c.line(width - 230, totals_y - 42, width - 50, totals_y - 42)
    
    c.setFillColor(primary_blue)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width - 225, totals_y - 62, "TOTAL:")
    c.drawRightString(width - 55, totals_y - 62, format_currency(total))
    
    # Pie de página
    c.setFillColor(gray_text)
    c.setFont("Helvetica", 8)
    c.drawString(40, 50, "Garantía de impresión: 30 días. Verifique medidas, textos y colores antes de aprobar.")
    c.drawString(40, 38, "VISIÓN Y PUBLICIDAD | E-mail: contacto@visionypublicidad.com | Colombia")
    
    c.setStrokeColor(accent_blue)
    c.setLineWidth(2)
    c.line(40, 65, width - 40, 65)
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# ==============================================================================
# 10. APLICACIÓN PRINCIPAL
# ==============================================================================
def main():
    apply_theme()
    
    is_light = st.session_state.theme_mode == 'light'
    mode_text = "Modo Pastel Gris & Blanco" if is_light else "Modo Oscuro Cyber Neon"
    toggle_target = "dark" if is_light else "light"
    toggle_label = "🌙 Cambiar a Modo Oscuro" if is_light else "☀️ Cambiar a Modo Pastel"
    
    # Render del logo oficial
    if LOGO_B64:
        logo_html = f'<img src="data:image/png;base64,{LOGO_B64}" width="62" height="62" style="border-radius: 14px; object-fit: contain; background: white; padding: 2px; box-shadow: 0 4px 14px rgba(0,0,0,0.15);">'
    else:
        logo_html = '<div style="background: linear-gradient(135deg, #2563eb, #1d4ed8); width: 60px; height: 60px; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 2rem;">🎨</div>'

    # HERO HEADER OFICIAL "VISIÓN Y PUBLICIDAD"
    st.markdown(f"""
    <div class="vp-hero">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1.25rem;">
            <div style="display: flex; align-items: center; gap: 1.35rem;">
                {logo_html}
                <div>
                    <div style="display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;">
                        <h1 class="vp-title">VISIÓN Y PUBLICIDAD</h1>
                        <span class="vp-badge vp-badge-active">
                            <span style="width: 7px; height: 7px; background: #10b981; border-radius: 50%;"></span>
                            ONLINE • v2.6
                        </span>
                    </div>
                    <p class="vp-subtitle">Sistema de Gestión & Diseño | Gran Formato, Plotter FPP, Editor PNG y Cotización Oficial</p>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap;">
                <div class="vp-badge">
                    <span>⚡ Plotter FPP 4.0</span>
                </div>
                <div class="vp-badge">
                    <span>✂️ Editor PNG Libre & IA</span>
                </div>
                <div class="vp-badge">
                    <span>{mode_text}</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Botón rápido para alternar tema
    col_t1, col_t2 = st.columns([8, 2])
    with col_t2:
        if st.button(toggle_label, key="toggle_theme_btn", use_container_width=True):
            st.session_state.theme_mode = toggle_target
            st.rerun()

    # BARRA LATERAL (SIDEBAR)
    with st.sidebar:
        if LOGO_B64:
            st.markdown(f"""
            <div style="text-align: center; padding: 0.5rem 0 0.8rem 0;">
                <img src="data:image/png;base64,{LOGO_B64}" width="85" style="border-radius: 16px; background: white; padding: 4px; box-shadow: 0 4px 16px rgba(0,0,0,0.15);">
                <h3 style="margin: 0.6rem 0 0.1rem 0; font-size: 1.2rem; font-weight: 800; font-family: 'Outfit', sans-serif;">VISIÓN Y PUBLICIDAD</h3>
                <p style="margin: 0; font-size: 0.85rem; font-weight: 600;">Sistema de Gestión & Diseño</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("### VISIÓN Y PUBLICIDAD")
            
        st.markdown("---")
        st.markdown("#### 🎨 Selector de Apariencia")
        selected_theme = st.radio(
            "Seleccionar Tema",
            options=["Pastel Gris con Blanco", "Oscuro Neón Cyber"],
            index=0 if is_light else 1,
            label_visibility="collapsed"
        )
        new_mode = "light" if "Pastel" in selected_theme else "dark"
        if new_mode != st.session_state.theme_mode:
            st.session_state.theme_mode = new_mode
            st.rerun()
            
        st.markdown("---")
        st.markdown("#### 📈 Métricas de la Sesión")
        
        total_sales_sum = st.session_state.sales_history['total'].sum() if len(st.session_state.sales_history) > 0 else 0
        total_items_sold = st.session_state.sales_history['cantidad'].sum() if len(st.session_state.sales_history) > 0 else 0
        
        st.markdown(f"""
        <div style="margin-bottom: 0.85rem;">
            <div style="font-size: 0.78rem; font-weight: 700; text-transform: uppercase;">VENTAS TOTALES</div>
            <div style="font-size: 1.55rem; font-weight: 800; font-family: 'Outfit'; color: {'#2563eb' if is_light else '#00d4ff'};">
                ${total_sales_sum:,.0f} <span class="notranslate" translate="no">COP</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.metric("Órdenes Procesadas", f"{len(st.session_state.sales_history)} ventas")
        st.metric("Unidades Vendidas", f"{total_items_sold:,} unidades")
        
        st.markdown("---")
        st.markdown("#### 📦 Inventario Oficial")
        st.caption(f"🔧 Materiales Gran Formato: **{len(st.session_state.services_by_measure)} referencias**")
        st.caption(f"📦 Catálogo Papelería: **{len(st.session_state.fixed_products)} productos**")
        
        st.markdown("---")
        st.markdown("""
        <div style="font-size: 0.8rem; text-align: center;">
            <strong>VISIÓN Y PUBLICIDAD</strong><br>
            Bogotá, Colombia • Moneda: <span class="notranslate" translate="no">COP</span>
        </div>
        """, unsafe_allow_html=True)

    # PESTAÑAS PRINCIPALES DEL SISTEMA (7 PESTAÑAS COMPLETAS)
    tab_cotizador, tab_converter, tab_png_editor, tab_papeleria, tab_inventario, tab_factura, tab_historial = st.tabs([
        "📐 Cotizador Gran Formato",
        "🖨️ Convertidor Imagen a PDF",
        "✂️ Editor PNG, Recorte Libre & Quitar Fondo",
        "📦 Papelería & Promocionales",
        "📋 Control de Inventario",
        "🧾 Facturación & Recibos",
        "📊 Historial de Ventas"
    ])

    # ==========================================================================
    # PESTAÑA 1: COTIZADOR GRAN FORMATO
    # ==========================================================================
    with tab_cotizador:
        st.markdown("""
        <div class="vp-card">
            <h2 class="vp-title">Cotizador Gran Formato & Avisos (Fórmulas Oficiales)</h2>
            <p class="vp-subtitle">Medidas en centímetros (cm). Fórmulas oficiales de la tabla de precios y transferencia directa al convertidor FPP.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_c1, col_c2 = st.columns([1, 1], gap="large")
        
        with col_c1:
            st.markdown("##### 📝 1. Especificaciones del Pedido")
            client_gf = st.text_input("Nombre del Cliente / Empresa", placeholder="Ej: Comercializadora Los Andes", key="gf_client_input")
            
            services_list = st.session_state.services_by_measure['servicio'].tolist()
            selected_srv = st.selectbox("Soporte Publicitario / Material", services_list, key="gf_srv_select")
            
            srv_row = st.session_state.services_by_measure[
                st.session_state.services_by_measure['servicio'] == selected_srv
            ].iloc[0]
            
            col_dim1, col_dim2 = st.columns(2)
            with col_dim1:
                width_in_cm = st.number_input("Ancho de Pieza (cm)", min_value=1.0, max_value=2000.0, value=100.0, step=1.0, key="gf_w_cm")
            with col_dim2:
                height_in_cm = st.number_input("Largo / Alto (cm)", min_value=1.0, max_value=5000.0, value=150.0, step=1.0, key="gf_h_cm")
                
            qty_gf = st.number_input("Cantidad de Piezas", min_value=1, max_value=1000, value=1, key="gf_qty_num")
            
            unit_p, total_p, area_m2, formula_p, rate_m2 = calculate_price(
                width_in_cm, height_in_cm, qty_gf, srv_row['tarifa_minima'], srv_row['factor']
            )
            
            st.markdown(f"""
            <div style="background: {'#f1f5f9' if is_light else 'rgba(0, 212, 255, 0.08)'}; 
                        border-radius: 12px; padding: 0.85rem 1.1rem; margin-top: 0.75rem; 
                        display: flex; align-items: center; justify-content: space-between; font-size: 0.88rem;
                        border: 1px solid {'#cbd5e1' if is_light else 'rgba(0, 212, 255, 0.25)'};">
                <div>📏 <strong>Área:</strong> {width_in_cm:.0f} × {height_in_cm:.0f} cm = <strong>{area_m2:.2f} m²</strong></div>
                <div>📊 <strong>Tarifa:</strong> ${rate_m2:,.0f} <span class="notranslate" translate="no">COP/m²</span></div>
            </div>
            """, unsafe_allow_html=True)

        with col_c2:
            st.markdown("##### 💰 2. Liquidación en Pesos Colombianos (COP)")
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                st.markdown(f"""
                <div class="vp-stat-box">
                    <div class="vp-stat-label">Costo por Fórmula</div>
                    <div class="vp-stat-val">${formula_p:,.0f} <span class="notranslate" translate="no" style="font-size: 0.9rem;">COP</span></div>
                </div>
                """, unsafe_allow_html=True)
            with col_b2:
                st.markdown(f"""
                <div class="vp-stat-box">
                    <div class="vp-stat-label">Tarifa Mínima Aplicable</div>
                    <div class="vp-stat-val">${srv_row['tarifa_minima']:,.0f} <span class="notranslate" translate="no" style="font-size: 0.9rem;">COP</span></div>
                </div>
                """, unsafe_allow_html=True)
                
            col_b3, col_b4 = st.columns(2)
            with col_b3:
                st.markdown(f"""
                <div class="vp-stat-box">
                    <div class="vp-stat-label">Valor Unitario</div>
                    <div class="vp-stat-val">${unit_p:,.0f} <span class="notranslate" translate="no" style="font-size: 0.9rem;">COP</span></div>
                </div>
                """, unsafe_allow_html=True)
            with col_b4:
                st.markdown(f"""
                <div class="vp-stat-box">
                    <div class="vp-stat-label">Stock en Inventario</div>
                    <div class="vp-stat-val">{srv_row['stock']} m/unid.</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown(f"""
            <div class="vp-stat-highlight" style="margin-top: 1rem;">
                <div class="vp-stat-label">TOTAL A COBRAR ({qty_gf} UNIDAD/ES)</div>
                <div class="vp-stat-val">${total_p:,.0f} <span class="notranslate" translate="no" style="font-size: 1.2rem;">COP</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("💾 Registrar Venta en Historial", key="gf_save_sale", use_container_width=True):
                    if not client_gf.strip():
                        st.warning("Ingrese el nombre del cliente para registrar la venta.")
                    else:
                        idx = st.session_state.services_by_measure[
                            st.session_state.services_by_measure['servicio'] == selected_srv
                        ].index[0]
                        st.session_state.services_by_measure.at[idx, 'stock'] = max(0, st.session_state.services_by_measure.at[idx, 'stock'] - qty_gf)
                        
                        new_sale = pd.DataFrame([{
                            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'cliente': client_gf,
                            'tipo': 'Gran Formato',
                            'producto': f"{selected_srv} ({width_in_cm:.0f}x{height_in_cm:.0f} cm)",
                            'cantidad': qty_gf,
                            'subtotal': total_p,
                            'iva': total_p * 0.19,
                            'total': total_p * 1.19
                        }])
                        st.session_state.sales_history = pd.concat([st.session_state.sales_history, new_sale], ignore_index=True)
                        st.success(f"Venta registrada para {client_gf}. ¡Inventario actualizado!")
                        st.rerun()
                        
            with col_btn2:
                if st.button("➡️ Enviar Medidas al Convertidor", key="gf_to_conv", use_container_width=True):
                    st.session_state.prefill_converter = {
                        'width': float(width_in_cm),
                        'height': float(height_in_cm),
                        'service': selected_srv
                    }
                    st.info(f"Medidas ({width_in_cm:.0f} × {height_in_cm:.0f} cm) enviadas al Convertidor. ¡Abra la pestaña 'Convertidor Imagen a PDF'!")

    # ==========================================================================
    # PESTAÑA 2: CONVERTIDOR DE IMAGEN A PDF (ORIENTACIÓN ADAPTATIVA AUTOMÁTICA)
    # ==========================================================================
    with tab_converter:
        st.markdown("""
        <div class="vp-card">
            <h2 class="vp-title">Convertidor de Imagen a PDF Profesional</h2>
            <p class="vp-subtitle">Genera archivos PDF adaptados automáticamente a la forma de la imagen (vertical u horizontal), con sangría y marcas de corte para Plotter FPP o documentos estándar.</p>
        </div>
        """, unsafe_allow_html=True)
        
        conv_mode = st.radio(
            "Seleccione el Modo de Conversión:",
            options=["🎯 Preprensa Gran Formato / Plotter (FPP)", "📄 Documento Estándar / Multipágina (Carta, A4, Original)"],
            horizontal=True,
            key="conv_mode_radio"
        )
        
        st.markdown("<hr style='margin: 1rem 0; opacity: 0.25;'>", unsafe_allow_html=True)
        
        # MODO PREPRENSA GRAN FORMATO
        if "Plotter" in conv_mode:
            col_p1, col_p2 = st.columns([1, 1], gap="large")
            
            with col_p1:
                st.markdown("##### 🎛️ 1. Parámetros Técnicos de Salida")
                
                default_w = st.session_state.prefill_converter.get('width', 100.0)
                default_h = st.session_state.prefill_converter.get('height', 150.0)
                
                col_w1, col_w2 = st.columns(2)
                with col_w1:
                    target_w = st.number_input("Ancho de Corte (cm)", min_value=5.0, max_value=3000.0, value=default_w, step=1.0, key="conv_target_w")
                with col_w2:
                    target_h = st.number_input("Alto de Corte (cm)", min_value=5.0, max_value=5000.0, value=default_h, step=1.0, key="conv_target_h")
                
                # Control inteligente de orientación según la forma de la imagen
                col_or1, col_or2 = st.columns([3, 2])
                with col_or1:
                    pdf_orient = st.selectbox(
                        "Orientación del Lienzo PDF",
                        options=["auto", "horizontal", "vertical"],
                        format_func=lambda x: "🔄 Automática (según la forma de la imagen)" if x=="auto" else ("↔️ Horizontal (Apaisada)" if x=="horizontal" else "↕️ Vertical (Retrato)"),
                        key="prepress_orient_selector"
                    )
                with col_or2:
                    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                    if st.button("🔄 Invertir Ancho y Alto", key="swap_wh_btn", use_container_width=True):
                        st.session_state.prefill_converter['width'] = float(target_h)
                        st.session_state.prefill_converter['height'] = float(target_w)
                        st.rerun()

                col_p_extra1, col_p_extra2 = st.columns(2)
                with col_p_extra1:
                    bleed_val = st.selectbox(
                        "Sangría (Bleed)",
                        options=[0.5, 1.0, 1.5, 2.0, 0.0],
                        index=0,
                        format_func=lambda x: f"{x} cm" if x > 0 else "Sin sangría (0 cm)",
                        key="conv_bleed_val"
                    )
                with col_p_extra2:
                    dpi_val = st.selectbox(
                        "Resolución (DPI)",
                        options=[150, 300, 72],
                        index=0,
                        format_func=lambda x: f"{x} DPI - {'Plotter Recomendado' if x==150 else ('Alta Definición' if x==300 else 'Borrador')}",
                        key="conv_dpi_val"
                    )
                    
                col_p_opt1, col_p_opt2 = st.columns(2)
                with col_p_opt1:
                    with_crop_marks = st.checkbox("Marcas de Corte Vectoriales", value=True, key="conv_crop_marks")
                with col_p_opt2:
                    fit_option = st.selectbox(
                        "Ajuste Proporcional",
                        options=["stretch", "fit", "cover"],
                        format_func=lambda x: "Estirar a medida exacta" if x=="stretch" else ("Ajustar proporcional (Letterbox)" if x=="fit" else "Rellenar y recortar centro"),
                        key="conv_fit_option"
                    )
                    
                st.markdown("##### 📁 Cargar Archivo de Imagen")
                uploaded_prepress_file = st.file_uploader(
                    "Seleccione su imagen (JPG, PNG, WEBP, TIFF, BMP)",
                    type=['jpg', 'jpeg', 'png', 'webp', 'tiff', 'bmp'],
                    key="prepress_file_upload"
                )
                
                col_btn_test, col_btn_clear = st.columns([2, 1])
                with col_btn_test:
                    if st.button("🖼️ Usar Logo Oficial de Prueba", key="load_logo_prepress"):
                        if os.path.exists("logo.png"):
                            with open("logo.png", "rb") as f:
                                st.session_state.prepress_img_bytes = f.read()
                                st.session_state.prepress_img_name = "logo_vision_publicidad.png"
                            st.success("Logo oficial cargado en el convertidor.")
                            st.rerun()
                with col_btn_clear:
                    if st.session_state.prepress_img_bytes:
                        if st.button("🗑️ Quitar", key="clear_prepress_img"):
                            st.session_state.prepress_img_bytes = None
                            st.session_state.prepress_img_name = None
                            st.rerun()

                if uploaded_prepress_file is not None:
                    st.session_state.prepress_img_bytes = uploaded_prepress_file.getvalue()
                    st.session_state.prepress_img_name = uploaded_prepress_file.name

            with col_p2:
                st.markdown("##### 🔬 2. Ficha Técnica & Generación de PDF")
                if st.session_state.prepress_img_bytes:
                    try:
                        pil_img = Image.open(io.BytesIO(st.session_state.prepress_img_bytes))
                        orig_w_px, orig_h_px = pil_img.size
                        megapixels = (orig_w_px * orig_h_px) / 1_000_000.0
                        img_name = st.session_state.get('prepress_img_name', 'arte_publicitario')
                        
                        # Diagnóstico de forma
                        is_landscape_img = orig_w_px > orig_h_px
                        shape_tag = "↔️ Horizontal (Apaisada)" if is_landscape_img else "↕️ Vertical (Retrato)"
                        
                        # Calcular medidas efectivas aplicando la orientación adaptativa
                        if pdf_orient == 'auto':
                            eff_w = max(target_w, target_h) if is_landscape_img else min(target_w, target_h)
                            eff_h = min(target_w, target_h) if is_landscape_img else max(target_w, target_h)
                            orient_applied_desc = f"Adaptado automáticamente a {shape_tag}"
                        elif pdf_orient == 'horizontal':
                            eff_w = max(target_w, target_h)
                            eff_h = min(target_w, target_h)
                            orient_applied_desc = "Fijado en Horizontal"
                        else:
                            eff_w = min(target_w, target_h)
                            eff_h = max(target_w, target_h)
                            orient_applied_desc = "Fijado en Vertical"

                        st.markdown(f"""
                        <div class="vp-card" style="margin-bottom: 1rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
                                <h4 style="margin: 0; font-size: 1.05rem; font-family: var(--font-heading);">📊 Ficha Técnica del Arte</h4>
                                <span class="vp-badge vp-badge-active">✅ {shape_tag}</span>
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.88rem;">
                                <div><strong>Archivo:</strong> {img_name[:25]}</div>
                                <div><strong>Resolución:</strong> {orig_w_px} × {orig_h_px} px</div>
                                <div><strong>Megapíxeles:</strong> {megapixels:.1f} MP</div>
                                <div><strong>Espacio de Color:</strong> {pil_img.mode}</div>
                                <div><strong>Orientación PDF:</strong> {orient_applied_desc}</div>
                                <div><strong>Medida Final:</strong> <strong>{eff_w:.1f} × {eff_h:.1f} cm</strong></div>
                                <div><strong>Con Sangría:</strong> {eff_w + 2*bleed_val:.1f} × {eff_h + 2*bleed_val:.1f} cm</div>
                                <div><strong>DPI Configurado:</strong> {dpi_val} DPI</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.image(pil_img, caption=f"Vista previa: {img_name} ({shape_tag})", use_container_width=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("🚀 Generar PDF FPP Listo para Plotter", key="btn_gen_prepress", use_container_width=True):
                            with st.spinner("Procesando orientación, dimensiones y marcas vectoriales..."):
                                pdf_bytes, applied_w, applied_h = create_prepress_pdf(
                                    pil_img, 
                                    width_cm=target_w, 
                                    height_cm=target_h, 
                                    bleed_cm=bleed_val, 
                                    dpi=dpi_val, 
                                    crop_marks=with_crop_marks, 
                                    fit_mode=fit_option,
                                    orientation=pdf_orient
                                )
                                
                                size_kb = len(pdf_bytes) / 1024.0
                                size_label = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{(size_kb/1024.0):.2f} MB"
                                clean_name = os.path.splitext(img_name)[0]
                                orient_suffix = "H" if applied_w >= applied_h else "V"
                                out_filename = f"PLOTTER_{clean_name}_{applied_w:.0f}x{applied_h:.0f}cm_{orient_suffix}_{datetime.now().strftime('%H%M%S')}.pdf"
                                
                                st.session_state['generated_plotter_pdf'] = pdf_bytes
                                st.session_state['generated_plotter_filename'] = out_filename
                                st.success(f"¡PDF generado con éxito ({applied_w:.0f}×{applied_h:.0f} cm)! Tamaño: {size_label}")
                                
                        if 'generated_plotter_pdf' in st.session_state and st.session_state['generated_plotter_pdf']:
                            st.download_button(
                                label="📥 Descargar PDF Plotter FPP",
                                data=st.session_state['generated_plotter_pdf'],
                                file_name=st.session_state.get('generated_plotter_filename', 'plotter.pdf'),
                                mime="application/pdf",
                                key="dl_prepress_pdf_active",
                                use_container_width=True
                            )
                    except Exception as e:
                        st.error(f"Error al procesar la imagen: {str(e)}")
                else:
                    st.info("Suba una imagen o haga clic en 'Usar Logo Oficial de Prueba' para comenzar la conversión.")

        # MODO DOCUMENTO ESTÁNDAR
        else:
            col_s1, col_s2 = st.columns([1, 1], gap="large")
            
            with col_s1:
                st.markdown("##### 📄 1. Ajustes del Documento")
                
                col_cfg1, col_cfg2 = st.columns(2)
                with col_cfg1:
                    std_page_size = st.selectbox(
                        "Tamaño de Hoja",
                        options=["Carta", "A4", "Tabloide (11x17 in)", "Oficio / Legal", "Tamaño Original"],
                        key="std_page_size"
                    )
                with col_cfg2:
                    std_orientation = st.selectbox(
                        "Orientación del PDF",
                        options=["auto", "vertical", "horizontal"],
                        format_func=lambda x: "🔄 Automática (según la forma de la imagen)" if x=="auto" else ("↕️ Vertical (Portrait)" if x=="vertical" else "↔️ Horizontal (Landscape)"),
                        key="std_orientation"
                    )
                    
                std_margin = st.selectbox(
                    "Márgenes",
                    options=[0.0, 0.5, 1.0, 1.5],
                    index=1,
                    format_func=lambda x: "Sin margen (Borde a borde)" if x==0 else f"Margen de {x} cm",
                    key="std_margin"
                )
                
                uploaded_std_files = st.file_uploader(
                    "Cargar una o varias imágenes (JPG, PNG, WEBP)",
                    type=['jpg', 'jpeg', 'png', 'webp', 'bmp'],
                    accept_multiple_files=True,
                    key="std_files_upload"
                )

            with col_s2:
                st.markdown("##### 📑 2. Compilación & Descarga")
                if uploaded_std_files:
                    st.write(f"📁 **{len(uploaded_std_files)} imagen(es) preparadas para compilar:**")
                    
                    loaded_imgs = []
                    for f in uploaded_std_files:
                        try:
                            im = Image.open(f)
                            loaded_imgs.append((f.name, im))
                        except Exception:
                            pass
                            
                    if loaded_imgs:
                        sample_name, sample_img = loaded_imgs[0]
                        s_w, s_h = sample_img.size
                        shape_sample = "Horizontal (Apaisada)" if s_w > s_h else "Vertical (Retrato)"
                        st.info(f"Página 1 detectada: **{shape_sample}** ({s_w} × {s_h} px). Si la orientación es automática, cada página se ajustará fielmente.")
                        st.image(sample_img, caption=f"Página 1: {sample_name}", use_container_width=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("📑 Convertir Todas a un Solo Documento PDF", key="btn_convert_std", use_container_width=True):
                            with st.spinner("Compilando documento PDF con orientación adaptativa..."):
                                just_images = [img for name, img in loaded_imgs]
                                pdf_data = create_standard_multipage_pdf(
                                    just_images,
                                    page_size_name=std_page_size,
                                    orientation=std_orientation,
                                    margin_cm=std_margin
                                )
                                
                                sz_kb = len(pdf_data) / 1024.0
                                sz_label = f"{sz_kb:.1f} KB" if sz_kb < 1024 else f"{(sz_kb/1024.0):.2f} MB"
                                out_name = f"Documento_{len(loaded_imgs)}_paginas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                                
                                st.session_state['generated_std_pdf'] = pdf_data
                                st.session_state['generated_std_name'] = out_name
                                st.success(f"¡PDF generado! Total de páginas: {len(loaded_imgs)} ({sz_label})")
                                
                        if 'generated_std_pdf' in st.session_state and st.session_state['generated_std_pdf']:
                            st.download_button(
                                label="📥 Descargar Documento PDF",
                                data=st.session_state['generated_std_pdf'],
                                file_name=st.session_state.get('generated_std_name', 'documento.pdf'),
                                mime="application/pdf",
                                key="dl_std_pdf_active",
                                use_container_width=True
                            )
                else:
                    st.info("Suba una o varias imágenes para unirlas y convertirlas en un PDF profesional con orientación automática.")

    # ==========================================================================
    # PESTAÑA 3: EDITOR PNG, RECORTE LIBRE & QUITAR FONDO (IA Y PINCEL MANUAL)
    # ==========================================================================
    with tab_png_editor:
        st.markdown("""
        <div class="vp-card">
            <h2 class="vp-title">Editor PNG: Recorte Libre & Eliminación de Fondo</h2>
            <p class="vp-subtitle">Recorte en cuadro de selección libre, elimine el fondo automáticamente con Inteligencia Artificial por defecto, o retoque manualmente con un pincel de grosor regulable.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_ed1, col_ed2 = st.columns([1, 1], gap="large")
        
        with col_ed1:
            st.markdown("##### 📁 1. Cargar Imagen para Editar")
            uploaded_editor_file = st.file_uploader(
                "Subir imagen para convertir a PNG transparente (JPG, PNG, WEBP, BMP)",
                type=['jpg', 'jpeg', 'png', 'webp', 'bmp'],
                key="png_editor_uploader"
            )
            
            col_ed_logo, col_ed_clr = st.columns([2, 1])
            with col_ed_logo:
                if st.button("🖼️ Cargar Logo Oficial de Prueba", key="load_logo_editor"):
                    if os.path.exists("logo.png"):
                        with open("logo.png", "rb") as f:
                            st.session_state.png_editor_bytes = f.read()
                            st.session_state.png_editor_name = "logo_vision_publicidad.png"
                            st.session_state.working_png_img = Image.open("logo.png")
                        st.success("Logo oficial cargado en el editor.")
                        st.rerun()
            with col_ed_clr:
                if st.session_state.png_editor_bytes:
                    if st.button("🗑️ Limpiar", key="clear_editor_bytes"):
                        st.session_state.png_editor_bytes = None
                        st.session_state.png_editor_name = None
                        st.session_state.working_png_img = None
                        st.rerun()

            if uploaded_editor_file is not None:
                new_bytes = uploaded_editor_file.getvalue()
                if st.session_state.png_editor_bytes != new_bytes:
                    st.session_state.png_editor_bytes = new_bytes
                    st.session_state.png_editor_name = uploaded_editor_file.name
                    st.session_state.working_png_img = Image.open(io.BytesIO(new_bytes))

        with col_ed2:
            st.markdown("##### ⚙️ 2. Flujo de Trabajo Seleccionado")
            if st.session_state.png_editor_bytes and st.session_state.working_png_img is not None:
                orig_dim_w, orig_dim_h = st.session_state.working_png_img.size
                st.markdown(f"""
                <div class="vp-stat-box" style="text-align: left; padding: 0.8rem 1.2rem;">
                    <div>🖼️ <strong>Imagen activa:</strong> {st.session_state.get('png_editor_name', 'arte.png')}</div>
                    <div>📐 <strong>Dimensiones actuales:</strong> {orig_dim_w} × {orig_dim_h} px</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Cargue una imagen en el panel izquierdo o pulse 'Cargar Logo Oficial' para activar las herramientas.")

        # SI HAY IMAGEN ACTIVA, MOSTRAR RECORTE LIBRE Y QUITAR FONDO
        if st.session_state.png_editor_bytes and st.session_state.working_png_img is not None:
            st.markdown("<hr style='margin: 1.2rem 0; opacity: 0.25;'>", unsafe_allow_html=True)
            
            tool_tab1, tool_tab2, tool_tab3 = st.tabs([
                "🔲 1. Recorte en Cuadro de Selección Libre",
                "🤖 2. Quitar Fondo Automático (IA por Defecto)",
                "🖌️ 3. Retoque Manual con Pincel (Grosor Regulable)"
            ])
            
            # ------------------------------------------------------------------
            # HERRAMIENTA 1: RECORTE EN CUADRO DE SELECCIÓN LIBRE
            # ------------------------------------------------------------------
            with tool_tab1:
                st.markdown("##### 🔲 Recorte Libre Interactivo")
                st.caption("Arrastre los bordes y esquinas con total libertad para encuadrar exactamente la zona que necesita:")
                
                col_cr_view, col_cr_res = st.columns([6, 4], gap="medium")
                with col_cr_view:
                    active_for_crop = st.session_state.working_png_img
                    try:
                        from streamlit_cropper import st_cropper
                        cropped_preview = st_cropper(
                            active_for_crop,
                            realtime_update=True,
                            box_color="#2563EB" if is_light else "#00D4FF",
                            aspect_ratio=None,
                            key="cropper_free_box"
                        )
                    except Exception:
                        cropped_preview = active_for_crop

                with col_cr_res:
                    st.markdown("###### Resultado del Recorte:")
                    if cropped_preview is not None:
                        cw, ch = cropped_preview.size
                        st.write(f"📏 Medida recortada: **{cw} × {ch} px**")
                        st.image(cropped_preview, caption="Área recortada", use_container_width=True)
                        
                        col_ap1, col_ap2 = st.columns(2)
                        with col_ap1:
                            if st.button("✂️ Aplicar Este Recorte", key="apply_crop_btn", use_container_width=True):
                                st.session_state.working_png_img = cropped_preview
                                st.success("¡Recorte libre aplicado a la imagen de trabajo!")
                                st.rerun()
                        with col_ap2:
                            if st.button("🔄 Restablecer Original", key="reset_crop_btn", use_container_width=True):
                                st.session_state.working_png_img = Image.open(io.BytesIO(st.session_state.png_editor_bytes))
                                st.info("Imagen restablecida a su versión inicial.")
                                st.rerun()

            # ------------------------------------------------------------------
            # HERRAMIENTA 2: QUITAR FONDO AUTOMÁTICO (POR DEFECTO CON IA)
            # ------------------------------------------------------------------
            with tool_tab2:
                st.markdown("##### 🤖 Eliminación Automática Inteligente de Fondo")
                st.caption("La página elimina el fondo de forma automática por defecto utilizando Inteligencia Artificial (rembg / U²-Net) o por filtro de color clave.")
                
                col_ai_cfg, col_ai_res = st.columns([1, 1], gap="large")
                
                with col_ai_cfg:
                    auto_method = st.radio(
                        "Método Automático:",
                        options=["Inteligencia Artificial (IA por defecto)", "Filtro de Color Clave (Blanco/Negro/Personalizado)"],
                        key="auto_bg_method"
                    )
                    
                    if "Color Clave" in auto_method:
                        bg_choice = st.selectbox(
                            "Color de Fondo a Eliminar",
                            options=["Blanco / Muy Claro", "Negro / Muy Oscuro", "Color Personalizado con Cuentagotas"],
                            key="key_color_preset"
                        )
                        if bg_choice == "Blanco / Muy Claro":
                            target_rgb = (255, 255, 255)
                        elif bg_choice == "Negro / Muy Oscuro":
                            target_rgb = (0, 0, 0)
                        else:
                            picked_hex = st.color_picker("Seleccione el color exacto", "#ffffff", key="custom_hex_picker")
                            h = picked_hex.lstrip('#')
                            target_rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
                            
                        tol_val = st.slider("Tolerancia / Sensibilidad del Color", 5, 120, 35, step=5, key="tol_slider_ai")
                        smooth_chk = st.checkbox("Suavizar Bordes (Anti-aliasing)", value=True, key="smooth_chk_ai")
                    else:
                        st.info("✨ **Modo IA por defecto:** Analiza los sujetos y separa personas, objetos, letreros y logos de forma limpia y transparente.")
                    
                    if st.button("⚡ Ejecutar Eliminación de Fondo", key="btn_run_auto_bg", use_container_width=True):
                        with st.spinner("Procesando transparencia y separando fondo..."):
                            curr_img = st.session_state.working_png_img
                            if "Color Clave" in auto_method:
                                transparent_result = remove_background_numpy(
                                    curr_img,
                                    target_color_rgb=target_rgb,
                                    tolerance=tol_val,
                                    feather_edges=smooth_chk
                                )
                            else:
                                transparent_result = remove_background_ai(curr_img)
                                
                            st.session_state.working_png_img = transparent_result
                            st.session_state['last_bg_removed_img'] = transparent_result
                            st.success("¡Fondo eliminado con éxito! Verifique el resultado al lado derecho.")
                            st.rerun()

                with col_ai_res:
                    st.markdown("###### Previsualización del Resultado Transparente:")
                    cur_disp = st.session_state.working_png_img
                    rw, rh = cur_disp.size
                    st.write(f"Formato: **PNG RGBA ({rw} × {rh} px)** con canal alfa activo")
                    st.image(cur_disp, caption="Resultado PNG con transparencia", use_container_width=True)
                    
                    png_buf = io.BytesIO()
                    cur_disp.save(png_buf, format='PNG')
                    dl_bytes = png_buf.getvalue()
                    
                    col_dla, col_dlb = st.columns(2)
                    with col_dla:
                        st.download_button(
                            label=f"📥 Descargar PNG ({len(dl_bytes)/1024:.1f} KB)",
                            data=dl_bytes,
                            file_name=f"{os.path.splitext(st.session_state.get('png_editor_name', 'imagen'))[0]}_transparente.png",
                            mime="image/png",
                            key="dl_auto_png_btn",
                            use_container_width=True
                        )
                    with col_dlb:
                        if st.button("➡️ Enviar a Convertidor PDF", key="send_png_to_pdf", use_container_width=True):
                            st.session_state.prepress_img_bytes = dl_bytes
                            st.session_state.prepress_img_name = f"{os.path.splitext(st.session_state.get('png_editor_name', 'arte'))[0]}_transparente.png"
                            st.info("¡Imagen transparente enviada al Convertidor de PDF! Vaya a la pestaña 'Convertidor Imagen a PDF'.")

            # ------------------------------------------------------------------
            # HERRAMIENTA 3: RETOQUE MANUAL CON PINCEL / LÁPIZ (GROSOR REGULABLE)
            # ------------------------------------------------------------------
            with tool_tab3:
                st.markdown("##### 🖌️ Estudio de Retoque Manual con Pincel (Borrador Interactivo)")
                st.markdown("""
                Pase el **pincel sobre el lienzo** para volver transparentes los detalles que desee eliminar. 
                Puede regular el **grosor del pincel o lápiz** con la barra deslizante y descargar el PNG final directamente.
                """)
                
                curr_work_img = st.session_state.working_png_img
                clean_base_name = os.path.splitext(st.session_state.get('png_editor_name', 'imagen'))[0]
                render_brush_canvas_studio(
                    curr_work_img, 
                    filename_download=f"{clean_base_name}_retoque_manual.png"
                )

    # ==========================================================================
    # PESTAÑA 4: PAPELERÍA & PROMOCIONALES
    # ==========================================================================
    with tab_papeleria:
        st.markdown("""
        <div class="vp-card">
            <h2 class="vp-title">Catálogo Oficial de Papelería & Promocionales</h2>
            <p class="vp-subtitle">Precios oficiales en Pesos Colombianos (COP). Validación de inventario y descuento automático.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_fp1, col_fp2 = st.columns([1, 1], gap="large")
        
        with col_fp1:
            st.markdown("##### 🛒 1. Generar Venta")
            client_fp = st.text_input("Nombre del Cliente", placeholder="Ej: Dr. Fernando Gómez", key="fp_client_input")
            
            product_list = st.session_state.fixed_products['producto'].tolist()
            selected_fp = st.selectbox("Seleccionar Producto", product_list, key="fp_prod_select")
            
            prod_data = st.session_state.fixed_products[
                st.session_state.fixed_products['producto'] == selected_fp
            ].iloc[0]
            
            available_stk = int(prod_data['stock'])
            
            col_q1, col_q2 = st.columns(2)
            with col_q1:
                qty_fp = st.number_input("Cantidad", min_value=1, max_value=max(1, available_stk), value=1, key="fp_qty_input")
            with col_q2:
                stock_status = "🟢 En Stock" if available_stk > 50 else ("🟡 Stock Limitado" if available_stk > 10 else "🔴 Stock Crítico")
                st.markdown(f"""
                <div class="vp-stat-box" style="margin-top: 0.2rem;">
                    <div class="vp-stat-label">{stock_status}</div>
                    <div class="vp-stat-val">{available_stk} unidades</div>
                </div>
                """, unsafe_allow_html=True)
                
            unit_price_fp = prod_data['precio']
            total_fp = unit_price_fp * qty_fp
            
            st.markdown(f"""
            <div class="vp-stat-highlight" style="margin-top: 1rem;">
                <div class="vp-stat-label">TOTAL A COBRAR ({qty_fp} UNIDAD/ES)</div>
                <div class="vp-stat-val">${total_fp:,.0f} <span class="notranslate" translate="no" style="font-size: 1.2rem;">COP</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🛒 Confirmar Venta y Descontar Stock", key="btn_sell_fp", use_container_width=True):
                if not client_fp.strip():
                    st.warning("Por favor ingrese el nombre del cliente.")
                elif qty_fp > available_stk:
                    st.error("No hay suficiente stock para completar la transacción.")
                else:
                    idx = st.session_state.fixed_products[
                        st.session_state.fixed_products['producto'] == selected_fp
                    ].index[0]
                    st.session_state.fixed_products.at[idx, 'stock'] -= qty_fp
                    
                    new_sale = pd.DataFrame([{
                        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'cliente': client_fp,
                        'tipo': 'Papelería / Fijo',
                        'producto': selected_fp,
                        'cantidad': qty_fp,
                        'subtotal': total_fp,
                        'iva': total_fp * 0.19,
                        'total': total_fp * 1.19
                    }])
                    st.session_state.sales_history = pd.concat([st.session_state.sales_history, new_sale], ignore_index=True)
                    st.success(f"¡Venta de {qty_fp}x {selected_fp} registrada exitosamente!")
                    st.rerun()

        with col_fp2:
            st.markdown("##### 📋 2. Catálogo con Precios Oficiales (COP)")
            search_query = st.text_input("🔍 Buscar artículo...", placeholder="Ej: Tarjetas, Mug, Sello, Rompetráfico...", key="fp_search")
            
            df_display = st.session_state.fixed_products.copy()
            if search_query:
                df_display = df_display[df_display['producto'].str.contains(search_query, case=False, na=False)]
                
            st.dataframe(
                df_display,
                column_config={
                    'producto': st.column_config.TextColumn("Producto / Artículo", width="large"),
                    'precio': st.column_config.NumberColumn("Precio (COP)", format="$%d"),
                    'stock': st.column_config.NumberColumn("Stock en Bodega")
                },
                use_container_width=True,
                hide_index=True
            )

    # ==========================================================================
    # PESTAÑA 5: CONTROL DE INVENTARIO
    # ==========================================================================
    with tab_inventario:
        st.markdown("""
        <div class="vp-card">
            <h2 class="vp-title">Administración de Inventario & Tarifas Oficiales</h2>
            <p class="vp-subtitle">Edite directamente las celdas para modificar tarifas mínimas, factores de fórmula o existencias.</p>
        </div>
        """, unsafe_allow_html=True)
        
        inv_sub1, inv_sub2 = st.tabs(["Materiales Gran Formato (Avisos)", "Catálogo Papelería y Promocionales"])
        
        with inv_sub1:
            st.markdown("##### Materiales Gran Formato (Medidas en cm)")
            edited_srv_df = st.data_editor(
                st.session_state.services_by_measure,
                column_config={
                    'servicio': st.column_config.TextColumn("Material / Servicio", required=True),
                    'tarifa_minima': st.column_config.NumberColumn("Tarifa Mínima Base (COP)", format="$%d", min_value=1000),
                    'factor': st.column_config.NumberColumn("Factor de Fórmula", min_value=0.1, step=1.0),
                    'stock': st.column_config.NumberColumn("Stock Disponible (m/unid.)", min_value=0)
                },
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                key="editor_srv_inventory"
            )
            
            if st.button("💾 Guardar Cambios en Gran Formato", key="save_srv_inv"):
                st.session_state.services_by_measure = edited_srv_df
                st.success("¡Tarifas y stock de servicios actualizados!")
                st.rerun()

        with inv_sub2:
            st.markdown("##### Catálogo de Productos Fijos (COP)")
            edited_fp_df = st.data_editor(
                st.session_state.fixed_products,
                column_config={
                    'producto': st.column_config.TextColumn("Nombre del Producto", required=True),
                    'precio': st.column_config.NumberColumn("Precio Unitario (COP)", format="$%d", min_value=500),
                    'stock': st.column_config.NumberColumn("Stock en Bodega", min_value=0)
                },
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                key="editor_fp_inventory"
            )
            
            if st.button("💾 Guardar Cambios en Productos Fijos", key="save_fp_inv"):
                st.session_state.fixed_products = edited_fp_df
                st.success("¡Catálogo de productos y existencias guardados!")
                st.rerun()

    # ==========================================================================
    # PESTAÑA 6: FACTURACIÓN & RECIBOS
    # ==========================================================================
    with tab_factura:
        st.markdown("""
        <div class="vp-card">
            <h2 class="vp-title">Emisión de Facturas & Recibos de Caja (COP)</h2>
            <p class="vp-subtitle">Comprobantes oficiales con consecutivo numérico, desglose de IVA y membrete oficial de VISIÓN Y PUBLICIDAD.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_fac1, col_fac2 = st.columns([1, 1], gap="large")
        
        with col_fac1:
            st.markdown("##### 👤 1. Datos del Cliente y Comprobante")
            col_rc1, col_rc2 = st.columns(2)
            with col_rc1:
                fac_client_name = st.text_input("Nombre / Razón Social", placeholder="Ej: Comercializadora Los Andes", key="fac_c_name")
            with col_rc2:
                fac_client_doc = st.text_input("NIT o Cédula", placeholder="Ej: 901.458.789-2", key="fac_c_doc")
                
            receipt_consec = st.number_input("Número Consecutivo de Recibo", value=st.session_state.receipt_counter, step=1, key="fac_consec_num")
            
            st.markdown("##### 📝 2. Detalle de Ítems")
            num_rows = st.number_input("Cantidad de Ítems a Facturar", min_value=1, max_value=8, value=2, key="fac_item_count")
            
            invoice_items = []
            for i in range(int(num_rows)):
                col_i1, col_i2, col_i3 = st.columns([3, 1, 2])
                with col_i1:
                    it_desc = st.text_input(f"Ítem {i+1} Descripción", value="Pendón con tubo y ojales 100x150 cm" if i==0 else ("Tarjetas Mate UV" if i==1 else ""), key=f"fac_it_desc_{i}")
                with col_i2:
                    it_qty = st.number_input(f"Cant. {i+1}", min_value=1, value=1 if i==0 else 1, key=f"fac_it_qty_{i}")
                with col_i3:
                    it_price = st.number_input(f"Valor Unit. {i+1} (COP)", min_value=0, value=82500 if i==0 else 150000, step=5000, key=f"fac_it_price_{i}")
                    
                if it_desc.strip():
                    invoice_items.append({
                        'descripcion': it_desc,
                        'cantidad': it_qty,
                        'unitario': it_price,
                        'subtotal': it_qty * it_price
                    })

        with col_fac2:
            st.markdown("##### 🧾 3. Resumen y Emisión")
            
            subtot_fac = sum(it['subtotal'] for it in invoice_items)
            apply_iva = st.checkbox("Aplicar IVA (19%)", value=True, key="fac_apply_iva")
            iva_fac = subtot_fac * 0.19 if apply_iva else 0.0
            total_fac = subtot_fac + iva_fac
            
            col_tot1, col_tot2 = st.columns(2)
            with col_tot1:
                st.markdown(f"""
                <div class="vp-stat-box">
                    <div class="vp-stat-label">Subtotal</div>
                    <div class="vp-stat-val">${subtot_fac:,.0f} <span class="notranslate" translate="no" style="font-size: 0.9rem;">COP</span></div>
                </div>
                """, unsafe_allow_html=True)
            with col_tot2:
                st.markdown(f"""
                <div class="vp-stat-box">
                    <div class="vp-stat-label">IVA Liquidado</div>
                    <div class="vp-stat-val">${iva_fac:,.0f} <span class="notranslate" translate="no" style="font-size: 0.9rem;">COP</span></div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown(f"""
            <div class="vp-stat-highlight" style="margin-top: 1rem;">
                <div class="vp-stat-label">TOTAL GENERAL A COBRAR</div>
                <div class="vp-stat-val">${total_fac:,.0f} <span class="notranslate" translate="no" style="font-size: 1.2rem;">COP</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📄 Emitir Recibo Oficial en PDF", key="btn_gen_receipt", use_container_width=True):
                if not fac_client_name.strip():
                    st.warning("Debe ingresar el nombre del cliente.")
                elif not invoice_items:
                    st.warning("Debe agregar al menos un ítem con descripción.")
                else:
                    try:
                        receipt_pdf_bytes = generate_receipt_pdf(
                            client_name=fac_client_name,
                            client_doc=fac_client_doc,
                            items=invoice_items,
                            subtotal=subtot_fac,
                            iva=iva_fac,
                            total=total_fac,
                            receipt_num=receipt_consec
                        )
                        
                        st.session_state.receipt_counter = receipt_consec + 1
                        
                        new_sale_entry = pd.DataFrame([{
                            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'cliente': fac_client_name,
                            'tipo': 'Factura / Recibo',
                            'producto': f"Recibo #{receipt_consec} ({len(invoice_items)} ítems)",
                            'cantidad': sum(it['cantidad'] for it in invoice_items),
                            'subtotal': subtot_fac,
                            'iva': iva_fac,
                            'total': total_fac
                        }])
                        st.session_state.sales_history = pd.concat([st.session_state.sales_history, new_sale_entry], ignore_index=True)
                        
                        st.session_state['generated_receipt_pdf'] = receipt_pdf_bytes
                        st.session_state['generated_receipt_name'] = f"Recibo_{receipt_consec}_{fac_client_name.replace(' ', '_')}.pdf"
                        st.success(f"¡Recibo #{receipt_consec} generado exitosamente!")
                        
                    except Exception as e:
                        st.error(f"Error al generar el recibo: {str(e)}")
                        
            if 'generated_receipt_pdf' in st.session_state and st.session_state['generated_receipt_pdf']:
                st.download_button(
                    label="📥 Descargar Recibo Oficial (PDF)",
                    data=st.session_state['generated_receipt_pdf'],
                    file_name=st.session_state.get('generated_receipt_name', 'recibo.pdf'),
                    mime="application/pdf",
                    key="dl_receipt_pdf_active",
                    use_container_width=True
                )

    # ==========================================================================
    # PESTAÑA 7: HISTORIAL DE VENTAS & REPORTES
    # ==========================================================================
    with tab_historial:
        st.markdown("""
        <div class="vp-card">
            <h2 class="vp-title">Historial de Operaciones & Reportes</h2>
            <p class="vp-subtitle">Auditoría contable completa en Pesos Colombianos (COP) con exportación directa a Excel/CSV.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if len(st.session_state.sales_history) > 0:
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                st.metric("Total Facturado", f"${st.session_state.sales_history['total'].sum():,.0f} COP")
            with col_m2:
                st.metric("IVA Liquidado", f"${st.session_state.sales_history['iva'].sum():,.0f} COP")
            with col_m3:
                st.metric("Transacciones", len(st.session_state.sales_history))
            with col_m4:
                avg_ticket = st.session_state.sales_history['total'].mean()
                st.metric("Ticket Promedio", f"${avg_ticket:,.0f} COP")
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            sale_types = ["Todos"] + list(st.session_state.sales_history['tipo'].unique())
            sel_type = st.selectbox("Filtrar por Categoría de Venta", sale_types, key="filter_sale_type")
            
            filtered_df = st.session_state.sales_history.copy()
            if sel_type != "Todos":
                filtered_df = filtered_df[filtered_df['tipo'] == sel_type]
                
            st.dataframe(
                filtered_df.sort_values('fecha', ascending=False),
                column_config={
                    'fecha': st.column_config.TextColumn("Fecha / Hora"),
                    'cliente': st.column_config.TextColumn("Cliente"),
                    'tipo': st.column_config.TextColumn("Categoría"),
                    'producto': st.column_config.TextColumn("Detalle"),
                    'cantidad': st.column_config.NumberColumn("Cant."),
                    'subtotal': st.column_config.NumberColumn("Subtotal (COP)", format="$%d"),
                    'iva': st.column_config.NumberColumn("IVA (COP)", format="$%d"),
                    'total': st.column_config.NumberColumn("Total (COP)", format="$%d")
                },
                use_container_width=True,
                hide_index=True
            )
            
            col_d1, col_d2 = st.columns([1, 1])
            with col_d1:
                csv_buffer = st.session_state.sales_history.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📊 Exportar Historial a CSV (Compatible con Excel)",
                    data=csv_buffer,
                    file_name=f"Reporte_Ventas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with col_d2:
                if st.button("🗑️ Limpiar Registro de la Sesión", key="clear_hist_btn", use_container_width=True):
                    st.session_state.sales_history = pd.DataFrame(columns=[
                        'fecha', 'cliente', 'tipo', 'producto', 'cantidad', 'subtotal', 'iva', 'total'
                    ])
                    st.rerun()
        else:
            st.info("Aún no hay transacciones registradas. Genere una cotización, venta o recibo para visualizar el reporte aquí.")

    # Footer oficial
    st.markdown(f"""
    <div class="vp-footer">
        <div style="display: flex; justify-content: center; align-items: center; gap: 2.5rem; flex-wrap: wrap;">
            <div><strong>VISIÓN Y PUBLICIDAD & Ingeniería Gráfica</strong></div>
            <div>PBX: (601) 320-0000 • Bogotá, Colombia</div>
            <div>Moneda: <span class="notranslate" translate="no">COP (Pesos Colombianos)</span></div>
            <div style="display: flex; align-items: center; gap: 0.45rem; color: #10b981; font-weight: 700;">
                <span style="width: 8px; height: 8px; background: #10b981; border-radius: 50%;"></span>
                Sistema de Gestión & Diseño Activo
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
