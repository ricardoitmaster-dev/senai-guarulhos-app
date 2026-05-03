import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup
import base64
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# Função para converter imagem local em base64 (essencial para o CSS)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- CSS: ESTILO 3D, FAIXA TOTAL E CORES ---
st.markdown("""
    <style>
    .stApp { background-color: #e0e5ec; }
    
    .logo-container {
        display: flex;
        justify-content: center;
        padding-top: 10px;
        margin-bottom: -20px;
        position: relative;
        z-index: 10;
    }

    .header-senai { 
        background: #ff0000; 
        padding: 40px 0px 25px 0px; 
        color: white; 
        text-align: center; 
        width: 100vw;
        position: relative;
        left: 50%;
        right: 50%;
        margin-left: -50vw;
        margin-right: -50vw;
        z-index: 5;
        box-shadow: 0px 10px 15px rgba(0,0,0,0.1);
        border-bottom: 4px solid #cc0000;
    }
    
    .header-senai h1 { font-size: 28px !important; margin: 0; color: white !important; font-weight: 800; }
    .header-senai p { font-size: 16px !important; margin: 5px 0 0 0; color: white !important; }

    /* Estilo Neumórfico para Inputs e Botões */
    label, [data-testid="stWidgetLabel"] p { color: #000000 !important; font-weight: 600 !important; }

    div.stButton > button { 
        background-color: #ff0000 !important;
        color: #ffffff !important; 
        font-weight: bold !important; 
        height: 55px !important;
        border-radius: 15px !important; 
        width: 100% !important;
        box-shadow: 6px 6px 12px #b8b9be, -6px -6px 12px #ffffff !important;
    }

    [data-testid="stForm"] {
        background-color: #e0e5ec !important;
        border-radius: 30px !important;
        padding: 2rem !important;
        box-shadow: inset 8px 8px 16px #bebebe, inset -8px -8px 16px #ffffff !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÕES DE CAMINHO ---
path_logo = os.path.join("imagens", "logo.png")
path_fachada = os.path.join("imagens", "fachada.jpg")

# --- SCRAPING DINÂMICO (LÓGICA DA ÂNCORA) ---
@st.cache_data(ttl=43200)
def buscar_cursos_ancora():
    api_key = "3e14f4393c5a034104b37c071a0d021f"
    url_alvo = "https://www.sp.senai.br/cursos/0/tecnologia-da-informacao?unidade=122"
    try:
        params = {'api_key': api_key, 'url': url_alvo, 'render': 'true'}
        response = requests.get('http://api.scraperapi.com', params=params, timeout=60)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            mapa = {}
            cards = soup.select('div[class*="card-curso"], .item-lista-curso')
            for card in cards:
                area_elem = card.select_one('.area-tematica, .txt-area')
                titulo_elem = card.select_one('.titulo-curso, h2')
                if area_elem and titulo_elem:
                    area = area_elem.get_text(strip=True).title()
                    titulo = titulo_elem.get_text(strip=True).upper()
                    if area not in mapa: mapa[area] = []
                    mapa[area].append(titulo)
            return mapa if mapa else {"TI": ["EXCEL AVANÇADO", "IA GENERATIVA"]}
    except:
        return {"TI": ["EXCEL AVANÇADO", "IA GENERATIVA"]}

# --- GOOGLE SHEETS ---
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

def salvar_lead(dados):
    try:
        service = conectar_google_sheets()
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sid = url.split("/d/")[1].split("/")[0]
        service.spreadsheets().values().append(
            spreadsheetId=sid, range="A1", valueInputOption="RAW",
            body={"values": [dados]}
        ).execute()
        return True
    except: return False

def ler_leads():
    try:
        service = conectar_google_sheets()
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sid = url.split("/d/")[1].split("/")[0]
        res = service.spreadsheets().values().get(spreadsheetId=sid, range="A1:Z1000").execute()
        v = res.get("values", [])
        return pd.DataFrame(v[1:], columns=v[0]) if v else pd.DataFrame()
    except: return pd.DataFrame()

# --- INTERFACE ---

# 1. Logo
if os.path.exists(path_logo):
    logo_base = get_base64_of_bin_file(path_logo)
    st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{logo_base}" width="150"></div>', unsafe_allow_html=True)

# 2. Cabeçalho
st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Registro de Interesse</p></div>', unsafe_allow_html=True)

# 3. Fachada
if os.path.exists(path_fachada):
    fachada_base = get_base64_of_bin_file(path_fachada)
    st.markdown(f'<div style="text-align:center; margin: 20px 0;"><img src="data:image/jpeg;base64,{fachada_base}" style="width: 80%; border-radius: 20px; box-shadow: 10px 10px 20px #bebebe;"></div>', unsafe_allow_html=True)

# 4. Dados
dados_cursos = buscar_cursos_ancora()

# 5. Formulário
col_main1, col_main2, col_main3 = st.columns([1, 2, 1])
with col_main2:
    area_sel = st.selectbox("Área Profissional:", sorted(list(dados_cursos.keys())))
    curso_sel = st.selectbox("Curso:", sorted(dados_cursos[area_sel]))

    with st.form("form_3d", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp")
        enviar = st.form_submit_button("REGISTRAR AGORA")

        if enviar:
            if nome and email:
                dt = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                if salvar_lead([nome, email, whats, area_sel, curso_sel, dt]):
                    st.success("Interesse registrado!")
                    st.balloons()
            else: st.error("Preencha os campos obrigatórios.")

# --- BARRA LATERAL ADMINISTRATIVA ---
st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Administração")
senha = st.sidebar.text_input("Senha de Acesso", type="password")

if senha == st.secrets["auth"]["admin_password"]:
    st.sidebar.success("Acesso Liberado")
    if st.sidebar.checkbox("Ver Leads"):
        df = ler_leads()
        if not df.empty:
            st.write("### Leads Registrados")
            st.dataframe(df)
        else:
            st.write("Nenhum registro encontrado.")
