import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from google.oauth2 import service_account
from googleapiclient.discovery import build
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# Função para converter imagem local em base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- CSS: FOCO NO EFEITO 3D DO TOPO ---
st.markdown("""
    <style>
    /* Fundo Neumórfico Geral */
    .stApp { background-color: #e0e5ec; }
    
    /* 1. LOGO EM 3D (EFEITO ELEVADO) */
    .logo-container-3d {
        display: flex;
        justify-content: center;
        padding: 20px 0;
        margin-bottom: -30px;
        position: relative;
        z-index: 10;
    }
    .logo-box {
        background: #e0e5ec;
        padding: 15px;
        border-radius: 20px;
        box-shadow: 7px 7px 14px #bebebe, -7px -7px 14px #ffffff;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    /* 2. FAIXA VERMELHA COM PROFUNDIDADE */
    .header-senai-3d { 
        background: #ff0000; 
        padding: 50px 0px 30px 0px; 
        color: white; 
        text-align: center; 
        width: 100vw;
        position: relative;
        left: 50%;
        right: 50%;
        margin-left: -50vw;
        margin-right: -50vw;
        z-index: 5;
        /* Sombra externa para elevar e interna para textura */
        box-shadow: 0px 10px 20px rgba(0,0,0,0.2), inset 0px -5px 10px rgba(0,0,0,0.1);
        border-bottom: 5px solid #cc0000;
    }
    .header-senai-3d h1 { 
        font-size: 32px !important; 
        margin: 0; 
        text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
        font-weight: 900;
        color: white !important;
    }
    .header-senai-3d p { font-size: 18px !important; margin-top: 10px; font-weight: 500; color: white !important; }

    /* 3. FACHADA COM MOLDURA 3D (EFEITO DE BOTÃO GRANDE) */
    .fachada-container-3d {
        margin-top: 30px;
        padding: 15px;
        background: #e0e5ec;
        border-radius: 30px;
        box-shadow: 12px 12px 24px #bebebe, -12px -12px 24px #ffffff;
        transition: transform 0.2s;
    }
    .fachada-container-3d:hover {
        transform: scale(1.01);
    }
    .fachada-img {
        border-radius: 20px;
        width: 100%;
        display: block;
    }

    /* Ajustes de formulário e botões (Mantidos da Âncora) */
    label, [data-testid="stWidgetLabel"] p { color: #000000 !important; font-weight: 600 !important; }
    div.stButton > button { 
        background-color: #ff0000 !important;
        color: #ffffff !important; 
        font-weight: bold !important; 
        height: 55px !important;
        border-radius: 15px !important; 
        width: 100% !important;
        box-shadow: 6px 6px 12px #b8b9be, -6px -6px 12px #ffffff !important;
    }
    [data-testid="stForm"] {
        background-color: #e0e5ec !important;
        border-radius: 30px !important;
        box-shadow: inset 8px 8px 16px #bebebe, inset -8px -8px 16px #ffffff !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÕES DE CAMINHO ---
path_logo = os.path.join("imagens", "logo.png")
path_fachada = os.path.join("imagens", "fachada.jpg")
url_senai = "https://www.sp.senai.br/cursos?unidade=122"

# --- INTERFACE ---

# 1. LOGO EM BOX 3D
if os.path.exists(path_logo):
    logo_base64 = get_base64_of_bin_file(path_logo)
    st.markdown(f'''
        <div class="logo-container-3d">
            <div class="logo-box">
                <img src="data:image/png;base64,{logo_base64}" width="140">
            </div>
        </div>
    ''', unsafe_allow_html=True)

# 2. FAIXA VERMELHA 3D
st.markdown(f'''
    <div class="header-senai-3d">
        <h1>SENAI GUARULHOS</h1>
        <p>Unidade 122 - Registro de Interesse Profissional</p>
    </div>
''', unsafe_allow_html=True)

# 3. FACHADA EM CONTAINER 3D
if os.path.exists(path_fachada):
    fachada_base64 = get_base64_of_bin_file(path_fachada)
    col_f1, col_f2, col_f3 = st.columns([1, 6, 1])
    with col_f2:
        st.markdown(f'''
            <div class="fachada-container-3d">
                <a href="{url_senai}" target="_blank">
                    <img src="data:image/jpeg;base64,{fachada_base64}" class="fachada-img">
                </a>
            </div>
        ''', unsafe_allow_html=True)

# --- ESPAÇO PARA O FORMULÁRIO (RESTANTE DO CÓDIGO) ---
st.markdown("<br>", unsafe_allow_html=True)
# O restante da sua lógica de formulário e scraping continua aqui...
