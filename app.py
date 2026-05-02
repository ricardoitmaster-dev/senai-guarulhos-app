import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- BANCO DE DADOS ---
conn = sqlite3.connect(r'G:\Formação IA Generativa - Google Cloud\Backup\senai_database_backup.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS leads 
             (nome TEXT, email TEXT, whatsapp TEXT, area TEXT, curso TEXT, sugestao TEXT, data TEXT)''')
conn.commit()

# --- ESTILO CSS ---
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

# --- 1. LOGO SENAI ---
col_l1, col_l2, col_l3 = st.columns([2, 1, 2])
with col_l2:
    if os.path.exists("imagens/logo.png"):
        st.image("imagens/logo.png", width=150)

# --- 2. CABEÇALHO ---
st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Hermenegildo Campos de Almeida</p></div>', unsafe_allow_html=True)

# --- 3. IMAGEM DA FACHADA ---
f_col1, f_col2, f_col3 = st.columns([1, 6, 1]) 
with f_col2:
    if os.path.exists("imagens/fachada.jpg"):
        st.image("imagens/fachada.jpg", use_container_width=True)

st.write("---")

# --- MAPEAMENTO DE CURSOS ---
dados_cursos = {
    "Tecnologia da Informação": [
        "IA Generativa: ChatGPT", "IA Generativa: Google Gemini",
        "IA Generativa: Microsoft Copilot", "Power BI", 
        "Excel Avançado", "Técnico em Desenvolvimento de Sistemas"
    ],
    "Administração e Gestão": ["Almoxarife", "Assistente Administrativo", "Assistente de RH"],
    "Outras Áreas": ["Logística", "Metalmecânica", "Eletroeletrônica"]
}

# --- INTERFACE DE CADASTRO ---
col_f1, col_f2, col_f3 = st.columns([1, 2, 1])

with col_f2:
    st.write("### 📋 Ficha de Interesse")
    
    area_sel = st.selectbox("1. Selecione a Área:", ["Selecione..."] + sorted(list(dados_cursos.keys())))
    lista_cursos = sorted(dados_cursos[area_sel]) if area_sel != "Selecione..." else []
    curso_sel = st.selectbox("2. Selecione o Curso:", ["Selecione..."] + lista_cursos)

    with st.form("form_final_v10", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp (com DDD)")
        sugestao = st.text_area("Sugestão de curso ou observação:")
        
        btn_enviar = st.form_submit_button("REGISTRAR INTERESSE")
        
        if btn_enviar:
            if nome and area_sel != "Selecione...":
                data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                c.execute("INSERT INTO leads VALUES (?, ?, ?, ?, ?, ?, ?)", 
                          (nome, email, whats, area_sel, curso_sel, sugestao, data_hora))
                conn.commit()
                st.success(f"Obrigado, {nome}! Interesse registrado.")
                st.balloons()
            else:
                st.error("Preencha os campos obrigatórios.")

# --- PAINEL ADMINISTRATIVO NO SIDEBAR ---
st.sidebar.title("🔒 Admin")
senha_adm = st.sidebar.text_input("Senha", type="password")

if senha_adm == "senai122":
    st.sidebar.success("Acesso Liberado")
    
    # Carregar dados
    df_leads = pd.read_sql_query("SELECT * FROM leads", conn)
    
    if st.sidebar.checkbox("Ver Interessados"):
        st.write("### 📊 Relatório")
        st.dataframe(df_leads)
    
    # Exportar CSV
    csv_data = df_leads.to_csv(index=False).encode('utf-8-sig')
    st.sidebar.download_button("📥 Baixar Planilha", csv_data, "leads.csv", "text/csv")
