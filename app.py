import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup
from google.oauth2 import service_account
from googleapiclient.discovery import build
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- CSS: AJUSTES 3D SOLICITADOS ---
st.markdown("""
    <style>
    .stApp { background-color: #e0e5ec; }
    
    /* 1. LOGO COM 3D PARA DENTRO (ESCAVADO) */
    .logo-container-3d {
        display: flex;
        justify-content: center;
        padding: 20px 0;
        margin-bottom: -35px;
        position: relative;
        z-index: 10;
    }
    .logo-box-inset {
        background: #e0e5ec;
        padding: 15px 25px;
        border-radius: 25px;
        /* Efeito Inset: Sombra para dentro */
        box-shadow: inset 6px 6px 12px #bebebe, inset -6px -6px 12px #ffffff;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    /* 2. FAIXA VERMELHA */
    .header-senai-3d { 
        background: #ff0000; 
        padding: 55px 0px 30px 0px; 
        color: white; 
        text-align: center; 
        width: 100vw;
        position: relative;
        left: 50%;
        right: 50%;
        margin-left: -50vw;
        margin-right: -50vw;
        z-index: 5;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.2);
        border-bottom: 5px solid #cc0000;
    }
    .header-senai-3d h1 { font-size: 32px !important; margin: 0; font-weight: 900; color: white !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }

    /* 3. FACHADA AMPLIADA COM 3D JUSTO */
    .fachada-container-full {
        margin-top: 25px;
        padding: 8px; /* Reduzi o padding para a imagem ocupar mais espaço */
        background: #e0e5ec;
        border-radius: 25px;
        box-shadow: 10px 10px 20px #bebebe, -10px -10px 20px #ffffff;
        width: 100%;
    }
    .fachada-img-full {
        border-radius: 20px;
        width: 100%;
        display: block;
        transition: transform 0.3s;
    }
    .fachada-img-full:hover { transform: scale(0.995); }

    /* Estilos de Formulário (Mantidos da Âncora) */
    [data-testid="stForm"] {
        background-color: #e0e5ec !important;
        border-radius: 30px !important;
        box-shadow: inset 8px 8px 16px #bebebe, inset -8px -8px 16px #ffffff !important;
        border: none !important;
    }
    label, [data-testid="stWidgetLabel"] p { color: #000000 !important; font-weight: 700 !important; }
    div.stButton > button { 
        background-color: #ff0000 !important;
        color: #ffffff !important; 
        font-weight: bold !important; 
        height: 55px !important;
        border-radius: 15px !important; 
        width: 100% !important;
        box-shadow: 5px 5px 10px #b8b9be, -5px -5px 10px #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INTERFACE ---

# 1. Logo Inset
path_logo = os.path.join("imagens", "logo.png")
if os.path.exists(path_logo):
    logo_64 = get_base64_of_bin_file(path_logo)
    st.markdown(f'''
        <div class="logo-container-3d">
            <div class="logo-box-inset">
                <img src="data:image/png;base64,{logo_64}" width="140">
            </div>
        </div>
    ''', unsafe_allow_html=True)

# 2. Faixa
st.markdown(f'''
    <div class="header-senai-3d">
        <h1>SENAI GUARULHOS</h1>
        <p>Unidade 122 - Registro de Interesse Profissional</p>
    </div>
''', unsafe_allow_html=True)

# 3. Fachada Ampliada
path_fachada = os.path.join("imagens", "fachada.jpg")
url_senai = "https://www.sp.senai.br/cursos?unidade=122"

if os.path.exists(path_fachada):
    fachada_64 = get_base64_of_bin_file(path_fachada)
    col_f1, col_f2, col_f3 = st.columns([0.5, 9, 0.5]) # Aumentei a proporção da coluna central
    with col_f2:
        st.markdown(f'''
            <div class="fachada-container-full">
                <a href="{url_senai}" target="_blank">
                    <img src="data:image/jpeg;base64,{fachada_64}" class="fachada-img-full">
                </a>
            </div>
        ''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- O restante do seu formulário e lógica seguem aqui ---
