import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- BANCO DE DADOS ---
conn = sqlite3.connect('senai_database.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS leads 
             (nome TEXT, email TEXT, whatsapp TEXT, area TEXT, curso TEXT, data TEXT)''')
conn.commit()

# --- ESTILO SENAI (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    div.stButton > button {
        background-color: #ff0000 !important;
        color: white !important;
        border-radius: 8px !important;
        width: 100% !important;
        height: 3em !important;
        font-weight: bold !important;
    }
    .header-senai {
        background-color: #ff0000;
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
    }
    label { font-weight: bold !important; color: #333 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- DICIONÁRIO DE CURSOS (ATUALIZADO SENAI GUARULHOS) ---
dados_cursos = {
    "Administração e Gestão": [
        "Técnico em Administração", "Assistente de Recursos Humanos", 
        "Assistente Financeiro", "Analista da Qualidade", "Dashboard em Excel"
    ],
    "Alimentos e Bebidas": [
        "Fabricação de Pães e Doces", "Confeiteiro", "Padeiro"
    ],
    "Automotiva": [
        "Mecânico de Motocicletas", "Lubrificação Automotiva", "Mecânico de Automóveis Leves"
    ],
    "Eletroeletrônica e Energia": [
        "Eletricista de Manutenção Eletroeletrônica", "Comandos Elétricos", 
        "Eletricista Instalador", "Energia Solar Fotovoltaica"
    ],
    "Logística e Transporte": [
        "Técnico em Logística", "Operador de Logística", "Analista de Logística", "Almoxarife"
    ],
    "Metalmecânica": [
        "Mecânico de Usinagem", "Ferramenteiro de Corte e Dobra", 
        "Torneiro Mecânico", "Ajustador Mecânico", "Inspetor de Qualidade"
    ],
    "Tecnologia da Informação": [
        "Técnico em Desenvolvimento de Sistemas", "Técnico em Informática", "Excel Avançado"
    ],
    "Segurança do Trabalho (NRs)": [
        "NR-10 Segurança em Eletricidade", "NR-11 Operação de Empilhadeira", "NR-35 Trabalho em Altura"
    ]
}

# --- INTERFACE ---
st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Hermenegildo Campos de Almeida</p></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.subheader("📋 Cadastro de Reserva")
    
    # --- CAMPOS FORA DO FORM PARA SEREM DINÂMICOS ---
    area_selecionada = st.selectbox("1. Escolha a Área de Interesse", list(dados_cursos.keys()))
    curso_selecionado = st.selectbox("2. Escolha o Curso", dados_cursos[area_selecionada])
    
    # --- FORMULÁRIO APENAS PARA DADOS PESSOAIS ---
    with st.form("cadastro_pessoal", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail para contato")
        whatsapp = st.text_input("WhatsApp (com DDD)")
        
        btn_enviar = st.form_submit_button("REGISTRAR MEU INTERESSE")
        
        if btn_enviar:
            if nome and email and whatsapp:
                data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                c.execute("INSERT INTO leads VALUES (?, ?, ?, ?, ?, ?)", 
                          (nome, email, whatsapp, area_selecionada, curso_selecionado, data_hora))
                conn.commit()
                st.success(f"Sucesso! {nome}, registramos seu interesse em {curso_selecionado}.")
                st.balloons()
            else:
                st.error("Por favor, preencha todos os campos antes de enviar.")

# --- ÁREA ADMIN ---
st.sidebar.markdown("---")
st.sidebar.title("🔒 Administrativo")
acesso = st.sidebar.text_input("Senha de Acesso", type="password")

if acesso == "senai122":
    st.sidebar.success("Acesso Autorizado")
    if st.sidebar.button("📊 Ver Lista de Interessados"):
        st.write("### Relatório de Leads")
        df = pd.read_sql_query("SELECT * FROM leads", conn)
        st.dataframe(df)
        
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Baixar Planilha Excel (CSV)", csv, "interessados_senai.csv", "text/csv")
