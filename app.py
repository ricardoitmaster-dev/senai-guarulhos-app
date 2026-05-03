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

# --- CSS: VOLTA AO ESTILO 3D E FACHADA AMPLIADA ---
st.markdown("""
    <style>
    /* Fundo Neumórfico */
    .stApp { background-color: #e0e5ec; }
    
    /* FAIXA VERMELHA LARGURA TOTAL */
    .header-senai { 
        background: #ff0000; 
        padding: 40px 0px 25px 0px; 
        color: white; 
        text-align: center; 
        width: 100vw;
        position: relative;
        left: 50%;
        right: 50%;
        margin-left: -50vw;
        margin-right: -50vw;
        z-index: 5;
        box-shadow: 0px 10px 15px rgba(0,0,0,0.1);
        border-bottom: 4px solid #cc0000;
    }
    .header-senai h1 { font-size: 30px !important; margin: 0; font-weight: 800; color: white !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }

    /* IMAGEM DA FACHADA AMPLIADA (BANNER) */
    .img-3d-grande {
        width: 100%;
        display: block;
        margin: 20px auto;
        border-radius: 20px;
        box-shadow: 10px 10px 20px #bebebe, -10px -10px 20px #ffffff;
        border: 5px solid #e0e5ec;
    }

    /* MENSAGEM DE SUCESSO (Correção de Contraste Mantida) */
    div[data-testid="stNotification"] {
        background-color: #ffffff !important; 
        border: 3px solid #155724 !important;
        border-radius: 15px !important;
    }
    div[data-testid="stNotification"] div {
        color: #000000 !important; 
        font-weight: 800 !important;
        font-size: 18px !important;
    }

    /* FORMULÁRIO 3D (Efeito Escavado) */
    [data-testid="stForm"] {
        background-color: #e0e5ec !important;
        border-radius: 30px !important;
        padding: 2rem !important;
        box-shadow: inset 8px 8px 16px #bebebe, inset -8px -8px 16px #ffffff !important;
        border: none !important;
    }

    /* BOTÃO 3D */
    div.stButton > button { 
        background-color: #ff0000 !important;
        color: #ffffff !important; 
        font-weight: bold !important; 
        height: 55px !important;
        border-radius: 15px !important; 
        width: 100% !important;
        border: none !important;
        box-shadow: 6px 6px 12px #b8b9be, -6px -6px 12px #ffffff !important;
        transition: 0.3s;
    }
    div.stButton > button:active {
        box-shadow: inset 4px 4px 8px #b8b9be, inset -4px -4px 8px #ffffff !important;
    }

    /* Labels em negrito para facilitar leitura */
    label, [data-testid="stWidgetLabel"] p {
        color: #000000 !important;
        font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CAMINHOS ---
url_senai = "https://www.sp.senai.br/cursos?unidade=122"
path_logo = os.path.join("imagens", "logo.png")
path_fachada = os.path.join("imagens", "fachada.jpg")

# --- INTERFACE ---

# 1. Logo
if os.path.exists(path_logo):
    logo_64 = get_base64_of_bin_file(path_logo)
    st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{logo_64}" width="150" style="margin-bottom: -15px;"></div>', unsafe_allow_html=True)

# 2. Cabeçalho
st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p style="color:white; opacity:0.9;">Unidade 122</p></div>', unsafe_allow_html=True)

# 3. Imagem da Fachada (Banner 3D Grande)
if os.path.exists(path_fachada):
    fachada_64 = get_base64_of_bin_file(path_fachada)
    st.markdown(f'<img src="data:image/jpeg;base64,{fachada_64}" class="img-3d-grande">', unsafe_allow_html=True)

# --- SCRAPING (Simplificado para o exemplo) ---
@st.cache_data(ttl=43200)
def buscar_cursos():
    # Retornando fallback para garantir que o app carregue rápido
    return {
        "Tecnologia da Informação": ["EXCEL AVANÇADO", "IA GENERATIVA", "PYTHON", "POWER BI"],
        "Eletroeletrônica": ["ELETRICISTA INSTALADOR", "COMANDOS ELÉTRICOS"],
        "Gestão": ["ASSISTENTE ADMINISTRATIVO", "LOGÍSTICA"]
    }

dados_cursos = buscar_cursos()

# 4. Formulário Neumórfico
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<h3 style='text-align: center; color: #000; margin-top: 30px;'>📋 Cadastro de Interesse</h3>", unsafe_allow_html=True)
    
    area_sel = st.selectbox("Área Profissional:", sorted(list(dados_cursos.keys())))
    curso_sel = st.selectbox("Curso de Interesse:", sorted(dados_cursos[area_sel]))

    with st.form("form_3d_final", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("Seu melhor E-mail")
        whats = st.text_input("WhatsApp com DDD")
        
        enviar = st.form_submit_button("REGISTRAR AGORA")

        if enviar:
            if nome and email:
                st.success(f"Excelente, {nome}! Seu interesse foi registrado com sucesso.")
                st.balloons()
            else:
                st.error("Por favor, preencha o nome e e-mail.")

# --- ADMIN ---
st.sidebar.markdown("---")
if st.sidebar.text_input("Acesso Restrito", type="password") == "Celina2610$$":
    st.sidebar.success("Acesso Liberado")
