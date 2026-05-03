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
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# --- CSS COMPLETO (DESIGN 3D ATUALIZADO + FORMULÁRIO) ---
st.markdown("""
    <style>
    .stApp { background-color: #e0e5ec; }
    
    /* 1. LOGO COM 3D INSET (AFUNDADO) */
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
    .header-senai-3d p { color: white !important; font-weight: 500; }

    /* 3. FACHADA AMPLIADA */
    .fachada-container-full {
        margin-top: 25px;
        padding: 8px;
        background: #e0e5ec;
        border-radius: 25px;
        box-shadow: 10px 10px 20px #bebebe, -10px -10px 20px #ffffff;
        width: 100%;
    }
    .fachada-img-full {
        border-radius: 20px;
        width: 100%;
        display: block;
    }

    /* FORMULÁRIO E INPUTS */
    [data-testid="stForm"] {
        background-color: #e0e5ec !important;
        border-radius: 30px !important;
        box-shadow: inset 8px 8px 16px #bebebe, inset -8px -8px 16px #ffffff !important;
        padding: 30px !important;
        border: none !important;
    }
    
    label, [data-testid="stWidgetLabel"] p { 
        color: #000000 !important; 
        font-weight: 700 !important; 
    }

    /* BOTÃO VERMELHO */
    div.stButton > button { 
        background-color: #ff0000 !important;
        color: #ffffff !important; 
        font-weight: bold !important; 
        height: 55px !important;
        border-radius: 15px !important; 
        width: 100% !important;
        box-shadow: 5px 5px 10px #b8b9be, -5px -5px 10px #ffffff !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE DADOS (SCRAPING) ---
@st.cache_data(ttl=3600)
def get_senai_courses():
    # Aqui vai sua lógica de scraping que configuramos com ScraperAPI
    # Retornando lista mockada para exemplo, mas mantendo a estrutura
    return ["Informatica Básica", "Excel Avançado", "IA Generativa", "Python para Dados"]

# --- INTERFACE ---

# 1. Logo Inset
path_logo = os.path.join("imagens", "logo.png")
logo_64 = get_base64_of_bin_file(path_logo)
if logo_64:
    st.markdown(f'''<div class="logo-container-3d"><div class="logo-box-inset"><img src="data:image/png;base64,{logo_64}" width="140"></div></div>''', unsafe_allow_html=True)

# 2. Faixa
st.markdown(f'''<div class="header-senai-3d"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Registro de Interesse Profissional</p></div>''', unsafe_allow_html=True)

# 3. Fachada
path_fachada = os.path.join("imagens", "fachada.jpg")
fachada_64 = get_base64_of_bin_file(path_fachada)
if fachada_64:
    col_f1, col_f2, col_f3 = st.columns([0.2, 9.6, 0.2])
    with col_f2:
        st.markdown(f'''<div class="fachada-container-full"><a href="https://www.sp.senai.br/cursos?unidade=122" target="_blank"><img src="data:image/jpeg;base64,{fachada_64}" class="fachada-img-full"></a></div>''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- FORMULÁRIO DE REGISTRO ---
cursos = get_senai_courses()

with st.form("registro_interesse"):
    st.subheader("Dados do Interessado")
    
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
    with col2:
        telefone = st.text_input("Telefone/WhatsApp")
        curso_interesse = st.selectbox("Selecione o Curso de Interesse", cursos)
    
    mensagem = st.text_area("Observações (Opcional)")
    
    submit = st.form_submit_button("REGISTRAR INTERESSE")

    if submit:
        if nome and email and telefone:
            st.success(f"Obrigado, {nome}! Seu interesse no curso {curso_interesse} foi registrado com sucesso.")
            # Aqui entra a lógica de salvar no Google Sheets que configuramos
        else:
            st.error("Por favor, preencha todos os campos obrigatórios.")
