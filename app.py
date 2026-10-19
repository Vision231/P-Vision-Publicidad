import streamlit as st
import pandas as pd
import io
from PIL import Image
import fitz  # PyMuPDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

# Configuración de la página
st.set_page_config(
    page_title="Visión Publicidad - Sistema de Gestión",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejor diseño
st.markdown("""
<style>
    /* Importar fuentes modernas */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Estilos generales - Dark Theme */
    .stApp {
        background-color: #0E1117;
    }
    
    .main {
        background: linear-gradient(135deg, #0E1117 0%, #1a1d24 100%);
        font-family: 'Inter', sans-serif;
        color: #ffffff;
    }
    
    /* Header principal */
    .header-container {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(30, 58, 138, 0.4);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
    }
    
    /* Cards - Dark Theme */
    .card {
        background: linear-gradient(135deg, #1a1d24 0%, #252830 100%);
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
        transition: all 0.3s ease;
    }
    
    .card:hover {
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
        border-color: rgba(59, 130, 246, 0.3);
        transform: translateY(-2px);
    }
    
    /* Sidebar - Dark Theme */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1d24 0%, #252830 100%);
        padding: 1rem;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    [data-testid="stSidebar"] > div {
        background: transparent;
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        background: rgba(30, 58, 138, 0.2);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(59, 130, 246, 0.2);
    }
    
    /* Métricas en sidebar */
    [data-testid="stSidebar"] [data-testid="stMetric"] {
        background: rgba(30, 58, 138, 0.15);
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(59, 130, 246, 0.2);
    }
    
    [data-testid="stSidebar"] [data-testid="stMetric"] label {
        color: rgba(255, 255, 255, 0.85) !important;
        font-weight: 500;
    }
    
    [data-testid="stSidebar"] [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #3B82F6 !important;
        font-weight: 700;
    }
    
    /* Títulos */
    h1 {
        color: #ffffff;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    
    h2 {
        color: #3B82F6;
        font-weight: 700;
        letter-spacing: -0.3px;
    }
    
    h3 {
        color: #60A5FA;
        font-weight: 600;
        letter-spacing: -0.2px;
    }
    
    /* Botones */
    .stButton > button {
        background: linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
        font-size: 0.95rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
        background: linear-gradient(135deg, #60A5FA 0%, #3B82F6 100%);
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
    }
    
    /* Tabs - Dark Theme */
    [data-testid="stTabs"] [role="tablist"] {
        background: rgba(26, 29, 36, 0.8);
        border-radius: 12px;
        padding: 0.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        gap: 0.5rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%);
        color: white;
        border-radius: 8px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
    }
    
    [data-testid="stTabs"] [role="tab"][aria-selected="false"] {
        color: #94A3B8;
        font-weight: 500;
    }
    
    [data-testid="stTabs"] [role="tab"][aria-selected="false"]:hover {
        background: rgba(59, 130, 246, 0.15);
        color: #ffffff;
    }
    
    /* Info boxes - Dark Theme */
    .stAlert {
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        background: rgba(26, 29, 36, 0.9);
    }
    
    /* Dataframes - Dark Theme */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    /* Inputs - Dark Theme */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background: rgba(26, 29, 36, 0.8);
        border-radius: 8px;
        border: 2px solid rgba(255, 255, 255, 0.15);
        color: #ffffff;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #3B82F6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
        background: rgba(30, 58, 138, 0.2);
    }
    
    /* Metrics - Dark Theme */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a1d24 0%, #252830 100%);
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    [data-testid="stMetric"] label {
        color: #94A3B8;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #3B82F6;
        font-weight: 700;
        font-size: 1.8rem;
    }
    
    /* File uploader - Dark Theme */
    [data-testid="stFileUploader"] {
        border-radius: 10px;
        border: 2px dashed rgba(59, 130, 246, 0.5);
        background: rgba(30, 58, 138, 0.1);
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        border-radius: 10px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5);
    }
    
    /* Scrollbar styling - Dark Theme */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1d24;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #60A5FA 0%, #3B82F6 100%);
    }
    
    /* Text colors for dark theme */
    p, span, div {
        color: #E2E8F0;
    }
    
    /* Label colors */
    label {
        color: #94A3B8;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# =============================================
# INICIALIZACIÓN DE SESSION STATE
# =============================================
def init_session_state():
    """Inicializa todas las variables de sesión necesarias"""
    if 'services_by_measure' not in st.session_state:
        st.session_state.services_by_measure = pd.DataFrame([
            {
                'servicio': 'Pendón con tubo / hojales',
                'tarifa_minima': 20000,
                'factor': 55,
                'stock': 1000
            },
            {
                'servicio': 'Aviso con estructura sencilla',
                'tarifa_minima': 100000,
                'factor': 35,
                'stock': 500
            },
            {
                'servicio': 'Aviso Luminoso Panaflex',
                'tarifa_minima': 350000,
                'factor': 38,
                'stock': 200
            },
            {
                'servicio': 'Adhesivo Laminado',
                'tarifa_minima': 25000,
                'factor': 8,
                'stock': 800
            },
            {
                'servicio': 'Adhesivo Troquelado',
                'tarifa_minima': 35000,
                'factor': 6,
                'stock': 600
            }
        ])
    
    if 'fixed_products' not in st.session_state:
        st.session_state.fixed_products = pd.DataFrame([
            {'producto': 'Tarjetas Mate UV (1.000 un)', 'precio': 150000, 'stock': 500},
            {'producto': 'Tarjetas Brillantes Full Color (1.000 un)', 'precio': 100000, 'stock': 500},
            {'producto': 'Factureros Original y 1 Copia (10 talonarios / 50 fec. c/u)', 'precio': 150000, 'stock': 200},
            {'producto': 'Volantes 1/2 Carta (1.000 un)', 'precio': 150000, 'stock': 1000},
            {'producto': 'Volantes 1/4 Carta (2.000 un)', 'precio': 150000, 'stock': 1000},
            {'producto': 'Letrero Luminoso Redondo en Panaflex (80x80 cm)', 'precio': 500000, 'stock': 50},
            {'producto': 'Rompetrafico 100x70 cm', 'precio': 150000, 'stock': 300},
            {'producto': 'Rompetrafico 80x120 cm', 'precio': 200000, 'stock': 300},
            {'producto': 'Sticker Redondos Adhesivo 5x5 cm (400 un)', 'precio': 60000, 'stock': 400},
            {'producto': 'Mug Fondo Color', 'precio': 25000, 'stock': 200},
            {'producto': 'Mug Blanco', 'precio': 20000, 'stock': 200},
            {'producto': 'Batilo', 'precio': 25000, 'stock': 150},
            {'producto': 'Cervezero', 'precio': 35000, 'stock': 150},
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
    
    if 'generated_pdfs' not in st.session_state:
        st.session_state.generated_pdfs = {}

# Ejecutar inicialización
init_session_state()

# =============================================
# FUNCIONES AUXILIARES
# =============================================
def format_currency(value):
    """Formatea un valor numérico como moneda COP"""
    return f"${value:,.0f} COP"

def calculate_price(width_cm, height_cm, quantity, tariff_min, factor):
    """
    Calcula el precio según la fórmula:
    Precio = MAX(Largo * Ancho * (Factor / 100), Tarifa_Minima) * Cantidad
    """
    area_price = width_cm * height_cm * (factor / 100)
    unit_price = max(area_price, tariff_min)
    total_price = unit_price * quantity
    return unit_price, total_price

def resize_image_to_cm(image_pil, width_cm, height_cm, dpi=150):
    """
    Redimensiona una imagen PIL a las dimensiones especificadas en cm
    a una resolución DPI dada.
    """
    # Convertir cm a píxeles
    width_px = int((width_cm * dpi) / 2.54)
    height_px = int((height_cm * dpi) / 2.54)
    
    # Redimensionar manteniendo la mejor calidad
    resized_image = image_pil.resize((width_px, height_px), Image.Resampling.LANCZOS)
    return resized_image

def create_pdf_with_crop_marks(image_pil, width_cm, height_cm, bleed_cm=0.5):
    """
    Crea un PDF con la imagen, sangría (bleed) y marcas de corte vectoriales.
    """
    # Calcular dimensiones en puntos (1 punto = 1/72 pulgada)
    dpi = 150
    width_px = int((width_cm * dpi) / 2.54)
    height_px = int((height_cm * dpi) / 2.54)
    bleed_px = int((bleed_cm * dpi) / 2.54)
    
    # Dimensiones totales con sangría
    total_width_px = width_px + (2 * bleed_px)
    total_height_px = height_px + (2 * bleed_px)
    
    # Convertir a puntos para PyMuPDF
    width_pt = total_width_px * 72 / dpi
    height_pt = total_height_px * 72 / dpi
    
    # Crear documento PDF
    doc = fitz.open()
    page = doc.new_page(width=width_pt, height=height_pt)
    
    # Crear imagen con fondo blanco y sangría
    img_with_bleed = Image.new('RGB', (total_width_px, total_height_px), 'white')
    
    # Pegar la imagen original en el centro (con sangría)
    paste_x = bleed_px
    paste_y = bleed_px
    img_with_bleed.paste(image_pil, (paste_x, paste_y))
    
    # Convertir a bytes para insertar en PDF
    img_bytes = io.BytesIO()
    img_with_bleed.save(img_bytes, format='PNG', dpi=(dpi, dpi))
    img_bytes.seek(0)
    
    # Insertar imagen en el PDF
    rect = fitz.Rect(0, 0, width_pt, height_pt)
    page.insert_image(rect, stream=img_bytes.read())
    
    # Dibujar marcas de corte (esquinas)
    mark_length_pt = 10  # Longitud de la marca de corte en puntos
    line_width = 0.5  # Grosor de la línea
    
    # Coordenadas de las esquinas del área de corte (sin sangría)
    crop_x1 = bleed_px * 72 / dpi
    crop_y1 = bleed_px * 72 / dpi
    crop_x2 = width_pt - crop_x1
    crop_y2 = height_pt - crop_y1
    
    # Dibujar marcas en las 4 esquinas
    # Esquina superior izquierda
    page.draw_line(
        fitz.Point(crop_x1 - mark_length_pt, crop_y1),
        fitz.Point(crop_x1 + mark_length_pt, crop_y1),
        color=(0, 0, 0),
        width=line_width
    )
    page.draw_line(
        fitz.Point(crop_x1, crop_y1 - mark_length_pt),
        fitz.Point(crop_x1, crop_y1 + mark_length_pt),
        color=(0, 0, 0),
        width=line_width
    )
    
    # Esquina superior derecha
    page.draw_line(
        fitz.Point(crop_x2 - mark_length_pt, crop_y1),
        fitz.Point(crop_x2 + mark_length_pt, crop_y1),
        color=(0, 0, 0),
        width=line_width
    )
    page.draw_line(
        fitz.Point(crop_x2, crop_y1 - mark_length_pt),
        fitz.Point(crop_x2, crop_y1 + mark_length_pt),
        color=(0, 0, 0),
        width=line_width
    )
    
    # Esquina inferior izquierda
    page.draw_line(
        fitz.Point(crop_x1 - mark_length_pt, crop_y2),
        fitz.Point(crop_x1 + mark_length_pt, crop_y2),
        color=(0, 0, 0),
        width=line_width
    )
    page.draw_line(
        fitz.Point(crop_x1, crop_y2 - mark_length_pt),
        fitz.Point(crop_x1, crop_y2 + mark_length_pt),
        color=(0, 0, 0),
        width=line_width
    )
    
    # Esquina inferior derecha
    page.draw_line(
        fitz.Point(crop_x2 - mark_length_pt, crop_y2),
        fitz.Point(crop_x2 + mark_length_pt, crop_y2),
        color=(0, 0, 0),
        width=line_width
    )
    page.draw_line(
        fitz.Point(crop_x2, crop_y2 - mark_length_pt),
        fitz.Point(crop_x2, crop_y2 + mark_length_pt),
        color=(0, 0, 0),
        width=line_width
    )
    
    # Guardar PDF en memoria
    pdf_bytes = io.BytesIO()
    doc.save(pdf_bytes)
    pdf_bytes.seek(0)
    
    return pdf_bytes

def generate_receipt_pdf(client_name, items, subtotal, iva, total):
    """
    Genera un PDF de recibo/factura con ReportLab.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Configuración de colores
    header_color = colors.HexColor('#1E3A8A')  # Dark blue
    line_color = colors.HexColor('#3B82F6')  # Light blue
    
    # Dibujar encabezado
    c.setFillColor(header_color)
    c.rect(0, height - 100, width, 100, fill=True, stroke=False)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 60, "VISIÓN PUBLICIDAD")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 85, "Sistema de Gestión Operativa")
    
    # Información del recibo
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 140, "RECIBO / FACTURA")
    
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 160, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    c.drawString(50, height - 180, f"Cliente: {client_name}")
    
    # Línea separadora
    c.setStrokeColor(line_color)
    c.setLineWidth(2)
    c.line(50, height - 200, width - 50, height - 200)
    
    # Encabezados de tabla
    y_position = height - 230
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y_position, "Descripción")
    c.drawString(300, y_position, "Cantidad")
    c.drawString(400, y_position, "Unitario")
    c.drawString(500, y_position, "Subtotal")
    
    # Línea debajo de encabezados
    c.setLineWidth(1)
    c.line(50, y_position - 10, width - 50, y_position - 10)
    
    # Items
    y_position -= 40
    c.setFont("Helvetica", 10)
    
    for item in items:
        descripcion = item['descripcion']
        cantidad = item['cantidad']
        unitario = item['unitario']
        item_subtotal = item['subtotal']
        
        c.drawString(50, y_position, descripcion[:40])  # Truncar si es muy largo
        c.drawString(300, y_position, str(cantidad))
        c.drawString(400, y_position, format_currency(unitario))
        c.drawString(500, y_position, format_currency(item_subtotal))
        
        y_position -= 25
    
    # Línea antes de totales
    y_position -= 10
    c.line(50, y_position, width - 50, y_position)
    
    # Totales
    y_position -= 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, y_position, "Subtotal:")
    c.drawString(500, y_position, format_currency(subtotal))
    
    y_position -= 25
    c.drawString(400, y_position, "IVA (19%):")
    c.drawString(500, y_position, format_currency(iva))
    
    y_position -= 25
    c.setFillColor(header_color)
    c.drawString(400, y_position, "TOTAL:")
    c.drawString(500, y_position, format_currency(total))
    
    # Pie de página
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 9)
    c.drawString(50, 50, "Gracias por su preferencia")
    c.drawString(50, 35, "Visión Publicidad - Todos los derechos reservados")
    
    c.save()
    buffer.seek(0)
    return buffer

# =============================================
# INTERFAZ PRINCIPAL
# =============================================
def main():
    # Header principal
    st.markdown("""
    <div class="header-container">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 800; letter-spacing: -1px;">🎨 VISION PUBLICIDAD</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.1rem; font-weight: 500;">Sistema de Gestión Operativa</p>
            </div>
            <div style="text-align: right;">
                <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 8px; font-size: 0.9rem; font-weight: 600;">🔧 Administrador</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar con información
    with st.sidebar:
        st.markdown("### 📊 Panel de Control")
        st.markdown("---")
        
        # Métricas principales
        total_products = st.session_state.fixed_products['stock'].sum()
        total_services = st.session_state.services_by_measure['stock'].sum()
        total_sales = st.session_state.sales_history['total'].sum() if len(st.session_state.sales_history) > 0 else 0
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.metric("📦 Productos", len(st.session_state.fixed_products))
        with col_s2:
            st.metric("🔧 Servicios", len(st.session_state.services_by_measure))
        
        st.metric("📊 Stock Total", f"{total_products:,} un")
        st.metric("💰 Ventas Totales", format_currency(total_sales))
        st.metric("🧾 Transacciones", len(st.session_state.sales_history))
        
        st.markdown("---")
        st.markdown("### ⏰ Fecha y Hora")
        st.markdown(f"📅 **{datetime.now().strftime('%d/%m/%Y')}**")
        st.markdown(f"🕐 **{datetime.now().strftime('%H:%M:%S')}**")
        
        st.markdown("---")
        st.markdown("### 📞 Visión Publicidad")
        st.markdown("Sistema de Gestión Operativa")
        st.caption("v2.4.1 - Professional Edition")
    
    # Pestañas principales
    tab1, tab2, tab3, tab4 = st.tabs([
        "📐 Cotizador Gran Formato",
        "📦 Papelería Comercial",
        "📋 Control de Inventario",
        "🧾 Facturación"
    ])
    
    # =============================================
    # PESTAÑA 1: COTIZADOR GRAN FORMATO Y PREPRENTA
    # =============================================
    with tab1:
        st.markdown("""
        <div class="card">
            <h2>📐 Cotizador Gran Formato y Preprensa (FPP)</h2>
            <p>Cotice y genere archivos PDF listos para impresión con marcas de corte vectoriales.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            <div class="card">
                <h3>📝 Datos del Cliente y Servicio</h3>
            </div>
            """, unsafe_allow_html=True)
            
            client_name = st.text_input("Nombre del Cliente", key="gf_client")
            
            service_options = st.session_state.services_by_measure['servicio'].tolist()
            selected_service = st.selectbox("Seleccione el Servicio", service_options, key="gf_service")
            
            # Obtener datos del servicio seleccionado
            service_data = st.session_state.services_by_measure[
                st.session_state.services_by_measure['servicio'] == selected_service
            ].iloc[0]
            
            col_a, col_b = st.columns(2)
            with col_a:
                width_cm = st.number_input("Ancho (cm)", min_value=1.0, value=100.0, step=0.1, key="gf_width")
            with col_b:
                height_cm = st.number_input("Largo (cm)", min_value=1.0, value=100.0, step=0.1, key="gf_height")
            
            quantity = st.number_input("Cantidad", min_value=1, value=1, key="gf_quantity")
            
            # Cálculo automático
            unit_price, total_price = calculate_price(
                width_cm, height_cm, quantity,
                service_data['tarifa_minima'],
                service_data['factor']
            )
            
            st.markdown("""
            <div class="card">
                <h3>💰 Cotización</h3>
            </div>
            """, unsafe_allow_html=True)
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.metric("Precio Unitario", format_currency(unit_price))
            with col_p2:
                st.metric("Precio Total", format_currency(total_price))
            
            st.info(f"📌 Fórmula aplicada: MAX({width_cm} × {height_cm} × {service_data['factor']/100}, {format_currency(service_data['tarifa_minima'])}) × {quantity}")
        
        with col2:
            st.markdown("""
            <div class="card">
                <h3>🖼️ Carga de Imagen y Generación PDF</h3>
            </div>
            """, unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Cargue la imagen (JPG/PNG)",
                type=['jpg', 'jpeg', 'png'],
                key="gf_image"
            )
            
            if uploaded_file is not None:
                try:
                    # Leer imagen
                    image_pil = Image.open(uploaded_file)
                    
                    # Mostrar información de la imagen
                    st.success(f"Imagen cargada: {image_pil.size[0]}x{image_pil.size[1]} píxeles")
                    
                    # Vista previa
                    st.image(image_pil, caption="Vista previa de la imagen", use_column_width=True)
                    
                    # Botón para generar PDF
                    if st.button("🚀 Generar PDF con Marcas de Corte", key="gf_generate"):
                        with st.spinner("Procesando imagen y generando PDF..."):
                            try:
                                # Redimensionar imagen
                                resized_image = resize_image_to_cm(image_pil, width_cm, height_cm, dpi=150)
                                
                                # Crear PDF con marcas de corte
                                pdf_bytes = create_pdf_with_crop_marks(resized_image, width_cm, height_cm, bleed_cm=0.5)
                                
                                # Guardar en session state para descarga
                                pdf_filename = f"FPP_{selected_service}_{client_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                                st.session_state.generated_pdfs[pdf_filename] = pdf_bytes
                                
                                # Descuento de inventario
                                idx = st.session_state.services_by_measure[
                                    st.session_state.services_by_measure['servicio'] == selected_service
                                ].index[0]
                                st.session_state.services_by_measure.at[idx, 'stock'] -= quantity
                                
                                # Registrar en historial de ventas
                                new_sale = pd.DataFrame([{
                                    'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    'cliente': client_name,
                                    'tipo': 'Gran Formato',
                                    'producto': f"{selected_service} ({width_cm}x{height_cm}cm)",
                                    'cantidad': quantity,
                                    'subtotal': total_price,
                                    'iva': total_price * 0.19,
                                    'total': total_price * 1.19
                                }])
                                st.session_state.sales_history = pd.concat([
                                    st.session_state.sales_history, new_sale
                                ], ignore_index=True)
                                
                                st.success("✅ PDF generado exitosamente e inventario actualizado!")
                                st.download_button(
                                    label="📥 Descargar PDF FPP",
                                    data=pdf_bytes.getvalue(),
                                    file_name=pdf_filename,
                                    mime="application/pdf"
                                )
                                
                            except Exception as e:
                                st.error(f"Error al generar PDF: {str(e)}")
                
                except Exception as e:
                    st.error(f"Error al procesar la imagen: {str(e)}")
            else:
                st.warning("⚠️ Por favor cargue una imagen para generar el PDF.")
    
    # =============================================
    # PESTAÑA 2: PRODUCTOS FIJOS Y PAPELERÍA
    # =============================================
    with tab2:
        st.markdown("""
        <div class="card">
            <h2>📦 Productos Fijos y Papelería</h2>
            <p>Venta de productos de papelería, avisos fijos y artículos promocionales.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            <div class="card">
                <h3>🛒 Selección de Producto</h3>
            </div>
            """, unsafe_allow_html=True)
            
            product_options = st.session_state.fixed_products['producto'].tolist()
            selected_product = st.selectbox("Seleccione el Producto", product_options, key="fp_product")
            
            # Obtener datos del producto
            product_data = st.session_state.fixed_products[
                st.session_state.fixed_products['producto'] == selected_product
            ].iloc[0]
            
            quantity_fp = st.number_input("Cantidad", min_value=1, value=1, key="fp_quantity")
            
            # Verificar stock disponible
            available_stock = product_data['stock']
            if quantity_fp > available_stock:
                st.warning(f"⚠️ Solo hay {available_stock} unidades disponibles.")
            
            # Cálculo del total
            total_fp = product_data['precio'] * quantity_fp
            
            st.markdown("""
            <div class="card">
                <h3>💰 Resumen de Compra</h3>
            </div>
            """, unsafe_allow_html=True)
            st.metric("Precio Unitario", format_currency(product_data['precio']))
            st.metric("Total a Cobrar", format_currency(total_fp))
            st.metric("Stock Disponible", available_stock)
            
            client_name_fp = st.text_input("Nombre del Cliente", key="fp_client")
            
            if st.button("🛍️ Vender y Descontar", key="fp_sell"):
                if quantity_fp <= available_stock:
                    # Actualizar inventario
                    idx = st.session_state.fixed_products[
                        st.session_state.fixed_products['producto'] == selected_product
                    ].index[0]
                    st.session_state.fixed_products.at[idx, 'stock'] -= quantity_fp
                    
                    # Registrar en historial
                    new_sale = pd.DataFrame([{
                        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'cliente': client_name_fp,
                        'tipo': 'Producto Fijo',
                        'producto': selected_product,
                        'cantidad': quantity_fp,
                        'subtotal': total_fp,
                        'iva': total_fp * 0.19,
                        'total': total_fp * 1.19
                    }])
                    st.session_state.sales_history = pd.concat([
                        st.session_state.sales_history, new_sale
                    ], ignore_index=True)
                    
                    st.success(f"✅ Venta registrada! {quantity_fp} unidades descontadas del inventario.")
                    st.rerun()
                else:
                    st.error("❌ Stock insuficiente para completar la venta.")
        
        with col2:
            st.markdown("""
            <div class="card">
                <h3>📋 Catálogo de Productos</h3>
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(
                st.session_state.fixed_products[['producto', 'precio', 'stock']],
                use_container_width=True,
                hide_index=True
            )
    
    # =============================================
    # PESTAÑA 3: CONTROL DE INVENTARIO
    # =============================================
    with tab3:
        st.markdown("""
        <div class="card">
            <h2>📋 Control de Inventario</h2>
            <p>Gestión de existencias de servicios por medida y productos fijos.</p>
        </div>
        """, unsafe_allow_html=True)
        
        subtab1, subtab2 = st.tabs(["Servicios por Medida", "Productos Fijos"])
        
        with subtab1:
            st.markdown("""
            <div class="card">
                <h3>🔧 Servicios por Medida y Gran Formato</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Editar dataframe
            edited_services = st.data_editor(
                st.session_state.services_by_measure,
                column_config={
                    'servicio': st.column_config.TextColumn("Servicio", disabled=True),
                    'tarifa_minima': st.column_config.NumberColumn("Tarifa Mínima (COP)", format="$%d"),
                    'factor': st.column_config.NumberColumn("Factor Fórmula"),
                    'stock': st.column_config.NumberColumn("Stock Disponible")
                },
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                key="edit_services"
            )
            
            if st.button("💾 Guardar Cambios en Servicios", key="save_services"):
                st.session_state.services_by_measure = edited_services
                st.success("✅ Cambios guardados exitosamente!")
                st.rerun()
        
        with subtab2:
            st.markdown("""
            <div class="card">
                <h3>📦 Productos Fijos y Papelería</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Editar dataframe
            edited_products = st.data_editor(
                st.session_state.fixed_products,
                column_config={
                    'producto': st.column_config.TextColumn("Producto", disabled=True),
                    'precio': st.column_config.NumberColumn("Precio (COP)", format="$%d"),
                    'stock': st.column_config.NumberColumn("Stock Disponible")
                },
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                key="edit_products"
            )
            
            if st.button("💾 Guardar Cambios en Productos", key="save_products"):
                st.session_state.fixed_products = edited_products
                st.success("✅ Cambios guardados exitosamente!")
                st.rerun()
    
    # =============================================
    # PESTAÑA 4: GENERACIÓN DE RECIBO/FACTURA
    # =============================================
    with tab4:
        st.markdown("""
        <div class="card">
            <h2>🧾 Generación de Recibo / Factura</h2>
            <p>Emisión de recibos y facturas con membrete oficial.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            <div class="card">
                <h3>📝 Datos del Recibo</h3>
            </div>
            """, unsafe_allow_html=True)
            
            receipt_client = st.text_input("Nombre del Cliente", key="receipt_client")
            
            st.markdown("""
            <div class="card">
                <h3>📋 Items del Recibo</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Número de items
            num_items = st.number_input("Cantidad de Items", min_value=1, max_value=10, value=1, key="num_items")
            
            receipt_items = []
            
            for i in range(num_items):
                st.markdown(f"**Item {i + 1}**")
                col_item1, col_item2, col_item3 = st.columns(3)
                
                with col_item1:
                    item_desc = st.text_input("Descripción", key=f"item_desc_{i}")
                with col_item2:
                    item_qty = st.number_input("Cantidad", min_value=1, value=1, key=f"item_qty_{i}")
                with col_item3:
                    item_price = st.number_input("Precio Unitario", min_value=0, value=0, step=1000, key=f"item_price_{i}")
                
                item_subtotal = item_qty * item_price
                receipt_items.append({
                    'descripcion': item_desc,
                    'cantidad': item_qty,
                    'unitario': item_price,
                    'subtotal': item_subtotal
                })
            
            # Calcular totales
            subtotal = sum(item['subtotal'] for item in receipt_items)
            iva = subtotal * 0.19
            total = subtotal + iva
            
            st.markdown("""
            <div class="card">
                <h3>💰 Totales</h3>
            </div>
            """, unsafe_allow_html=True)
            col_t1, col_t2, col_t3 = st.columns(3)
            with col_t1:
                st.metric("Subtotal", format_currency(subtotal))
            with col_t2:
                st.metric("IVA (19%)", format_currency(iva))
            with col_t3:
                st.metric("Total", format_currency(total))
            
            if st.button("🧾 Generar Recibo PDF", key="generate_receipt"):
                if receipt_client and any(item['descripcion'] for item in receipt_items):
                    try:
                        pdf_buffer = generate_receipt_pdf(receipt_client, receipt_items, subtotal, iva, total)
                        
                        st.success("✅ Recibo generado exitosamente!")
                        st.download_button(
                            label="📥 Descargar Recibo PDF",
                            data=pdf_buffer.getvalue(),
                            file_name=f"Recibo_{receipt_client}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"Error al generar recibo: {str(e)}")
                else:
                    st.warning("⚠️ Por favor complete el nombre del cliente y al menos un item.")
    
    # Footer
    st.markdown("""
    <div style="margin-top: 3rem; padding: 1.5rem; border-top: 1px solid rgba(255,255,255,0.1); text-align: center;">
        <p style="color: #64748b; margin: 0; font-size: 0.85rem;">v2.4.1 | © 2016 VISION PUBLICIDAD e Ingeniería</p>
        <p style="color: #10B981; margin: 0.5rem 0 0 0; font-size: 0.8rem;">● Estado de red activo</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
