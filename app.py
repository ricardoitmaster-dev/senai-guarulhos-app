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

# --- CSS: FOCO EM TAMANHO NATURAL E LEGIBILIDADE ---
st.markdown("""
    <style>
    .stApp { background-color: #e0e5ec; }
    
    /* Faixa Vermelha */
    .header-senai { 
        background: #ff0000; 
        padding: 30px 0px; 
        color: white; 
        text-align: center; 
        width: 100vw;
        position: relative;
        left: 50%;
        right: 50%;
        margin-left: -50vw;
        margin-right: -50vw;
        border-bottom: 4px solid #cc0000;
    }
    .header-senai h1 { font-size: 26px !important; margin: 0; font-weight: 800; color: white !important; }

    /* IMAGEM DA FACHADA: Tamanho Natural e Centralizada */
    .img-fachada-container {
        width: 100%;
        text-align: center;
        margin: 20px 0;
    }
    .img-fachada-container img {
        max-width: 100%; /* Garante que não estoure a tela do celular */
        height: auto;    /* Mantém a proporção original */
        border-radius: 10px;
    }

    /* MENSAGEM DE SUCESSO: Contraste Máximo para Celular */
    div[data-testid="stNotification"] {
        background-color: #ffffff !important; 
        border: 2px solid #ff0000 !important;
        padding: 20px !important;
    }
    div[data-testid="stNotification"] div {
        color: #000000 !important; 
        font-weight: bold !important;
        font-size: 18px !important;
    }

    /* Botão Registrar */
    div.stButton > button { 
        background-color: #ff0000 !important;
        color: #ffffff !important; 
        height: 50px !important;
        width: 100% !important;
        font-weight: bold !important;
        border-radius: 10px !important;
    }

    label { color: #000000 !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CAMINHOS ---
url_senai = "https://www.sp.senai.br/cursos?unidade=122"
path_logo = os.path.join("imagens", "logo.png")
path_fachada = os.path.join("imagens", "fachada.jpg")

# --- SCRAPING ---
@st.cache_data(ttl=43200)
def buscar_cursos_dinamicos():
    api_key = "3e14f4393c5a034104b37c071a0d021f" 
    try:
        params = {'api_key': api_key, 'url': url_senai, 'render': 'true'}
        response = requests.get('http://api.scraperapi.com', params=params, timeout=60)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            cards = soup.select('div[class*="card-curso"]') or soup.select('.item-lista-curso')
            mapa_real = {}
            for card in cards:
                area = card.select_one('.area-tematica, .txt-area').get_text(strip=True).title()
                titulo = card.select_one('.titulo-curso, h2').get_text(strip=True).upper()
                if area not in mapa_real: mapa_real[area] = []
                mapa_real[area].append(titulo)
            return mapa_real if mapa_real else {"TI": ["EXCEL"]}
        return {"TI": ["EXCEL"]}
    except: return {"TI": ["EXCEL"]}

# --- INTERFACE ---

# 1. Logo
if os.path.exists(path_logo):
    st.image(path_logo, width=120)

# 2. Cabeçalho
st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS - UNIT 122</h1></div>', unsafe_allow_html=True)

# 3. Imagem da Fachada (Tamanho Natural)
if os.path.exists(path_fachada):
    img_64 = get_base64_of_bin_file(path_fachada)
    st.markdown(f'<div class="img-fachada-container"><img src="data:image/jpeg;base64,{img_64}"></div>', unsafe_allow_html=True)

dados_cursos = buscar_cursos_dinamicos()

# 4. Formulário
col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    st.markdown("<h3 style='text-align: center;'>📋 Registro de Interesse</h3>", unsafe_allow_html=True)
    area_sel = st.selectbox("Escolha a Área:", sorted(list(dados_cursos.keys())))
    curso_sel = st.selectbox("Escolha o Curso:", sorted(dados_cursos[area_sel]))

    with st.form("meu_form"):
        nome = st.text_input("Nome")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp")
        enviar = st.form_submit_button("REGISTRAR AGORA")

        if enviar:
            if nome and email:
                st.success(f"Excelente, {nome}! Recebemos seu interesse.")
                st.balloons()
            else:
                st.error("Preencha os campos obrigatórios.")
