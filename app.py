import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- BANCO DE DADOS ---
# O banco de dados será criado automaticamente no servidor
conn = sqlite3.connect('senai_database.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS leads 
             (nome TEXT, email TEXT, whatsapp TEXT, area TEXT, curso TEXT, data TEXT)''')
conn.commit()

# --- ESTILO SENAI (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button {
        background-color: #ff0000;
        color: white;
        border-radius: 5px;
        width: 100%;
        font-weight: bold;
    }
    .header {
        background-color: #ff0000;
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DICIONÁRIO DE CURSOS ---
dados_cursos = {
    "Tecnologia da Informação": ["Técnico em Desenvolvimento de Sistemas", "Técnico em Informática", "Excel Avançado"],
    "Logística e Gestão": ["Técnico em Logística", "Almoxarife", "Assistente Administrativo"],
    "Metalmecânica": ["Mecânico de Usinagem", "Mecânico de Manutenção", "Soldador"],
    "Eletroeletrônica": ["Técnico em Eletrotécnica", "Eletricista Instalador"]
}

# --- INTERFACE DO USUÁRIO ---
st.markdown('<div class="header"><h1>SENAI GUARULHOS 122</h1><p>Cadastro de Reserva de Vagas</p></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    with st.form("meu_formulario", clear_on_submit=True):
        st.subheader("Preencha seus dados")
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whatsapp = st.text_input("WhatsApp (com DDD)")
        
        area = st.selectbox("Área de Interesse", list(dados_cursos.keys()))
        curso = st.selectbox("Curso", dados_cursos[area])
        
        enviado = st.form_submit_button("REGISTRAR INTERESSE")
        
        if enviado:
            if nome and email and whatsapp:
                data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                c.execute("INSERT INTO leads VALUES (?, ?, ?, ?, ?, ?)", 
                          (nome, email, whatsapp, area, curso, data_atual))
                conn.commit()
                st.success(f"Obrigado, {nome}! Seu interesse no curso de {curso} foi registrado.")
            else:
                st.error("Por favor, preencha todos os campos.")

# --- ÁREA DO ADMINISTRADOR (SIMPLES) ---
st.sidebar.title("Área Administrativa")
senha = st.sidebar.text_input("Senha", type="password")

if senha == "senai122": # Você pode mudar essa senha
    st.sidebar.success("Acesso Liberado")
    if st.sidebar.button("Visualizar Cadastros"):
        st.write("### Lista de Interessados")
        df = pd.read_sql_query("SELECT * FROM leads", conn)
        st.dataframe(df)
        
        # Botão para baixar Excel
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Baixar Planilha (CSV)", csv, "interessados_senai.csv", "text/csv")
