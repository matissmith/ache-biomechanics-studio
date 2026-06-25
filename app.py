"""
Ache Innovation — Sistema de Parametrización Morfológica Canina
App principal (Streamlit).

Para iniciar:
    streamlit run app.py
"""

import sys
import io
import base64
import numpy as np
from pathlib import Path
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

# ── Agregar directorio raíz al path ─────────────────────────────────────────
ROOT = Path(__file__).parent
MASTER_ROOT = ROOT.parents[2] if len(ROOT.parents) >= 3 else ROOT
sys.path.insert(0, str(ROOT))

from modules.database import (
    init_db, save_case, save_measurements, save_prosthetic_specs,
    update_case_breed, get_cases, get_case, get_case_measurements
)
from modules.breed_detector import detect_breed, format_breed_name
from modules.measurement import detect_aruco, generate_aruco_marker_png
from modules.breed_database import get_breed_info, get_all_breed_names, estimate_limb_from_weight
from modules.report_generator import generate_pdf_report
from modules.stl_renderer import render_scad_to_stl, parse_stl, openscad_available
from modules.guia_quirurgica import render_guia_quirurgica

# ── Configuración ────────────────────────────────────────────────────────────
DB_PATH = ROOT / "data" / "ache.db"
init_db(DB_PATH)

st.set_page_config(
    page_title="Ache Innovation",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow:wght@300;400;500;600;700;800&display=swap');
:root{--ache-navy:#0A2560;--ache-navy-2:#071840;--ache-navy-3:#041127;--ache-yellow:#F29E1F;--ache-yellow-2:#F5B84A;--ache-bg:#F5F7FB;--ache-card:#FFFFFF;--ache-text:#0D1B35;--ache-muted:#4A5568;--ache-border:#E2E9F5;}
html, body, [class*="css"]{font-family:'Barlow',system-ui,-apple-system,BlinkMacSystemFont,sans-serif!important;}
.stApp{background:linear-gradient(180deg,#F7F9FC 0%,#EEF3F8 100%);color:var(--ache-text);} .block-container{padding-top:1.4rem;padding-bottom:3rem;max-width:1280px;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,var(--ache-navy) 0%,var(--ache-navy-3) 100%);border-right:1px solid rgba(255,255,255,.08);} [data-testid="stSidebar"] *{color:#F7FAFF!important;} [data-testid="stSidebar"] img{border-radius:16px;background:white;padding:10px;box-shadow:0 12px 28px rgba(0,0,0,.18);} [data-testid="stSidebar"] .stRadio>div{gap:6px;} [data-testid="stSidebar"] .stRadio label div[data-testid="stMarkdownContainer"] p{padding:10px 12px;border-radius:12px;margin:0;color:rgba(255,255,255,.88)!important;font-weight:600;} [data-testid="stSidebar"] .stRadio label:hover div[data-testid="stMarkdownContainer"] p{background:rgba(242,170,36,.14);}
h1{color:var(--ache-navy);font-weight:800!important;letter-spacing:-.02em;margin-bottom:.6rem;} h2{color:var(--ache-navy);font-weight:750!important;border:none!important;padding-bottom:0!important;} h3{color:var(--ache-navy);font-weight:700!important;} p,li,label,span{font-size:1.02rem;}
.ache-hero{background:linear-gradient(135deg,var(--ache-navy) 0%,#214666 62%,#1B3A5A 100%);border-radius:24px;padding:28px 32px;margin-bottom:22px;box-shadow:0 18px 45px rgba(23,53,85,.22);position:relative;overflow:hidden;} .ache-hero:after{content:"";position:absolute;right:-90px;top:-90px;width:260px;height:260px;border:28px solid rgba(255,255,255,.08);border-radius:50%;} .ache-hero h1{color:white!important;margin:0;font-size:2.35rem;} .ache-hero p{color:rgba(255,255,255,.78);margin:.45rem 0 0;max-width:760px;} .ache-pill{display:inline-flex;align-items:center;gap:8px;background:rgba(242,170,36,.18);color:#FFE3A5;border:1px solid rgba(242,170,36,.32);padding:6px 10px;border-radius:999px;font-weight:700;font-size:.88rem;margin-bottom:10px;} .ache-card{background:var(--ache-card);border:1px solid var(--ache-border);border-radius:18px;padding:18px 20px;box-shadow:0 10px 30px rgba(23,53,85,.07);margin:10px 0;} .ache-card h3{margin-top:0;} .ache-step{background:white;border:1px solid var(--ache-border);border-radius:16px;padding:16px;height:100%;box-shadow:0 8px 22px rgba(23,53,85,.06);} .ache-step-number{width:34px;height:34px;border-radius:50%;background:var(--ache-yellow);color:var(--ache-navy);display:flex;align-items:center;justify-content:center;font-weight:800;margin-bottom:10px;} .ache-muted{color:var(--ache-muted);}
.stButton>button,.stDownloadButton>button{border-radius:12px!important;font-weight:700!important;border:1px solid var(--ache-border)!important;} .stButton>button[kind="primary"],.stDownloadButton>button[kind="primary"]{background:linear-gradient(90deg,var(--ache-yellow),var(--ache-yellow-2))!important;color:var(--ache-navy)!important;border:none!important;box-shadow:0 10px 24px rgba(242,170,36,.28)!important;} .stButton>button[kind="primary"]:hover,.stDownloadButton>button[kind="primary"]:hover{filter:brightness(.98);transform:translateY(-1px);}
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,textarea,.stSelectbox [data-baseweb="select"]{border-radius:12px!important;border-color:var(--ache-border)!important;} [data-testid="metric-container"]{background:white;border:1px solid var(--ache-border);border-left:5px solid var(--ache-yellow);border-radius:16px;padding:14px 16px;box-shadow:0 8px 20px rgba(23,53,85,.06);} [data-testid="metric-container"] label{color:var(--ache-muted)!important;}
.ache-info{background:#EAF2FA;border:1px solid #C9D8E8;border-left:5px solid var(--ache-navy);border-radius:14px;padding:14px 16px;margin:10px 0;} .ache-warning{background:#FFF6E4;border:1px solid #FFE1A5;border-left:5px solid var(--ache-yellow);border-radius:14px;padding:14px 16px;margin:10px 0;}
.js-plotly-plot .modebar{top:8px!important;right:8px!important;background:rgba(255,255,255,.92)!important;border-radius:12px!important;padding:5px!important;box-shadow:0 6px 16px rgba(0,0,0,.12);} .js-plotly-plot .modebar-btn svg{fill:var(--ache-navy)!important;}
</style>
""", unsafe_allow_html=True)
st.markdown("""<style>

/* ── QA visual overrides ───────────────────────────────── */
[data-testid="stHeader"] { background: transparent !important; height: 0 !important; }
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden !important; height: 0 !important; }
.block-container { padding-top: 1.1rem !important; }

/* Sidebar logo + nav */
[data-testid="stSidebar"] img { max-height: 178px !important; object-fit: contain !important; width: 100% !important; }
[data-testid="stSidebar"] [role="radiogroup"] label { display: block !important; margin: 4px 0 !important; }
[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child { opacity:.45 !important; transform:scale(.75); }
[data-testid="stSidebar"] [role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
  background: transparent !important;
  border: 1px solid transparent !important;
  transition: all .15s ease;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover div[data-testid="stMarkdownContainer"] p {
  background: rgba(255,255,255,.08) !important;
  border-color: rgba(242,170,36,.22) !important;
}

/* Metrics readable */
[data-testid="metric-container"] * { color: var(--ache-navy) !important; }
[data-testid="metric-container"] label, [data-testid="metric-container"] [data-testid="stMetricLabel"] * { color: var(--ache-muted) !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] * { color: var(--ache-navy) !important; font-weight: 800 !important; }

/* Hero and cards spacing */
.ache-hero { margin-top: 0 !important; padding: 30px 34px !important; }
.ache-step { min-height: 210px !important; }
.ache-step h3 { line-height: 1.05 !important; margin-bottom: 10px !important; }
.ache-step p { line-height: 1.45 !important; }

/* Better general contrast */
.stMarkdown, .stText, p, li { color: #26384A; }
[data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span { color: rgba(255,255,255,.88) !important; }

/* Mobile friendliness */
@media (max-width: 768px) {
  .block-container { padding-left: .85rem !important; padding-right: .85rem !important; padding-top: 3.7rem !important; }
  .ache-hero { border-radius: 18px !important; padding: 22px 20px !important; }
  .ache-hero h1 { font-size: 1.9rem !important; }
  .ache-step { min-height: auto !important; }
  [data-testid="stSidebar"] img { max-height: 130px !important; }

  /* En mobile NO escondemos la barra de Streamlit porque contiene el botón para reabrir el menú */
  [data-testid="stHeader"] {
    height: 3.25rem !important;
    background: rgba(247,249,252,.96) !important;
    backdrop-filter: blur(10px) !important;
    box-shadow: 0 1px 0 rgba(23,53,85,.08) !important;
    visibility: visible !important;
  }
  [data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 999999 !important;
    position: fixed !important;
    top: .55rem !important;
    left: .55rem !important;
    background: var(--ache-navy) !important;
    border-radius: 999px !important;
    width: 42px !important;
    height: 42px !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 8px 22px rgba(23,53,85,.22) !important;
  }
  [data-testid="collapsedControl"] svg { fill: white !important; stroke: white !important; }

  .ache-mobile-nav-card { display: block !important; }
}

@media (min-width: 769px) {
  .ache-mobile-nav-card { display: none !important; }
}
</style>""", unsafe_allow_html=True)




st.markdown("""<style>
/* ── Ache product demo polish v3 ───────────────────────────── */
:root{
  --ache-navy:#173555;--ache-navy-dark:#0B1D2F;--ache-blue:#214666;
  --ache-yellow:#F2AA24;--ache-yellow-soft:#FFF3D8;
  --ache-bg:#F4F7FA;--ache-card:#FFFFFF;--ache-ink:#172B3F;--ache-muted:#68798A;--ache-line:#DCE5EE;
}
.block-container{max-width:1180px!important;padding-top:1.35rem!important;}
.ache-page-title{display:flex;align-items:flex-start;justify-content:space-between;gap:18px;margin:0 0 18px;}
.ache-page-title h1{font-size:2.15rem!important;line-height:1.05!important;margin:0!important;color:var(--ache-navy)!important;}
.ache-page-title p{margin:.45rem 0 0;color:var(--ache-muted);max-width:760px;line-height:1.45;}
.ache-status-pill{white-space:nowrap;border-radius:999px;padding:8px 12px;font-weight:800;font-size:.86rem;background:var(--ache-yellow-soft);color:#7A4E00;border:1px solid #F8D78F;}
.ache-product-card{background:var(--ache-card);border:1px solid var(--ache-line);border-radius:22px;padding:22px;box-shadow:0 12px 34px rgba(23,53,85,.075);}
.ache-product-card.compact{padding:16px 18px;border-radius:18px;}
.ache-section-label{font-size:.78rem;text-transform:uppercase;letter-spacing:.08em;font-weight:800;color:var(--ache-muted);margin-bottom:8px;}
.ache-flow{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin:18px 0 24px;}
.ache-flow-step{background:white;border:1px solid var(--ache-line);border-radius:18px;padding:15px;min-height:142px;box-shadow:0 8px 22px rgba(23,53,85,.055);}
.ache-flow-step strong{display:block;color:var(--ache-navy);font-size:1.03rem;line-height:1.12;margin:8px 0 6px;}
.ache-flow-step span{font-size:.94rem;color:var(--ache-muted);line-height:1.32;}
.ache-num{width:30px;height:30px;border-radius:10px;background:linear-gradient(135deg,var(--ache-yellow),#FFC65C);display:flex;align-items:center;justify-content:center;font-weight:900;color:var(--ache-navy);}
.ache-callout{border-radius:18px;padding:16px 18px;margin:12px 0;border:1px solid #CFE0F0;background:#EDF5FC;color:#173555;}
.ache-callout.warning{border-color:#F8D78F;background:#FFF7E8;color:#5E4100;}
.ache-cad-shell{background:white;border:1px solid var(--ache-line);border-radius:24px;padding:14px;box-shadow:0 16px 42px rgba(23,53,85,.09);}
.ache-cad-toolbar{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:0 0 12px;padding:4px 4px 10px;border-bottom:1px solid var(--ache-line);}
.ache-cad-toolbar h3{margin:0!important;font-size:1.18rem!important;color:var(--ache-navy)!important;}
.ache-cad-toolbar small{color:var(--ache-muted);display:block;margin-top:2px;}
.ache-cad-badge{background:#EEF4FA;border:1px solid #D5E3F0;color:var(--ache-navy);border-radius:999px;padding:7px 10px;font-weight:800;font-size:.82rem;}
.ache-param-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:12px;}
.ache-param{background:#F8FAFC;border:1px solid var(--ache-line);border-radius:16px;padding:12px;}
.ache-param b{display:block;color:var(--ache-navy);font-size:1.08rem;}.ache-param span{color:var(--ache-muted);font-size:.86rem;}
/* Streamlit widgets calmer */
[data-testid="stNumberInput"] label,[data-testid="stSelectbox"] label{font-weight:750!important;color:var(--ache-navy)!important;}
[data-testid="stSidebar"] img{max-height:132px!important;object-fit:contain!important;background:rgba(255,255,255,.96)!important;padding:8px!important;border-radius:18px!important;}
[data-testid="stSidebar"] hr{border-color:rgba(255,255,255,.14)!important;}
/* Plotly modebar: no longer on top of titles */
.js-plotly-plot .modebar{top:14px!important;right:14px!important;background:rgba(255,255,255,.96)!important;border:1px solid rgba(23,53,85,.12)!important;border-radius:14px!important;}
@media(max-width:900px){
 .ache-page-title{display:block}.ache-status-pill{display:inline-flex;margin-top:12px}.ache-flow{grid-template-columns:repeat(2,1fr)}.ache-param-grid{grid-template-columns:1fr}.ache-cad-toolbar{display:block}.ache-cad-badge{display:inline-flex;margin-top:8px}.block-container{padding-left:.9rem!important;padding-right:.9rem!important;}
}
@media(max-width:520px){.ache-flow{grid-template-columns:1fr}.ache-page-title h1{font-size:1.75rem!important}.ache-product-card{padding:16px;border-radius:18px}}
</style>""", unsafe_allow_html=True)



st.markdown("""<style>
/* ── UX correction: clean navigation + contrast ───────────────── */
/* Hide the old Streamlit top selectbox navigation on desktop and mobile; we replace it with clean links */
.ache-mobile-nav-card + div[data-testid="stSelectbox"] { display:none !important; }

.ache-mobile-linknav{display:none;}
@media(max-width:768px){
  .ache-mobile-linknav{
    display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;
    background:#FFFFFF;border:1px solid #DCE5EE;border-radius:18px;
    padding:12px;margin:0 0 16px;box-shadow:0 10px 28px rgba(23,53,85,.10);
  }
  .ache-mobile-linknav-title{grid-column:1/-1;font-weight:900;color:#173555;font-size:.92rem;margin-bottom:2px;}
  .ache-mobile-linknav a{
    display:flex;align-items:center;justify-content:center;min-height:42px;text-align:center;
    text-decoration:none!important;border-radius:12px;border:1px solid #DCE5EE;
    background:#F7FAFD;color:#173555!important;font-weight:800;font-size:.92rem;padding:8px 10px;
  }
  .ache-mobile-linknav a.primary{background:#173555;color:#FFFFFF!important;border-color:#173555;}
}

/* Stronger text contrast */
.stApp, .stMarkdown, .stText, p, li, label, span { color:#1C2F42; }
.ache-product-card p,.ache-step p,.ache-flow-step span,.ache-card p{color:#4F6173!important;}
.ache-product-card h1,.ache-product-card h2,.ache-product-card h3,
.ache-card h1,.ache-card h2,.ache-card h3{color:#173555!important;}
.ache-callout{color:#173555!important;}
.ache-callout *{color:inherit!important;}
.ache-callout.warning{color:#5B3B00!important;}
.ache-hero p{color:rgba(255,255,255,.86)!important;}
.ache-hero h1,.ache-hero .ache-pill{color:#FFFFFF!important;}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] span,[data-testid="stSidebar"] label,[data-testid="stSidebar"] .stMarkdown{color:rgba(255,255,255,.92)!important;}
[data-testid="stSidebar"] b,[data-testid="stSidebar"] strong{color:#FFFFFF!important;}
[data-testid="metric-container"]{background:#FFFFFF!important;}
[data-testid="metric-container"] *{color:#173555!important;}
[data-testid="metric-container"] label *{color:#5F7182!important;}

/* More breathing room, fewer random dark panels */
.ache-product-card,.ache-card,.ache-flow-step{background:#FFFFFF!important;}
hr{border-color:#DCE5EE!important;}
</style>""", unsafe_allow_html=True)



st.markdown("""<style>
/* ── Contrast audit hardening v4 ─────────────────────────────── */
:root { color-scheme: light; }
html, body, .stApp { background:#F4F7FA !important; color:#173555 !important; }
.block-container { color:#173555 !important; }

/* Typography: predictable contrast */
h1,h2,h3,h4,h5,h6 { color:#173555 !important; font-weight:800 !important; }
p, li, label, .stMarkdown, .stCaption, [data-testid="stMarkdownContainer"] { color:#26384A !important; }
small, caption, [data-testid="stCaptionContainer"], .caption { color:#5F7182 !important; }
a { color:#173555 !important; font-weight:700; }

/* Main navigation bar restored: desktop + mobile, no selectbox */
.ache-top-nav{
  display:flex;gap:8px;align-items:center;flex-wrap:wrap;
  background:#FFFFFF;border:1px solid #DCE5EE;border-radius:18px;
  padding:10px;margin:0 0 18px;box-shadow:0 10px 26px rgba(23,53,85,.075);
}
.ache-top-nav-title{font-size:.76rem;text-transform:uppercase;letter-spacing:.08em;font-weight:900;color:#6B7A8C;margin:0 8px 0 4px;}
.ache-top-nav a{
  text-decoration:none!important;color:#173555!important;background:#F7FAFD;
  border:1px solid #DCE5EE;border-radius:999px;padding:9px 13px;
  font-weight:800;font-size:.92rem;line-height:1;display:inline-flex;align-items:center;justify-content:center;
}
.ache-top-nav a:hover{background:#FFF3D8;border-color:#F2AA24;color:#173555!important;}
.ache-top-nav a.active{background:#173555;color:#FFFFFF!important;border-color:#173555;box-shadow:0 8px 18px rgba(23,53,85,.18);}
@media(max-width:768px){
  .ache-top-nav{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));border-radius:18px;padding:10px;margin-top:2px;}
  .ache-top-nav-title{grid-column:1/-1;margin:0 0 2px 2px;}
  .ache-top-nav a{border-radius:12px;min-height:42px;padding:9px 10px;font-size:.9rem;}
}

/* Streamlit buttons: never dark-on-dark */
.stButton > button, .stDownloadButton > button, button[kind="secondary"]{
  background:#FFFFFF !important;color:#173555 !important;border:1px solid #BFD0DF !important;
  border-radius:14px !important;font-weight:850 !important;box-shadow:0 6px 16px rgba(23,53,85,.08) !important;
}
.stButton > button:hover, .stDownloadButton > button:hover{
  background:#F7FAFD !important;color:#173555 !important;border-color:#F2AA24 !important;
}
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"], button[kind="primary"]{
  background:linear-gradient(90deg,#F2AA24,#FFBE45) !important;color:#173555 !important;
  border:1px solid #F2AA24 !important;box-shadow:0 12px 26px rgba(242,170,36,.25) !important;
}
.stButton > button[kind="primary"] *, .stDownloadButton > button[kind="primary"] *, button[kind="primary"] *{ color:#173555 !important; }
.stButton > button[kind="secondary"] *, .stDownloadButton > button[kind="secondary"] *, button[kind="secondary"] *{ color:#173555 !important; }

/* Expander / history cards: fix the dark header issue */
[data-testid="stExpander"]{
  background:#FFFFFF !important;border:1px solid #DCE5EE !important;border-radius:18px !important;
  box-shadow:0 8px 22px rgba(23,53,85,.055) !important;overflow:hidden !important;margin:12px 0 !important;
}
[data-testid="stExpander"] details{background:#FFFFFF !important;}
[data-testid="stExpander"] summary{
  background:#FFFFFF !important;color:#173555 !important;border-bottom:1px solid #EEF3F8 !important;
  min-height:56px !important;
}
[data-testid="stExpander"] summary *{color:#173555 !important;font-weight:850 !important;}
[data-testid="stExpander"] div[role="button"]{background:#FFFFFF !important;color:#173555 !important;}
[data-testid="stExpander"] div[role="button"] *{color:#173555 !important;}
[data-testid="stExpander"] svg{fill:#173555 !important;stroke:#173555 !important;}

/* Cards and callouts */
.ache-product-card,.ache-card,.ache-flow-step,.ache-cad-shell,[data-testid="metric-container"]{
  background:#FFFFFF !important;color:#173555 !important;border-color:#DCE5EE !important;
}
.ache-product-card *,.ache-card *,.ache-flow-step *,.ache-cad-shell *{color:inherit;}
.ache-muted,.ache-product-card p,.ache-flow-step span{color:#4F6173 !important;}
.ache-param span{color:#5F7182 !important;}.ache-param b{color:#173555 !important;}

/* Sidebar remains dark, but text must be white */
[data-testid="stSidebar"]{background:linear-gradient(180deg,#173555 0%,#0B1D2F 100%) !important;}
[data-testid="stSidebar"] *{color:rgba(255,255,255,.94) !important;}
[data-testid="stSidebar"] img{background:#FFFFFF !important;}
[data-testid="stSidebar"] label div[data-testid="stMarkdownContainer"] p{color:#FFFFFF !important;}
</style>""", unsafe_allow_html=True)



st.markdown("""<style>
/* ── Reduce Streamlit raw look v5 ────────────────────────────── */
/* Headers: less gigantic, more product-like */
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3{
  color:#173555 !important;
  letter-spacing:-.025em !important;
}
[data-testid="stMarkdownContainer"] h1{font-size:2.05rem !important;line-height:1.08 !important;margin-bottom:.45rem !important;}
[data-testid="stMarkdownContainer"] h2{font-size:1.72rem !important;line-height:1.12 !important;margin-bottom:.35rem !important;}
[data-testid="stMarkdownContainer"] h3{font-size:1.22rem !important;line-height:1.2 !important;}

/* Keep content centered and less empty on ultra-wide screens */
.block-container{max-width:1180px !important;padding-left:2.2rem !important;padding-right:2.2rem !important;}
@media(max-width:768px){.block-container{padding-left:.9rem !important;padding-right:.9rem !important;}}

/* Better history/case rows */
[data-testid="stExpander"] summary{
  padding:0 18px !important;
  font-size:1rem !important;
}
[data-testid="stExpander"] summary p{font-size:1rem !important;color:#173555 !important;}
[data-testid="stExpanderDetails"]{
  background:#FFFFFF !important;color:#173555 !important;padding:18px 22px 22px !important;
}
[data-testid="stExpanderDetails"] *{color:#26384A !important;}
[data-testid="stExpanderDetails"] strong{color:#173555 !important;}

/* Captions and metadata must be readable */
[data-testid="stCaptionContainer"] p,
[data-testid="stCaptionContainer"] span,
[data-testid="stCaptionContainer"]{
  color:#5C6F82 !important;font-weight:600 !important;
}

/* Download buttons: bigger but not shouting */
.stDownloadButton > button{min-height:48px !important;}
.stButton > button{min-height:44px !important;}
.stDownloadButton > button p,.stButton > button p{font-size:1rem !important;margin:0 !important;}

/* Plotly/chart area should not create dark text collisions */
.js-plotly-plot, .plot-container{background:#FFFFFF !important;border-radius:18px !important;}

/* Avoid accidental nearly-invisible navy-on-black from old inline blocks */
div[style*="rgba(255,255,255,.04)"], div[style*="rgba(255,255,255,.045)"]{
  background:#FFFFFF !important;border-color:#DCE5EE !important;color:#173555 !important;
}
div[style*="rgba(255,255,255,.04)"] *, div[style*="rgba(255,255,255,.045)"] *{color:#173555 !important;}
</style>""", unsafe_allow_html=True)



st.markdown("""<style>
/* ── Emergency stability/contrast fixes v6 ───────────────────── */
.ache-hero h1,
.ache-hero [data-testid="stMarkdownContainer"] h1,
.ache-hero * h1{
  color:#FFFFFF !important;
  text-shadow:0 2px 10px rgba(0,0,0,.14) !important;
}
.ache-hero p{color:rgba(255,255,255,.92) !important;}
.ache-hero .ache-pill{color:#FFFFFF !important;border-color:rgba(242,170,36,.55) !important;background:rgba(255,255,255,.10) !important;}
.ache-top-nav-label{font-size:.76rem;text-transform:uppercase;letter-spacing:.08em;font-weight:900;color:#6B7A8C;margin:0 0 8px 4px;}
.ache-nav-box{background:#FFFFFF;border:1px solid #DCE5EE;border-radius:18px;padding:12px 14px;margin:0 0 18px;box-shadow:0 10px 26px rgba(23,53,85,.075);}
/* Top nav buttons only */
div[data-testid="column"] .stButton > button{white-space:nowrap;min-height:42px !important;border-radius:999px !important;box-shadow:none !important;}
div[data-testid="column"] .stButton > button[kind="secondary"]{background:#F7FAFD !important;color:#173555 !important;border:1px solid #DCE5EE !important;}
div[data-testid="column"] .stButton > button[kind="secondary"] *{color:#173555 !important;}
div[data-testid="column"] .stButton > button[kind="primary"]{background:#173555 !important;color:#FFFFFF !important;border:1px solid #173555 !important;}
div[data-testid="column"] .stButton > button[kind="primary"] *{color:#FFFFFF !important;}
@media(max-width:768px){
  .ache-nav-box{padding:10px;margin-bottom:14px;}
  div[data-testid="column"] .stButton > button{border-radius:12px !important;font-size:.9rem !important;min-height:42px !important;padding-left:8px !important;padding-right:8px !important;}
}
</style>""", unsafe_allow_html=True)



st.markdown("""<style>
/* ── Brand/mobile cleanup v7 ─────────────────────────────────── */
.ache-brand-header{
  display:flex;align-items:center;gap:14px;background:#FFFFFF;border:1px solid #DCE5EE;
  border-radius:20px;padding:12px 16px;margin:0 0 14px;box-shadow:0 10px 26px rgba(23,53,85,.07);
}
.ache-brand-logo{width:74px;height:54px;display:flex;align-items:center;justify-content:center;flex:0 0 auto;}
.ache-brand-logo img{max-width:100%;max-height:100%;object-fit:contain;display:block;}
.ache-brand-title{font-size:1.05rem;font-weight:900;color:#173555;line-height:1.05;}
.ache-brand-subtitle{font-size:.9rem;font-weight:650;color:#5F7182;margin-top:2px;}
.ache-brand-tag{margin-left:auto;background:#FFF3D8;border:1px solid #F2AA24;color:#173555;font-size:.78rem;font-weight:900;border-radius:999px;padding:7px 10px;white-space:nowrap;}

/* Replace tall button stack with compact brand navigation */
.ache-nav-box{padding:11px 12px !important;}
.ache-top-nav-html{display:flex;gap:8px;align-items:center;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none;}
.ache-top-nav-html::-webkit-scrollbar{display:none;}
.ache-top-nav-html .label{font-size:.76rem;text-transform:uppercase;letter-spacing:.08em;font-weight:900;color:#6B7A8C;margin-right:8px;white-space:nowrap;}
.ache-top-nav-html a{display:inline-flex;align-items:center;justify-content:center;white-space:nowrap;text-decoration:none!important;background:#FFFFFF;color:#173555!important;border:1px solid #D6E1EC;border-radius:999px;padding:10px 15px;font-weight:850;line-height:1;}
.ache-top-nav-html a.active{background:#173555;color:#FFFFFF!important;border-color:#173555;}
.ache-top-nav-html a:hover{background:#FFF3D8;color:#173555!important;border-color:#F2AA24;}

.ache-status-strip{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:18px 0 20px;}
.ache-status-item{background:#FFFFFF;border:1px solid #DCE5EE;border-radius:16px;padding:14px 16px;box-shadow:0 8px 20px rgba(23,53,85,.055);}
.ache-status-item span{display:block;color:#5F7182!important;font-weight:750;font-size:.86rem;margin-bottom:4px;}
.ache-status-item b{display:block;color:#173555!important;font-size:1.45rem;line-height:1;font-weight:900;}

@media(max-width:768px){
  .block-container{padding-top:.8rem !important;}
  .ache-brand-header{border-radius:16px;padding:10px 12px;gap:10px;margin-bottom:10px;}
  .ache-brand-logo{width:58px;height:42px;}
  .ache-brand-title{font-size:.98rem;}.ache-brand-subtitle{font-size:.78rem;line-height:1.15;}.ache-brand-tag{display:none;}
  .ache-nav-box{border-radius:16px !important;padding:10px !important;margin-bottom:12px !important;}
  .ache-top-nav-html{gap:7px;}
  .ache-top-nav-html .label{display:none;}
  .ache-top-nav-html a{padding:10px 13px;font-size:.9rem;border-radius:999px;}
  .ache-hero{padding:20px 20px !important;border-radius:18px !important;margin-bottom:14px !important;}
  .ache-hero h1{font-size:1.8rem !important;line-height:1.08 !important;}
  .ache-hero p{font-size:1rem !important;line-height:1.42 !important;}
  .ache-status-strip{display:none;}
}
</style>""", unsafe_allow_html=True)



st.markdown("""<style>
/* ── Native navigation fix v8: no links, no new tabs ─────────── */
.ache-nav-native{
  background:#FFFFFF;border:1px solid #DCE5EE;border-radius:18px;
  padding:12px 14px;margin:0 0 18px;box-shadow:0 10px 26px rgba(23,53,85,.075);
}
.ache-nav-native-title{font-size:.76rem;text-transform:uppercase;letter-spacing:.08em;font-weight:900;color:#6B7A8C;margin-bottom:8px;}
/* Radio horizontal nav */
div[data-testid="stRadio"] label{cursor:pointer;}
div[data-testid="stRadio"] [role="radiogroup"]{gap:8px !important;flex-wrap:wrap !important;}
div[data-testid="stRadio"] [role="radiogroup"] label{
  background:#FFFFFF !important;border:1px solid #D6E1EC !important;border-radius:999px !important;
  padding:8px 13px !important;margin:0 !important;box-shadow:none !important;
}
div[data-testid="stRadio"] [role="radiogroup"] label:has(input:checked){
  background:#173555 !important;border-color:#173555 !important;
}
div[data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) p,
div[data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) span{color:#FFFFFF !important;}
div[data-testid="stRadio"] [role="radiogroup"] label p{font-weight:850 !important;color:#173555 !important;font-size:.92rem !important;}
div[data-testid="stRadio"] [role="radiogroup"] label > div:first-child{display:none !important;}
@media(max-width:768px){
  .ache-nav-native{padding:10px;border-radius:16px;margin-bottom:12px;}
  div[data-testid="stRadio"] [role="radiogroup"]{display:flex !important;overflow-x:auto !important;flex-wrap:nowrap !important;padding-bottom:2px !important;-webkit-overflow-scrolling:touch;scrollbar-width:none;}
  div[data-testid="stRadio"] [role="radiogroup"]::-webkit-scrollbar{display:none;}
  div[data-testid="stRadio"] [role="radiogroup"] label{flex:0 0 auto !important;padding:8px 12px !important;border-radius:999px !important;}
  div[data-testid="stRadio"] [role="radiogroup"] label p{font-size:.88rem !important;white-space:nowrap !important;}
}
</style>""", unsafe_allow_html=True)



st.markdown("""<style>
/* ── Remove old HTML nav leftovers v9 ─────────────────────────── */
.ache-top-nav-html{display:none !important;}
</style>""", unsafe_allow_html=True)



st.markdown("""<style>
/* ── Repair desktop after mobile nav v10 ─────────────────────── */
/* remove giant top whitespace */
.block-container{padding-top:.45rem !important;}
@media(min-width:769px){.block-container{padding-top:.65rem !important;}}

/* Restore sidebar labels: previous mobile radio styles accidentally hit sidebar */
[data-testid="stSidebar"] div[data-testid="stRadio"] [role="radiogroup"]{
  display:flex !important;flex-direction:column !important;gap:8px !important;overflow:visible !important;
}
[data-testid="stSidebar"] div[data-testid="stRadio"] [role="radiogroup"] label{
  display:flex !important;align-items:center !important;gap:8px !important;
  background:transparent !important;border:1px solid transparent !important;border-radius:16px !important;
  padding:10px 12px !important;margin:0 !important;color:#FFFFFF !important;
}
[data-testid="stSidebar"] div[data-testid="stRadio"] [role="radiogroup"] label:hover{
  background:rgba(255,255,255,.08) !important;border-color:rgba(242,170,36,.20) !important;
}
[data-testid="stSidebar"] div[data-testid="stRadio"] [role="radiogroup"] label:has(input:checked){
  background:rgba(242,170,36,.16) !important;border-color:rgba(242,170,36,.28) !important;
}
[data-testid="stSidebar"] div[data-testid="stRadio"] [role="radiogroup"] label > div:first-child{
  display:flex !important;opacity:.55 !important;transform:scale(.78) !important;
}
[data-testid="stSidebar"] div[data-testid="stRadio"] [role="radiogroup"] label p{
  color:#FFFFFF !important;font-weight:800 !important;font-size:1rem !important;white-space:normal !important;
  padding:0 !important;margin:0 !important;
}

/* New stable section bar using Streamlit pills */
.ache-nav-pills{
  background:#FFFFFF;border:1px solid #DCE5EE;border-radius:18px;
  padding:12px 14px;margin:0 0 18px;box-shadow:0 10px 26px rgba(23,53,85,.075);
}
.ache-nav-pills-title{font-size:.76rem;text-transform:uppercase;letter-spacing:.08em;font-weight:900;color:#6B7A8C;margin-bottom:8px;}
.ache-nav-pills div[data-testid="stPills"] button,
.ache-nav-pills div[data-testid="stSegmentedControl"] button{
  border-radius:999px !important;font-weight:850 !important;color:#173555 !important;
}
.ache-nav-pills div[data-testid="stPills"] button[aria-pressed="true"],
.ache-nav-pills div[data-testid="stSegmentedControl"] button[aria-pressed="true"]{
  background:#173555 !important;color:#FFFFFF !important;border-color:#173555 !important;
}
.ache-nav-pills div[data-testid="stPills"] button[aria-pressed="true"] *,
.ache-nav-pills div[data-testid="stSegmentedControl"] button[aria-pressed="true"] *{color:#FFFFFF !important;}
@media(max-width:768px){
  .ache-nav-pills{padding:10px;border-radius:16px;margin-bottom:12px;}
  .ache-nav-pills-title{display:none;}
}
</style>""", unsafe_allow_html=True)



st.markdown("""<style>
/* ── Remove invisible CSS block gaps v11 ─────────────────────── */
[data-testid="stElementContainer"]:has(style){display:none !important;height:0 !important;margin:0 !important;padding:0 !important;}
[data-testid="stMarkdown"]:has(style){display:none !important;height:0 !important;margin:0 !important;padding:0 !important;}
[data-testid="stHeader"]{display:none !important;height:0 !important;min-height:0 !important;}
.block-container{padding-top:.75rem !important;}
</style>""", unsafe_allow_html=True)



st.markdown("""<style>
/* ── FINAL pills contrast fix v12 ────────────────────────────── */
/* Streamlit renders st.pills outside our wrapper, so this must target stPills directly. */
div[data-testid="stPills"] button,
div[data-testid="stPills"] button[kind],
div[data-testid="stPills"] [role="button"]{
  background:#FFFFFF !important;
  color:#173555 !important;
  border:1px solid #D6E1EC !important;
  border-radius:999px !important;
  box-shadow:0 4px 12px rgba(23,53,85,.05) !important;
  font-weight:850 !important;
}
div[data-testid="stPills"] button *,
div[data-testid="stPills"] [role="button"] *{
  color:#173555 !important;
  fill:#173555 !important;
}
div[data-testid="stPills"] button[aria-pressed="true"],
div[data-testid="stPills"] button[aria-selected="true"],
div[data-testid="stPills"] button[aria-checked="true"],
div[data-testid="stPills"] [role="button"][aria-pressed="true"],
div[data-testid="stPills"] [role="button"][aria-selected="true"],
div[data-testid="stPills"] [role="button"][aria-checked="true"]{
  background:#173555 !important;
  color:#FFFFFF !important;
  border-color:#173555 !important;
}
div[data-testid="stPills"] button[aria-pressed="true"] *,
div[data-testid="stPills"] button[aria-selected="true"] *,
div[data-testid="stPills"] button[aria-checked="true"] *,
div[data-testid="stPills"] [role="button"][aria-pressed="true"] *,
div[data-testid="stPills"] [role="button"][aria-selected="true"] *,
div[data-testid="stPills"] [role="button"][aria-checked="true"] *{
  color:#FFFFFF !important;
  fill:#FFFFFF !important;
}
</style>""", unsafe_allow_html=True)



st.markdown("""<style>
/* ── Mobile nav reliability fix v13 ──────────────────────────── */
.ache-mobile-select-nav{display:none;}
.ache-desktop-pills-nav{display:block;}
@media(max-width:768px){
  .ache-desktop-pills-nav{display:none !important;}
  .ache-mobile-select-nav{
    display:block !important;background:#FFFFFF;border:1px solid #DCE5EE;border-radius:16px;
    padding:12px;margin:0 0 12px;box-shadow:0 8px 22px rgba(23,53,85,.07);
  }
  .ache-mobile-select-nav-title{font-size:.76rem;text-transform:uppercase;letter-spacing:.08em;font-weight:900;color:#6B7A8C;margin-bottom:8px;}
  .ache-mobile-select-nav [data-testid="stSelectbox"] label{display:none !important;}
  .ache-mobile-select-nav [data-baseweb="select"]{
    background:#F7FAFD !important;border:1px solid #D6E1EC !important;border-radius:12px !important;
  }
  .ache-mobile-select-nav [data-baseweb="select"] *{color:#173555 !important;font-weight:800 !important;}
}
</style>""", unsafe_allow_html=True)



st.markdown("""<style>
/* ── ABSOLUTE nav contrast fix v14 ───────────────────────────── */
/* No more dark section pills. Every nav control stays light with navy text. */
.ache-nav-pills,
.ache-desktop-pills-nav,
.ache-mobile-select-nav{
  background:#FFFFFF !important;
  color:#173555 !important;
}

/* Desktop section pills: force readable contrast regardless of Streamlit internals */
div[data-testid="stPills"],
div[data-testid="stPills"] *,
div[data-testid="stPills"] button,
div[data-testid="stPills"] [role="button"],
div[data-testid="stPills"] label,
div[data-testid="stPills"] div{
  color:#173555 !important;
}
div[data-testid="stPills"] button,
div[data-testid="stPills"] [role="button"],
div[data-testid="stPills"] label{
  background:#FFFFFF !important;
  border:1px solid #D6E1EC !important;
  border-radius:999px !important;
  box-shadow:0 4px 12px rgba(23,53,85,.05) !important;
  font-weight:850 !important;
}
div[data-testid="stPills"] button *,
div[data-testid="stPills"] [role="button"] *,
div[data-testid="stPills"] label *{
  color:#173555 !important;
  fill:#173555 !important;
  opacity:1 !important;
}

/* Selected/active pill: use yellow border/background, NOT dark navy */
div[data-testid="stPills"] button[aria-pressed="true"],
div[data-testid="stPills"] button[aria-selected="true"],
div[data-testid="stPills"] button[aria-checked="true"],
div[data-testid="stPills"] [role="button"][aria-pressed="true"],
div[data-testid="stPills"] [role="button"][aria-selected="true"],
div[data-testid="stPills"] [role="button"][aria-checked="true"]{
  background:#FFF3D8 !important;
  color:#173555 !important;
  border:2px solid #F2AA24 !important;
}
div[data-testid="stPills"] button[aria-pressed="true"] *,
div[data-testid="stPills"] button[aria-selected="true"] *,
div[data-testid="stPills"] button[aria-checked="true"] *,
div[data-testid="stPills"] [role="button"][aria-pressed="true"] *,
div[data-testid="stPills"] [role="button"][aria-selected="true"] *,
div[data-testid="stPills"] [role="button"][aria-checked="true"] *{
  color:#173555 !important;
  fill:#173555 !important;
  opacity:1 !important;
}

/* Mobile select contrast */
.ache-mobile-select-nav [data-baseweb="select"],
.ache-mobile-select-nav [data-baseweb="select"] > div{
  background:#FFFFFF !important;
  color:#173555 !important;
  border-color:#D6E1EC !important;
}
.ache-mobile-select-nav [data-baseweb="select"] *{
  color:#173555 !important;
  fill:#173555 !important;
  opacity:1 !important;
}
</style>""", unsafe_allow_html=True)



st.markdown("""<style>
/* ── Single custom nav v15: kill duplicate Streamlit nav widgets ─ */
/* If any previous pills/select remnants render, hide them. */
.ache-desktop-pills-nav,
.ache-mobile-select-nav,
.ache-nav-pills,
div[data-testid="stPills"]{
  display:none !important;
  height:0 !important;
  margin:0 !important;
  padding:0 !important;
  overflow:hidden !important;
}
</style>""", unsafe_allow_html=True)



st.markdown("""<style>
/* ── Smooth internal nav v16 ─────────────────────────────────── */
.ache-nav-lite{
  background:#FFFFFF;border:1px solid #DCE5EE;border-radius:18px;
  padding:12px 14px;margin:0 0 18px;box-shadow:0 10px 26px rgba(23,53,85,.075);
}
.ache-nav-lite-title{font-size:.76rem;text-transform:uppercase;letter-spacing:.08em;font-weight:900;color:#6B7A8C;margin-bottom:8px;}
/* hide old iframe/component nav if any browser cache keeps it around */
iframe[title="streamlit-component"]{max-height:0 !important;display:none !important;}
@media(max-width:768px){
  .ache-nav-lite{padding:10px;border-radius:16px;margin-bottom:12px;}
  .ache-nav-lite-title{display:none;}
}
</style>""", unsafe_allow_html=True)



st.markdown("""<style>
/* ==========================================================================
   ACHE CONTRAST SYSTEM — final accessibility pass 2026-06-23
   This block intentionally comes last: it neutralizes accumulated old CSS
   that caused dark text on dark buttons/cards and pale text on white cards.
   ========================================================================== */
:root{
  --ache-readable:#173555;
  --ache-readable-2:#26384A;
  --ache-muted-readable:#536679;
  --ache-white:#FFFFFF;
  --ache-bg-soft:#F7FAFD;
  --ache-line-strong:#C8D6E4;
  --ache-yellow-strong:#F2AA24;
  --ache-danger-readable:#8B1E1E;
  --ache-success-readable:#1F5F32;
  --ache-warning-readable:#6B4700;
}

/* Base readable text */
.stApp,
.block-container,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] label,
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] *{
  color:var(--ache-readable-2) !important;
}

h1,h2,h3,h4,h5,h6,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4,
[data-testid="stMarkdownContainer"] strong,
[data-testid="stMarkdownContainer"] b{
  color:var(--ache-readable) !important;
}

/* Hero / dark brand areas must stay light */
.ache-hero,
.ache-hero *,
.ache-brand-dark,
.ache-brand-dark *,
div[style*="background:#1B335C"] *,
div[style*="background: #1B335C"] *,
div[style*="background:#173555"] *,
div[style*="background: #173555"] *,
div[style*="background:linear-gradient"] .ache-hero *{
  color:var(--ache-white) !important;
}
.ache-hero p,
.ache-hero span,
.ache-hero li{color:rgba(255,255,255,.92) !important;}

/* Sidebar: no dark text on navy */
[data-testid="stSidebar"],
[data-testid="stSidebar"] *,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] li,
[data-testid="stSidebar"] strong{
  color:var(--ache-white) !important;
}
[data-testid="stSidebar"] img{background:#FFFFFF !important;}

/* Buttons: every button gets explicit text/background contrast */
.stButton > button,
.stDownloadButton > button,
button[kind="secondary"],
button[data-testid="baseButton-secondary"]{
  background:#FFFFFF !important;
  color:var(--ache-readable) !important;
  border:1px solid var(--ache-line-strong) !important;
  box-shadow:none !important;
}
.stButton > button *,
.stDownloadButton > button *,
button[kind="secondary"] *,
button[data-testid="baseButton-secondary"] *{
  color:var(--ache-readable) !important;
  opacity:1 !important;
}
.stButton > button:hover,
.stDownloadButton > button:hover{
  background:#FFF3D8 !important;
  color:var(--ache-readable) !important;
  border-color:var(--ache-yellow-strong) !important;
}
.stButton > button[kind="primary"],
.stDownloadButton > button[kind="primary"],
button[kind="primary"],
button[data-testid="baseButton-primary"]{
  background:linear-gradient(90deg,#F2AA24,#FFBE45) !important;
  color:var(--ache-readable) !important;
  border:1px solid #E29A16 !important;
}
.stButton > button[kind="primary"] *,
.stDownloadButton > button[kind="primary"] *,
button[kind="primary"] *,
button[data-testid="baseButton-primary"] *{
  color:var(--ache-readable) !important;
  opacity:1 !important;
}

/* Top navigation columns: readable inactive + active */
div[data-testid="column"] .stButton > button[kind="secondary"]{
  background:#FFFFFF !important;
  color:var(--ache-readable) !important;
  border:1px solid var(--ache-line-strong) !important;
}
div[data-testid="column"] .stButton > button[kind="secondary"] *{color:var(--ache-readable) !important;}
div[data-testid="column"] .stButton > button[kind="primary"]{
  background:#F2AA24 !important;
  color:var(--ache-readable) !important;
  border:1px solid #E29A16 !important;
}
div[data-testid="column"] .stButton > button[kind="primary"] *{color:var(--ache-readable) !important;}

/* Inputs / dropdowns / textarea */
input, textarea,
[data-baseweb="select"],
[data-baseweb="select"] *,
[data-testid="stTextInput"] *,
[data-testid="stNumberInput"] *,
[data-testid="stTextArea"] *,
[data-testid="stSelectbox"] *{
  color:var(--ache-readable) !important;
}
input, textarea,
[data-baseweb="select"]{
  background:#FFFFFF !important;
  border-color:var(--ache-line-strong) !important;
}

/* Tabs: inactive and selected readable */
[data-testid="stTabs"] button,
[data-testid="stTabs"] button *{
  color:var(--ache-readable) !important;
  opacity:1 !important;
}
[data-testid="stTabs"] button[aria-selected="true"],
[data-testid="stTabs"] button[aria-selected="true"] *{
  color:var(--ache-readable) !important;
  font-weight:850 !important;
}

/* Expanders/cards/metrics */
[data-testid="stExpander"],
[data-testid="stExpander"] *,
[data-testid="metric-container"],
[data-testid="metric-container"] *,
.ache-card,
.ache-card *,
.ache-product-card,
.ache-product-card *,
.ache-flow-step,
.ache-flow-step *,
.ache-status-item,
.ache-status-item *{
  color:var(--ache-readable) !important;
}
.ache-muted,
.ache-flow-step span,
.ache-product-card p,
.ache-brand-subtitle,
.ache-status-item span,
small,
caption{
  color:var(--ache-muted-readable) !important;
}

/* Alerts / callouts: explicit readable semantic colors */
.ache-info,
.ache-info *,
.ache-callout,
.ache-callout *{color:var(--ache-readable) !important;}
.ache-warning,
.ache-warning *,
.ache-callout.warning,
.ache-callout.warning *{color:var(--ache-warning-readable) !important;}
[data-testid="stAlert"] *{opacity:1 !important;}

/* Tables generated inside Markdown / guide */
table, table td, table td *, table tbody, table tbody *{
  color:var(--ache-readable-2) !important;
}
table th, table th *{
  color:#FFFFFF !important;
}

/* Plotly toolbar */
.js-plotly-plot .modebar{background:#FFFFFF !important;border:1px solid var(--ache-line-strong) !important;}
.js-plotly-plot .modebar-btn svg{fill:var(--ache-readable) !important;opacity:1 !important;}

/* Safety: any black/dark inline pills/cards with non-white children */
div[style*="background:#0"],
div[style*="background: #0"],
div[style*="background:#1"],
div[style*="background: #1"]{
  color:#FFFFFF !important;
}
div[style*="background:#0"] *,
div[style*="background: #0"] *,
div[style*="background:#1"] *,
div[style*="background: #1"] *{
  color:#FFFFFF !important;
}
</style>""", unsafe_allow_html=True)



st.markdown("""<style>
/* ────────────────────────────────────────────────────────────────
   TARGETED CONTRAST FIX v18 — no layout changes
   Fixes only visible low-contrast components reported in QA.
   ──────────────────────────────────────────────────────────────── */

/* 1) Hero / dark blue cards: never allow navy text over navy background */
.ache-hero,
.ache-hero *,
.ache-hero h1,
.ache-hero h2,
.ache-hero h3,
.ache-hero p,
.ache-hero span,
.ache-hero strong,
.ache-hero b,
.ache-hero [data-testid="stMarkdownContainer"],
.ache-hero [data-testid="stMarkdownContainer"] * {
  color: #FFFFFF !important;
  opacity: 1 !important;
}
.ache-hero p,
.ache-hero li,
.ache-hero small { color: rgba(255,255,255,.92) !important; }

/* 2) Any dark inline header/card from guide module must have white text */
div[style*="background:#173555"],
div[style*="background:#173555"] *,
div[style*="background: #173555"],
div[style*="background: #173555"] *,
div[style*="background:#1B335C"],
div[style*="background:#1B335C"] *,
div[style*="background: #1B335C"],
div[style*="background: #1B335C"] *,
div[style*="background:#102840"],
div[style*="background:#102840"] *,
div[style*="background:#0B1D2F"],
div[style*="background:#0B1D2F"] * {
  color: #FFFFFF !important;
  opacity: 1 !important;
}

/* 3) Sidebar status/warning/info cards: white text on dark sidebar */
[data-testid="stSidebar"] [data-testid="stAlert"],
[data-testid="stSidebar"] [data-testid="stAlert"] *,
[data-testid="stSidebar"] .stAlert,
[data-testid="stSidebar"] .stAlert *,
[data-testid="stSidebar"] div[role="alert"],
[data-testid="stSidebar"] div[role="alert"] * {
  color: #FFFFFF !important;
  opacity: 1 !important;
}
[data-testid="stSidebar"] [data-testid="stAlert"] strong,
[data-testid="stSidebar"] div[role="alert"] strong {
  color: #FFFFFF !important;
}

/* 4) Selectbox: force light control + navy text everywhere */
[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stSelectbox"] [data-baseweb="select"] div {
  background: #FFFFFF !important;
  color: #173555 !important;
  border-color: #BFD0DF !important;
  opacity: 1 !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] *,
[data-testid="stSelectbox"] [data-baseweb="select"] input,
[data-testid="stSelectbox"] [data-baseweb="select"] span,
[data-testid="stSelectbox"] [data-baseweb="select"] svg {
  color: #173555 !important;
  fill: #173555 !important;
  opacity: 1 !important;
}

/* 5) Dropdown menu/options: light background and readable text */
div[data-baseweb="popover"],
div[data-baseweb="popover"] *,
ul[role="listbox"],
ul[role="listbox"] *,
li[role="option"],
li[role="option"] * {
  background: #FFFFFF !important;
  color: #173555 !important;
  opacity: 1 !important;
}
li[role="option"]:hover,
li[role="option"][aria-selected="true"] {
  background: #FFF3D8 !important;
  color: #173555 !important;
}

/* 6) Text inputs/textarea placeholders: visible but not too pale */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
  background: #FFFFFF !important;
  color: #173555 !important;
  border-color: #BFD0DF !important;
  opacity: 1 !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder,
[data-testid="stNumberInput"] input::placeholder {
  color: #6B7A8C !important;
  opacity: 1 !important;
}

/* 7) Number steppers: no blue signs on black block */
[data-testid="stNumberInput"] button,
[data-testid="stNumberInput"] button * {
  background: #FFFFFF !important;
  color: #173555 !important;
  fill: #173555 !important;
  opacity: 1 !important;
  border-color: #BFD0DF !important;
}

/* 8) Red/destructive looking primary buttons: white text if Streamlit paints them red */
.stButton > button[style*="255, 75, 75"],
.stButton > button[style*="#ff4b4b"],
.stButton > button[style*="#FF4B4B"],
.stButton > button[style*="red"] {
  color: #FFFFFF !important;
}
.stButton > button[style*="255, 75, 75"] *,
.stButton > button[style*="#ff4b4b"] *,
.stButton > button[style*="#FF4B4B"] *,
.stButton > button[style*="red"] * {
  color: #FFFFFF !important;
}
</style>""", unsafe_allow_html=True)



st.markdown("""<style>
/* ────────────────────────────────────────────────────────────────
   ACHE PALETTE + CONTRAST FIX v19 — targeted, no layout rewrite
   Purpose: remove off-brand gray/black controls and guarantee readable text.
   ──────────────────────────────────────────────────────────────── */
:root{
  --ache-navy:#173555;
  --ache-navy-2:#0F2A44;
  --ache-orange:#F2AA24;
  --ache-orange-2:#FFBE45;
  --ache-sky:#D6E6F5;
  --ache-line:#C8D8E8;
  --ache-muted:#5B6E82;
  --ache-bg:#F6FAFE;
  --ache-white:#FFFFFF;
}

/* Brand dark hero/card: white text only, never navy-on-navy */
.ache-hero h1,.ache-hero h2,.ache-hero h3,.ache-hero p,.ache-hero span,.ache-hero b,.ache-hero strong,
.ache-hero [data-testid="stMarkdownContainer"],.ache-hero [data-testid="stMarkdownContainer"] *{
  color:#FFFFFF !important; opacity:1 !important;
}
.ache-hero p{color:rgba(255,255,255,.94) !important;}

/* Inputs: clean Ache form fields, not thick black boxes */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stSelectbox"] [data-baseweb="select"] > div{
  background:#FFFFFF !important;
  color:var(--ache-navy) !important;
  border:1.5px solid var(--ache-line) !important;
  border-radius:12px !important;
  box-shadow:none !important;
  outline:none !important;
  opacity:1 !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stSelectbox"] [data-baseweb="select"]:focus-within{
  border-color:var(--ache-orange) !important;
  box-shadow:0 0 0 3px rgba(242,170,36,.18) !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder,
[data-testid="stNumberInput"] input::placeholder{
  color:#7A8A9B !important; opacity:1 !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] *,
[data-testid="stSelectbox"] [data-baseweb="select"] input,
[data-testid="stSelectbox"] [data-baseweb="select"] span,
[data-testid="stSelectbox"] [data-baseweb="select"] svg{
  color:var(--ache-navy) !important; fill:var(--ache-navy) !important; opacity:1 !important;
}
/* Dropdown menu itself */
div[data-baseweb="popover"],div[data-baseweb="popover"] *,ul[role="listbox"],ul[role="listbox"] *,li[role="option"],li[role="option"] *{
  background:#FFFFFF !important; color:var(--ache-navy) !important; opacity:1 !important;
}
li[role="option"]:hover,li[role="option"][aria-selected="true"]{background:#FFF4DA !important;color:var(--ache-navy) !important;}

/* Number +/- controls: no black tail */
[data-testid="stNumberInput"] button,
[data-testid="stNumberInput"] button *{
  background:#F7FAFD !important;
  color:var(--ache-navy) !important;
  fill:var(--ache-navy) !important;
  border-color:var(--ache-line) !important;
  box-shadow:none !important;
  opacity:1 !important;
}
[data-testid="stNumberInput"] button:hover,
[data-testid="stNumberInput"] button:hover *{background:#FFF4DA !important;color:var(--ache-navy) !important;fill:var(--ache-navy) !important;}

/* Buttons: Ache palette; no Streamlit red/off-brand primary */
.stButton > button[kind="primary"],
button[data-testid="baseButton-primary"],
.stDownloadButton > button[kind="primary"]{
  background:linear-gradient(90deg,var(--ache-orange),var(--ache-orange-2)) !important;
  color:var(--ache-navy) !important;
  border:1px solid #E49C18 !important;
  box-shadow:0 10px 22px rgba(242,170,36,.20) !important;
}
.stButton > button[kind="primary"] *,button[data-testid="baseButton-primary"] *, .stDownloadButton > button[kind="primary"] *{
  color:var(--ache-navy) !important; fill:var(--ache-navy) !important; opacity:1 !important;
}
.stButton > button[kind="secondary"],.stDownloadButton > button[kind="secondary"],button[data-testid="baseButton-secondary"]{
  background:#FFFFFF !important; color:var(--ache-navy) !important; border:1px solid var(--ache-line) !important; box-shadow:none !important;
}
.stButton > button[kind="secondary"] *, .stDownloadButton > button[kind="secondary"] *, button[data-testid="baseButton-secondary"] *{
  color:var(--ache-navy) !important; fill:var(--ache-navy) !important; opacity:1 !important;
}

/* Top section bar: active orange, inactive white; all readable */
.ache-nav-lite .stButton > button{min-height:42px !important;border-radius:999px !important;}
.ache-nav-lite .stButton > button[kind="primary"]{
  background:linear-gradient(90deg,var(--ache-orange),var(--ache-orange-2)) !important;
  color:var(--ache-navy) !important;
  border:1px solid #E49C18 !important;
}
.ache-nav-lite .stButton > button[kind="primary"] *{color:var(--ache-navy) !important;}
.ache-nav-lite .stButton > button[kind="secondary"]{background:#FFFFFF !important;color:var(--ache-navy) !important;border:1px solid var(--ache-line) !important;}
.ache-nav-lite .stButton > button[kind="secondary"] *{color:var(--ache-navy) !important;}

/* Sidebar: selected state inside Ache palette, not gray. */
[data-testid="stSidebar"] [role="radiogroup"] label{
  background:transparent !important;
  border:1px solid transparent !important;
  box-shadow:none !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{
  background:rgba(255,255,255,.08) !important;
  border-color:rgba(242,170,36,.35) !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){
  background:rgba(242,170,36,.22) !important;
  border:1px solid rgba(242,170,36,.82) !important;
  box-shadow:0 0 0 1px rgba(242,170,36,.08) inset !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label p,
[data-testid="stSidebar"] [role="radiogroup"] label span,
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p,
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) span{
  color:#FFFFFF !important; opacity:1 !important;
}
/* Sidebar case status card */
[data-testid="stSidebar"] div[style*="rgba(242,170,36,.12)"]{
  background:rgba(242,170,36,.14) !important;
  border:1px solid rgba(242,170,36,.55) !important;
  border-left:4px solid var(--ache-orange) !important;
}
[data-testid="stSidebar"] div[style*="rgba(242,170,36,.12)"] b{color:#FFFFFF !important;}
[data-testid="stSidebar"] div[style*="rgba(242,170,36,.12)"] span{color:rgba(255,255,255,.88) !important; opacity:1 !important;}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] *{color:rgba(255,255,255,.86) !important;}

/* Guide mini hero replacing the problematic dark block */
.ache-guide-minihero{
  background:#FFFFFF !important;
  border:1px solid var(--ache-line) !important;
  border-left:5px solid var(--ache-orange) !important;
  border-radius:16px !important;
  padding:16px 18px !important;
  margin:0 0 16px 0 !important;
  box-shadow:0 10px 24px rgba(23,53,85,.06) !important;
}
.ache-guide-kicker{color:var(--ache-navy) !important;font-weight:900 !important;font-size:1.12rem !important;line-height:1.25 !important;}
.ache-guide-subtitle{color:var(--ache-muted) !important;font-weight:650 !important;margin-top:5px !important;}

/* Specific safety: any Ache dark panel must have readable white text */
div[style*="background:#173555"] *, div[style*="background: #173555"] *, div[style*="background:#1B335C"] *, div[style*="background: #1B335C"] *{
  color:#FFFFFF !important; opacity:1 !important;
}
</style>""", unsafe_allow_html=True)



st.markdown("""<style>
/* ────────────────────────────────────────────────────────────────
   ACHE HARD CONTRAST/POLISH FIX v20
   Fixes BaseWeb wrappers, form submit buttons, sidebar active state.
   ──────────────────────────────────────────────────────────────── */
:root{--ache-navy:#173555;--ache-dark:#0B1D2F;--ache-orange:#F2AA24;--ache-orange-2:#FFBE45;--ache-border:#C9D8E8;--ache-bg:#F7FAFD;--ache-muted:#657789;--ache-white:#FFFFFF;}

/* FORM CONTROLS — style the real BaseWeb wrappers, not only the inner input */
[data-baseweb="input"],
[data-baseweb="input"] > div,
[data-baseweb="base-input"],
[data-baseweb="textarea"],
[data-baseweb="textarea"] > div,
[data-testid="stTextInput"] div,
[data-testid="stTextArea"] div,
[data-testid="stNumberInput"] div[data-baseweb="input"],
[data-testid="stNumberInput"] div[data-baseweb="input"] > div,
[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stSelectbox"] [data-baseweb="select"] > div{
  background:#FFFFFF !important;
  border-color:var(--ache-border) !important;
  border-width:1.25px !important;
  border-radius:14px !important;
  box-shadow:none !important;
  outline:none !important;
}
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] [data-baseweb="select"] *,
[data-testid="stSelectbox"] [data-baseweb="select"] input{
  color:var(--ache-navy) !important;
  background:#FFFFFF !important;
  opacity:1 !important;
  -webkit-text-fill-color:var(--ache-navy) !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder,
[data-testid="stNumberInput"] input::placeholder{
  color:#738497 !important;
  opacity:1 !important;
  -webkit-text-fill-color:#738497 !important;
}
[data-baseweb="input"]:focus-within,
[data-baseweb="textarea"]:focus-within,
[data-testid="stSelectbox"] [data-baseweb="select"]:focus-within{
  border-color:var(--ache-orange) !important;
  box-shadow:0 0 0 3px rgba(242,170,36,.18) !important;
}
/* Avoid black browser outline remnants */
input, textarea, select, button, [role="button"]{outline-color:var(--ache-orange) !important;}

/* Number steppers: separated but not black */
[data-testid="stNumberInput"] button,
[data-testid="stNumberInput"] button[kind],
[data-testid="stNumberInput"] button *{
  background:#FFFFFF !important;
  color:var(--ache-navy) !important;
  fill:var(--ache-navy) !important;
  border-color:var(--ache-border) !important;
  box-shadow:none !important;
  opacity:1 !important;
}
[data-testid="stNumberInput"] button:hover,
[data-testid="stNumberInput"] button:hover *{background:#FFF4DA !important;color:var(--ache-navy) !important;fill:var(--ache-navy) !important;}

/* All submit/primary buttons in Ache palette. This catches st.form_submit_button too. */
[data-testid="stFormSubmitButton"] button,
[data-testid="stFormSubmitButton"] button *,
.stButton > button[kind="primary"],
.stButton > button[kind="primary"] *,
button[data-testid="baseButton-primary"],
button[data-testid="baseButton-primary"] *{
  color:var(--ache-navy) !important;
  fill:var(--ache-navy) !important;
  opacity:1 !important;
  -webkit-text-fill-color:var(--ache-navy) !important;
}
[data-testid="stFormSubmitButton"] button,
.stButton > button[kind="primary"],
button[data-testid="baseButton-primary"]{
  background:linear-gradient(90deg,var(--ache-orange),var(--ache-orange-2)) !important;
  border:1px solid #E49C18 !important;
  border-radius:14px !important;
  box-shadow:0 10px 22px rgba(242,170,36,.22) !important;
}

/* Top section buttons */
.ache-nav-lite [data-testid="stButton"] button{border-radius:999px !important;}
.ache-nav-lite [data-testid="stButton"] button[kind="primary"]{background:linear-gradient(90deg,var(--ache-orange),var(--ache-orange-2)) !important;color:var(--ache-navy) !important;border-color:#E49C18 !important;}
.ache-nav-lite [data-testid="stButton"] button[kind="primary"] *{color:var(--ache-navy) !important;-webkit-text-fill-color:var(--ache-navy) !important;}
.ache-nav-lite [data-testid="stButton"] button[kind="secondary"]{background:#FFFFFF !important;color:var(--ache-navy) !important;border-color:var(--ache-border) !important;}
.ache-nav-lite [data-testid="stButton"] button[kind="secondary"] *{color:var(--ache-navy) !important;-webkit-text-fill-color:var(--ache-navy) !important;}

/* SIDEBAR — selected item: no gray box. Ache orange active pill. */
[data-testid="stSidebar"] [role="radiogroup"] label,
[data-testid="stSidebar"] [role="radiogroup"] label div[data-testid="stMarkdownContainer"] p{
  background:transparent !important;
  border-color:transparent !important;
  box-shadow:none !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover div[data-testid="stMarkdownContainer"] p{
  background:rgba(255,255,255,.08) !important;
  border-color:rgba(242,170,36,.35) !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p{
  background:linear-gradient(90deg,var(--ache-orange),var(--ache-orange-2)) !important;
  color:var(--ache-navy) !important;
  -webkit-text-fill-color:var(--ache-navy) !important;
  border:1px solid #E49C18 !important;
  border-radius:16px !important;
  box-shadow:0 10px 22px rgba(242,170,36,.18) !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p *,
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) span{
  color:var(--ache-navy) !important;
  -webkit-text-fill-color:var(--ache-navy) !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label:not(:has(input:checked)) div[data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [role="radiogroup"] label:not(:has(input:checked)) span{
  color:#FFFFFF !important;
  -webkit-text-fill-color:#FFFFFF !important;
}
/* Sidebar status box: readable and in brand palette */
[data-testid="stSidebar"] div[style*="rgba(242,170,36,.12)"]{
  background:rgba(242,170,36,.13) !important;
  border:1px solid rgba(242,170,36,.55) !important;
  border-left:4px solid var(--ache-orange) !important;
  box-shadow:none !important;
}
[data-testid="stSidebar"] div[style*="rgba(242,170,36,.12)"] b,
[data-testid="stSidebar"] div[style*="rgba(242,170,36,.12)"] span{
  color:#FFFFFF !important;
  -webkit-text-fill-color:#FFFFFF !important;
  opacity:1 !important;
}

/* Guide header/card — if any old dark module card remains, force readable text */
.ache-guide-minihero,.ache-guide-minihero *{opacity:1 !important;}
.ache-guide-kicker{color:var(--ache-navy) !important;-webkit-text-fill-color:var(--ache-navy) !important;}
.ache-guide-subtitle{color:var(--ache-muted) !important;-webkit-text-fill-color:var(--ache-muted) !important;}
div[style*="background:#173555"] *, div[style*="background: #173555"] *, div[style*="background:#1B335C"] *, div[style*="background: #1B335C"] *{color:#FFFFFF !important;-webkit-text-fill-color:#FFFFFF !important;opacity:1 !important;}
.ache-hero h1,.ache-hero h1 *, .ache-hero p,.ache-hero p *, .ache-pill,.ache-pill *{color:#FFFFFF !important;-webkit-text-fill-color:#FFFFFF !important;opacity:1 !important;}
</style>""", unsafe_allow_html=True)



st.markdown("""<style>
/* ────────────────────────────────────────────────────────────────
   ACHE SIDEBAR FINAL FIX v21
   Remove gray active wrapper and make sidebar status cards yellow.
   ──────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] [role="radiogroup"] label,
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){
  background:transparent !important;
  border:1px solid transparent !important;
  box-shadow:none !important;
  outline:none !important;
  padding:0 !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child{
  opacity:.55 !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label div[data-testid="stMarkdownContainer"] p{
  background:transparent !important;
  border:1px solid transparent !important;
  border-radius:16px !important;
  padding:10px 14px !important;
  color:#FFFFFF !important;
  -webkit-text-fill-color:#FFFFFF !important;
  box-shadow:none !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover div[data-testid="stMarkdownContainer"] p{
  background:rgba(255,255,255,.08) !important;
  border-color:rgba(242,170,36,.28) !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p{
  background:linear-gradient(90deg,#F2AA24,#FFBE45) !important;
  border:1px solid #F2AA24 !important;
  color:#173555 !important;
  -webkit-text-fill-color:#173555 !important;
  box-shadow:0 8px 18px rgba(242,170,36,.20) !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p *,
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) span{
  color:#173555 !important;
  -webkit-text-fill-color:#173555 !important;
}
/* Bottom case card: yellow, readable, brand-only. */
[data-testid="stSidebar"] div[style*="rgba(242,170,36,.12)"],
[data-testid="stSidebar"] div[style*="rgba(242,170,36,.13)"],
[data-testid="stSidebar"] div[style*="rgba(242,170,36,.14)"]{
  background:linear-gradient(90deg,#F2AA24,#FFBE45) !important;
  border:1px solid #F2AA24 !important;
  border-left:0 !important;
  box-shadow:0 10px 22px rgba(242,170,36,.20) !important;
}
[data-testid="stSidebar"] div[style*="rgba(242,170,36,.12)"] *,
[data-testid="stSidebar"] div[style*="rgba(242,170,36,.13)"] *,
[data-testid="stSidebar"] div[style*="rgba(242,170,36,.14)"] *{
  color:#173555 !important;
  -webkit-text-fill-color:#173555 !important;
  opacity:1 !important;
}
</style>""", unsafe_allow_html=True)



st.markdown("""<style>
/* ═══════════════════════════════════════════════════════════════
   Ache Innovation unified visual system — web-first v1
   Source visual language: institutional web / marketplace
════════════════════════════════════════════════════════════════ */
:root{
  --ache-navy:#0A2560!important;
  --ache-navy-2:#071840!important;
  --ache-navy-3:#041127!important;
  --ache-yellow:#F29E1F!important;
  --ache-yellow-2:#F5B84A!important;
  --ache-bg:#F5F7FB!important;
  --ache-card:#FFFFFF!important;
  --ache-text:#0D1B35!important;
  --ache-muted:#4A5568!important;
  --ache-border:#E2E9F5!important;
}
.stApp{background:var(--ache-bg)!important;color:var(--ache-text)!important;}
.block-container{max-width:1360px!important;padding-top:1rem!important;}

/* Typography: formal, web/brand-like */
h1,h2,h3{color:var(--ache-text)!important;font-family:'Barlow',system-ui,sans-serif!important;letter-spacing:-.025em!important;}
h1{font-size:clamp(2rem,4vw,3.6rem)!important;font-weight:800!important;}
h2{font-size:clamp(1.55rem,2.8vw,2.4rem)!important;font-weight:800!important;}
h3{font-weight:750!important;}
p,li,label,span,div{color:inherit;}
.ache-muted, small{color:var(--ache-muted)!important;}

/* Cards consistent with marketplace */
.ache-card,.ache-step,.ache-status-strip,[data-testid="stMetric"],[data-testid="metric-container"]{
  background:#fff!important;border:1px solid var(--ache-border)!important;border-radius:18px!important;
  box-shadow:0 14px 38px rgba(10,37,96,.08)!important;color:var(--ache-text)!important;
}
.ache-step{padding:22px!important;}
.ache-step-number{background:var(--ache-yellow)!important;color:var(--ache-navy-2)!important;border-radius:12px!important;}
.ache-card *,.ache-step *,.ache-status-strip *{color:var(--ache-text)!important;}

/* Hero aligned with web dark section */
.ache-hero{
  background:radial-gradient(ellipse at 82% 15%,rgba(242,158,31,.14),transparent 36%),linear-gradient(135deg,var(--ache-navy-2),var(--ache-navy))!important;
  border-radius:28px!important;border:1px solid rgba(242,158,31,.14)!important;
  box-shadow:0 24px 70px rgba(10,37,96,.24)!important;
}
.ache-hero h1,.ache-hero h2,.ache-hero strong{color:#FFFFFF!important;}
.ache-hero p,.ache-hero li{color:rgba(255,255,255,.84)!important;}
.ache-pill{background:rgba(242,158,31,.14)!important;border:1px solid rgba(242,158,31,.42)!important;color:#FFD186!important;}

/* Inputs: no dark-on-dark, no invisible placeholders */
input, textarea, [data-baseweb="select"]{
  background:#FFFFFF!important;color:var(--ache-text)!important;border:1.5px solid #C9D5E6!important;border-radius:12px!important;
  box-shadow:none!important;
}
input::placeholder, textarea::placeholder{color:#6F7E93!important;opacity:1!important;}
[data-baseweb="select"] *{color:var(--ache-text)!important;}
[data-baseweb="popover"] *{color:var(--ache-text)!important;background:#FFFFFF!important;}
[data-baseweb="menu"] li{color:var(--ache-text)!important;background:#FFFFFF!important;}
[data-baseweb="menu"] li:hover{background:#FFF3DF!important;color:var(--ache-navy)!important;}
[data-testid="stNumberInput"] button{background:#FFFFFF!important;color:var(--ache-navy)!important;border-color:#C9D5E6!important;}

/* Buttons */
.stButton>button,.stDownloadButton>button{
  border-radius:999px!important;font-weight:750!important;border:1.5px solid #C9D5E6!important;
  background:#FFFFFF!important;color:var(--ache-navy)!important;box-shadow:0 8px 22px rgba(10,37,96,.06)!important;
}
.stButton>button[kind="primary"],.stDownloadButton>button[kind="primary"]{
  background:linear-gradient(135deg,var(--ache-yellow),var(--ache-yellow-2))!important;color:var(--ache-navy-2)!important;
  border-color:var(--ache-yellow)!important;box-shadow:0 14px 32px rgba(242,158,31,.26)!important;
}
.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-1px);border-color:var(--ache-yellow)!important;}

/* Top nav: web/marketplace-style chips */
.ache-nav-lite{background:#FFFFFF!important;border:1px solid var(--ache-border)!important;border-radius:22px!important;padding:18px!important;box-shadow:0 18px 48px rgba(10,37,96,.07)!important;margin-bottom:22px!important;}
.ache-nav-lite-title{color:#6A7890!important;font-weight:900!important;letter-spacing:.12em!important;text-transform:uppercase!important;font-size:.78rem!important;margin-bottom:12px!important;}
.ache-nav-lite + div .stButton>button{min-height:46px!important;padding:.55rem .85rem!important;}

/* Sidebar: no gray selection, only Ache palette */
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0A2560 0%,#071840 100%)!important;}
[data-testid="stSidebar"] *{color:#FFFFFF!important;}
[data-testid="stSidebar"] .stRadio label{border-radius:999px!important;padding:0!important;margin:4px 0!important;}
[data-testid="stSidebar"] .stRadio label div[data-testid="stMarkdownContainer"] p{
  color:#FFFFFF!important;background:transparent!important;border:1px solid transparent!important;border-radius:999px!important;
  padding:11px 14px!important;font-weight:800!important;
}
[data-testid="stSidebar"] .stRadio label:hover div[data-testid="stMarkdownContainer"] p{
  background:rgba(242,158,31,.13)!important;border-color:rgba(242,158,31,.35)!important;color:#FFFFFF!important;
}
[data-testid="stSidebar"] .stRadio label:has(input:checked) div[data-testid="stMarkdownContainer"] p{
  background:linear-gradient(135deg,var(--ache-yellow),var(--ache-yellow-2))!important;color:#071840!important;border-color:var(--ache-yellow)!important;
  box-shadow:0 12px 28px rgba(242,158,31,.25)!important;
}
[data-testid="stSidebar"] .stRadio label:has(input:checked) *{color:#071840!important;}
[data-testid="stSidebar"] hr{border-color:rgba(255,255,255,.16)!important;}
[data-testid="stSidebar"] .ache-sidebar-status{
  background:rgba(255,255,255,.08)!important;border:1px solid rgba(242,158,31,.26)!important;border-radius:18px!important;
  padding:14px!important;color:#FFFFFF!important;
}
[data-testid="stSidebar"] .ache-sidebar-status *{color:#FFFFFF!important;}

/* Alerts/callouts */
.ache-info,.ache-callout{background:#EAF2FA!important;border:1px solid #C9D8E8!important;border-left:5px solid var(--ache-navy)!important;color:var(--ache-text)!important;}
.ache-warning{background:#FFF7E8!important;border:1px solid #F7D08A!important;border-left:5px solid var(--ache-yellow)!important;color:#573800!important;}
.stAlert{border-radius:16px!important;}

/* Embedded web should feel like the main page, not a technical iframe card */
.ache-embedded-web-note{display:none!important;}
iframe{border-radius:22px!important;box-shadow:0 18px 52px rgba(10,37,96,.11)!important;background:#FFFFFF!important;}

@media(max-width:768px){
  .block-container{padding-left:1rem!important;padding-right:1rem!important;}
  .ache-nav-lite{padding:12px!important;border-radius:18px!important;}
  .stButton>button{width:100%!important;}
}
</style>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — Navegación
# ─────────────────────────────────────────────────────────────────────────────

NAV_OPTIONS = [
    "🏠 Inicio software",
    "🐕 Biomechanics Studio",
    "📸 Fotos y análisis",
    "🦿 Diseño biomecánico",
    "🩺 Guía quirúrgica",
    "📄 Reporte",
    "🗄 Historial",
    "🐄 Productivos",
]

NAV_MAPPING = {
    "🏠 Inicio software": "🏠  Inicio",
    "🐄 Productivos": "🐄  Animales Productivos",
    "🐕 Biomechanics Studio": "🐕  Nuevo Caso",
    "📸 Fotos y análisis": "📸  Análisis de Imágenes",
    "🦿 Diseño biomecánico": "🦴  Diseño de Prótesis",
    "🩺 Guía quirúrgica": "🔪  Guía Quirúrgica",
    "📄 Reporte": "📋  Generar Reporte",
    "🗄 Historial": "🗄️  Historial de Casos",
}




def _asset_data_uri(filename):
    path = ROOT / "assets" / filename
    if not path.exists():
        return ""
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def render_brand_header():
    """Visible brand header for desktop and mobile, independent from sidebar."""
    logo_uri = _asset_data_uri("ache_logo_transparent.png") or _asset_data_uri("ache_logo_main.png")
    logo_html = f'<img src="{logo_uri}" alt="Ache Innovation" />' if logo_uri else '<strong>ACHE</strong>'
    st.markdown(f"""
    <header class="ache-brand-header">
      <div class="ache-brand-logo">{logo_html}</div>
      <div class="ache-brand-copy">
        <div class="ache-brand-title">Ache Innovation</div>
        <div class="ache-brand-subtitle">Ache Innovation · Parametrización morfológica y Biomechanics Studio</div>
      </div>
      <div class="ache-brand-tag">MVP interno</div>
    </header>
    """, unsafe_allow_html=True)

PAGE_KEYS = {
    "caso": ("🐕 Biomechanics Studio", "🐕  Nuevo Caso"),
    "productivos": ("🐄 Productivos", "🐄  Animales Productivos"),
    "inicio": ("🏠 Inicio software", "🏠  Inicio"),
    "fotos": ("📸 Fotos y análisis", "📸  Análisis de Imágenes"),
    "diseno": ("🦿 Diseño biomecánico", "🦴  Diseño de Prótesis"),
    "guia": ("🩺 Guía quirúrgica", "🔪  Guía Quirúrgica"),
    "reporte": ("📄 Reporte", "📋  Generar Reporte"),
    "historial": ("🗄 Historial", "🗄️  Historial de Casos"),
}
DISPLAY_TO_KEY = {display: key for key, (display, internal) in PAGE_KEYS.items()}
INTERNAL_TO_KEY = {internal: key for key, (display, internal) in PAGE_KEYS.items()}


def _query_page_key():
    # Only used for initial deep links. Normal navigation is session-state based
    # to avoid full browser refreshes.
    key = st.query_params.get("page", "inicio")
    return key if key in PAGE_KEYS else "inicio"



def _embed_mode():
    return st.query_params.get("embed", "0") in ("1", "true", "yes")


def _embed_page_internal():
    key = st.query_params.get("page", "caso")
    return PAGE_KEYS.get(key, PAGE_KEYS["caso"])[1]

def _ensure_nav_state(default="🏠 Inicio software"):
    if "active_nav" not in st.session_state:
        query_key = _query_page_key()
        query_display, _ = PAGE_KEYS[query_key]
        st.session_state.active_nav = query_display
    # Safe here: this runs before sidebar_nav radio is instantiated.
    st.session_state.sidebar_nav = st.session_state.active_nav


def _sync_nav_from_sidebar():
    selected = st.session_state.get("sidebar_nav", "🏠 Inicio software")
    st.session_state.active_nav = selected


def _go_to_page(key):
    if key in PAGE_KEYS:
        # Do not mutate sidebar_nav here. The sidebar radio already exists by now.
        # It will be synchronized safely at the start of the next run.
        st.session_state.active_nav = PAGE_KEYS[key][0]

def render_top_navigation(default_page_label="🏠 Inicio software"):
    """Pill navigation using horizontal st.radio — clean, no ugly buttons."""
    active_display = st.session_state.get("active_nav", default_page_label)
    if active_display not in NAV_OPTIONS:
        active_display = default_page_label
    safe_idx = NAV_OPTIONS.index(active_display)

    selected = st.radio(
        "Secciones",
        NAV_OPTIONS,
        index=safe_idx,
        key="top_nav_radio",
        label_visibility="collapsed",
        horizontal=True,
    )

    if selected != active_display:
        st.session_state.active_nav = selected
        st.rerun()

    return NAV_MAPPING.get(selected, NAV_MAPPING[default_page_label])

def render_sidebar():
    logo_path = ROOT / "assets" / "ache_logo_transparent.png"
    with st.sidebar:
        if logo_path.exists():
            st.image(str(logo_path), width="stretch")
        else:
            st.markdown("## Ache Innovation")

        st.markdown("""
        <div style="margin:10px 0 18px; opacity:.82; line-height:1.35;">
          <b>Ache Innovation</b><br>
          Parametrización morfológica · Software clínico
        </div>
        """, unsafe_allow_html=True)

        _ensure_nav_state()
        page = st.radio(
            "Navegación principal",
            NAV_OPTIONS,
            index=NAV_OPTIONS.index(st.session_state.active_nav),
            label_visibility="collapsed",
            key="sidebar_nav",
            on_change=_sync_nav_from_sidebar,
        )

        st.markdown("---")
        if "current_case" in st.session_state:
            c = st.session_state.current_case
            st.markdown("""
            <div style="background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.12); border-radius:14px; padding:12px;">
              <div style="font-size:.78rem; opacity:.7; text-transform:uppercase; letter-spacing:.08em;">Caso activo</div>
              <div style="font-size:1.05rem; font-weight:800; margin-top:4px;">🐶 %s</div>
              <div style="font-size:.9rem; opacity:.82; margin-top:2px;">%s</div>
            </div>
            """ % (c.get('nombre_perro', 'Sin nombre'), c.get('extremidad', 'Extremidad no definida')), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(242,170,36,.12); border:1px solid rgba(242,170,36,.24); border-radius:14px; padding:12px;">
              <b>Sin caso activo</b><br>
              <span style="opacity:.78;">Creá un caso para empezar.</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.caption("Ache Innovation · MVP interno")

    return NAV_MAPPING[page]




st.markdown("""<style>
/* ────────────────────────────────────────────────────────────────
   ACHE HOME UX REDESIGN v1
   A clearer guided landing page for first-time users.
   ──────────────────────────────────────────────────────────────── */
.ache-next-action{
  background:#FFFFFF;border:1px solid #C9D8E8;border-left:6px solid #F2AA24;border-radius:20px;
  padding:22px 24px;margin:18px 0 22px;box-shadow:0 14px 34px rgba(23,53,85,.08);
}
.ache-next-action .kicker,.ache-workflow-card .kicker,.ache-section-map .kicker{
  color:#6B7A8C !important;text-transform:uppercase;letter-spacing:.08em;font-weight:900;font-size:.78rem;margin-bottom:8px;
}
.ache-next-action h2{margin:.05rem 0 .35rem !important;color:#173555 !important;font-size:1.65rem !important;}
.ache-next-action p{color:#4F6173 !important;margin:0 !important;line-height:1.45 !important;}
.ache-home-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:18px 0 22px;}
.ache-workflow-card{
  background:#FFFFFF;border:1px solid #D6E1EC;border-radius:18px;padding:18px;box-shadow:0 10px 26px rgba(23,53,85,.06);
}
.ache-workflow-card .num{width:34px;height:34px;border-radius:12px;background:#F2AA24;color:#173555;display:flex;align-items:center;justify-content:center;font-weight:900;margin-bottom:12px;}
.ache-workflow-card h3{margin:0 0 8px !important;color:#173555 !important;font-size:1.08rem !important;}
.ache-workflow-card p{margin:0;color:#536679 !important;line-height:1.42 !important;font-size:.98rem !important;}
.ache-workflow-card strong{color:#173555 !important;}
.ache-section-map{background:#FFFFFF;border:1px solid #D6E1EC;border-radius:20px;padding:20px;margin:16px 0;box-shadow:0 10px 26px rgba(23,53,85,.06);}
.ache-section-row{display:grid;grid-template-columns:190px 1fr;gap:14px;padding:12px 0;border-top:1px solid #E5EEF7;align-items:start;}
.ache-section-row:first-of-type{border-top:0;}
.ache-section-row b{color:#173555 !important;font-weight:900;}
.ache-section-row span{color:#536679 !important;line-height:1.4;}
.ache-warning-simple{background:#FFF7E6;border:1px solid #F4D28B;border-radius:16px;padding:14px 16px;color:#6B4700 !important;margin-top:14px;}
.ache-warning-simple *{color:#6B4700 !important;}
@media(max-width:900px){.ache-home-grid{grid-template-columns:1fr;}.ache-section-row{grid-template-columns:1fr;gap:4px;}}
</style>""", unsafe_allow_html=True)



st.markdown("""<style>
/* ────────────────────────────────────────────────────────────────
   ACHE PROFESSIONAL WORKFLOW HOME v2
   Clinical/professional dashboard, guided by state, not a tutorial.
   ──────────────────────────────────────────────────────────────── */
.ache-workbench{display:grid;grid-template-columns:1.12fr .88fr;gap:18px;margin:18px 0 20px;align-items:stretch;}
.ache-panel{background:#FFFFFF;border:1px solid #D6E1EC;border-radius:20px;padding:22px 24px;box-shadow:0 14px 34px rgba(23,53,85,.075);}
.ache-panel.accent{border-left:6px solid #F2AA24;}
.ache-kicker{color:#6B7A8C !important;text-transform:uppercase;letter-spacing:.08em;font-weight:900;font-size:.78rem;margin-bottom:8px;}
.ache-panel h2{color:#173555 !important;margin:0 0 8px !important;font-size:1.55rem !important;line-height:1.15 !important;}
.ache-panel h3{color:#173555 !important;margin:0 0 8px !important;font-size:1.12rem !important;}
.ache-panel p{color:#536679 !important;line-height:1.46 !important;margin:.25rem 0 !important;}
.ache-status-list{display:grid;gap:9px;margin-top:14px;}
.ache-status-item2{display:flex;align-items:flex-start;gap:10px;padding:10px 12px;border-radius:14px;background:#F7FAFD;border:1px solid #E2EBF4;}
.ache-status-dot{width:10px;height:10px;border-radius:50%;margin-top:7px;background:#C9D8E8;flex:0 0 10px;}
.ache-status-item2.done .ache-status-dot{background:#1F8A4C;}
.ache-status-item2.current .ache-status-dot{background:#F2AA24;box-shadow:0 0 0 4px rgba(242,170,36,.18);}
.ache-status-item2.blocked .ache-status-dot{background:#C9D8E8;}
.ache-status-item2 b{color:#173555 !important;display:block;margin-bottom:2px;}
.ache-status-item2 span{color:#5B6E82 !important;line-height:1.35 !important;}
.ache-clinical-note{background:#EAF2FA;border:1px solid #C9D8E8;border-left:5px solid #173555;border-radius:16px;padding:14px 16px;margin-top:14px;color:#173555 !important;}
.ache-clinical-note *{color:#173555 !important;}
.ache-action-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:14px;}
.ache-action-card{background:#FFFFFF;border:1px solid #D6E1EC;border-radius:16px;padding:15px;min-height:118px;}
.ache-action-card.enabled{border-color:#F2AA24;background:#FFF9ED;}
.ache-action-card h4{margin:0 0 6px !important;color:#173555 !important;font-size:1.02rem !important;}
.ache-action-card p{font-size:.94rem !important;color:#5B6E82 !important;margin:0 !important;}
.ache-disabled{opacity:.58;}
.ache-flowline{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin:20px 0;}
.ache-flow-node{position:relative;background:#FFFFFF;border:1px solid #D6E1EC;border-radius:16px;padding:12px 10px;min-height:94px;box-shadow:0 8px 22px rgba(23,53,85,.05);}
.ache-flow-node .n{display:inline-flex;width:28px;height:28px;border-radius:10px;align-items:center;justify-content:center;background:#EDF3F9;color:#173555;font-weight:900;margin-bottom:8px;}
.ache-flow-node.done .n{background:#1F8A4C;color:#FFFFFF;}
.ache-flow-node.current{border-color:#F2AA24;box-shadow:0 10px 26px rgba(242,170,36,.14);}
.ache-flow-node.current .n{background:#F2AA24;color:#173555;}
.ache-flow-node b{display:block;color:#173555 !important;font-size:.92rem;line-height:1.15;}
.ache-flow-node span{display:block;color:#6B7A8C !important;font-size:.82rem;line-height:1.25;margin-top:4px;}
.ache-purpose-map{background:#FFFFFF;border:1px solid #D6E1EC;border-radius:20px;padding:20px 22px;margin:16px 0;box-shadow:0 12px 30px rgba(23,53,85,.06);}
.ache-purpose-map h3{margin:0 0 12px !important;color:#173555 !important;}
.ache-purpose-row{display:grid;grid-template-columns:210px 1fr 190px;gap:14px;padding:12px 0;border-top:1px solid #E6EEF6;align-items:start;}
.ache-purpose-row:first-of-type{border-top:0;}
.ache-purpose-row b{color:#173555 !important;}
.ache-purpose-row span{color:#536679 !important;line-height:1.38;}
.ache-purpose-tag{justify-self:start;background:#F7FAFD;border:1px solid #D6E1EC;border-radius:999px;padding:4px 9px;color:#173555 !important;font-size:.82rem;font-weight:800;}
@media(max-width:1000px){.ache-workbench{grid-template-columns:1fr;}.ache-flowline{grid-template-columns:repeat(2,1fr);}.ache-purpose-row{grid-template-columns:1fr;gap:5px;}.ache-action-grid{grid-template-columns:1fr;}}
</style>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PÁGINA: INICIO
# ─────────────────────────────────────────────────────────────────────────────
def page_inicio():
    casos = get_cases(DB_PATH)
    active = "current_case" in st.session_state
    active_case = st.session_state.get("current_case", {})
    has_images = bool(st.session_state.get("uploaded_images"))
    has_measurements = "measurements" in st.session_state
    has_design = "prosthetic_specs" in st.session_state or "scad_code" in st.session_state

    # Estado del flujo: el sistema decide qué corresponde hacer, no el usuario.
    if not active:
        stage_idx = 1
        stage_title = "Apertura del caso clínico"
        stage_text = "Antes de analizar imágenes o generar geometría, el sistema necesita identificar al paciente, extremidad comprometida, peso y contexto clínico básico."
        primary_key = "caso"
        primary_label = "Abrir nuevo caso"
    elif not has_measurements:
        stage_idx = 2
        stage_title = "Documentación fotográfica y medición"
        stage_text = "El caso ya está abierto. El siguiente paso operativo es cargar imágenes útiles y registrar medidas morfológicas iniciales con referencia de escala cuando sea posible."
        primary_key = "fotos"
        primary_label = "Cargar fotos y medir"
    elif not has_design:
        stage_idx = 3
        stage_title = "Parametrización biomecánica"
        stage_text = "Con datos clínicos y medidas disponibles, corresponde generar un diseño conceptual parametrizado para revisión profesional."
        primary_key = "diseno"
        primary_label = "Generar diseño 3D"
    else:
        stage_idx = 4
        stage_title = "Revisión y documentación"
        stage_text = "El caso ya cuenta con diseño conceptual. Corresponde revisar criterios clínicos, generar reporte y preparar archivos para discusión con el equipo tratante."
        primary_key = "reporte"
        primary_label = "Generar reporte"

    steps = [
        ("Caso", active, stage_idx == 1, "Datos clínicos base"),
        ("Fotos", has_measurements, stage_idx == 2, "Imágenes y escala"),
        ("Análisis", has_measurements, False, "Raza, tamaño, medidas"),
        ("Diseño", has_design, stage_idx == 3, "CAD/STL conceptual"),
        ("Guía", False, stage_idx == 4, "Criterios clínicos"),
        ("Reporte", False, stage_idx == 4, "Entrega del caso"),
    ]

    st.markdown("""
    <div class="ache-hero">
      <div class="ache-pill">Ache Innovation · Biomechanics Studio</div>
      <h1>Flujo de evaluación y diseño protésico canino</h1>
      <p>Herramienta interna para ordenar casos, documentar morfología, estimar parámetros de diseño y preparar una revisión clínica/fabricación. El sistema acompaña el recorrido por etapas para evitar saltos de información.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='ache-flowline'>" + "".join([
        f"<div class='ache-flow-node {'done' if done else 'current' if current else ''}'><div class='n'>{i}</div><b>{name}</b><span>{desc}</span></div>"
        for i, (name, done, current, desc) in enumerate(steps, 1)
    ]) + "</div>", unsafe_allow_html=True)

    left, right = st.columns([1.15, .85], gap="large")
    with left:
        st.markdown(f"""
        <section class="ache-panel accent">
          <div class="ache-kicker">Etapa actual</div>
          <h2>{stage_title}</h2>
          <p>{stage_text}</p>
          <div class="ache-clinical-note"><b>Criterio de uso:</b> esta plataforma organiza información para revisión profesional. No define por sí sola una conducta quirúrgica ni habilita fabricación sin validación clínica, biomecánica y técnica.</div>
        </section>
        """, unsafe_allow_html=True)
        if st.button(primary_label, type="primary", width="stretch"):
            _go_to_page(primary_key)
            st.rerun()

    with right:
        case_title = active_case.get('nombre_perro', 'Sin caso activo') if active else 'Sin caso activo'
        case_sub = f"{active_case.get('extremidad','—')} · {active_case.get('peso_actual','—')} kg" if active else "El flujo comienza al abrir un caso clínico."
        st.markdown(f"""
        <section class="ache-panel">
          <div class="ache-kicker">Estado del caso</div>
          <h3>{case_title}</h3>
          <p>{case_sub}</p>
          <div class="ache-status-list">
            <div class="ache-status-item2 {'done' if active else 'current'}"><div class="ache-status-dot"></div><div><b>Identificación clínica</b><span>{'Completa para avanzar.' if active else 'Pendiente: abrir caso.'}</span></div></div>
            <div class="ache-status-item2 {'done' if has_measurements else 'current' if active else 'blocked'}"><div class="ache-status-dot"></div><div><b>Fotos y medidas</b><span>{'Registradas.' if has_measurements else 'Pendiente.'}</span></div></div>
            <div class="ache-status-item2 {'done' if has_design else 'current' if has_measurements else 'blocked'}"><div class="ache-status-dot"></div><div><b>Diseño biomecánico</b><span>{'Generado.' if has_design else 'Pendiente.'}</span></div></div>
          </div>
        </section>
        """, unsafe_allow_html=True)

    st.markdown("""
    <section class="ache-purpose-map">
      <div class="ache-kicker">Recorrido operativo</div>
      <h3>Qué hace cada módulo y cuándo corresponde usarlo</h3>
      <div class="ache-purpose-row"><b>🐕 Nuevo caso</b><span>Registro inicial del paciente, tutor, peso, extremidad afectada, estado actual y notas clínicas. Es obligatorio para dar contexto al resto del sistema.</span><div class="ache-purpose-tag">Inicio</div></div>
      <div class="ache-purpose-row"><b>📸 Fotos y análisis</b><span>Carga de imágenes y extracción/registro de información morfológica. Se usa después de abrir el caso, antes de diseñar.</span><div class="ache-purpose-tag">Datos de entrada</div></div>
      <div class="ache-purpose-row"><b>🦿 Diseño biomecánico</b><span>Generación paramétrica del modelo conceptual: encaje/socket, largo, apoyo, arquitectura y archivo 3D revisable.</span><div class="ache-purpose-tag">Resultado técnico</div></div>
      <div class="ache-purpose-row"><b>🩺 Guía clínica</b><span>Material de apoyo para evaluar compatibilidad protésica externa, alertas, requisitos del muñón y comunicación con profesionales.</span><div class="ache-purpose-tag">Revisión profesional</div></div>
      <div class="ache-purpose-row"><b>📄 Reporte</b><span>Documento de salida para compartir el caso con veterinario, rehabilitador, fabricante o equipo interno.</span><div class="ache-purpose-tag">Entrega</div></div>
      <div class="ache-purpose-row"><b>🗄 Historial</b><span>Recuperación de casos ya cargados. No es un paso obligatorio dentro de un caso nuevo.</span><div class="ache-purpose-tag">Archivo</div></div>
    </section>
    """, unsafe_allow_html=True)

def page_nuevo_caso():
    st.header("🐕 Nuevo Caso")

    with st.form("form_nuevo_caso", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Datos del Paciente")
            nombre_perro  = st.text_input("Nombre del perro *", placeholder="Ej: Max")
            nombre_dueno  = st.text_input("Nombre del dueño *", placeholder="Ej: Juan García")
            peso_actual   = st.number_input("Peso actual (kg) *", 0.5, 120.0, 15.0, 0.5)
            sexo          = st.selectbox("Sexo", ["Macho", "Hembra"])
            edad          = st.text_input("Edad", placeholder="Ej: 4 años")

        with col2:
            st.subheader("Datos Clínicos")
            extremidad = st.selectbox(
                "Extremidad afectada *",
                ["Delantera Izquierda", "Delantera Derecha",
                 "Trasera Izquierda", "Trasera Derecha"]
            )
            estado = st.selectbox(
                "Estado actual",
                ["Requiere amputación", "Ya amputado (tiene muñón)", "Evaluación inicial"]
            )
            raza_manual = st.text_input(
                "Raza (opcional — se detecta automáticamente)",
                placeholder="Ej: Labrador Retriever"
            )
            vet_nombre = st.text_input("Veterinario tratante", placeholder="Dr. / Dra.")
            notas = st.text_area("Notas clínicas",
                                 placeholder="Observaciones del veterinario...",
                                 height=100)

        submitted = st.form_submit_button("💾 Registrar Caso", type="primary")

    if submitted:
        if not nombre_perro.strip() or not nombre_dueno.strip():
            st.error("Los campos marcados con * son obligatorios.")
            return

        case_data = {
            "nombre_perro": nombre_perro.strip(),
            "nombre_dueno": nombre_dueno.strip(),
            "peso_actual":  peso_actual,
            "sexo":         sexo,
            "edad":         edad,
            "extremidad":   extremidad,
            "estado":       estado,
            "raza_manual":  raza_manual.strip(),
            "notas":        notas.strip(),
            "vet_nombre":   vet_nombre.strip(),
            "fecha":        datetime.now().isoformat(),
        }

        case_id = save_case(DB_PATH, case_data)
        st.session_state.current_case_id = case_id
        st.session_state.current_case    = case_data
        # Limpiar análisis anteriores
        for key in ["measurements", "breed_info", "detected_breed",
                    "prosthetic_specs", "uploaded_images", "scale_mm_per_px"]:
            st.session_state.pop(key, None)

        st.success(f"✅ Caso #{case_id} registrado — **{nombre_perro}**. "
                   "Ahora podés ir a **Análisis de Imágenes**.")
        st.balloons()


# ─────────────────────────────────────────────────────────────────────────────
# PÁGINA: ANÁLISIS DE IMÁGENES
# ─────────────────────────────────────────────────────────────────────────────
def page_analisis():
    st.header("📸 Análisis de Imágenes")

    if "current_case" not in st.session_state:
        st.warning("⚠️ No hay caso activo. Creá uno en **Nuevo Caso** o cargá uno desde **Historial**.")
        return

    case = st.session_state.current_case
    st.success(f"Caso activo: **{case.get('nombre_perro')}** — {case.get('extremidad')}")

    tab1, tab2, tab3 = st.tabs([
        "📷 Fotos y Detección de Raza",
        "📏 Medición con ArUco",
        "📊 Resumen de Medidas"
    ])

    # ── TAB 1: Fotos + Raza ──────────────────────────────────────────────────
    with tab1:
        st.subheader("Subí las fotos del paciente")

        col_inst, col_up = st.columns([1, 2])
        with col_inst:
            st.markdown("""
            **Instrucciones:**
            1. Colocá el marcador ArUco junto a la extremidad
            2. Fotografiá desde varios ángulos:
               - Lateral izquierdo
               - Lateral derecho
               - Frontal
               - Superior
            3. El animal puede estar despierto; intentá que esté quieto unos segundos
            4. Buena iluminación mejora la detección
            """)

        with col_up:
            uploaded = st.file_uploader(
                "Seleccioná las fotos (JPG o PNG)",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True,
                key="foto_uploader"
            )

        if uploaded:
            st.session_state.uploaded_images = uploaded
            cols = st.columns(min(len(uploaded), 4))
            for i, f in enumerate(uploaded):
                with cols[i % 4]:
                    f.seek(0)
                    st.image(Image.open(f), caption=f"Foto {i+1}", width="stretch")

            st.divider()
            st.subheader("🔍 Detección automática de raza")

            if st.button("Detectar raza", type="primary"):
                best_results  = None
                best_score    = 0.0
                best_file_idx = 0

                progress = st.progress(0, text="Analizando fotos...")

                for idx, f in enumerate(uploaded):
                    progress.progress(
                        (idx + 1) / len(uploaded),
                        text=f"Analizando foto {idx+1}/{len(uploaded)}..."
                    )
                    f.seek(0)
                    img = Image.open(f).convert("RGB")
                    try:
                        results = detect_breed(img)
                        if results and results[0]["score"] > best_score:
                            best_score    = results[0]["score"]
                            best_results  = results
                            best_file_idx = idx
                    except Exception as e:
                        st.warning(f"No se pudo analizar foto {idx+1}: {e}")

                progress.empty()

                if best_results:
                    st.session_state.breed_results = best_results

                    col_r, col_info = st.columns(2)
                    with col_r:
                        st.markdown("**Top 3 razas detectadas:**")
                        for i, r in enumerate(best_results[:3]):
                            name  = format_breed_name(r["label"])
                            score = r["score"] * 100
                            emoji = ["🥇", "🥈", "🥉"][i]
                            st.markdown(f"{emoji} **{name}** — {score:.1f}%")
                            st.progress(r["score"])

                    top_breed  = format_breed_name(best_results[0]["label"])
                    breed_info = get_breed_info(top_breed)

                    # Fallback: buscar por palabras del nombre
                    if not breed_info:
                        for r in best_results:
                            breed_info = get_breed_info(format_breed_name(r["label"]))
                            if breed_info:
                                top_breed = format_breed_name(r["label"])
                                break

                    with col_info:
                        if breed_info:
                            st.markdown(f"**Raza:** {top_breed}")
                            st.metric("Peso promedio",
                                      f"{breed_info['peso_min']}–{breed_info['peso_max']} kg")
                            st.metric("Altura",
                                      f"{breed_info['altura_min']}–{breed_info['altura_max']} cm")
                            st.metric("Longitud miembro delantero",
                                      f"~{breed_info['miembro_delantero_cm']} cm")
                            st.metric("Longitud miembro trasero",
                                      f"~{breed_info['miembro_trasero_cm']} cm")
                            st.session_state.breed_info    = breed_info
                            st.session_state.detected_breed = top_breed

                            if "current_case_id" in st.session_state:
                                update_case_breed(DB_PATH,
                                                  st.session_state.current_case_id,
                                                  top_breed)
                        else:
                            st.info(f"Raza detectada: **{top_breed}** — no está en la base de datos aún.")
                            peso = case.get("peso_actual", 15)
                            ext  = case.get("extremidad", "Delantera")
                            est_del = estimate_limb_from_weight(peso, "delantera")
                            est_tra = estimate_limb_from_weight(peso, "trasera")
                            st.markdown(f"Estimación por peso ({peso} kg):")
                            st.metric("Miembro delantero estimado", f"~{est_del} cm")
                            st.metric("Miembro trasero estimado",  f"~{est_tra} cm")
                            breed_info = {
                                "miembro_delantero_cm": est_del,
                                "miembro_trasero_cm":   est_tra,
                                "peso_min": peso * 0.85,
                                "peso_max": peso * 1.15,
                                "altura_min": 0, "altura_max": 0,
                                "circunf_miembro_cm": 10,
                                "talla": "desconocida"
                            }
                            st.session_state.breed_info    = breed_info
                            st.session_state.detected_breed = top_breed
                else:
                    st.error("No se pudo detectar la raza. Verificá que las fotos muestren claramente al perro.")

    # ── TAB 2: Medición ArUco ────────────────────────────────────────────────
    with tab2:
        st.subheader("📏 Detección de marcador y medición")

        if "uploaded_images" not in st.session_state:
            st.info("Primero subí fotos en la pestaña anterior.")
            return

        imgs = st.session_state.uploaded_images
        foto_idx = st.selectbox(
            "Elegí la foto que tiene el marcador ArUco",
            range(len(imgs)),
            format_func=lambda x: f"Foto {x+1}"
        )

        imgs[foto_idx].seek(0)
        selected_img = Image.open(imgs[foto_idx]).convert("RGB")
        img_array    = np.array(selected_img)

        col_btn, col_info = st.columns([1, 2])
        with col_btn:
            if st.button("🔎 Detectar marcador ArUco", type="primary"):
                with st.spinner("Buscando marcador..."):
                    result_img, scale, found = detect_aruco(img_array.copy())

                if found:
                    st.session_state.scale_mm_per_px = scale
                    st.session_state.aruco_result_img = result_img
                    st.success(f"✅ Marcador detectado\nEscala: **{scale:.4f} mm/px**")
                else:
                    st.error("❌ No se detectó el marcador. Probá con otra foto o mejorá la iluminación.")

        with col_info:
            if "scale_mm_per_px" in st.session_state:
                sc = st.session_state.scale_mm_per_px
                st.info(f"📐 Escala activa: **{sc:.4f} mm/px**  \n"
                        f"1 cm = {10/sc:.0f} píxeles en esta foto")

        if "aruco_result_img" in st.session_state:
            st.image(st.session_state.aruco_result_img,
                     caption="Foto con marcador ArUco detectado", width="stretch")
        else:
            st.image(selected_img, width="stretch")

        st.divider()
        st.subheader("📝 Ingresá las medidas del muñón")
        st.markdown("""
        <div class="ache-info">
        Medí estas dimensiones con una cinta métrica sobre la extremidad del animal.
        Los valores de largo los podés confirmar con la foto y la escala calculada arriba.
        </div>
        """, unsafe_allow_html=True)

        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            munon_largo = st.number_input(
                "Largo del muñón (cm)", 0.0, 80.0,
                st.session_state.get("measurements", {}).get("munon_largo_cm", 0.0),
                0.1, help="Desde la articulación proximal hasta el extremo distal del muñón"
            )
        with col_m2:
            circunf_base = st.number_input(
                "Circunferencia en la base (cm)", 0.0, 80.0,
                st.session_state.get("measurements", {}).get("munon_circunf_base_cm", 0.0),
                0.1, help="La parte más gruesa del muñón, cerca de la articulación"
            )
        with col_m3:
            circunf_distal = st.number_input(
                "Circunferencia en el extremo (cm)", 0.0, 80.0,
                st.session_state.get("measurements", {}).get("munon_circunf_distal_cm", 0.0),
                0.1, help="La parte más estrecha, en el extremo del muñón (donde va el encaje)"
            )

        if st.button("💾 Guardar medidas", type="primary"):
            meas = {
                "munon_largo_cm":          munon_largo,
                "munon_circunf_base_cm":   circunf_base,
                "munon_circunf_distal_cm": circunf_distal,
                "scale_mm_per_px": st.session_state.get("scale_mm_per_px"),
            }
            st.session_state.measurements = meas

            if "current_case_id" in st.session_state:
                save_measurements(
                    DB_PATH,
                    st.session_state.current_case_id,
                    meas,
                    st.session_state.get("breed_info")
                )

            st.success("✅ Medidas guardadas correctamente.")

    # ── TAB 3: Resumen ────────────────────────────────────────────────────────
    with tab3:
        st.subheader("📊 Resumen de medidas")

        if "measurements" not in st.session_state:
            st.info("Completá las medidas en la pestaña **Medición con ArUco**.")
            return

        m  = st.session_state.measurements
        bi = st.session_state.get("breed_info", {})

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Largo del muñón", f"{m['munon_largo_cm']} cm")
        with col2:
            st.metric("Circunf. base",   f"{m['munon_circunf_base_cm']} cm")
        with col3:
            st.metric("Circunf. distal", f"{m['munon_circunf_distal_cm']} cm")

        if bi:
            extremidad = case.get("extremidad", "Delantera Izquierda")
            long_ref   = (bi.get("miembro_delantero_cm", 0)
                          if "Delantera" in extremidad
                          else bi.get("miembro_trasero_cm", 0))

            long_prot = max(0.0, long_ref - m["munon_largo_cm"])

            st.divider()
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Longitud total del miembro (referencia raza)", f"{long_ref} cm")
            with col_b:
                st.metric("Longitud estimada de la prótesis", f"{long_prot:.1f} cm",
                          delta=f"Raza: {st.session_state.get('detected_breed', '—')}")

            st.session_state.prosthetic_length = long_prot


# ─────────────────────────────────────────────────────────────────────────────
# PÁGINA: DISEÑO DE PRÓTESIS
# ─────────────────────────────────────────────────────────────────────────────
def _generate_scad(specs: dict) -> str:
    # Genera el template biomecánico v4 parametrizado con las medidas del caso actual.
    import re

    template_path = ROOT / "cad_templates" / "ache_canine_biomech_limb_v4.scad"
    if template_path.exists():
        scad = template_path.read_text(encoding="utf-8")
    else:
        return "// ERROR: no se encontró ache_canine_biomech_limb_v4.scad"

    longitud_mm = max(float(specs["longitud_total_cm"]) * 10, 90)
    socket_depth_mm = max(float(specs["profundidad_socket_cm"]) * 10, 28)
    socket_diam_mm = max(float(specs["diametro_socket_cm"]) * 10, 28)
    pylon_diam_mm = max(float(specs["diametro_pata_cm"]) * 10, 16)
    tipo = specs.get("tipo", "Delantera")
    limb_type = "front" if "Delantera" in tipo else "rear"

    # Escalado biomecánico inicial.
    # Se ajusta por proporciones, no por raza fija, así también sirve para mestizos/callejeros.
    upper_cuff_h = min(max(socket_depth_mm * 0.95, 34), longitud_mm * 0.34)
    upper_cuff_w = socket_diam_mm * 1.18
    upper_cuff_d = socket_diam_mm * 0.92
    shank_len = max(longitud_mm - upper_cuff_h - 58, 42)
    shank_w = max(pylon_diam_mm * 1.10, socket_diam_mm * 0.55)
    shank_d = max(pylon_diam_mm * 0.90, socket_diam_mm * 0.42)
    foot_len = max(pylon_diam_mm * 2.85, socket_diam_mm * 1.45, 62)
    foot_w = max(pylon_diam_mm * 1.35, socket_diam_mm * 0.72, 30)
    foot_h = max(pylon_diam_mm * 0.90, 20)
    hinge_d = max(pylon_diam_mm * 0.90, 18)
    tendon_d = max(pylon_diam_mm * 0.14, 3.0)
    spring_d = max(pylon_diam_mm * 0.28, 6.0)

    replacements = {
        "limb_type": f'"{limb_type}"',
        "prosthesis_height": f"{longitud_mm:.1f}",
        "upper_cuff_h": f"{upper_cuff_h:.1f}",
        "upper_cuff_w": f"{upper_cuff_w:.1f}",
        "upper_cuff_d": f"{upper_cuff_d:.1f}",
        "shank_len": f"{shank_len:.1f}",
        "shank_w": f"{shank_w:.1f}",
        "shank_d": f"{shank_d:.1f}",
        "foot_len": f"{foot_len:.1f}",
        "foot_w": f"{foot_w:.1f}",
        "foot_h": f"{foot_h:.1f}",
        "hinge_d": f"{hinge_d:.1f}",
        "tendon_d": f"{tendon_d:.1f}",
        "spring_d": f"{spring_d:.1f}",
    }

    for key, value in replacements.items():
        scad = re.sub(rf"^{key}\s*=\s*[^;]+;", f"{key} = {value};", scad, flags=re.MULTILINE)

    header = (
        "// ============================================================\n"
        "// Ache Innovation — Prótesis biomecánica parametrizada desde software\n"
        f"// Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"// Material sugerido: {specs.get('material', 'PETG/Nylon + TPU')}\n"
        f"// Tipo: {tipo}\n"
        "// Arquitectura: cuff + articulación + segmento inferior + pie móvil + tendones/resortes\n"
        "// ============================================================\n\n"
    )
    return header + scad


def page_diseno():
    st.markdown("""
    <div class="ache-page-title">
      <div>
        <h1>Diseño biomecánico</h1>
        <p>Generá un modelo CAD/STL conceptual desde las medidas del caso. La vista 3D sale del mismo OpenSCAD que se descarga para edición/fabricación.</p>
      </div>
      <div class="ache-status-pill">Preview técnico · no clínicamente validado</div>
    </div>
    """, unsafe_allow_html=True)

    if "measurements" not in st.session_state:
        st.markdown("""
        <div class="ache-product-card">
          <div class="ache-section-label">Antes de diseñar</div>
          <h3 style="margin-top:0">Faltan fotos y medidas del caso</h3>
          <p>Para generar una prótesis parametrizada primero necesitás completar el análisis de imágenes. Eso carga las medidas base del muñón/pata y evita diseñar a ojo.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📸 Ir a fotos y análisis", type="primary"):
            _go_to_page("fotos")
            st.rerun()
        return

    m = st.session_state.measurements

    with st.container():
        st.markdown("""
        <div class="ache-callout warning">
          <b>Uso correcto:</b> este módulo genera una base biomecánica conceptual. El archivo final debe ser ajustado y validado por veterinario, ortesista/biomecánico y fabricante antes de cualquier uso real.
        </div>
        """, unsafe_allow_html=True)

    col_params, col_3d = st.columns([0.86, 1.35], gap="large")

    with col_params:
        st.markdown("""
        <div class="ache-product-card compact">
          <div class="ache-section-label">Paso 1</div>
          <h3 style="margin-top:0">Parámetros principales</h3>
          <p style="margin-bottom:0;color:#68798A">Ajustá solo lo esencial. El resto lo calcula el template biomecánico.</p>
        </div>
        """, unsafe_allow_html=True)

        long_default = float(st.session_state.get("prosthetic_length", 10.0))
        long_prot = st.number_input(
            "Longitud total prótesis (cm)",
            value=long_default,
            min_value=1.0, max_value=80.0, step=0.5,
            help="Desde el encaje/socket hasta la base de apoyo."
        )
        diam_socket = st.number_input(
            "Diámetro socket / encaje (cm)",
            value=round(m.get("munon_circunf_distal_cm", 8.0) / 3.14159, 1),
            min_value=1.0, max_value=25.0, step=0.1,
            help="Estimado por circunferencia distal ÷ π. Ajustable por el profesional."
        )
        prof_socket = st.number_input(
            "Profundidad socket (cm)",
            value=round(min(m.get("munon_largo_cm", 5.0) * 0.6, long_prot * 0.4), 1),
            min_value=1.0, max_value=30.0, step=0.5,
            help="Cuánto entra el muñón dentro del encaje."
        )
        tipo_ext = st.selectbox("Extremidad", ["Delantera", "Trasera"], help="Luego se sumará izquierda/derecha y presets por extremidad.")
        material = st.selectbox("Material sugerido", ["PETG", "Nylon PA12", "TPU (flexible)", "PLA"], help="PLA queda para demo; para uso real habría que validar material y fatiga.")

        if st.button("⚙️ Generar / actualizar diseño", type="primary", width="stretch"):
            diam_eje = diam_socket * 0.65
            specs = {
                "longitud_total_cm": long_prot,
                "diametro_socket_cm": diam_socket,
                "profundidad_socket_cm": prof_socket,
                "diametro_pata_cm": round(diam_eje, 2),
                "tipo": tipo_ext,
                "material": material,
            }
            st.session_state.prosthetic_specs = specs
            scad = _generate_scad(specs)
            st.session_state.scad_code = scad
            if "current_case_id" in st.session_state:
                save_prosthetic_specs(DB_PATH, st.session_state.current_case_id, specs, scad)
            st.success("Diseño actualizado")

        if "prosthetic_specs" in st.session_state:
            specs = st.session_state.prosthetic_specs
            st.markdown(f"""
            <div class="ache-param-grid">
              <div class="ache-param"><span>Longitud</span><b>{specs['longitud_total_cm']} cm</b></div>
              <div class="ache-param"><span>Ø socket</span><b>{specs['diametro_socket_cm']} cm</b></div>
              <div class="ache-param"><span>Socket</span><b>{specs['profundidad_socket_cm']} cm</b></div>
              <div class="ache-param"><span>Eje</span><b>{specs['diametro_pata_cm']} cm</b></div>
              <div class="ache-param"><span>Extremidad</span><b>{specs['tipo']}</b></div>
              <div class="ache-param"><span>Material</span><b>{specs['material']}</b></div>
            </div>
            """, unsafe_allow_html=True)

    with col_3d:
        if "prosthetic_specs" not in st.session_state:
            st.markdown("""
            <div class="ache-product-card">
              <div class="ache-section-label">Paso 2</div>
              <h3 style="margin-top:0">Preview CAD</h3>
              <p>Presioná <b>Generar / actualizar diseño</b> para renderizar la prótesis biomecánica.</p>
            </div>
            """, unsafe_allow_html=True)
            return

        specs = st.session_state.prosthetic_specs
        scad_parametrizado = _generate_scad(specs)

        st.markdown("""
        <div class="ache-cad-shell">
          <div class="ache-cad-toolbar">
            <div><h3>Modelo 3D real</h3><small>Renderizado desde OpenSCAD · STL interactivo</small></div>
            <div class="ache-cad-badge">Biomech v4</div>
          </div>
        """, unsafe_allow_html=True)

        if not openscad_available():
            st.error("OpenSCAD no está disponible. Instalalo para renderizar el preview CAD real.")
        else:
            with st.spinner("Renderizando CAD real con OpenSCAD…"):
                try:
                    import plotly.graph_objects as go

                    scad_key = str(hash(scad_parametrizado))
                    cache = st.session_state.setdefault("stl_render_cache", {})
                    if scad_key in cache:
                        stl_bytes = cache[scad_key]
                    else:
                        stl_bytes = render_scad_to_stl(scad_parametrizado)
                        cache[scad_key] = stl_bytes

                    verts, faces = parse_stl(stl_bytes)

                    fig = go.Figure(data=[go.Mesh3d(
                        x=verts[:,0], y=verts[:,1], z=verts[:,2],
                        i=faces[:,0], j=faces[:,1], k=faces[:,2],
                        color="#4F5D6A",
                        opacity=1.0,
                        flatshading=False,
                        lighting=dict(ambient=0.62, diffuse=0.8, specular=0.22, roughness=0.68),
                        lightposition=dict(x=80, y=-120, z=160),
                        hoverinfo="skip"
                    )])

                    zmax = float(np.max(verts[:,2])) if len(verts) else 10
                    ymax = float(np.max(verts[:,1])) if len(verts) else 8
                    fig.add_trace(go.Scatter3d(
                        x=[0,0], y=[0, ymax+1.4], z=[0.25,0.25],
                        mode="lines+text", text=["", "frente / pie"],
                        line=dict(color="#F2AA24", width=5),
                        textposition="top center", showlegend=False, hoverinfo="skip"
                    ))
                    fig.add_trace(go.Scatter3d(
                        x=[0,0], y=[0,0], z=[0,zmax],
                        mode="lines+text", text=["suelo", "socket"],
                        line=dict(color="#173555", width=3, dash="dot"),
                        textposition="top center", showlegend=False, hoverinfo="skip"
                    ))

                    fig.update_layout(
                        scene=dict(
                            xaxis_title="Ancho (cm)", yaxis_title="Frente / atrás (cm)", zaxis_title="Altura (cm)",
                            aspectmode="data",
                            camera=dict(eye=dict(x=1.35, y=-2.55, z=1.05), up=dict(x=0,y=0,z=1)),
                            xaxis=dict(showbackground=True, backgroundcolor="#F8FAFC", gridcolor="rgba(23,53,85,.13)", zeroline=False),
                            yaxis=dict(showbackground=True, backgroundcolor="#F8FAFC", gridcolor="rgba(23,53,85,.13)", zeroline=False),
                            zaxis=dict(showbackground=True, backgroundcolor="#F8FAFC", gridcolor="rgba(23,53,85,.16)", zeroline=False),
                        ),
                        height=650,
                        margin=dict(l=0, r=0, t=4, b=0),
                        paper_bgcolor="#FFFFFF",
                        scene_bgcolor="#FFFFFF",
                    )
                    st.plotly_chart(fig, use_container_width=True, config={
                        "displayModeBar": True,
                        "displaylogo": False,
                        "scrollZoom": True,
                        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                        "toImageButtonOptions": {"format":"png", "filename":"ache_cad_real"},
                    })

                    dl1, dl2 = st.columns(2)
                    with dl1:
                        st.download_button("📥 Descargar STL", data=stl_bytes, file_name="ache_protesis_biomecanica.stl", mime="model/stl", type="secondary", width="stretch")
                    with dl2:
                        st.download_button("📥 Descargar OpenSCAD", data=scad_parametrizado.encode("utf-8"), file_name="ache_protesis_biomecanica.scad", mime="text/plain", type="primary", width="stretch")
                    st.caption(f"Malla real: {len(verts):,} vértices · {len(faces):,} caras · Template biomecánico v4")

                except Exception as e:
                    st.error(f"No se pudo renderizar el CAD real con OpenSCAD: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="ache-callout">
      <b>Próximas mejoras CAD:</b> presets para delantera/trasera, izquierda/derecha, perros mestizos por peso/medidas reales, rigidez de resortes/amortiguadores y biblioteca de templates propios de Ache.
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PÁGINA: GUÍA QUIRÚRGICA
# ─────────────────────────────────────────────────────────────────────────────
def page_guia():
    """Guía clínica/protésica interactiva basada en la Guía Ache v0.2."""
    st.header("🩺 Guía clínica y protésica")

    st.markdown("""
    <div class="ache-info">
      <b>Enfoque:</b> esta sección no indica dónde amputar. Ayuda a evaluar
      compatibilidad protésica externa, alertas clínicas, requisitos del muñón,
      adaptación y comunicación entre veterinario, cirujano, rehabilitador,
      fabricante y tutor.
    </div>
    """, unsafe_allow_html=True)

    guia_docx = ROOT / "assets" / "Ache_Innovation_Guia_v0.2.docx"
    if guia_docx.exists():
        with open(guia_docx, "rb") as f:
            st.download_button(
                "📄 Descargar guía técnica completa v0.2",
                data=f.read(),
                file_name="Ache_Innovation_Guia_Tecnica_v0.2.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="secondary",
                width="stretch",
            )

    case = st.session_state.get("current_case", {}) or {}
    measurements = st.session_state.get("measurements", {}) or {}
    specs = st.session_state.get("prosthetic_specs", {}) or {}
    breed_info = st.session_state.get("breed_info", {}) or {}

    # Adaptador para el módulo v0.2 generado como herramienta independiente.
    caso_activo = {
        "nombre_paciente": case.get("nombre_perro", "—"),
        "nombre_perro": case.get("nombre_perro", "—"),
        "tutor": case.get("nombre_dueno", "—"),
        "veterinario": case.get("vet_nombre", "—"),
        "raza": st.session_state.get("detected_breed") or case.get("raza_detectada") or case.get("raza_manual") or "—",
        "peso_kg": case.get("peso_actual", "—"),
        "edad": case.get("edad", "—"),
        "sexo": case.get("sexo", "—"),
        "extremidad": case.get("extremidad", "—"),
        "estado": case.get("estado", "—"),
        "notas": case.get("notas", ""),
        "munon_largo_cm": measurements.get("munon_largo_cm", "—"),
        "munon_circunf_base_cm": measurements.get("munon_circunf_base_cm", "—"),
        "munon_circunf_distal_cm": measurements.get("munon_circunf_distal_cm", "—"),
        "profundidad_socket_cm": specs.get("profundidad_socket_cm", "—"),
        "longitud_protesis_cm": specs.get("longitud_total_cm", "—"),
        "breed_info": breed_info,
    }

    if not case:
        st.warning("No hay caso activo. Podés usar la guía como referencia general, pero para obtener recomendaciones aplicadas creá o cargá un caso primero.")

    render_guia_quirurgica(caso_activo=caso_activo if case else None)


# ─────────────────────────────────────────────────────────────────────────────
# PÁGINA: GENERAR REPORTE
# ─────────────────────────────────────────────────────────────────────────────
def page_reporte():
    st.header("📋 Generar Reporte PDF")

    case = st.session_state.get("current_case", {})
    if not case:
        st.warning("No hay caso activo. Creá o cargá uno primero.")
        return

    st.markdown(f"**Caso:** {case.get('nombre_perro', '—')} — {case.get('nombre_dueno', '—')}")
    st.divider()

    if st.button("📄 Generar PDF completo", type="primary"):
        if "measurements" not in st.session_state:
            st.warning("Agregá al menos las medidas del muñón antes de generar el reporte.")
            return

        with st.spinner("Generando PDF..."):
            report_data = {
                "case":           case,
                "measurements":   st.session_state.get("measurements", {}),
                "breed_info":     st.session_state.get("breed_info", {}),
                "detected_breed": st.session_state.get("detected_breed", "No detectada"),
                "prosthetic_specs": st.session_state.get("prosthetic_specs", {}),
                "fecha":          datetime.now().strftime("%d/%m/%Y %H:%M"),
            }
            pdf_bytes = generate_pdf_report(report_data)

        nombre   = case.get("nombre_perro", "paciente").replace(" ", "_")
        fecha_fn = datetime.now().strftime("%Y%m%d")

        st.download_button(
            "⬇️ Descargar reporte PDF",
            data=pdf_bytes,
            file_name=f"Ache_{nombre}_{fecha_fn}.pdf",
            mime="application/pdf",
            type="primary"
        )
        st.success("✅ Reporte generado. Descargalo con el botón de arriba.")


# ─────────────────────────────────────────────────────────────────────────────
# PÁGINA: HISTORIAL
# ─────────────────────────────────────────────────────────────────────────────

def _inline_local_assets_for_html(html: str, base_dir: Path) -> str:
    """Make standalone HTML previews work inside Streamlit by inlining local images."""
    import re, mimetypes
    def repl(match):
        attr, quote, ref = match.group(1), match.group(2), match.group(3)
        if ref.startswith(("http://", "https://", "data:", "#", "mailto:", "tel:")):
            return match.group(0)
        local = (base_dir / ref).resolve()
        try:
            local.relative_to(base_dir.resolve())
        except Exception:
            return match.group(0)
        if not local.exists() or not local.is_file():
            return match.group(0)
        mime = mimetypes.guess_type(str(local))[0] or "application/octet-stream"
        data = base64.b64encode(local.read_bytes()).decode("ascii")
        return f'{attr}={quote}data:{mime};base64,{data}{quote}'
    return re.sub(r'\b(src|href)=("|\')([^"\']+)("|\')', lambda m: repl(m), html)


def _render_embedded_html_page(title: str, path: Path, intro: str, download_name: str, clean: bool = False):
    if not path.exists():
        st.error(f"No encontré el archivo integrado: {path}")
        st.caption("La carpeta está ordenada, pero falta copiar ese HTML a la ubicación esperada.")
        return
    html = path.read_text(encoding="utf-8", errors="ignore")
    html = _inline_local_assets_for_html(html, path.parent)
    if not clean:
        st.header(title)
        st.markdown(f"""
        <div class="ache-callout">
          <strong>Vista integrada:</strong> {intro}
        </div>
        """, unsafe_allow_html=True)
        st.download_button(
            "⬇️ Descargar esta página HTML",
            data=html.encode("utf-8"),
            file_name=download_name,
            mime="text/html",
            width="stretch",
        )
    components.html(html, height=1120, scrolling=True)

def page_web_marketplace():
    _render_embedded_html_page(
        "🌐 Web institucional y marketplace",
        MASTER_ROOT / "02_Web_Institucional" / "ache-innovation-claude.html",
        "esta es la experiencia principal de Ache Innovation. Desde esta web se presenta la marca, productos, marketplace y acceso al módulo Biomechanics Studio para parametrización clínica.",
        "ache_innovation_web_marketplace.html",
        clean=True,
    )


def page_productivos():
    bovinos_dir = MASTER_ROOT / "03_Animales_Productivos" / "Bovinos" / "Ache_Bovinos"
    path = bovinos_dir / "ache-innovation.html"
    if not path.exists():
        path = bovinos_dir / "ache_innovation_SHARE.html"
    _render_embedded_html_page(
        "🐄 Animales productivos",
        path,
        "sección separada para bovinos y animales productivos, sin mezclarla con el software canino.",
        "ache_innovation_animales_productivos.html",
        clean=True,
    )

def page_historial():
    st.header("🗄️ Historial de Casos")

    casos = get_cases(DB_PATH)

    if not casos:
        st.info("No hay casos registrados todavía.")
        return

    st.markdown(f"**{len(casos)} caso(s) registrado(s)**")

    for row in casos:
        case_id, nombre, dueno, extremidad, raza, estado, fecha = row
        fecha_fmt = fecha[:10] if fecha else "—"

        with st.expander(f"#{case_id} — {nombre} ({dueno}) — {fecha_fmt}"):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**Extremidad:** {extremidad}  \n"
                            f"**Raza:** {raza}  \n"
                            f"**Estado:** {estado}")
            with col2:
                if st.button(f"Cargar caso #{case_id}", key=f"load_{case_id}",
                             type="primary"):
                    case_full = get_case(DB_PATH, case_id)
                    if case_full:
                        st.session_state.current_case_id = case_id
                        st.session_state.current_case    = dict(case_full)

                        # Cargar medidas si existen
                        meas_row = get_case_measurements(DB_PATH, case_id)
                        if meas_row:
                            st.session_state.measurements = {
                                "munon_largo_cm":          meas_row.get("munon_largo_cm", 0),
                                "munon_circunf_base_cm":   meas_row.get("munon_circunf_base_cm", 0),
                                "munon_circunf_distal_cm": meas_row.get("munon_circunf_distal_cm", 0),
                                "scale_mm_per_px":         meas_row.get("scale_mm_per_px"),
                            }
                            if meas_row.get("breed_info"):
                                st.session_state.breed_info = meas_row["breed_info"]

                        st.success(f"Caso #{case_id} cargado: **{nombre}**")
                        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def _check_password() -> bool:
    """Pantalla de login simple. Devuelve True si ya autenticado."""
    if st.session_state.get("_authenticated"):
        return True

    # En embed mode no pedimos contraseña (el iframe está dentro de la web de Ache)
    if _embed_mode():
        return True

    PWD = st.secrets.get("APP_PASSWORD", "ache2025") if hasattr(st, "secrets") else "ache2025"

    st.markdown("""
    <style>
    [data-testid="stSidebar"]{display:none!important}
    .block-container{max-width:440px!important;padding-top:5rem!important}
    </style>
    """, unsafe_allow_html=True)

    logo_path = ROOT / "assets" / "ache_logo_transparent.png"
    if logo_path.exists():
        col = st.columns([1, 2, 1])[1]
        col.image(str(logo_path), width=180)

    st.markdown("<h2 style='text-align:center;color:#0A2560;margin:.5rem 0 1.5rem'>Ache Innovation</h2>", unsafe_allow_html=True)

    pwd = st.text_input("Contraseña", type="password", placeholder="Ingresá la clave de acceso", label_visibility="collapsed")
    if st.button("Entrar →", type="primary", use_container_width=True):
        if pwd == PWD:
            st.session_state._authenticated = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta")
    return False


def main():
    if not _check_password():
        return
    if _embed_mode():
        st.markdown("""<style>
        [data-testid="stSidebar"], .ache-brand-header, .ache-nav-lite {display:none!important;}
        .block-container{padding-top:1rem!important;max-width:1180px!important;}
        iframe{box-shadow:none!important;border-radius:16px!important;}
        </style>""", unsafe_allow_html=True)
        page = _embed_page_internal()
    else:
        _ensure_nav_state()
        render_sidebar()
        render_brand_header()
        page = render_top_navigation(st.session_state.active_nav)

    if   page == "🏠  Inicio":                    page_inicio()
    elif page == "🐄  Animales Productivos":      page_productivos()
    elif page == "🐕  Nuevo Caso":                page_nuevo_caso()
    elif page == "📸  Análisis de Imágenes":      page_analisis()
    elif page == "🦴  Diseño de Prótesis":        page_diseno()
    elif page == "🔪  Guía Quirúrgica":           page_guia()
    elif page == "📋  Generar Reporte":           page_reporte()
    elif page == "🗄️  Historial de Casos":        page_historial()


if __name__ == "__main__":
    main()
