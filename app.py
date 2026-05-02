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

# --- ESTILO CSS ---
st.markdown("""
    <style>
    /* Centralizar a imagem e garantir que ela não estique */
    .stImage > div {
        display: flex;
        justify-content: center;
        width: 100%;
        margin-bottom: -15px; /* Reduz espaço abaixo da logo */
    }
    .header-senai {
        background-color: #ff0000;
        padding: 15px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    .header-senai h1 { font-size: 24px; margin: 0; }
    .header-senai p { font-size: 16px; margin: 5px 0 0 0; }

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

# --- 1. LOGO (Centralizada, PEQUENA E FIXA) ---
# Se o arquivo não existir, não mostra nada
if os.path.exists("imagens/logo.png"):
    # REDUÇÃO DRÁSTICA: width=120 e use_column_width=False
    st.image("imagens/logo.png", width=120, use_column_width=False)

# --- 2. CABEÇALHO ---
st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - H. Campos de Almeida</p></div>', unsafe_allow_html=True)

st.write("---")

# --- MAPEAMENTO DE CURSOS (Simplificado para o exemplo) ---
dados_cursos = {
    "Tecnologia da Informação": [
        "Implantação de Serviços de IA em Nuvem", "IA Generativa: ChatGPT",
        "Power BI", "Excel Avançado", "Técnico em Desenvolvimento de Sistemas"
    ],
    "Outras Áreas": ["Administração", "Logística", "Metalmecânica", "Eletroeletrônica"]
}

# --- INTERFACE DE CADASTRO ---
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.write("### 📋 Ficha de Interesse")
    
    # Menus dinâmicos
    area_sel = st.selectbox("1. Área:", ["Selecione..."] + sorted(list(dados_cursos.keys())))
    curso_sel = st.selectbox("2. Curso:", ["Selecione..."] + (sorted(dados_cursos[area_sel]) if area_sel != "Selecione..." else []))
    
    with st.form("form_final_v5", clear_on_submit=True):
        nome = st.text_input("Nome")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp")
        sugestao = st.text_area("Sugestão de curso:")
        if st.form_submit_button("REGISTRAR INTERESSE"):
            if nome and area_sel != "Selecione..." and curso_sel != "Selecione...":
                data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                c.execute("INSERT INTO leads VALUES (?, ?, ?, ?, ?, ?, ?)", (nome, email, whats, area_sel, curso_sel, sugestao, data_hora))
                conn.commit()
                st.success("Interesse registrado!")
                st.balloons()
            else:
                st.error("Preencha todos os campos corretamente.")

# --- ADMIN ---
st.sidebar.title("🔒 Admin")
senha = st.sidebar.text_input("Senha de Acesso", type="password")
if senha == "senai122":
    st.sidebar.success("Acesso Liberado")
    df = pd.read_sql_query("SELECT * FROM leads", conn)
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.sidebar.download_button("Baixar Planilha (Excel)", csv, "leads.csv", "text/csv")
