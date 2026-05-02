import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- BANCO DE DADOS ---
conn = sqlite3.connect('senai_guarulhos_final.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS leads 
             (nome TEXT, email TEXT, whatsapp TEXT, area TEXT, curso TEXT, sugestao TEXT, data TEXT)''')
conn.commit()

# --- ESTILO CSS (Blindado para centralização e botões) ---
st.markdown("""
    <style>
    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
        margin-left: auto;
        margin-right: auto;
        width: 100%;
    }
    .header-senai {
        background-color: #ff0000;
        padding: 15px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    div.stButton > button {
        background-color: #000000 !important;
        color: white !important;
        font-weight: bold !important;
        width: 100% !important;
        height: 3.5em !important;
        border-radius: 8px !important;
        border: none !important;
    }
    label { font-weight: bold !important; color: #1e1e1e !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. LOGO SENAI (Centralizada via Colunas) ---
col_l1, col_l2, col_l3 = st.columns([2, 1, 2])
with col_l2:
    if os.path.exists("imagens/logo.png"):
        st.image("imagens/logo.png", width=150)

# --- 2. CABEÇALHO ---
st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Hermenegildo Campos de Almeida</p></div>', unsafe_allow_html=True)

# --- 3. IMAGEM DA FACHADA (Nova imagem que você subiu) ---
f_col1, f_col2, f_col3 = st.columns([1, 6, 1]) 
with f_col2:
    if os.path.exists("imagens/fachada.jpg"):
        st.image("imagens/fachada.jpg", use_container_width=True)
    else:
        st.info("Aguardando nova imagem 'fachada.jpg' na pasta imagens.")

st.write("---")

# --- MAPEAMENTO DE CURSOS ---
dados_cursos = {
    "Tecnologia da Informação": [
        "Implantação de Serviços de IA em Nuvem", "IA Generativa: ChatGPT",
        "IA Generativa: Google Gemini", "IA Generativa: Microsoft Copilot",
        "Power BI", "Excel Avançado", "Técnico em Desenvolvimento de Sistemas"
    ],
    "Administração e Gestão": ["Almoxarife", "Assistente Administrativo", "Assistente de RH", "Assistente Financeiro"],
    "Outras Áreas": ["Logística", "Metalmecânica", "Eletroeletrônica", "Segurança do Trabalho"]
}

# --- INTERFACE DE CADASTRO ---
col_f1, col_f2, col_f3 = st.columns([1, 2, 1])

with col_f2:
    st.write("### 📋 Ficha de Interesse")
    
    area_sel = st.selectbox("1. Selecione a Área:", ["Selecione..."] + sorted(list(dados_cursos.keys())))
    lista_cursos = sorted(dados_cursos
