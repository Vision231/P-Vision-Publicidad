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

# CSS personalizado para estilo Glassmorphism
st.markdown("""
<style>
    /* Importar fuentes modernas */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Variables CSS para tema Glassmorphism */
    :root {
        --glass-bg: rgba(255, 255, 255, 0.05);
        --glass-border: rgba(255, 255, 255, 0.1);
        --glass-shadow: rgba(0, 0, 0, 0.3);
        --neon-blue: #00d4ff;
        --neon-purple: #9d4edd;
        --neon-cyan: #00ff88;
        --dark-bg: #0a0a0f;
        --dark-surface: #12121a;
    }
    
    /* Fondo principal con degradado */
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%);
        min-height: 100vh;
    }
    
    .main {
        background: transparent;
        font-family: 'Inter', sans-serif;
        color: #ffffff;
    }
    
    /* Header con Glassmorphism */
    .header-container {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 2rem 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    
    /* Tarjetas Glassmorphism */
    .card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.03) 100%);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Sidebar Glassmorphism */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 2rem;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Métricas en sidebar con efecto neón */
    [data-testid="stSidebar"] [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(157, 78, 221, 0.1) 100%);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(0, 212, 255, 0.2);
        box-shadow: 0 4px 16px rgba(0, 212, 255, 0.1);
    }
    
    [data-testid="stSidebar"] [data-testid="stMetric"] label {
        color: rgba(255, 255, 255, 0.7) !important;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    [data-testid="stSidebar"] [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #00d4ff !important;
        font-weight: 700;
        font-size: 1.5rem;
    }
    
    /* Títulos con degradado neón */
    h1 {
        color: rgba(255, 255, 255, 0.95);
        font-weight: 800;
        background: linear-gradient(135deg, #00d4ff 0%, #9d4edd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    h2 {
        color: rgba(255, 255, 255, 0.9);
        font-weight: 700;
    }
    
    h3 {
        color: rgba(255, 255, 255, 0.85);
        font-weight: 600;
    }
    
    /* Botones con degradado neón */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff 0%, #9d4edd 100%);
        color: white;
        border-radius: 12px;
        padding: 0.875rem 2rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 16px rgba(0, 212, 255, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(0, 212, 255, 0.5);
    }
    
    /* Tabs con Glassmorphism */
    [data-testid="stTabs"] [role="tablist"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%);
        backdrop-filter: blur(15px);
        border-radius: 16px;
        padding: 0.75rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #00d4ff 0%, #9d4edd 100%);
        color: white;
        border-radius: 10px;
        font-weight: 600;
    }
    
    [data-testid="stTabs"] [role="tab"][aria-selected="false"] {
        color: rgba(255, 255, 255, 0.6);
    }
    
    /* Inputs con Glassmorphism */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stSelectbox > div > div > div {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(157, 78, 221, 0.1) 100%) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 212, 255, 0.3) !important;
        border-radius: 12px !important;
        color: rgba(255, 255, 255, 0.9) !important;
        padding: 0.875rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #00d4ff !important;
        box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.2);
        outline: none;
    }
    
    /* Selectbox container */
    .stSelectbox > div {
        background: transparent !important;
    }
    
    /* Text input container */
    .stTextInput > div {
        background: transparent !important;
    }
    
    /* Number input container */
    .stNumberInput > div {
        background: transparent !important;
    }
    
    /* File uploader con efecto neón */
    [data-testid="stFileUploader"] {
        border: 2px dashed rgba(0, 212, 255, 0.5) !important;
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(157, 78, 221, 0.1) 100%) !important;
        backdrop-filter: blur(10px);
        border-radius: 16px !important;
    }
    
    [data-testid="stFileUploader"] > div {
        background: transparent !important;
    }
    
    /* Input containers específicos */
    [data-testid="stTextInput"] > div > div {
        background: transparent !important;
    }
    
    [data-testid="stNumberInput"] > div > div {
        background: transparent !important;
    }
    
    [data-testid="stSelectbox"] > div > div {
        background: transparent !important;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #00ff88 0%, #00d4ff 100%);
        color: white;
        border-radius: 12px;
        font-weight: 600;
        box-shadow: 0 4px 16px rgba(0, 255, 136, 0.3);
    }
    
    /* Texto general */
    p, span, div {
        color: rgba(255, 255, 255, 0.85);
    }
    
    p, span {
        color: rgba(255, 255, 255, 0.85);
    }
    
    label {
        color: rgba(255, 255, 255, 0.7);
        font-weight: 500;
    }
    
    /* Eliminar fondos blancos de elementos Streamlit */
    .stMarkdown, .stText, .stWrite {
        background: transparent !important;
    }
    
    /* Ajustar colores de información */
    .stAlert {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(157, 78, 221, 0.15) 100%) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 12px;
    }
    
    .stSuccess {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.15) 0%, rgba(0, 212, 255, 0.15) 100%) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 255, 136, 0.3);
        border-radius: 12px;
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(255, 193, 7, 0.15) 0%, rgba(255, 152, 0, 0.15) 100%) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 193, 7, 0.3);
        border-radius: 12px;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(244, 67, 54, 0.15) 0%, rgba(233, 30, 99, 0.15) 100%) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(244, 67, 54, 0.3);
        border-radius: 12px;
    }
    
    /* Métricas principales */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(157, 78, 221, 0.1) 100%);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(0, 212, 255, 0.2);
        box-shadow: 0 4px 16px rgba(0, 212, 255, 0.1);
    }
    
    [data-testid="stMetric"] label {
        color: rgba(255, 255, 255, 0.7);
        font-weight: 600;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #00d4ff;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# =============================================
# INICIALIZACIÓN DE SESSION STATE
# =============================================
def init_session_state():
    """Inicializa todas las variables de sesión necesarias"""
    if 'theme_mode' not in st.session_state:
        st.session_state.theme_mode = 'dark'
    
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
    
    # Leer los bytes de la imagen
    img_data = img_bytes.read()
    
    # Insertar imagen en el PDF
    rect = fitz.Rect(0, 0, width_pt, height_pt)
    page.insert_image(rect, stream=img_data)
    
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
    
    # Leer los bytes para retorno
    pdf_data = pdf_bytes.getvalue()
    
    # Crear nuevo BytesIO con los datos
    result = io.BytesIO(pdf_data)
    result.seek(0)
    
    return result

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
    # Aplicar CSS según el tema (Glassmorphism para ambos temas) - ANTES de cualquier elemento
    if st.session_state.theme_mode == "dark":
        # CSS Dark Theme con Glassmorphism
        st.markdown("""
        <style>
            [data-testid="stAppViewBlockContainer"] {
                background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%);
                min-height: 100vh;
            }
            [data-testid="stSidebar"] {
                background: linear-gradient(135deg, rgba(10, 10, 15, 0.95) 0%, rgba(26, 26, 46, 0.95) 100%);
                backdrop-filter: blur(20px);
                border-right: 1px solid rgba(0, 212, 255, 0.2);
            }
            .header-container {
                background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(157, 78, 221, 0.15) 100%);
                backdrop-filter: blur(15px);
                border-radius: 20px;
                padding: 1.5rem 2rem;
                border: 1px solid rgba(0, 212, 255, 0.3);
                box-shadow: 0 8px 32px rgba(0, 212, 255, 0.2);
                margin-bottom: 2rem;
            }
            .card {
                background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 1.5rem;
                border: 1px solid rgba(255, 255, 255, 0.08);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                margin-bottom: 1.5rem;
            }
            [data-testid="stTabs"] [role="tablist"] {
                background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(157, 78, 221, 0.15) 100%);
                backdrop-filter: blur(15px);
                border-radius: 16px;
                padding: 0.75rem;
                border: 1px solid rgba(0, 212, 255, 0.3);
            }
            [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
                background: linear-gradient(135deg, #00d4ff 0%, #9d4edd 100%);
                color: white;
                border-radius: 10px;
                font-weight: 600;
            }
            [data-testid="stTabs"] [role="tab"][aria-selected="false"] {
                color: rgba(255, 255, 255, 0.6);
            }
            [data-testid="stSidebar"] [data-testid="stMetric"] {
                background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(157, 78, 221, 0.1) 100%);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 1.5rem;
                border: 1px solid rgba(0, 212, 255, 0.2);
                box-shadow: 0 4px 16px rgba(0, 212, 255, 0.1);
            }
            [data-testid="stSidebar"] [data-testid="stMetric"] label {
                color: rgba(255, 255, 255, 0.7);
                font-weight: 600;
                font-size: 0.85rem;
            }
            [data-testid="stSidebar"] [data-testid="stMetric"] [data-testid="stMetricValue"] {
                color: #00d4ff !important;
                font-weight: 700;
                font-size: 1.5rem;
            }
            h1 {
                color: rgba(255, 255, 255, 0.95);
                font-weight: 800;
                background: linear-gradient(135deg, #00d4ff 0%, #9d4edd 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            h2 {
                color: rgba(255, 255, 255, 0.9);
                font-weight: 700;
            }
            h3 {
                color: rgba(255, 255, 255, 0.85);
                font-weight: 600;
            }
            .stButton > button {
                background: linear-gradient(135deg, #00d4ff 0%, #9d4edd 100%);
                color: white;
                border-radius: 12px;
                padding: 0.875rem 2rem;
                font-weight: 600;
                border: none;
                box-shadow: 0 4px 16px rgba(0, 212, 255, 0.3);
                transition: all 0.3s ease;
            }
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0, 212, 255, 0.4);
            }
            .stTextInput > div > div > input,
            .stNumberInput > div > div > input,
            .stSelectbox > div > div > select,
            .stSelectbox > div > div > div {
                background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(157, 78, 221, 0.1) 100%) !important;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(0, 212, 255, 0.3) !important;
                border-radius: 12px !important;
                color: rgba(255, 255, 255, 0.9) !important;
                padding: 0.875rem 1rem;
                font-weight: 500;
                transition: all 0.3s ease;
            }
            .stTextInput > div > div > input:focus,
            .stNumberInput > div > div > input:focus,
            .stSelectbox > div > div > select:focus {
                border-color: #00d4ff !important;
                box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.2);
                outline: none;
            }
            .stSelectbox > div {
                background: transparent !important;
            }
            .stTextInput > div {
                background: transparent !important;
            }
            .stNumberInput > div {
                background: transparent !important;
            }
            [data-testid="stFileUploader"] {
                border: 2px dashed rgba(0, 212, 255, 0.5) !important;
                background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(157, 78, 221, 0.1) 100%) !important;
                backdrop-filter: blur(10px);
                border-radius: 16px !important;
            }
            [data-testid="stFileUploader"] > div {
                background: transparent !important;
            }
            [data-testid="stTextInput"] > div > div {
                background: transparent !important;
            }
            [data-testid="stNumberInput"] > div > div {
                background: transparent !important;
            }
            [data-testid="stSelectbox"] > div > div {
                background: transparent !important;
            }
            .stDownloadButton > button {
                background: linear-gradient(135deg, #00ff88 0%, #00d4ff 100%);
                color: white;
                border-radius: 12px;
                font-weight: 600;
                box-shadow: 0 4px 16px rgba(0, 255, 136, 0.3);
            }
            p, span, div {
                color: rgba(255, 255, 255, 0.85);
            }
            p, span {
                color: rgba(255, 255, 255, 0.85);
            }
            label {
                color: rgba(255, 255, 255, 0.7);
                font-weight: 500;
            }
            .stMarkdown, .stText, .stWrite {
                background: transparent !important;
            }
            .stAlert {
                background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(157, 78, 221, 0.15) 100%) !important;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(0, 212, 255, 0.3);
                border-radius: 12px;
            }
            .stSuccess {
                background: linear-gradient(135deg, rgba(0, 255, 136, 0.15) 0%, rgba(0, 212, 255, 0.15) 100%) !important;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 12px;
            }
            .stWarning {
                background: linear-gradient(135deg, rgba(255, 193, 7, 0.15) 0%, rgba(255, 152, 0, 0.15) 100%) !important;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 193, 7, 0.3);
                border-radius: 12px;
            }
            .stError {
                background: linear-gradient(135deg, rgba(244, 67, 54, 0.15) 0%, rgba(233, 30, 99, 0.15) 100%) !important;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(244, 67, 54, 0.3);
                border-radius: 12px;
            }
            [data-testid="stMetric"] {
                background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(157, 78, 221, 0.1) 100%);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 1.5rem;
                border: 1px solid rgba(0, 212, 255, 0.2);
                box-shadow: 0 4px 16px rgba(0, 212, 255, 0.1);
            }
            [data-testid="stMetric"] label {
                color: rgba(255, 255, 255, 0.7);
                font-weight: 600;
            }
            [data-testid="stMetric"] [data-testid="stMetricValue"] {
                color: #00d4ff;
                font-weight: 700;
            }
        </style>
        """, unsafe_allow_html=True)
    else:  # Light theme con Glassmorphism
        st.markdown("""
        <style>
            .stApp {
                background: linear-gradient(135deg, #f0f4f8 0%, #e8ecf0 50%, #dfe4e8 100%);
            }
            .main {
                background: transparent;
                font-family: 'Inter', sans-serif;
                color: #333333;
            }
            .header-container {
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                padding: 2rem 2.5rem;
                border-radius: 20px;
                margin-bottom: 2rem;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
            .card {
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
                backdrop-filter: blur(15px);
                -webkit-backdrop-filter: blur(15px);
                padding: 2rem;
                border-radius: 20px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.8);
                margin-bottom: 1.5rem;
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                padding: 2rem;
                border-right: 1px solid rgba(255, 255, 255, 0.5);
            }
            [data-testid="stSidebar"] [data-testid="stMetric"] {
                background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(157, 78, 221, 0.15) 100%);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 1.25rem;
                margin-bottom: 1rem;
                border: 1px solid rgba(0, 212, 255, 0.3);
                box-shadow: 0 4px 16px rgba(0, 212, 255, 0.15);
            }
            [data-testid="stSidebar"] [data-testid="stMetric"] label {
                color: #666666 !important;
                font-weight: 600;
                font-size: 0.85rem;
            }
            [data-testid="stSidebar"] [data-testid="stMetric"] [data-testid="stMetricValue"] {
                color: #0066cc !important;
                font-weight: 700;
                font-size: 1.5rem;
            }
            h1 {
                color: rgba(51, 51, 51, 0.95);
                font-weight: 800;
                background: linear-gradient(135deg, #0066cc 0%, #9d4edd 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            h2 {
                color: rgba(51, 51, 51, 0.9);
                font-weight: 700;
            }
            h3 {
                color: rgba(51, 51, 51, 0.85);
                font-weight: 600;
            }
            .stButton > button {
                background: linear-gradient(135deg, #0066cc 0%, #9d4edd 100%);
                color: white;
                border-radius: 12px;
                padding: 0.875rem 2rem;
                font-weight: 600;
                border: none;
                box-shadow: 0 4px 16px rgba(0, 102, 204, 0.3);
                transition: all 0.3s ease;
            }
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0, 102, 204, 0.4);
            }
            .stDownloadButton > button {
                background: linear-gradient(135deg, #00cc66 0%, #0066cc 100%);
                color: white;
                border-radius: 12px;
                font-weight: 600;
                box-shadow: 0 4px 16px rgba(0, 204, 102, 0.3);
            }
            [data-testid="stTabs"] [role="tablist"] {
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
                backdrop-filter: blur(15px);
                border-radius: 16px;
                padding: 0.75rem;
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
            [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
                background: linear-gradient(135deg, #0066cc 0%, #9d4edd 100%);
                color: white;
                border-radius: 10px;
                font-weight: 600;
            }
            [data-testid="stTabs"] [role="tab"][aria-selected="false"] {
                color: #666666;
            }
            [data-testid="stMetric"] {
                background: linear-gradient(135deg, rgba(0, 102, 204, 0.1) 0%, rgba(157, 78, 221, 0.1) 100%);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 1.5rem;
                border: 1px solid rgba(0, 102, 204, 0.2);
                box-shadow: 0 4px 16px rgba(0, 102, 204, 0.1);
            }
            [data-testid="stMetric"] label {
                color: #666666;
                font-weight: 600;
            }
            [data-testid="stMetric"] [data-testid="stMetricValue"] {
                color: #0066cc;
                font-weight: 700;
            }
            .stTextInput > div > div > input,
            .stNumberInput > div > div > input,
            .stSelectbox > div > div > select,
            .stSelectbox > div > div > div {
                background: linear-gradient(135deg, rgba(0, 102, 204, 0.1) 0%, rgba(157, 78, 221, 0.1) 100%) !important;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(0, 102, 204, 0.3) !important;
                border-radius: 12px !important;
                color: #333333 !important;
                padding: 0.875rem 1rem;
                font-weight: 500;
                transition: all 0.3s ease;
            }
            .stTextInput > div > div > input:focus,
            .stNumberInput > div > div > input:focus,
            .stSelectbox > div > div > select:focus {
                border-color: #0066cc !important;
                box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.2);
                outline: none;
            }
            .stSelectbox > div {
                background: transparent !important;
            }
            .stTextInput > div {
                background: transparent !important;
            }
            .stNumberInput > div {
                background: transparent !important;
            }
            [data-testid="stFileUploader"] {
                border: 2px dashed rgba(0, 102, 204, 0.5) !important;
                background: linear-gradient(135deg, rgba(0, 102, 204, 0.1) 0%, rgba(157, 78, 221, 0.1) 100%) !important;
                backdrop-filter: blur(10px);
                border-radius: 16px !important;
            }
            [data-testid="stFileUploader"] > div {
                background: transparent !important;
            }
            [data-testid="stTextInput"] > div > div {
                background: transparent !important;
            }
            [data-testid="stNumberInput"] > div > div {
                background: transparent !important;
            }
            [data-testid="stSelectbox"] > div > div {
                background: transparent !important;
            }
            p, span, div {
                color: #333333;
            }
            p, span {
                color: #333333;
            }
            label {
                color: #666666;
                font-weight: 500;
            }
            .stMarkdown, .stText, .stWrite {
                background: transparent !important;
            }
            .stAlert {
                background: linear-gradient(135deg, rgba(0, 102, 204, 0.15) 0%, rgba(157, 78, 221, 0.15) 100%) !important;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(0, 102, 204, 0.3);
                border-radius: 12px;
            }
            .stSuccess {
                background: linear-gradient(135deg, rgba(0, 204, 102, 0.15) 0%, rgba(0, 102, 204, 0.15) 100%) !important;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(0, 204, 102, 0.3);
                border-radius: 12px;
            }
            .stWarning {
                background: linear-gradient(135deg, rgba(255, 193, 7, 0.15) 0%, rgba(255, 152, 0, 0.15) 100%) !important;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 193, 7, 0.3);
                border-radius: 12px;
            }
            .stError {
                background: linear-gradient(135deg, rgba(244, 67, 54, 0.15) 0%, rgba(233, 30, 99, 0.15) 100%) !important;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(244, 67, 54, 0.3);
                border-radius: 12px;
            }
        </style>
        """, unsafe_allow_html=True)
    
    # Header principal con Glassmorphism y efectos neón
    st.markdown("""
    <div class="header-container">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 1.5rem;">
                <div style="background: linear-gradient(135deg, #00d4ff 0%, #9d4edd 100%); 
                            padding: 0.75rem; 
                            border-radius: 16px; 
                            box-shadow: 0 4px 16px rgba(0, 212, 255, 0.3);">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5">
                        <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                        <path d="M2 17l10 5 10-5"/>
                        <path d="M2 12l10 5 10-5"/>
                    </svg>
                </div>
                <div>
                    <h1 style="margin: 0; font-size: 1.85rem; font-weight: 800; 
                               background: linear-gradient(135deg, #00d4ff 0%, #9d4edd 100%);
                               -webkit-background-clip: text;
                               -webkit-text-fill-color: transparent;
                               background-clip: text;
                               letter-spacing: -0.5px;">VISION PUBLICIDAD</h1>
                    <p style="margin: 0.35rem 0 0; font-size: 0.9rem; 
                               color: rgba(255, 255, 255, 0.7); 
                               font-weight: 500;">Sistema de Gestión Operativa</p>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.2) 0%, rgba(157, 78, 221, 0.2) 100%);
                            backdrop-filter: blur(10px);
                            padding: 0.6rem 1.25rem; 
                            border-radius: 12px; 
                            font-size: 0.85rem; 
                            font-weight: 600; 
                            color: #00d4ff;
                            border: 1px solid rgba(0, 212, 255, 0.3);
                            box-shadow: 0 4px 12px rgba(0, 212, 255, 0.2);">
                    <span style="display: flex; align-items: center; gap: 0.5rem;">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                            <circle cx="12" cy="7" r="4"/>
                        </svg>
                        Administrador
                    </span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Botón de cambio de tema con estilo neón
    col_theme = st.columns([1])
    with col_theme[0]:
        st.markdown("""
        <div style="margin-bottom: 1.5rem;">
        """, unsafe_allow_html=True)
        if st.button("⋮ Cambiar Tema (Dark/Light)", key="header_theme_toggle", use_container_width=True):
            st.session_state.theme_mode = 'light' if st.session_state.theme_mode == 'dark' else 'dark'
            st.rerun()
        st.markdown("""
        </div>
        """, unsafe_allow_html=True)
    
    # Sidebar con información y métricas modernas
    with st.sidebar:
        st.markdown("""
        <div style="margin-bottom: 2rem;">
            <h2 style="margin: 0; font-size: 1.5rem; font-weight: 700; 
                       background: linear-gradient(135deg, #00d4ff 0%, #9d4edd 100%);
                       -webkit-background-clip: text;
                       -webkit-text-fill-color: transparent;
                       background-clip: text;">Panel de Control</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar tema actual con estilo
        current_theme_display = st.session_state.theme_mode.capitalize()
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(157, 78, 221, 0.15) 100%);
                    backdrop-filter: blur(10px);
                    padding: 1rem;
                    border-radius: 12px;
                    border: 1px solid rgba(0, 212, 255, 0.3);
                    margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#00d4ff" stroke-width="2.5">
                    <circle cx="12" cy="12" r="5"/>
                    <line x1="12" y1="1" x2="12" y2="3"/>
                    <line x1="12" y1="21" x2="12" y2="23"/>
                    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
                    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                    <line x1="1" y1="12" x2="3" y2="12"/>
                    <line x1="21" y1="12" x2="23" y2="12"/>
                </svg>
                <span style="color: rgba(255, 255, 255, 0.85); font-weight: 600; font-size: 0.9rem;">
                    Tema actual: {current_theme_display}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Selector de modo (Dark/Light) - sincronizado con el botón del header
        theme_mode_selection = st.selectbox(
            "Modo de Tema", 
            ["Dark", "Light"], 
            key="sidebar_theme_mode",
            index=0 if st.session_state.theme_mode == 'dark' else 1
        )
        
        # Actualizar session_state cuando cambia el tema desde el sidebar
        if theme_mode_selection.lower() != st.session_state.theme_mode:
            st.session_state.theme_mode = theme_mode_selection.lower()
            st.rerun()
        
        st.markdown("---")
        
        # Métricas principales
        total_products = st.session_state.fixed_products['stock'].sum()
        total_services = st.session_state.services_by_measure['stock'].sum()
        total_sales = st.session_state.sales_history['total'].sum() if len(st.session_state.sales_history) > 0 else 0
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.metric("Productos", len(st.session_state.fixed_products))
        with col_s2:
            st.metric("Servicios", len(st.session_state.services_by_measure))
        
        st.metric("Stock Total", f"{total_products:,} un")
        st.metric("Ventas Totales", format_currency(total_sales))
        st.metric("Transacciones", len(st.session_state.sales_history))
        
        st.markdown("---")
        st.markdown("### Fecha y Hora")
        st.markdown(f"**{datetime.now().strftime('%d/%m/%Y')}**")
        st.markdown(f"**{datetime.now().strftime('%H:%M:%S')}**")
        
        st.markdown("---")
        st.markdown("### Visión Publicidad")
        st.markdown("Sistema de Gestión Operativa")
        st.caption("v2.4.1 - Professional Edition")
    
    # Pestañas principales
    tab1, tab2, tab3, tab4 = st.tabs([
        "Cotizador Gran Formato",
        "Papelería Comercial",
        "Control de Inventario",
        "Facturación"
    ])
    
    # =============================================
    # PESTAÑA 1: COTIZADOR GRAN FORMATO Y PREPRENTA
    # =============================================
    with tab1:
        st.markdown("""
        <div style="margin-bottom: 2rem;">
            <h2 style="font-size: 1.85rem; font-weight: 700; margin: 0 0 0.5rem 0; letter-spacing: -0.5px;
                       background: linear-gradient(135deg, #00d4ff 0%, #9d4edd 100%);
                       -webkit-background-clip: text;
                       -webkit-text-fill-color: transparent;
                       background-clip: text;">Cotizador Gran Formato y Preprensa</h2>
            <p style="color: rgba(255, 255, 255, 0.7); margin: 0; font-size: 0.95rem; font-weight: 500;">
                Cotice y genere archivos PDF listos para impresión con marcas de corte vectoriales.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Sección 1: Cotización y Medidas con Glassmorphism
            st.markdown("""
            <div class="card">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;">
                    <div style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.2) 0%, rgba(157, 78, 221, 0.2) 100%);
                                padding: 0.6rem;
                                border-radius: 10px;
                                border: 1px solid rgba(0, 212, 255, 0.3);">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#00d4ff" stroke-width="2.5">
                            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                            <path d="M2 17l10 5 10-5"/>
                            <path d="M2 12l10 5 10-5"/>
                        </svg>
                    </div>
                    <h3 style="color: rgba(255, 255, 255, 0.95); margin: 0; font-size: 1.25rem; font-weight: 700; letter-spacing: -0.25px;">
                        1. Cotización y Medidas
                    </h3>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            client_name = st.text_input("Nombre del Cliente", key="gf_client")
            
            service_options = st.session_state.services_by_measure['servicio'].tolist()
            selected_service = st.selectbox("Servicio / Material", service_options, key="gf_service")
            
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
            
            # Indicadores de costo - estilo Glassmorphism con degradado neón
            st.markdown("""
            <div class="card">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.25rem;">
                    <div style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.2) 0%, rgba(157, 78, 221, 0.2) 100%);
                                padding: 0.6rem;
                                border-radius: 10px;
                                border: 1px solid rgba(0, 212, 255, 0.3);">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#00d4ff" stroke-width="2.5">
                            <path d="M12 1v22M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                        </svg>
                    </div>
                    <h3 style="color: rgba(255, 255, 255, 0.95); margin: 0; font-size: 1.25rem; font-weight: 700; letter-spacing: -0.25px;">
                        Resumen de Costos
                    </h3>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                    <div style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(157, 78, 221, 0.15) 100%);
                                backdrop-filter: blur(10px);
                                padding: 1rem; 
                                border-radius: 12px; 
                                border: 1px solid rgba(0, 212, 255, 0.3);
                                box-shadow: 0 4px 12px rgba(0, 212, 255, 0.1);">
                        <div style="color: rgba(255, 255, 255, 0.7); font-size: 0.85rem; font-weight: 600; margin-bottom: 0.5rem;">Costo por Fórmula</div>
                        <div style="color: #00d4ff; font-size: 1.5rem; font-weight: 700;">""" + format_currency(unit_price) + """</div>
                    </div>
                    <div style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(157, 78, 221, 0.15) 100%);
                                backdrop-filter: blur(10px);
                                padding: 1rem; 
                                border-radius: 12px; 
                                border: 1px solid rgba(0, 212, 255, 0.3);
                                box-shadow: 0 4px 12px rgba(0, 212, 255, 0.1);">
                        <div style="color: rgba(255, 255, 255, 0.7); font-size: 0.85rem; font-weight: 600; margin-bottom: 0.5rem;">Tarifa Mínima Aplicable</div>
                        <div style="color: #00d4ff; font-size: 1.5rem; font-weight: 700;">""" + format_currency(service_data['tarifa_minima']) + """</div>
                    </div>
                </div>
                <div style="background: linear-gradient(135deg, #00d4ff 0%, #9d4edd 100%); 
                           padding: 1.5rem; 
                           border-radius: 16px; 
                           box-shadow: 0 8px 24px rgba(0, 212, 255, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2);">
                    <div style="color: rgba(255, 255, 255, 0.9); font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem; letter-spacing: 0.5px;">TOTAL A COBRAR</div>
                    <div style="color: white; font-size: 2.25rem; font-weight: 800; letter-spacing: -1px;">""" + format_currency(total_price) + """</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Sección 2: Preprensa Digital y Archivos con Glassmorphism
            st.markdown("""
            <div class="card">
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;">
                    <div style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.2) 0%, rgba(157, 78, 221, 0.2) 100%);
                                padding: 0.6rem;
                                border-radius: 10px;
                                border: 1px solid rgba(0, 212, 255, 0.3);">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#00d4ff" stroke-width="2.5">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                            <polyline points="17 8 12 3 7 8"/>
                            <line x1="12" y1="3" x2="12" y2="15"/>
                        </svg>
                    </div>
                    <h3 style="color: rgba(255, 255, 255, 0.95); margin: 0; font-size: 1.25rem; font-weight: 700; letter-spacing: -0.25px;">
                        2. Preprensa Digital y Archivos
                    </h3>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Subir archivo del arte (JPG, PNG)",
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
                    if st.button("Generar PDF FPP con Marcas de Corte", key="gf_generate"):
                        with st.spinner("Procesando imagen y generando PDF..."):
                            try:
                                st.info("Redimensionando imagen...")
                                # Redimensionar imagen
                                resized_image = resize_image_to_cm(image_pil, width_cm, height_cm, dpi=150)
                                
                                st.info("Creando PDF con marcas de corte...")
                                # Crear PDF con marcas de corte
                                pdf_bytes = create_pdf_with_crop_marks(resized_image, width_cm, height_cm, bleed_cm=0.5)
                                
                                st.info("Preparando descarga...")
                                # Leer los bytes del PDF
                                pdf_bytes.seek(0)
                                pdf_data = pdf_bytes.read()
                                
                                st.info(f"Tamaño del PDF: {len(pdf_data)} bytes")
                                
                                # Nombre del archivo
                                pdf_filename = f"FPP_{selected_service}_{client_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                                
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
                                
                                st.success("PDF generado exitosamente e inventario actualizado!")
                                st.download_button(
                                    label="Descargar FPP para Plotter",
                                    data=pdf_data,
                                    file_name=pdf_filename,
                                    mime="application/pdf",
                                    key="download_pdf_fpp"
                                )
                                
                            except Exception as e:
                                import traceback
                                st.error(f"Error al generar PDF: {str(e)}")
                                st.error(f"Detalles: {traceback.format_exc()}")
                
                except Exception as e:
                    st.error(f"Error al procesar la imagen: {str(e)}")
            else:
                st.warning("Por favor cargue una imagen para generar el PDF.")
    
    # =============================================
    # PESTAÑA 2: PRODUCTOS FIJOS Y PAPELERÍA
    # =============================================
    with tab2:
        st.markdown("""
        <div class="card">
            <h2>Productos Fijos y Papelería</h2>
            <p>Venta de productos de papelería, avisos fijos y artículos promocionales.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            <div class="card">
                <h3>Selección de Producto</h3>
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
                st.warning(f"Solo hay {available_stock} unidades disponibles.")
            
            # Cálculo del total
            total_fp = product_data['precio'] * quantity_fp
            
            st.markdown("""
            <div class="card">
                <h3>Resumen de Compra</h3>
            </div>
            """, unsafe_allow_html=True)
            st.metric("Precio Unitario", format_currency(product_data['precio']))
            st.metric("Total a Cobrar", format_currency(total_fp))
            st.metric("Stock Disponible", available_stock)
            
            client_name_fp = st.text_input("Nombre del Cliente", key="fp_client")
            
            if st.button("Vender y Descontar", key="fp_sell"):
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
                    
                    st.success(f"Venta registrada! {quantity_fp} unidades descontadas del inventario.")
                    st.rerun()
                else:
                    st.error("Stock insuficiente para completar la venta.")
        
        with col2:
            st.markdown("""
            <div class="card">
                <h3>Catálogo de Productos</h3>
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
            
            if st.button("Guardar Cambios en Servicios", key="save_services"):
                st.session_state.services_by_measure = edited_services
                st.success("Cambios guardados exitosamente!")
                st.rerun()
        
        with subtab2:
            st.markdown("""
            <div class="card">
                <h3>Productos Fijos y Papelería</h3>
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
                <h3>Datos del Recibo</h3>
            </div>
            """, unsafe_allow_html=True)
            
            receipt_client = st.text_input("Nombre del Cliente", key="receipt_client")
            
            st.markdown("""
            <div class="card">
                <h3>Items del Recibo</h3>
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
                <h3>Totales</h3>
            </div>
            """, unsafe_allow_html=True)
            col_t1, col_t2, col_t3 = st.columns(3)
            with col_t1:
                st.metric("Subtotal", format_currency(subtotal))
            with col_t2:
                st.metric("IVA (19%)", format_currency(iva))
            with col_t3:
                st.metric("Total", format_currency(total))
            
            if st.button("Generar Recibo PDF", key="generate_receipt"):
                if receipt_client and any(item['descripcion'] for item in receipt_items):
                    try:
                        pdf_buffer = generate_receipt_pdf(receipt_client, receipt_items, subtotal, iva, total)
                        
                        # Leer los bytes del PDF
                        pdf_data = pdf_buffer.getvalue()
                        
                        st.success("Recibo generado exitosamente!")
                        st.download_button(
                            label="Descargar Recibo PDF",
                            data=pdf_data,
                            file_name=f"Recibo_{receipt_client}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"Error al generar recibo: {str(e)}")
                else:
                    st.warning("Por favor complete el nombre del cliente y al menos un item.")
    
    # Footer
    st.markdown("""
    <div style="margin-top: 3rem; padding: 1.5rem; border-top: 1px solid #555; text-align: center; background: #2d2d2d; border-radius: 8px;">
        <div style="display: flex; justify-content: center; align-items: center; gap: 2rem; flex-wrap: wrap;">
            <div style="color: #b0b0b0; font-size: 0.85rem; font-weight: 500;">v2.4.1</div>
            <div style="color: #b0b0b0; font-size: 0.85rem; font-weight: 500;">© 2016 VISION PUBLICIDAD e Ingeniería</div>
            <div style="display: flex; align-items: center; gap: 0.5rem; color: #4a90e2; font-size: 0.8rem; font-weight: 600;">
                <span style="width: 8px; height: 8px; background: #4a90e2; border-radius: 50%;"></span>
                Estado de red activo
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
