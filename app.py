import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- ESTILO CSS (Blindado) ---
st.markdown("""
    <style>
    /* Forçar centralização de qualquer imagem */
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
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. LOGO SENAI (Centralizado por Colunas) ---
col_l1, col_l2, col_l3 = st.columns([2, 1, 2])
with col_l2: # Coluna do meio
    if os.path.exists("imagens/logo.png"):
        st.image("imagens/logo.png", width=150)

# --- 2. CABEÇALHO ---
st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - H. Campos de Almeida</p></div>', unsafe_allow_html=True)

# --- 3. IMAGEM DA FACHADA (Logo abaixo do cabeçalho) ---
# Usando colunas para controlar o tamanho e centralização da fachada também
f_col1, f_col2, f_col3 = st.columns([1, 6, 1]) 
with f_col2:
    if os.path.exists("imagens/fachada.jpg"):
        st.image("imagens/fachada.jpg", use_container_width=True)
    else:
        st.warning("⚠️ Arquivo 'imagens/fachada.jpg' não detectado no GitHub.")

st.write("---")

# --- BANCO DE DADOS ---
conn = sqlite3.connect('senai_guarulhos_final.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS leads 
             (nome TEXT, email TEXT, whatsapp TEXT, area TEXT, curso TEXT, sugestao TEXT, data TEXT)''')
conn.commit()

# --- CURSOS ---
dados_cursos = {
    "Tecnologia da Informação": ["IA Generativa: ChatGPT", "Power BI", "Excel Avançado", "Técnico em Desenvolvimento de Sistemas"],
    "Outras Áreas": ["Administração", "Logística", "Metalmecânica"]
}

# --- FORMULÁRIO ---
col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
with col_f2:
    st.write("### 📋 Ficha de Interesse")
    area_sel = st.selectbox("1. Área:", ["Selecione..."] + list(dados_cursos.keys()))
    curso_sel = st.selectbox("2. Curso:", ["Selecione..."] + (dados_cursos[area_sel] if area_sel != "Selecione..." else []))

    with st.form("form_v6", clear_on_submit=True):
        nome = st.text_input("Nome")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp")
        sugestao = st.text_area("Sugestão:")
        if st.form_submit_button("REGISTRAR INTERESSE"):
            if nome and area_sel != "Selecione...":
                data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                c.execute("INSERT INTO leads VALUES (?,?,?,?,?,?,?)", (nome, email, whats, area_sel, curso_sel, sugestao, data_hora))
                conn.commit()
                st.success("Registrado!")
                st.balloons()
