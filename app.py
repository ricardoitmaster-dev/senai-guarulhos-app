import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- BANCO DE DADOS (VERSÃO PARA NUVEM) ---
# Usamos um nome novo para forçar o Streamlit a criar um banco limpo e funcional na nuvem
db_file = 'dados_senai_v1.db'

conn = sqlite3.connect(db_file, check_same_thread=False)
c = conn.cursor()

# Criar a tabela se ela não existir
c.execute('''CREATE TABLE IF NOT EXISTS leads 
             (nome TEXT, email TEXT, whatsapp TEXT, area TEXT, curso TEXT, sugestao TEXT, data TEXT)''')
conn.commit()

# --- MAPEAMENTO DE CURSOS (LISTA FIEL) ---
dados_cursos = {
    "Administração e Gestão": ["Almoxarife", "Assistente Administrativo", "Assistente de RH", "Logística"],
    "Eletroeletrônica": ["Eletricista Instalador", "Comandos Elétricos", "CLP"],
    "Metalmecânica": ["Mecânico de Usinagem", "Soldador", "Programador e Operador de CNC"],
    "Tecnologia da Informação": [
        "Excel Avançado", "IA Generativa: ChatGPT", "IA Generativa: Google Gemini",
        "IA Generativa: Microsoft Copilot", "Power BI", "Técnico em Desenvolvimento de Sistemas"
    ],
    "Automobilística": ["Mecânico de Automóveis", "Eletricista Veicular"],
    "Outras Áreas": ["Segurança do Trabalho", "Alimentos"]
}

# --- ESTILO CSS ---
st.markdown("""
    <style>
    [data-testid="stImage"] { display: flex; justify-content: center; margin: auto; width: 100%; }
    .header-senai { background-color: #ff0000; padding: 15px; border-radius: 12px; color: white; text-align: center; margin: 20px 0; }
    div.stButton > button { background-color: #000000 !important; color: white !important; font-weight: bold !important; width: 100% !important; border-radius: 8px !important; }
    label { font-weight: bold !important; color: #1e1e1e !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. LOGO SENAI (CAMINHO RELATIVO) ---
path_logo = os.path.join("imagens", "logo.png")
col_l1, col_l2, col_l3 = st.columns([2, 1, 2])
with col_l2:
    if os.path.exists(path_logo):
        st.image(Image.open(path_logo), width=150)

# --- 2. CABEÇALHO ---
st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Hermenegildo Campos de Almeida</p></div>', unsafe_allow_html=True)

# --- 3. IMAGEM DA FACHADA (CAMINHO RELATIVO) ---
path_fachada = os.path.join("imagens", "fachada.jpg")
f_col1, f_col2, f_col3 = st.columns([1, 6, 1]) 
with f_col2:
    if os.path.exists(path_fachada):
        st.image(Image.open(path_fachada), use_container_width=True)

st.write("---")

# --- INTERFACE DE CADASTRO ---
col_f1, col_f2, col_f3 = st.columns([1, 2, 1])

with col_f2:
    st.write("### 📋 Ficha de Interesse")
    
    opcoes_areas = ["Selecione..."] + sorted(list(dados_cursos.keys()))
    area_sel = st.selectbox("1. Selecione a Área:", opcoes_areas)
    
    lista_cursos = ["Selecione..."] + sorted(dados_cursos[area_sel]) if area_sel != "Selecione..." else ["Selecione..."]
    curso_sel = st.selectbox("2. Selecione o Curso:", lista_cursos)

    with st.form("form_final_github", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp (com DDD)")
        sugestao = st.text_area("Sugestão de curso ou observação:")
        
        btn_enviar = st.form_submit_button("REGISTRAR INTERESSE")
        
        if btn_enviar:
            if nome and area_sel != "Selecione..." and curso_sel != "Selecione...":
                data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                c.execute("INSERT INTO leads VALUES (?, ?, ?, ?, ?, ?, ?)", 
                          (nome, email, whats, area_sel, curso_sel, sugestao, data_hora))
                conn.commit()
                st.success(f"Obrigado, {nome}! Seu interesse no curso de {curso_sel} foi registrado. Entraremos em contato assim que novas turmas forem abertas!")
                st.balloons()
            else:
                st.error("Por favor, preencha seu nome e selecione a Área e o Curso.")

# --- PAINEL ADMINISTRATIVO ---
st.sidebar.title("🔒 Admin")
senha_adm = st.sidebar.text_input("Senha", type="password")
if senha_adm == "senai122":
    df_leads = pd.read_sql_query("SELECT * FROM leads", conn)
    if st.sidebar.checkbox("Ver Interessados"):
        st.write("### 📊 Relatório")
        st.dataframe(df_leads)
    csv_data = df_leads.to_csv(index=False).encode('utf-8-sig')
    st.sidebar.download_button("📥 Baixar Planilha", csv_data, "leads.csv", "text/csv")
