import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from google.oauth2 import service_account
from googleapiclient.discovery import build
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# Função para converter imagem local em base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- CSS: ESTILO 3D, FAIXA TOTAL E CORREÇÃO DE CORES MOBILE ---
st.markdown("""
    <style>
    /* Fundo Neumórfico */
    .stApp { background-color: #e0e5ec; }
    
    /* Container do Logo acima da faixa */
    .logo-container {
        position: relative;
        z-index: 10;
        margin-bottom: -20px;
        display: flex;
        justify-content: center;
        padding-top: 10px;
    }

    /* FAIXA VERMELHA LARGURA TOTAL */
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
    
    .header-senai h1 { 
        font-size: 28px !important; 
        margin: 0; 
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        font-weight: 800;
        color: white !important;
    }
    .header-senai p { font-size: 16px !important; margin: 5px 0 0 0; opacity: 0.9; color: white !important; }

    /* CORREÇÃO PARA SMARTPHONES: Labels em PRETO */
    label, [data-testid="stWidgetLabel"] p {
        color: #000000 !important;
        font-weight: 600 !important;
    }

    /* CORREÇÃO CRÍTICA DO BOTÃO PARA CELULAR */
    div.stButton > button { 
        background-color: #ff0000 !important;
        color: #ffffff !important; 
        font-weight: bold !important; 
        height: 55px !important;
        border-radius: 15px !important; 
        width: 100% !important;
        border: none !important;
        box-shadow: 6px 6px 12px #b8b9be, -6px -6px 12px #ffffff !important;
        /* Impede que o sistema mobile altere a cor no clique */
        -webkit-tap-highlight-color: transparent;
    }
    
    div.stButton > button p {
        color: #ffffff !important; /* Força o texto dentro do botão a ser branco */
    }

    div.stButton > button:hover, div.stButton > button:active, div.stButton > button:focus {
        background-color: #cc0000 !important;
        color: #ffffff !important;
    }

    /* Efeito de Botão 3D nas Imagens */
    .img-3d-link {
        display: block;
        margin: auto;
        transition: all 0.3s ease;
        text-decoration: none;
        border-radius: 25px;
        overflow: hidden;
        width: fit-content;
    }
    .img-3d-link img {
        border-radius: 25px;
        box-shadow: 10px 10px 20px #bebebe, -10px -10px 20px #ffffff;
        transition: all 0.3s ease;
        border: 4px solid #e0e5ec;
    }
    .img-3d-link:hover { transform: scale(0.98); }

    /* Formulário Escavado */
    [data-testid="stForm"] {
        background-color: #e0e5ec !important;
        border-radius: 30px !important;
        padding: 2rem !important;
        box-shadow: inset 8px 8px 16px #bebebe, inset -8px -8px 16px #ffffff !important;
        border: none !important;
    }

    /* Inputs Neumórficos */
    .stTextInput div[data-baseweb="input"], .stSelectbox div[data-baseweb="select"], .stTextArea div[data-baseweb="textarea"] {
        background-color: #e0e5ec !important;
        border-radius: 15px !important;
        box-shadow: inset 3px 3px 6px #bebebe, inset -3px -3px 6px #ffffff !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÕES ---
url_senai = "https://www.sp.senai.br/cursos?unidade=122"
path_logo = os.path.join("imagens", "logo.png")
path_fachada = os.path.join("imagens", "fachada.jpg")

# --- SCRAPING DINÂMICO ---
@st.cache_data(ttl=43200)
def buscar_cursos_dinamicos():
    api_key = "3e14f4393c5a034104b37c071a0d021f" 
    url_alvo = url_senai
    mapa_fallback = {
        "Tecnologia da Informação": ["Excel Avançado", "IA Generativa", "Python", "Power BI"],
        "Eletroeletrônica": ["Eletricista Instalador", "Comandos Elétricos"],
        "Gestão e Logística": ["Almoxarife", "Assistente Administrativo"]
    }
    try:
        params = {'api_key': api_key, 'url': url_alvo, 'render': 'true', 'wait_until': 'networkidle'}
        response = requests.get('http://api.scraperapi.com', params=params, timeout=90)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            cards = soup.select('div[class*="card-curso"]') or soup.select('.item-lista-curso')
            if not cards: return mapa_fallback
            mapa_real = {}
            for card in cards:
                try:
                    area_elem = card.select_one('.area-tematica, .txt-area, .tag-area')
                    titulo_elem = card.select_one('.titulo-curso, h2, .nome-curso')
                    if area_elem and titulo_elem:
                        area = area_elem.get_text(strip=True).title()
                        titulo = titulo_elem.get_text(strip=True).upper()
                        if area not in mapa_real: mapa_real[area] = []
                        if titulo not in mapa_real[area]: mapa_real[area].append(titulo)
                except: continue
            return mapa_real if len(mapa_real) > 0 else mapa_fallback
        return mapa_fallback
    except: return mapa_fallback

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

def salvar_novo_lead(lista_dados):
    try:
        service = conectar_google_sheets()
        if service is None: return False
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

# 1. Logo
if os.path.exists(path_logo):
    logo_base64 = get_base64_of_bin_file(path_logo)
    st.markdown(f'''
        <div class="logo-container">
            <a href="{url_senai}" target="_blank" class="img-3d-link">
                <img src="data:image/png;base64,{logo_base64}" width="150">
            </a>
        </div>
    ''', unsafe_allow_html=True)

# Faixa Vermelha
st.markdown(f'''
    <div class="header-senai">
        <h1>SENAI GUARULHOS</h1>
        <p>Unidade 122 - Registro de Interesse Profissional</p>
    </div>
''', unsafe_allow_html=True)

# 2. Fachada
if os.path.exists(path_fachada):
    fachada_base64 = get_base64_of_bin_file(path_fachada)
    c_f1, c_f2, c_f3 = st.columns([1, 6, 1])
    with c_f2:
        st.markdown(f'''
            <a href="{url_senai}" target="_blank" class="img-3d-link">
                <img src="data:image/jpeg;base64,{fachada_base64}" style="width: 100%;">
            </a>
        ''', unsafe_allow_html=True)

with st.spinner("Sincronizando cursos..."):
    dados_cursos = buscar_cursos_dinamicos()

# Formulário
col_main1, col_main2, col_main3 = st.columns([1, 2, 1])
with col_main2:
    st.markdown("<h3 style='text-align: center; margin-top: 20px; color: #000000;'>📋 Cadastro de Interesse</h3>", unsafe_allow_html=True)
    
    area_sel = st.selectbox("Área Profissional:", ["Selecione..."] + sorted(list(dados_cursos.keys())))
    opcoes = sorted(dados_cursos[area_sel]) if area_sel != "Selecione..." else []
    curso_sel = st.selectbox("Curso:", ["Aguardando área..."] + opcoes, disabled=(area_sel == "Selecione..."))

    with st.form("form_3d", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp")
        obs = st.text_area("Observações")
        enviar = st.form_submit_button("REGISTRAR AGORA")

        if enviar:
            if area_sel != "Selecione..." and nome and email:
                data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                if salvar_novo_lead([nome, email, whats, area_sel, curso_sel, obs, data_atual]):
                    st.success(f"Excelente, {nome}! Registramos seu interesse. Entraremos em contato assim que as inscrições para o curso estiverem abertas.")
                    st.balloons()
            else: st.error("Por favor, preencha os campos obrigatórios.")

# --- ADMIN ---
st.sidebar.markdown("---")
senha = st.sidebar.text_input("Senha", type="password")
if senha == "Celina2610$$":
    if st.sidebar.checkbox("Ver Dados"):
        df = ler_todos_leads()
        if not df.empty: st.dataframe(df)
