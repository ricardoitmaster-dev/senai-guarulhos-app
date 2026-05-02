import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- BANCO DE DADOS ---
conn = sqlite3.connect('senai_guarulhos_database.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS leads 
             (nome TEXT, email TEXT, whatsapp TEXT, area TEXT, curso TEXT, sugestao TEXT, data TEXT)''')
conn.commit()

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .header-senai {
        background-color: #ff0000;
        padding: 25px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
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

# --- DICIONÁRIO DE CURSOS OFICIAL (SENAI GUARULHOS) ---
dados_cursos = {
    "Administração e Gestão": [
        "Almoxarife", "Assistente Administrativo", "Assistente de Recursos Humanos", 
        "Assistente Financeiro", "Liderança e Gestão de Equipes", "Logística Reversa"
    ],
    "Alimentos e Bebidas": [
        "Confeiteiro", "Padeiro", "Fabricação de Pizzas", "Fabricação de Pães Doces", "Chocolateiro"
    ],
    "Automotiva": [
        "Mecânico de Automóveis Leves", "Mecânico de Motocicletas", "Eletricista Automotivo"
    ],
    "Eletroeletrônica": [
        "Eletricista Instalador", "Comandos Elétricos", "CLP - Controladores Lógicos", "Energia Solar Fotovoltaica"
    ],
    "Logística": [
        "Técnico em Logística", "Operador de Empilhadeira (NR11)", "Operador de Paleteira Elétrica", "Gestão de Estoques"
    ],
    "Metalmecânica": [
        "Mecânico de Usinagem", "Torneiro Mecânico", "Soldador MAG", "Soldador TIG", "Ajustador Mecânico", "Caldeireiro"
    ],
    "Tecnologia da Informação": [
        "Técnico em Desenvolvimento de Sistemas", "Excel Avançado", "Power BI", "Informática Básica"
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
    
    # Seleção de Área e Curso (Dinâmicos)
    area_sel = st.selectbox("1. Selecione a Área de Interesse:", ["Selecione..."] + list(dados_cursos.keys()))
    
    lista_cursos = dados_cursos[area_sel] if area_sel != "Selecione..." else []
    curso_sel = st.selectbox("2. Selecione o Curso:", ["Selecione..."] + lista_cursos)

    # Formulário de Dados
    with st.form("form_leads", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whatsapp = st.text_input("WhatsApp (com DDD)")
        
        st.write("---")
        sugestao = st.text_area("Não encontrou o curso? Sugira aqui ou deixe uma observação:", 
                                placeholder="Ex: Gostaria de saber sobre o curso de Robótica...")
        
        enviado = st.form_submit_button("REGISTRAR INTERESSE")
        
        if enviado:
            if nome and email and whatsapp and area_sel != "Selecione..." and curso_sel != "Selecione...":
                data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                
                # Salva no Banco de Dados
                c.execute("INSERT INTO leads VALUES (?, ?, ?, ?, ?, ?, ?)", 
                          (nome, email, whatsapp, area_sel, curso_sel, sugestao, data_atual))
                conn.commit()
                
                # Resposta conforme solicitado
                st.success(f"Obrigado, {nome}!")
                st.info("Assim que o curso for liberado, ou caso já exista uma turma disponível para o seu interesse, nossa equipe entrará em contato com você imediatamente através dos dados informados.")
                st.balloons()
            else:
                st.error("Por favor, preencha todos os dados e selecione a área e o curso.")

# --- PAINEL ADMIN ---
st.sidebar.title("🔒 Administrativo")
senha = st.sidebar.text_input("Senha", type="password")

if senha == "senai122":
    st.sidebar.success("Acesso Liberado")
    if st.sidebar.checkbox("Ver Interessados"):
        df = pd.read_sql_query("SELECT * FROM leads", conn)
        st.write("### Lista de Candidatos")
        st.dataframe(df)
        
        # Download para o setor administrativo
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.sidebar.download_button("Baixar Planilha Excel", csv, "interessados_senai.csv", "text/csv")
