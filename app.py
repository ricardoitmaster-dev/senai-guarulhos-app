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

# --- ESTILO CSS (Identidade SENAI + Botão Preto) ---
st.markdown("""
    <style>
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

# --- 1. LOGO (Lendo da sua pasta 'imagens') ---
if os.path.exists("imagens/logo.png"):
    st.image("imagens/logo.png", width=200)

# --- 2. CABEÇALHO ---
st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Hermenegildo Campos de Almeida</p></div>', unsafe_allow_html=True)

# --- 3. IMAGEM DA FACHADA (Lendo da sua pasta 'imagens') ---
if os.path.exists("imagens/fachada.jpg"):
    st.image("imagens/fachada.jpg", caption="Unidade SENAI Hermenegildo Campos de Almeida - Guarulhos", use_container_width=True)

st.write("---")

# --- MAPEAMENTO DE CURSOS (TI ATUALIZADO + ÁREAS OFICIAIS) ---
dados_cursos = {
    "Tecnologia da Informação": [
        "Implantação de Serviços de Inteligência Artificial em Nuvem",
        "Inteligência Artificial Generativa: Google Gemini",
        "Inteligência Artificial Generativa: Microsoft Copilot",
        "Inteligência Artificial Generativa: ChatGPT",
        "Business Intelligence com Power BI",
        "Excel Avançado",
        "Excel Básico",
        "Excel Avançado",
        "Informática Básica",
        "Lógica de Programação",
        "Técnico em Desenvolvimento de Sistemas",
        "Técnico em Informática"
    ],
    "Administração e Gestão": [
        "Almoxarife", "Assistente Administrativo", "Assistente de RH", "Assistente Financeiro", 
        "Liderança e Gestão de Equipes", "Logística Reversa"
    ],
    "Alimentos e Bebidas": ["Confeiteiro", "Padeiro", "Fabricação de Pizzas", "Fabricação de Panetones"],
    "Automotiva": ["Mecânico de Automóveis Leves", "Mecânico de Motocicletas", "Eletricista Automotivo"],
    "Eletroeletrônica": ["Eletricista Instalador", "Comandos Elétricos", "CLP - Controladores Lógicos", "Energia Solar"],
    "Logística": ["Técnico em Logística", "Operador de Empilhadeira (NR11)", "Gestão de Estoques"],
    "Metalmecânica": ["Mecânico de Usinagem", "Torneiro Mecânico", "Soldador MAG/TIG", "Caldeireiro", "Metrologia"],
    "Segurança do Trabalho": ["NR-10", "NR-35 (Trabalho em Altura)", "NR-12"]
}

# --- INTERFACE DE CADASTRO ---
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.write("### 📋 Cadastro de Reserva")
    
    # Menus dinâmicos
    area_sel = st.selectbox("1. Selecione a Área de Interesse:", ["Selecione..."] + sorted(list(dados_cursos.keys())))
    lista_cursos = sorted(dados_cursos[area_sel]) if area_sel != "Selecione..." else []
    curso_sel = st.selectbox("2. Selecione o Curso:", ["Selecione o Curso..."] + lista_cursos)

    # Formulário
    with st.form("form_final_senai", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("Seu melhor E-mail")
        whatsapp = st.text_input("WhatsApp (com DDD)")
        
        st.write("---")
        sugestao = st.text_area("Não encontrou o curso? Sugira um curso aqui ou deixe uma observação:", 
                                placeholder="Ex: Gostaria de saber sobre o curso de Robótica...")
        
        btn_enviar = st.form_submit_button("REGISTRAR INTERESSE")
        
        if btn_enviar:
            if nome and email and whatsapp and area_sel != "Selecione..." and curso_sel != "Selecione o Curso...":
                data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                c.execute("INSERT INTO leads VALUES (?, ?, ?, ?, ?, ?, ?)", 
                          (nome, email, whatsapp, area_sel, curso_sel, sugestao, data_hora))
                conn.commit()
                
                st.success(f"Excelente, {nome}! Seu interesse foi registrado com sucesso.")
                st.info("Assim que o curso for liberado ou houver uma nova turma, nossa equipe entrará em contato imediatamente.")
                st.balloons()
            else:
                st.error("Por favor, preencha todos os campos e selecione a área/curso corretamente.")

# --- PAINEL ADMINISTRATIVO ---
st.sidebar.title("🔒 Admin")
senha = st.sidebar.text_input("Senha de Acesso", type="password")

if senha == "senai122":
    df = pd.read_sql_query("SELECT * FROM leads", conn)
    if st.sidebar.checkbox("Visualizar Interessados"):
        st.write("### Lista Geral de Leads")
        st.dataframe(df)
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.sidebar.download_button("📥 Baixar Planilha (Excel)", csv, "leads_senai_guarulhos.csv", "text/csv")
