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

# Função para converter imagens locais em Base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- CSS ORIGINAL: CORES BMW BLUE E GOLD ---
st.markdown("""
    <style>
    .stApp { background-color: #e0e5ec; }
    .header-senai { 
        background: #0066b2; /* Azul BMW */
        padding: 30px; 
        color: white; 
        text-align: center; 
        border-bottom: 5px solid #d4af37; /* Dourado */
        margin-bottom: 20px;
    }
    div.stButton > button { 
        background-color: #0066b2 !important; 
        color: white !important;
        border-radius: 10px !important; 
        font-weight: bold;
    }
    label, [data-testid="stWidgetLabel"] p { color: #000000 !important; font-weight: 600 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE COLETA DE DADOS (ÂNCOMA DE SEGURANÇA) ---
@st.cache_data(ttl=3600)
def carregar_cursos_oficiais():
    api_key = "3e14f4393c5a034104b37c071a0d021f"
    url = "https://www.sp.senai.br/cursos/0/tecnologia-da-informacao?unidade=122"
    try:
        params = {'api_key': api_key, 'url': url, 'render': 'true'}
        r = requests.get('http://api.scraperapi.com', params=params, timeout=30)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            mapa = {}
            for card in soup.select('.item-lista-curso, div[class*="card-curso"]'):
                area_elem = card.select_one('.area-tematica, .txt-area')
                titulo_elem = card.select_one('.titulo-curso, h2')
                if area_elem and titulo_elem:
                    area = area_elem.get_text(strip=True).title()
                    curso = titulo_elem.get_text(strip=True).upper()
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
st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS 122</h1><p>Registro de Interesse em Cursos</p></div>', unsafe_allow_html=True)

# Imagem de Fachada
if os.path.exists("imagens/fachada.jpg"):
    fachada_base64 = get_base64_of_bin_file("imagens/fachada.jpg")
    st.markdown(f'<div style="text-align:center;"><img src="data:image/jpeg;base64,{fachada_base64}" style="width:70%; border-radius:15px; margin-bottom:20px;"></div>', unsafe_allow_html=True)

# Lógica de Seleção
mapa_cursos = carregar_cursos_oficiais()
col_f1, col_f2, col_f3 = st.columns([1,2,1])
with col_f2:
    area_selecionada = st.selectbox("Área Profissional:", sorted(list(mapa_cursos.keys())))
    curso_selecionado = st.selectbox("Curso Disponível:", sorted(mapa_cursos[area_selecionada]))
    
    with st.form("form_registro", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        whats = st.text_input("WhatsApp")
        submit = st.form_submit_button("REGISTRAR INTERESSE")
        
        if submit and nome and whats:
            try:
                service = get_sheets_service()
                sid = st.secrets["connections"]["gsheets"]["spreadsheet"].split("/d/")[1].split("/")[0]
                values = [[nome, whats, area_selecionada, curso_selecionado, datetime.now().strftime("%d/%m/%Y %H:%M")]]
                service.spreadsheets().values().append(spreadsheetId=sid, range="Página1!A1", 
                                                      valueInputOption="RAW", body={"values": values}).execute()
                st.success(f"Obrigado {nome}! Interesse registrado.")
                st.balloons()
            except Exception as e:
                st.error(f"Erro ao salvar dados: {e}")

# --- BARRA LATERAL ADMINISTRATIVA ---
with st.sidebar:
    if os.path.exists("imagens/logo.png"):
        logo_base64 = get_base64_of_bin_file("imagens/logo.png")
        st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{logo_base64}" width="150"></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    senha = st.sidebar.text_input("Senha Admin", type="password")
    if senha == st.secrets["auth"]["admin_password"]:
        st.sidebar.success("Acesso Autorizado")
        # Aqui você pode adicionar botões para baixar o CSV ou ver os leads
