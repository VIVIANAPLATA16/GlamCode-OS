import streamlit as st
import pandas as pd

# 1. Configuración de la Suite de Lujo
st.set_page_config(page_title="GlamCode OS", page_icon="💎", layout="wide")

# 2. MAQUILLAJE DE LA APP (CSS PROFESIONAL)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    /* Fondo Negro Profundo */
    .stApp {
        background-color: #050505 !important;
        font-family: 'Inter', sans-serif;
        color: white;
    }

    /* Título con Degradado Dorado */
    .main-title {
        background: linear-gradient(90deg, #D4AF37, #F9E79F);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0px;
        letter-spacing: -2px;
    }

    /* Tarjetas tipo Cristal (Glassmorphism) */
    .card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        backdrop-filter: blur(10px);
    }

    /* Botón Dorado Redondeado */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #D4AF37, #B8860B) !important;
        color: black !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 15px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0px 0px 20px rgba(212, 175, 55, 0.4);
    }

    /* Estilo para las tablas */
    .stTable {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-radius: 15px;
    }

    /* Ocultar elementos estándar de Streamlit */
    /* ESCUDO DE INVISIBILIDAD TOTAL */
    .stAppDeployButton, .st-emotion-cache-12fmjuu, .st-emotion-cache-ch5vc8, .st-emotion-cache-6q9sum {
        display: none !important;
    }
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    .block-container {padding-top: 2rem;}
    </style>
    """, unsafe_allow_html=True)

# 3. INTERFAZ VISUAL
st.markdown('<h1 class="main-title">GLAMCODE OS</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 1rem; letter-spacing: 3px;'>PREMIUM MANAGEMENT SYSTEM</p>", unsafe_allow_html=True)
st.write("##")

# Fila de Indicadores (Métricas)
m1, m2, m3 = st.columns(3)
with m1:
    st.markdown('<div class="card"><p style="color:#D4AF37; font-size: 0.7rem; letter-spacing: 1px;">INGRESOS HOY</p><h2 style="color:white; margin:0;">$ 1.250.000</h2></div>', unsafe_allow_html=True)
with m2:
    st.markdown('<div class="card"><p style="color:#D4AF37; font-size: 0.7rem; letter-spacing: 1px;">CITAS ACTIVAS</p><h2 style="color:white; margin:0;">14</h2></div>', unsafe_allow_html=True)
with m3:
    st.markdown('<div class="card"><p style="color:#D4AF37; font-size: 0.7rem; letter-spacing: 1px;">SISTEMA</p><h2 style="color:white; margin:0;">ONLINE ✨</h2></div>', unsafe_allow_html=True)

st.write("---")

# Cuerpo de la Aplicación
col_form, col_tabla = st.columns([1, 1.8], gap="large")

with col_form:
    st.markdown("<h3 style='color:#D4AF37; font-weight: 300;'>🖋️ REGISTRO VIP</h3>", unsafe_allow_html=True)
    nombre = st.text_input("NOMBRE DEL CLIENTE", placeholder="Nombre completo")
    servicio = st.selectbox("SERVICIO", ["Corte Boutique", "Balayage Diamond", "Seda Capilar", "Barbería Pro"])
    precio = st.number_input("VALOR SERVICIO ($)", min_value=0, step=10000)
    
    if st.button("CONFIRMAR Y GUARDAR"):
        st.balloons()
        st.success(f"¡Registrado con éxito!")

with col_tabla:
    st.markdown("<h3 style='color:#D4AF37; font-weight: 300;'>📋 AGENDA DE HOY</h3>", unsafe_allow_html=True)
    datos = {
        "CLIENTE": ["Viviana Plata", "Carolina Herrera", "Julian Casablancas", "Elena Rose"],
        "SERVICIO": ["Corte Boutique", "Color Pro", "Barbería Real", "Seda Capilar"],
        "ESTADO": ["✅ Pago", "⌛ En Silla", "📅 Agendado", "📅 Agendado"]
    }
    df = pd.DataFrame(datos)
    st.table(df)

# Sidebar
st.sidebar.markdown("<h1 style='text-align:center;'>👑</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<h3 style='text-align:center; color:#D4AF37; letter-spacing: 2px;'>GLAM ADMIN</h3>", unsafe_allow_html=True)
st.sidebar.write("---")
st.sidebar.caption("Desarrollado por Viviana Plata | Edición 2026")
