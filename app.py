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

# Função para imagens
def get_base64(file):
    with open(file, 'rb') as f:
        return base64.b64encode(f.read()).decode()

# --- CSS ORIGINAL (CORES BMW E ESTRUTURA) ---
st.markdown("""
    <style>
    .stApp { background-color: #e0e5ec; }
    .header-senai { 
        background: #0066b2; /* Azul BMW */
        padding: 30px; color: white; text-align: center; 
        border-bottom: 5px solid #d4af37; /* Dourado */
        margin-bottom: 20px;
    }
    div.stButton > button { 
        background-color: #0066b2 !important; color: white !important;
        border-radius: 10px !important; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS (BACKUP SEGURO) ---
@st.cache_data(ttl=3600)
def carregar_dados_oficiais():
    # Esta é a lógica que mantém seu app vivo mesmo se o site do SENAI falhar
    api_key = "3e14f4393c5a034104b37c071a0d021f"
    url = "https://www.sp.senai.br/cursos/0/tecnologia-da-informacao?unidade=122"
    try:
        params = {'api_key': api_key, 'url': url, 'render': 'true'}
        r = requests.get('http://api.scraperapi.com', params=params, timeout=30)
        soup = BeautifulSoup(r.text, 'html.parser')
        mapa = {}
        # Lógica de extração que você validou
        for card in soup.select('.item-lista-curso'):
            area = card.select_one('.area-tematica').text.strip().title()
            curso = card.select_one('.titulo-curso').text.strip().upper()
            if area not in mapa: mapa[area] = []
            mapa[area].append(curso)
        return mapa if mapa else {"TI e Gestão": ["EXCEL AVANÇADO", "IA GENERATIVA"]}
    except:
        return {"TI e Gestão": ["EXCEL AVANÇADO", "IA GENERATIVA"]}

# --- CONEXÃO GOOGLE SHEETS ---
def get_sheets_service():
    s = st.secrets["connections"]["gsheets"]
    creds = service_account.Credentials.from_service_account_info({
        "type": "service_account", "project_id": s["project_id"],
        "private_key_id": s["private_key_id"],
        "private_key": s["private_key"].replace("\\n", "\n"),
        "client_email": s["client_email"], "client_id": s["client_id"],
        "auth_uri": s["auth_uri"], "token_uri": s["token_uri"],
        "auth_provider_x509_cert_url": s["auth_provider_x509_cert_url"],
        "client_x509_cert_url": s["client_x509_cert_url"]
    }, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    return build("sheets", "v4", credentials=creds)

# --- INTERFACE PRINCIPAL ---
st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS 122</h1><p>Interesse em Cursos e Treinamentos</p></div>', unsafe_allow_html=True)

# Imagens Locais
col_img1, col_img2, col_img3 = st.columns([1,2,1])
with col_img2:
    if os.path.exists("imagens/fachada.jpg"):
        st.image("imagens/fachada.jpg", use_column_width=True)

# Carregamento dos Cursos
mapa_cursos = carregar_dados_oficiais()

# Formulário
col_f1, col_f2, col_f3 = st.columns([1,2,1])
with col_f2:
    area_selecionada = st.selectbox("Selecione a Área:", sorted(list(mapa_cursos.keys())))
    curso_selecionado = st.selectbox("Selecione o Curso:", sorted(mapa_cursos[area_selecionada]))
    
    with st.form("meu_form", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        whats = st.text_input("WhatsApp")
        submit = st.form_submit_button("REGISTRAR INTERESSE")
        
        if submit and nome and whats:
            # Lógica de salvamento na planilha
            try:
                service = get_sheets_service()
                sid = st.secrets["connections"]["gsheets"]["spreadsheet"].split("/d/")[1].split("/")[0]
                values = [[nome, whats, area_selecionada, curso_selecionado, datetime.now().strftime("%d/%m/%Y %H:%M")]]
                service.spreadsheets().values().append(spreadsheetId=sid, range="Página1!A1", 
                                                      valueInputOption="RAW", body={"values": values}).execute()
                st.success("Sucesso! Entraremos em contato.")
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

# --- BARRA LATERAL (ADMIN) ---
with st.sidebar:
    st.image("imagens/logo.png", width=150) if os.path.exists("imagens/logo.png") else None
    st.markdown("---")
    acesso = st.text_input("Acesso Administrativo", type="password")
    if acesso == st.secrets["auth"]["admin_password"]:
        st.write("### Painel de Controle")
        if st.button("Ver Relatório de Leads"):
            # Aqui entra a lógica de ler a planilha que você já tinha
            st.info("Carregando dados da planilha...")
