import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

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
    .header-senai { background-color: #ff0000; padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 25px; }
    div.stButton > button { background-color: #000000 !important; color: white !important; font-weight: bold !important; width: 100% !important; height: 3.5em !important; border-radius: 8px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- DICIONÁRIO DE CURSOS (TI ATUALIZADO VIA IMAGEM + OUTRAS ÁREAS) ---
dados_cursos = {
    "Tecnologia da Informação": [
        "Implantação de Serviços de Inteligência Artificial em Nuvem",
        "Inteligência Artificial Generativa: Google Gemini",
        "Inteligência Artificial Generativa: Microsoft Copilot",
        "Inteligência Artificial Generativa: ChatGPT",
        "Business Intelligence com Power BI",
        "Excel Avançado",
        "Informática Básica",
        "Lógica de Programação",
        "Técnico em Desenvolvimento de Sistemas",
        "Técnico em Informática",
        "Redes de Computadores"
    ],
    "Administração e Gestão": [
        "Almoxarife", "Assistente Administrativo", "Assistente de RH", "Assistente Financeiro", 
        "Liderança e Gestão de Equipes", "Logística Reversa"
    ],
    "Alimentos e Bebidas": [
        "Confeiteiro", "Padeiro", "Fabricação de Pizzas", "Fabricação de Panetones"
    ],
    "Automotiva": [
        "Mecânico de Automóveis Leves", "Mecânico de Motocicletas", "Eletricista Automotivo"
    ],
    "Eletroeletrônica": [
        "Eletricista Instalador", "Comandos Elétricos", "CLP - Controladores Lógicos", "Energia Solar"
    ],
    "Logística": [
        "Técnico em Logística", "Operador de Empilhadeira (NR11)", "Operador de Paleteira", "Gestão de Estoques"
    ],
    "Metalmecânica": [
        "Mecânico de Usinagem", "Torneiro Mecânico", "Soldador MAG/TIG", "Ajustador Mecânico", "Caldeireiro"
    ],
    "Segurança do Trabalho": [
        "NR-10", "NR-35 (Trabalho em Altura)", "NR-12"
    ]
}

# --- INTERFACE ---
st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Hermenegildo Campos de Almeida</p></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.write("### 📋 Cadastro de Reserva")
    
    # Menus dinâmicos (fora do form)
    area_sel = st.selectbox("1. Selecione a Área de Interesse:", ["Selecione..."] + sorted(list(dados_cursos.keys())))
    
    lista_cursos = sorted(dados_cursos[area_sel]) if area_sel != "Selecione..." else []
    curso_sel = st.selectbox("2. Selecione o Curso:", ["Selecione o Curso..."] + lista_cursos)

    # Formulário de Cadastro
    with st.form("form_leads_v2", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whatsapp = st.text_input("WhatsApp (com DDD)")
        
        st.write("---")
        sugestao = st.text_area("Sugira um curso ou deixe uma observação:", 
                                placeholder="Caso não tenha encontrado o curso desejado, escreva aqui...")
        
        enviado = st.form_submit_button("REGISTRAR INTERESSE")
        
        if enviado:
            if nome and email and whatsapp and area_sel != "Selecione..." and curso_sel != "Selecione o Curso...":
                data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                c.execute("INSERT INTO leads VALUES (?, ?, ?, ?, ?, ?, ?)", 
                          (nome, email, whatsapp, area_sel, curso_sel, sugestao, data_hora))
                conn.commit()
                
                st.success(f"Excelente, {nome}! Interesse registrado.")
                st.info("Assim que o curso for liberado ou houver uma nova turma, entraremos em contato imediatamente pelos seus dados informados.")
                st.balloons()
            else:
                st.error("Por favor, preencha todos os campos e selecione a área/curso.")

# --- ADMIN ---
st.sidebar.title("🔒 Administrativo")
senha = st.sidebar.text_input("Senha", type="password")
if senha == "senai122":
    df = pd.read_sql_query("SELECT * FROM leads", conn)
    if st.sidebar.checkbox("Visualizar Leads"):
        st.write("### Relatório de Interessados")
        st.dataframe(df)
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.sidebar.download_button("Baixar Planilha", csv, "leads_senai.csv", "text/csv")
