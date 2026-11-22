# Estilos, encabezado y navegación superior (requiere Streamlit >= 1.39)
import streamlit as st

AZUL, ROJO, DORADO, FONDO = "#1B2A49", "#C8102E", "#F2A900", "#F4F6FA"

CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, .stApp {{ font-family:'Inter',sans-serif; }}
.stApp {{ background:{FONDO}; }}
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"] {{ display:none; }}
.block-container {{ padding-top:1.2rem; max-width:1300px; }}

/* Texto siempre legible (oscuro sobre fondo claro) */
.stApp p, .stApp li, .stApp label, .stApp span, .stApp td, .stApp th {{ color:{AZUL}; }}
.stApp p, .stApp li {{ font-size:1.05rem; line-height:1.6; }}
h1, h2, h3, h4 {{ color:{AZUL} !important; font-weight:800; letter-spacing:-0.3px; }}
h1 {{ border-bottom:4px solid {ROJO}; padding-bottom:8px; display:inline-block; }}
[data-testid="stCaptionContainer"] p {{ color:#3D4A66 !important; font-size:.95rem; }}
code {{ color:{ROJO} !important; }}

/* Encabezado */
.encabezado {{ display:flex; align-items:center; gap:22px; background:linear-gradient(120deg,{AZUL},#2E4A7D);
  border-radius:16px 16px 0 0; padding:16px 28px; border-bottom:4px solid {ROJO}; }}
.encabezado img {{ height:54px; background:white; border-radius:8px; padding:6px; }}
.encabezado .t {{ color:white !important; font-size:1.45rem; font-weight:800; line-height:1.1; }}
.encabezado .s {{ color:{DORADO} !important; font-size:1rem; font-weight:500; }}

/* Navegación principal */
.st-key-nav_sec {{ background:{AZUL}; border-radius:0 0 16px 16px; padding:6px 14px 10px; margin-bottom:10px;
  box-shadow:0 6px 16px rgba(0,0,0,.15); }}
.st-key-nav_sec label p {{ color:#FFFFFF !important; font-weight:600; font-size:1.02rem; }}
.st-key-nav_sec label {{ background:transparent !important; border:1px solid rgba(255,255,255,.25) !important; }}
.st-key-nav_sec label:has(input:checked) {{ background:{ROJO} !important; border-color:{ROJO} !important; }}

/* Radios horizontales como botones (sub-menús y selectores) */
div[role="radiogroup"] {{ gap:8px; flex-wrap:wrap; }}
div[role="radiogroup"] label {{ background:white; border:1px solid #CBD3E3; border-radius:999px; padding:6px 16px; cursor:pointer;
  transition:all .15s; }}
div[role="radiogroup"] label > div:first-child {{ display:none; }}
div[role="radiogroup"] label:hover {{ border-color:{ROJO}; }}
div[role="radiogroup"] label:has(input:checked) {{ background:{ROJO}; border-color:{ROJO}; }}
div[role="radiogroup"] label:has(input:checked) p {{ color:white !important; font-weight:700; }}
div[role="radiogroup"] label p {{ font-weight:600; margin:0; }}

/* Pestañas */
button[data-baseweb="tab"] p {{ color:{AZUL} !important; font-weight:700; font-size:1.02rem; }}
button[data-baseweb="tab"][aria-selected="true"] p {{ color:{ROJO} !important; }}

/* Botones */
.stButton > button {{ background:{ROJO}; color:white; border:none; border-radius:10px; font-weight:700; padding:.55rem 1.3rem; }}
.stButton > button p {{ color:white !important; }}
.stButton > button:hover {{ background:#9E0C23; }}

/* Portada, tarjetas y métricas */
.portada {{ background:linear-gradient(135deg,{AZUL},#2E4A7D); border-left:10px solid {ROJO}; border-radius:18px;
  padding:40px 50px; box-shadow:0 8px 24px rgba(0,0,0,.18); }}
.portada h1 {{ color:white !important; font-size:3rem; margin:0; border:none; }}
.portada h3 {{ color:{DORADO} !important; margin:4px 0 24px; font-weight:500; }}
.portada .campo, .portada .campo li {{ font-size:1.15rem; margin:6px 0; color:#FFFFFF !important; }}
.portada .campo b {{ color:{DORADO} !important; }}
.tarjeta {{ background:white; border-radius:14px; padding:20px 24px; border-top:5px solid {ROJO};
  box-shadow:0 3px 12px rgba(0,0,0,.08); margin-bottom:14px; }}
.tarjeta h4 {{ margin-top:0; }}
.tarjeta, .tarjeta p, .tarjeta li {{ color:#1F2937 !important; }}
.pendiente {{ background:white; border:3px dashed {DORADO}; border-radius:16px; padding:40px; text-align:center; }}
[data-testid="stMetric"] {{ background:white; border-radius:12px; padding:14px 18px; border-left:5px solid {DORADO};
  box-shadow:0 2px 8px rgba(0,0,0,.07); }}
[data-testid="stMetricValue"] {{ color:{AZUL}; font-weight:800; }}
[data-testid="stMetricLabel"] p {{ color:#3D4A66 !important; font-weight:600; }}
[data-testid="stExpander"] {{ background:white; border-radius:12px; border:1px solid #CBD3E3; }}
[data-testid="stExpander"] summary p {{ font-weight:700; font-size:1.05rem; }}
"""

def estilos():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

def tarjeta(titulo, contenido):
    st.markdown(f'<div class="tarjeta"><h4>{titulo}</h4>{contenido}</div>', unsafe_allow_html=True)

def encabezado(logo, titulo, subtitulo):
    st.markdown(f'<div class="encabezado"><img src="{logo}"><div><div class="t">{titulo}</div>'
                f'<div class="s">{subtitulo}</div></div></div>', unsafe_allow_html=True)

def navegacion(secciones, submenus):
    """Barra superior. submenus = {sección: [opciones]}. Devuelve (sección, opción)."""
    seccion = st.radio("Sección", secciones, horizontal=True, label_visibility="collapsed", key="nav_sec")
    sub = None
    if seccion in submenus:
        sub = st.radio("Opción", submenus[seccion], horizontal=True, label_visibility="collapsed",
                       key=f"nav_sub_{seccion}")
    return seccion, sub
