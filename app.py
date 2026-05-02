import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- BANCO DE DADOS ---
conn = sqlite3.connect('senai_guarulhos_leads.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS leads 
             (nome TEXT, email TEXT, whatsapp TEXT, area TEXT, curso TEXT, sugestao TEXT, data TEXT)''')
conn.commit()

# --- ESTILO CSS ---
st.markdown("""
    <style>
    /* Cabeçalho Vermelho SENAI */
    .header-senai {
        background-color: #ff0000;
        padding: 25px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    /* Botão de Registro PRETO */
    div.stButton > button {
        background-color: #000000 !important;
        color: white !important;
        font-weight: bold !important;
        width: 100% !important;
        height: 3.5em !important;
        border-radius: 8px !important;
        border: none !important;
    }
    /* Estilo para labels */
    label { font-weight: bold !important; color: #1e1e1e !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ITEM 1: LOGO DO SENAI ---
# Posicionando o logo no topo
st.image("https://www.sp.senai.br/images/senai.png", width=220)

# --- ITEM 2: CABEÇALHO E FOTO DA FACHADA ---
st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Hermenegildo Campos de Almeida</p></div>', unsafe_allow_html=True)

# Imagem da fachada da escola (Banner Principal)
st.image("https://www.sp.senai.br/Imagens/Unidades/122/Fachada.jpg", 
         caption="Fachada da Unidade SENAI Guarulhos", 
         use_container_width=True)

st.write("---")

# --- MAPEAMENTO DE CURSOS (Mantendo a estrutura do seu pedido anterior) ---
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
        "Técnico em Informática"
    ],
    "Administração e Gestão": [
        "Almoxarife", "Assistente Administrativo", "Assistente de RH", "Assistente Financeiro"
    ],
    "Logística": [
        "Técnico em Logística", "Operador de Empilhadeira (NR11)", "Gestão de Estoques"
    ],
    "Metalmecânica": [
        "Mecânico de Usinagem", "Torneiro Mecânico", "Soldador MAG/TIG", "Caldeireiro"
    ]
}

# --- INTERFACE DE CADASTRO ---
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.write("### 📋 Cadastro de Reserva")
    
    # Seleção Dinâmica
    area_sel = st.selectbox("Selecione a Área de Interesse:", ["Selecione..."] + sorted(list(dados_cursos.keys())))
    lista_cursos = sorted(dados_cursos[area_sel]) if area_sel != "Selecione..." else []
    curso_sel = st.selectbox("Selecione o Curso:", ["Selecione o Curso..."] + lista_cursos)

    # Formulário
    with st.form("form_contato_oficial", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whatsapp = st.text_input("WhatsApp (com DDD)")
        
        st.write("---")
        sugestao = st.text_area("Sugira um curso ou deixe uma observação:", 
                                placeholder="Caso não tenha encontrado seu curso, escreva aqui...")
        
        enviado = st.form_submit_button("REGISTRAR INTERESSE")
        
        if enviado:
            if nome and email and whatsapp and area_sel != "Selecione..." and curso_sel != "Selecione o Curso...":
                data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                c.execute("INSERT INTO leads VALUES (?, ?, ?, ?, ?, ?, ?)", 
                          (nome, email, whatsapp, area_sel, curso_sel, sugestao, data_hora))
                conn.commit()
                
                st.success(f"Excelente, {nome}! Seu interesse foi registrado.")
                st.info("Nossa equipe entrará em contato assim que novas turmas forem liberadas.")
                st.balloons()
            else:
                st.error("Por favor, preencha todos os campos corretamente.")

# --- ADMIN ---
st.sidebar.title("🔒 Admin")
senha = st.sidebar.text_input("Senha", type="password")
if senha == "senai122":
    df = pd.read_sql_query("SELECT * FROM leads", conn)
    if st.sidebar.checkbox("Ver Cadastros"):
        st.dataframe(df)
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.sidebar.download_button("Baixar Planilha", csv, "leads_senai.csv", "text/csv")
