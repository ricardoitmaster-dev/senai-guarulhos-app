import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup
from google.oauth2 import service_account
from googleapiclient.discovery import build
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- CSS: ESTILO 3D (NEUMORPHISM) ---
st.markdown("""
    <style>
    .stApp { background-color: #e0e5ec; }
    .header-senai { 
        background: #ff0000; padding: 30px; color: white; text-align: center; 
        border-radius: 0 0 30px 30px; margin-bottom: 20px;
        box-shadow: 0px 10px 15px rgba(0,0,0,0.1);
    }
    div.stButton > button { 
        background-color: #ff0000 !important; color: white !important;
        border-radius: 15px !important; height: 50px; width: 100%;
        box-shadow: 6px 6px 12px #b8b9be, -6px -6px 12px #ffffff !important;
    }
    [data-testid="stForm"] {
        background-color: #e0e5ec !important; border-radius: 30px !important;
        box-shadow: inset 8px 8px 16px #bebebe, inset -8px -8px 16px #ffffff !important;
        border: none !important; padding: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SCRAPING DINÂMICO (ÂNCORA) ---
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
            return mapa
    except:
        pass
    
    # Fallback Profissional (Dados de redundância)
    return {"TI e Gestão": ["EXCEL AVANÇADO", "IA GENERATIVA", "ASSISTENTE ADMINISTRATIVO"]}

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

# --- INTERFACE PRINCIPAL ---
st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Registro de Interesse</p></div>', unsafe_allow_html=True)

dados_cursos = buscar_cursos_ancora()

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    area_sel = st.selectbox("Área Profissional:", sorted(list(dados_cursos.keys())))
    curso_sel = st.selectbox("Curso de Interesse:", sorted(dados_cursos[area_sel]))

    with st.form("form_registro"):
        nome = st.text_input("Nome")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp")
        enviar = st.form_submit_button("ENVIAR INTERESSE")

        if enviar:
            if nome and email:
                data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                if salvar_lead([nome, email, whats, area_sel, curso_sel, data]):
                    st.success("Registro realizado com sucesso!")
                    st.balloons()
            else:
                st.warning("Por favor, preencha os campos obrigatórios.")
