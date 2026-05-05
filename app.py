import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
from google.oauth2 import service_account
from googleapiclient.discovery import build
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# Função para converter imagem local em base64
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

# --- CSS: ESTILO 3D E AJUSTE DA MOLDURA DA FACHADA ---
st.markdown("""
    <style>
    .stApp { background-color: #e0e5ec; }
    .logo-container { position: relative; z-index: 10; margin-bottom: -20px; display: flex; justify-content: center; padding-top: 10px; }
    .header-senai { 
        background: #ff0000; padding: 40px 0px 25px 0px; color: white; text-align: center; 
        width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw;
        z-index: 5; box-shadow: 0px 10px 15px rgba(0,0,0,0.1); border-bottom: 4px solid #cc0000;
    }
    .header-senai h1 { font-size: 28px !important; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); font-weight: 800; color: white !important; }
    
    /* Moldura da Fachada Justa */
    .moldura-fachada {
        display: inline-block;
        padding: 10px;
        background: #e0e5ec;
        border-radius: 25px;
        box-shadow: 10px 10px 20px #bebebe, -10px -10px 20px #ffffff;
        margin: 20px auto;
    }
    .moldura-fachada img { border-radius: 20px; display: block; max-width: 100%; height: auto; }

    label, [data-testid="stWidgetLabel"] p { color: #000000 !important; font-weight: 600 !important; }
    div.stButton > button { 
        background-color: #ff0000 !important; color: #ffffff !important; font-weight: bold !important; 
        height: 55px !important; border-radius: 15px !important; width: 100% !important; border: none !important;
        box-shadow: 6px 6px 12px #b8b9be, -6px -6px 12px #ffffff !important;
    }
    [data-testid="stForm"] { 
        background-color: #e0e5ec !important; border-radius: 30px !important; padding: 2rem !important; 
        box-shadow: inset 8px 8px 16px #bebebe, inset -8px -8px 16px #ffffff !important; border: none !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- DADOS FIXOS ---
DADOS_CURSOS = {
    "Tecnologia da Informação": ["EXCEL BÁSICO", "INFORMÁTICA BÁSICA", "EXCEL COMPLETO", "PYTHON PARA ANÁLISE DE DADOS", "POWER BI (DASHBOARDS)"],
    "Metalmecânica": ["MECÂNICO DE USINAGEM", "PROGRAMADOR CNC", "SOLDADOR MAG/TIG"],
    "Eletroeletrônica": ["ELETRICISTA INSTALADOR", "COMANDOS ELÉTRICOS", "SISTEMAS FOTOVOLTAICOS"],
    "Gestão e Logística": ["ALMOXARIFE", "ASSISTENTE ADMINISTRATIVO", "LOGÍSTICA INTEGRADA"]
}

# --- FUNÇÕES GOOGLE SHEETS ---
def conectar_google_sheets():
    try:
        s = st.secrets["connections"]["gsheets"]
        info = {
            "type": "service_account", "project_id": s["project_id"],
            "private_key_id": s["private_key_id"],
            "private_key": s["private_key"].replace("\\n", "\n").strip(),
            "client_email": s["client_email"], "client_id": s["client_id"],
            "auth_uri": s["auth_uri"], "token_uri": s["token_uri"],
            "auth_provider_x509_cert_url": s["auth_provider_x509_cert_url"],
            "client_x509_cert_url": s["client_x509_cert_url"]
        }
        creds = service_account.Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
        return build("sheets", "v4", credentials=creds, cache_discovery=False)
    except: return None

def salvar_novo_lead(lista_dados):
    try:
        service = conectar_google_sheets()
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_id = url.split("/d/")[1].split("/")[0]
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id, range="A1", valueInputOption="RAW",
            insertDataOption="INSERT_ROWS", body={"values": [lista_dados]}
        ).execute()
        return True
    except: return False

def ler_todos_leads():
    try:
        service = conectar_google_sheets()
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_id = url.split("/d/")[1].split("/")[0]
        result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="A1:Z2000").execute()
        values = result.get("values", [])
        return pd.DataFrame(values[1:], columns=values[0]) if values else pd.DataFrame()
    except: return pd.DataFrame()

# --- INTERFACE ---
path_logo = os.path.join("imagens", "logo.png")
path_fachada = os.path.join("imagens", "fachada.jpg")

if os.path.exists(path_logo):
    logo_base = get_base64_of_bin_file(path_logo)
    st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{logo_base}" width="150"></div>', unsafe_allow_html=True)

st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Registro de Interesse Profissional</p></div>', unsafe_allow_html=True)

if os.path.exists(path_fachada):
    fachada_base = get_base64_of_bin_file(path_fachada)
    st.markdown(f'<div style="text-align:center;"><div class="moldura-fachada"><img src="data:image/jpeg;base64,{fachada_base}" style="width: 700px;"></div></div>', unsafe_allow_html=True)

# --- FORMULÁRIO ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    area_sel = st.selectbox("Área Profissional:", ["Selecione..."] + sorted(list(DADOS_CURSOS.keys())))
    opcoes = sorted(DADOS_CURSOS[area_sel]) if area_sel != "Selecione..." else []
    curso_sel = st.selectbox("Curso:", ["Aguardando área..."] + opcoes, disabled=(area_sel == "Selecione..."))

    with st.form("form_registro", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp")
        obs = st.text_area("Observações")
        enviar = st.form_submit_button("REGISTRAR AGORA")

        if enviar:
            if area_sel != "Selecione..." and nome and email:
                data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                if salvar_novo_lead([nome, email, f"'{whats}", area_sel, curso_sel, obs, data_atual]):
                    st.success(f"Excelente, {nome}! Registramos seu interesse no curso de {curso_sel}.")
                    st.info("Nossa equipe entrará em contato assim que as inscrições forem abertas.")
                    st.balloons()
                else: st.error("Erro ao salvar.")
            else: st.error("Preencha os campos obrigatórios.")

# --- ADMIN (CORRIGIDO) ---
with st.sidebar:
    st.markdown("---")
    st.subheader("🔒 Área Administrativa")
    senha_mestra = st.secrets["auth"]["admin_password"] if "auth" in st.secrets else None
    senha_digitada = st.text_input("Senha", type="password")

    if senha_digitada and senha_mestra and senha_digitada == senha_mestra:
        st.success("Acesso Liberado")
        if st.checkbox("Ver Leads Cadastrados"):
            df_leads = ler_todos_leads()
            if not df_leads.empty:
                st.dataframe(df_leads)
            else:
                st.info("Nenhum lead encontrado.")
    elif senha_digitada:
        st.error("Senha incorreta")
