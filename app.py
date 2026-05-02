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

# --- ESTILO CSS (Centralização da Logo + Identidade SENAI) ---
st.markdown("""
    <style>
    /* CSS para centralizar a imagem da logo */
    .stImage > div {
        display: flex;
        justify-content: center;
        width: 100%;
    }
    .header-senai {
        background-color: #ff0000;
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-top: 10px;
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

# --- 1. LOGO (Centralizada via CSS) ---
if os.path.exists("imagens/logo.png"):
    st.image("imagens/logo.png", width=200)

# --- 2. CABEÇALHO ---
st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Hermenegildo Campos de Almeida</p></div>', unsafe_allow_html=True)

# --- 3. IMAGEM DA FACHADA (Lendo da sua pasta 'imagens') ---
if os.path.exists("imagens/fachada.jpg"):
    st.image("imagens/fachada.jpg", caption="Unidade SENAI Hermenegildo Campos de Almeida - Guarulhos", use_container_width=True)
else:
    # Mostra um alerta informativo se o arquivo não for encontrado
    st.info("📌 Dica: A imagem 'fachada.jpg' não foi encontrada na pasta 'imagens'. Verifique o nome do arquivo no GitHub.")

st.write("---")

# --- MAPEAMENTO DE CURSOS ---
dados_cursos = {
    "Tecnologia da Informação": [
        "Implantação de Serviços de IA em Nuvem", "IA Generativa: Google Gemini",
        "IA Generativa: Microsoft Copilot", "IA Generativa: ChatGPT",
        "Power BI", "Excel Avançado", "Técnico em Desenvolvimento de Sistemas"
    ],
    "Administração e Gestão": ["Almoxarife", "Assistente Administrativo", "Assistente de RH", "Financeiro"],
    "Metalmecânica": ["Usinagem", "Soldagem"],
    "Outras Áreas": ["Logística", "Eletroeletrônica"]
}

# --- INTERFACE DE CADASTRO ---
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.write("### 📋 Ficha de Interesse")
    
    # Menus dinâmicos
    area_sel = st.selectbox("1. Área:", ["Selecione..."] + list(dados_cursos.keys()))
    curso_sel = st.selectbox("2. Curso:", ["Selecione..."] + (dados_cursos[area_sel] if area_sel != "Selecione..." else []))
    
    with st.form("form_final_v4", clear_on_submit=True):
        nome = st.text_input("Nome")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp")
        sugestao = st.text_area("Sugestão de curso:")
        if st.form_submit_button("REGISTRAR INTERESSE"):
            if nome and area_sel != "Selecione...":
                data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                c.execute("INSERT INTO leads VALUES (?, ?, ?, ?, ?, ?, ?)", (nome, email, whats, area_sel, curso_sel, sugestao, data_hora))
                conn.commit()
                st.success("Interesse registrado!")
                st.balloons()
