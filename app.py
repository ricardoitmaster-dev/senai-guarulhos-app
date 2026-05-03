import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- CSS: ESTILO 3D AVANÇADO (BOTÕES E IMAGENS) ---
st.markdown("""
    <style>
    /* Fundo Neumórfico */
    .stApp { background-color: #e0e5ec; }
    
    /* Cabeçalho 3D */
    .header-senai { 
        background: #ff0000; 
        padding: 20px;
        border-radius: 20px;
        color: white; 
        text-align: center; 
        margin: 10px auto 30px auto;
        max-width: 95%;
        box-shadow: 9px 9px 16px #b8b9be, -9px -9px 16px #ffffff;
        border: 1px solid rgba(255,255,255,0.2);
    }

    /* EFEITO BOTÃO 3D PARA AS IMAGENS */
    .img-container {
        display: flex;
        justify-content: center;
        padding: 10px;
    }
    
    /* Estilo da Imagem como Botão (Alto Relevo) */
    [data-testid="stImage"] img {
        border-radius: 25px !important;
        background: #e0e5ec;
        box-shadow: 10px 10px 20px #bebebe, -10px -10px 20px #ffffff !important;
        transition: all 0.3s ease-in-out !important;
        cursor: pointer;
        border: 5px solid #e0e5ec !important;
    }

    /* Efeito de Clique/Hover na Imagem (Baixo Relevo) */
    [data-testid="stImage"] img:hover {
        transform: scale(0.98);
        box-shadow: inset 6px 6px 12px #bebebe, inset -6px -6px 12px #ffffff !important;
        filter: brightness(1.05);
    }

    /* Formulário Escavado */
    [data-testid="stForm"] {
        background-color: #e0e5ec !important;
        border-radius: 30px !important;
        padding: 3rem !important;
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

    /* Botão de Envio 3D */
    div.stButton > button { 
        background-color: #ff0000 !important;
        color: white !important; 
        font-weight: bold !important; 
        height: 55px !important;
        border-radius: 15px !important; 
        box-shadow: 6px 6px 12px #b8b9be, -6px -6px 12px #ffffff !important;
        border: none !important;
        transition: 0.2s;
    }
    div.stButton > button:hover {
        box-shadow: 2px 2px 5px #b8b9be, -2px -2px 5px #ffffff !important;
        transform: translateY(2px);
    }
    </style>
    """, unsafe_allow_html=True)

# --- SCRAPING DINÂMICO ---
@st.cache_data(ttl=43200)
def buscar_cursos_dinamicos():
    api_key = "3e14f4393c5a034104b37c071a0d021f" 
    url_alvo = "https://www.sp.senai.br/cursos?unidade=122"
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

# 1. Logo (Botão 3D)
path_logo = os.path.join("imagens", "logo.png")
if os.path.exists(path_logo):
    c_logo1, c_logo2, c_logo3 = st.columns([2, 1, 2])
    with c_logo2: st.image(Image.open(path_logo), width=150)

# Cabeçalho
st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Registro de Interesse</p></div>', unsafe_allow_html=True)

# 2. Fachada (Botão 3D)
path_fachada = os.path.join("imagens", "fachada.jpg")
if os.path.exists(path_fachada):
    c_fac1, c_fac2, c_fac3 = st.columns([1, 6, 1])
    with c_fac2: st.image(Image.open(path_fachada), use_container_width=True)

with st.spinner("Carregando cursos..."):
    dados_cursos = buscar_cursos_dinamicos()

# Área do Formulário
col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
with col_f2:
    st.markdown("<h3 style='text-align: center; color: #333; margin-top: 20px;'>📋 Cadastro de Interesse</h3>", unsafe_allow_html=True)
    
    area_escolhida = st.selectbox("Área Profissional:", ["Selecione..."] + sorted(list(dados_cursos.keys())))
    opcoes_cursos = sorted(dados_cursos[area_escolhida]) if area_escolhida != "Selecione..." else []
    curso_escolhido = st.selectbox("Curso de Interesse:", ["Aguardando área..."] + opcoes_cursos, disabled=(area_escolhida == "Selecione..."))

    with st.form("form_interessado", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp (com DDD)")
        sugestao = st.text_area("Observações:")
        btn_enviar = st.form_submit_button("REGISTRAR AGORA")

        if btn_enviar:
            if area_escolhida != "Selecione..." and nome and email:
                data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                if salvar_novo_lead([nome, email, whats, area_escolhida, curso_escolhido, sugestao, data_atual]):
                    st.success(f"Excelente, {nome}! Seu interesse foi registrado.")
                    st.balloons()
            else: st.error("Por favor, preencha os campos obrigatórios.")

# --- ADMIN ---
st.sidebar.markdown("---")
senha = st.sidebar.text_input("Senha", type="password")
if senha == "Celina2610$$":
    if st.sidebar.checkbox("Ver Leads"):
        df = ler_todos_leads()
        if not df.empty: st.dataframe(df)
