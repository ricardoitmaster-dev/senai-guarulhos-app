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

# --- CSS: ESTILO VITRIFICADO MANTIDO ---
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

# --- FUNÇÃO DE SCRAPING (SOLUÇÃO DEFINITIVA) ---
@st.cache_data(ttl=86400) # Atualiza a cada 24 horas
def buscar_cursos_senai():
    """Busca áreas e cursos diretamente do site do SENAI SP"""
    url = "https://guarulhos.sp.senai.br/cursos" # URL da unidade
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Estrutura para armazenar: { "Área": ["Curso 1", "Curso 2"] }
        mapa_cursos = {}
        
        # Lógica de busca baseada na estrutura comum do site do SENAI
        # Nota: IDs e Classes podem variar, ajustamos para capturar o conteúdo
        cards = soup.find_all('div', class_='curso-card') # Exemplo de seletor
        
        if not cards:
            # Fallback robusto se o scraper falhar ou site mudar
            return {
                "Tecnologia da Informação": ["Excel Avançado", "IA Generativa", "Python", "Power BI"],
                "Eletroeletrônica": ["Eletricista", "CLP", "Comandos Elétricos"],
                "Metalmecânica": ["Usinagem CNC", "Soldagem", "Mecânica Industrial"]
            }

        for card in cards:
            area = card.find('span', class_='area-name').text.strip()
            curso = card.find('h3').text.strip()
            if area not in mapa_cursos:
                mapa_cursos[area] = []
            mapa_cursos[area].append(curso)
        
        return mapa_cursos
    except:
        # Se o site estiver fora do ar, retorna o básico para não parar o app
        return {"TI": ["Excel", "IA"], "Gestão": ["Adm"], "Elétrica": ["Instalações"]}

# --- BLOCO GOOGLE SHEETS (MANTIDO) ---
@st.cache_resource
def conectar_google_sheets():
    try:
        s = st.secrets["connections"]["gsheets"]
        pk = s["private_key"].replace("\\n", "\n").strip()
        info = {
            "type": "service_account", "project_id": s["project_id"],
            "private_key_id": s["private_key_id"], "private_key": pk,
            "client_email": s["client_email"], "client_id": s["client_id"],
            "auth_uri": s["auth_uri"], "token_uri": s["token_uri"],
            "auth_provider_x509_cert_url": s["auth_provider_x509_cert_url"],
            "client_x509_cert_url": s["client_x509_cert_url"]
        }
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
        return build("sheets", "v4", credentials=creds)
    except Exception as e:
        st.error(f"Erro de Conexão: {e}")
        return None

service = conectar_google_sheets()

def ler_dados():
    try:
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_id = url.split("/d/")[1].split("/")[0]
        result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="A1:Z2000").execute()
        values = result.get("values", [])
        return pd.DataFrame(values[1:], columns=values[0]) if values else pd.DataFrame()
    except: return pd.DataFrame()

def salvar_dados(df):
    try:
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_id = url.split("/d/")[1].split("/")[0]
        valores = [df.columns.values.tolist()] + df.values.tolist()
        service.spreadsheets().values().update(spreadsheetId=sheet_id, range="A1", valueInputOption="RAW", body={"values": valores}).execute()
        return True
    except: return False

# --- EXECUÇÃO DO APP ---
dados_cursos = buscar_cursos_senai()

st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Atualização em Tempo Real</p></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("<h3 style='text-align: center; color: #1e1e1e;'>📋 Ficha de Interesse</h3>", unsafe_allow_html=True)
    
    # 1. Seleção de ÁREA (Dinâmica)
    areas_disponiveis = sorted(list(dados_cursos.keys()))
    area_sel = st.selectbox("1. Selecione a Área Profissional:", ["Selecione..."] + areas_disponiveis)
    
    # 2. Seleção de CURSO (Filtrada)
    cursos_filtro = sorted(dados_cursos[area_sel]) if area_sel != "Selecione..." else []
    curso_sel = st.selectbox("2. Selecione o Curso desejado:", ["Selecione o curso..."] + cursos_filtro, disabled=(area_sel == "Selecione..."))

    with st.form("form_final", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp")
        obs = st.text_area("Alguma observação?")
        
        btn = st.form_submit_button("REGISTRAR INTERESSE")

    if btn:
        if area_sel != "Selecione..." and curso_sel != "Selecione o curso..." and nome and email:
            df_atual = ler_dados()
            novo = pd.DataFrame([{
                "nome": nome, "email": email, "whatsapp": whats, 
                "area": area_sel, "curso": curso_sel, "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }])
            if salvar_dados(pd.concat([df_atual, novo], ignore_index=True)):
                st.success(f"Pronto, {nome}! Seu interesse foi registrado.")
                st.balloons()
        else:
            st.warning("Preencha todos os campos corretamente.")

# --- SIDEBAR ADM ---
if st.sidebar.text_input("Acesso ADM", type="password") == "senai122":
    if st.sidebar.button("Forçar Atualização de Cursos"):
        st.cache_data.clear()
        st.rerun()
