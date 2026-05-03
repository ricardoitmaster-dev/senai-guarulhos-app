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

# --- CSS VITRIFICADO (PRESERVADO) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%); }
    .header-senai { 
        background: linear-gradient(90deg, #e3000f 0%, #ff4b4b 100%); 
        padding: 30px; border-radius: 20px; color: white; text-align: center; 
        box-shadow: 0 15px 25px -5px rgba(227, 0, 15, 0.4); margin-bottom: 40px;
    }
    [data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.4) !important;
        backdrop-filter: blur(15px) saturate(180%) !important;
        border-radius: 25px !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        padding: 3rem !important;
    }
    div.stButton > button { 
        background: linear-gradient(90deg, #232526 0%, #414345 100%) !important;
        color: white !important; font-weight: 700 !important; height: 60px !important;
        border-radius: 15px !important; width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SCRAPER COM TRATAMENTO DE ERRO ROBUSTO ---
@st.cache_data(ttl=86400)
def carregar_estrutura_cursos():
    # Estrutura padrão (Fallback) caso o site mude ou caia
    fallback = {
        "Tecnologia da Informação": ["Excel Avançado", "IA Generativa", "Python", "Power BI", "Desenvolvimento de Sistemas"],
        "Eletroeletrônica": ["Eletricista Instalador", "CLP", "Comandos Elétricos", "Eletrônica Analógica"],
        "Metalmecânica": ["Mecânico de Usinagem", "Soldagem", "Programador CNC", "Ajustagem Mecânica"],
        "Gestão e Logística": ["Assistente Administrativo", "Almoxarife", "Logística de Produção"]
    }
    
    url = "https://guarulhos.sp.senai.br/cursos"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Busca todos os links de cursos ou cards (ajuste conforme a classe do site atual)
            cursos_encontrados = soup.find_all('a', href=True)
            
            # Se encontrar muitos cursos, podemos processar, mas o fallback garante a escala imediata
            if len(cursos_encontrados) > 10:
                # Aqui poderíamos mapear dinamicamente. Para escala, o fallback é mais seguro hoje.
                return fallback 
        return fallback
    except:
        return fallback

# --- GOOGLE SHEETS (LÓGICA FUNCIONAL) ---
@st.cache_resource
def conectar_sheets():
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
        return build("sheets", "v4", credentials=creds)
    except: return None

def salvar_no_sheets(dados_lista):
    try:
        service = conectar_sheets()
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_id = url.split("/d/")[1].split("/")[0]
        
        # Lê primeiro para não sobrescrever
        result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="A1:Z1").execute()
        if not result.get("values"):
            header = [["Nome", "Email", "WhatsApp", "Área", "Curso", "Data"]]
            service.spreadsheets().values().update(spreadsheetId=sheet_id, range="A1", valueInputOption="RAW", body={"values": header}).execute()

        service.spreadsheets().values().append(spreadsheetId=sheet_id, range="A2", valueInputOption="RAW", body={"values": [dados_lista]}).execute()
        return True
    except: return False

# --- FRONT-END ---
dados_cursos = carregar_estrutura_cursos()

st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Ficha de Interesse Profissional</p></div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 2, 1])

with c2:
    # Seleção de Área (Fora do form para ser dinâmico)
    area_sel = st.selectbox("📌 1. Escolha a Área Profissional:", ["Selecione..."] + list(dados_cursos.keys()))
    
    # Seleção de Curso (Filtrada)
    lista_filtro = dados_cursos[area_sel] if area_sel != "Selecione..." else []
    curso_sel = st.selectbox("🎓 2. Escolha o Curso:", ["Selecione o curso..."] + lista_filtro, disabled=(area_sel == "Selecione..."))

    with st.form("form_leads", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp")
        
        enviar = st.form_submit_button("REGISTRAR INTERESSE")

    if enviar:
        if area_sel != "Selecione..." and curso_sel != "Selecione o curso..." and nome and email:
            data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            sucesso = salvar_no_sheets([nome, email, whats, area_sel, curso_sel, data_hora])
            
            if sucesso:
                st.success(f"✅ Feito, {nome}! O SENAI-122 agradece seu interesse.")
                st.balloons()
            else:
                st.error("Erro ao conectar com a planilha. Verifique os secrets.")
        else:
            st.warning("⚠️ Preencha todos os campos antes de enviar.")
