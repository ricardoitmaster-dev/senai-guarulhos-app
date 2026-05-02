import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- CONEXÃO COM GOOGLE SHEETS: SOLUÇÃO DE BYPASS TOTAL ---
@st.cache_resource
def iniciar_conexao():
    try:
        # Criamos a conexão sem passar NENHUM argumento extra no construtor
        # Deixamos a biblioteca ler os segredos puramente pelo ambiente
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error(f"Erro ao inicializar driver: {e}")
        return None

conn = iniciar_conexao()

# --- MAPEAMENTO DE CURSOS ---
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

# --- CABEÇALHO ---
path_logo = os.path.join("imagens", "logo.png")
if os.path.exists(path_logo):
    col_l1, col_l2, col_l3 = st.columns([2, 1, 2])
    with col_l2: st.image(Image.open(path_logo), width=150)

st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Hermenegildo Campos de Almeida</p></div>', unsafe_allow_html=True)

path_fachada = os.path.join("imagens", "fachada.jpg")
if os.path.exists(path_fachada):
    f_col1, f_col2, f_col3 = st.columns([1, 6, 1]) 
    with f_col2: st.image(Image.open(path_fachada), use_container_width=True)

st.write("---")

# --- INTERFACE DE CADASTRO ---
col_f1, col_f2, col_f3 = st.columns([1, 2, 1])

with col_f2:
    st.write("### 📋 Ficha de Interesse")
    opcoes_areas = ["Selecione..."] + sorted(list(dados_cursos.keys()))
    area_sel = st.selectbox("1. Selecione a Área:", opcoes_areas)
    
    lista_cursos = ["Selecione..."] + sorted(dados_cursos[area_sel]) if area_sel != "Selecione..." else ["Selecione..."]
    curso_sel = st.selectbox("2. Selecione o Curso:", lista_cursos)

    with st.form("form_gsheets", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp (com DDD)")
        sugestao = st.text_area("Sugestão de curso ou observação:")
        btn_enviar = st.form_submit_button("REGISTRAR INTERESSE")

if btn_enviar:
    if nome and area_sel != "Selecione..." and curso_sel != "Selecione..." and conn:
        try:
            # AQUI ESTÁ O SEGREDO: Passamos a URL apenas no momento da LEITURA
            url_planilha = st.secrets["connections"]["gsheets"]["spreadsheet"]
            
            df_atual = conn.read(spreadsheet=url_planilha)
            
            novo_lead = pd.DataFrame([{
                "nome": nome, "email": email, "whatsapp": whats,
                "area": area_sel, "curso": curso_sel, "sugestao": sugestao,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }])
            
            df_final = pd.concat([df_atual, novo_lead], ignore_index=True)
            
            # E passamos a URL novamente no momento do UPDATE
            conn.update(spreadsheet=url_planilha, data=df_final)
            
            st.success(f"Sucesso, {nome}! Seu interesse foi registrado.")
            st.balloons()
        except Exception as e:
            st.error(f"Erro na operação: {e}")
    else:
        st.error("Preencha todos os campos obrigatórios.")

# --- ADMIN ---
st.sidebar.title("🔒 Admin")
senha_adm = st.sidebar.text_input("Senha", type="password")
if senha_adm == "senai122" and conn:
    try:
        url_planilha = st.secrets["connections"]["gsheets"]["spreadsheet"]
        df_leads = conn.read(spreadsheet=url_planilha)
        if st.sidebar.checkbox("Ver Interessados"):
            st.dataframe(df_leads)
    except:
        st.sidebar.write("Aguardando registros...")
