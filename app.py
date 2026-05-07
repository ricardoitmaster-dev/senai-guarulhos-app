import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64
import urllib.parse
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- ESTILIZAÇÃO CSS (BMW PORTINARI, PRETO E OURO) ---
estilo_css = """
<style>
    .stApp { background-color: #003366; } 
    .logo-container { position: relative; z-index: 10; margin-bottom: -20px; display: flex; justify-content: center; padding-top: 10px; }
    .moldura-3d-ajustada { 
        display: block; border-radius: 25px; 
        box-shadow: 10px 10px 20px #001a33, -5px -5px 15px #004080; 
        border: 4px solid #D4AF37; overflow: hidden; margin: 25px auto; 
    }
    .moldura-3d-ajustada img { border-radius: 20px; display: block; width: 100%; height: auto; }
    .header-senai { 
        background: #000000; padding: 40px 0px 25px 0px; color: #D4AF37; 
        text-align: center; width: 100vw; position: relative; left: 50%; right: 50%; 
        margin-left: -50vw; margin-right: -50vw; z-index: 5; 
        box-shadow: 0px 10px 15px rgba(0,0,0,0.5); border-bottom: 4px solid #D4AF37; 
    }
    .header-senai h1 { font-size: 28px !important; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); font-weight: 800; color: #D4AF37 !important; }
    .btn-whatsapp { 
        display: inline-flex; align-items: center; justify-content: center; 
        background-color: #25D366 !important; color: white !important; 
        padding: 15px 25px; border-radius: 12px; text-decoration: none; 
        font-weight: bold; font-size: 18px; box-shadow: 4px 4px 10px rgba(0,0,0,0.4); 
        margin-top: 15px; width: 100%; transition: 0.3s; 
    }
    [data-testid="stForm"] { 
        background-color: rgba(0, 0, 0, 0.7) !important; border-radius: 30px !important; 
        padding: 2rem !important; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8) !important; 
        border: 2px solid #D4AF37 !important; 
    }
    label, [data-testid="stWidgetLabel"] p { color: #D4AF37 !important; font-weight: 600 !important; }
    div.stButton > button { 
        background-color: #D4AF37 !important; color: #000000 !important; 
        font-weight: bold !important; height: 55px !important; border-radius: 15px !important; 
        width: 100% !important; border: none !important; box-shadow: 4px 4px 8px rgba(0,0,0,0.5) !important; 
    }
    .footer-container { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; margin-top: 50px; }
    .footer-top { background-color: #000000; padding: 15px 0; text-align: center; color: #D4AF37; display: flex; justify-content: center; gap: 20px; font-size: 12px; }
    .footer-social { background-color: #D4AF37; padding: 15px 0; text-align: center; color: #000000; display: flex; justify-content: center; gap: 25px; font-size: 20px; }
    .footer-content { background-color: #000000; padding: 40px 10% 20px 10%; color: #D4AF37; display: grid; grid-template-columns: 1fr 1fr; gap: 50px; }
    .footer-bottom { background-color: #000000; padding: 20px 0; border-top: 1px solid #D4AF37; display: flex; justify-content: center; color: #D4AF37; font-weight: bold; }
</style>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
"""

st.markdown(estilo_css, unsafe_allow_html=True)

# --- FUNÇÕES DE APOIO ---
def reset_geral_callback():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

def get_base64_of_bin_file(bin_file):
    try:
        if os.path.exists(bin_file):
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()
    except:
        return ""
    return ""

def limpar_whatsapp(numero):
    return re.sub(r'\D', '', numero)

# --- DADOS DOS CURSOS ---
DADOS_CURSOS = {
    "Tecnologia da Informação": [
        "EXCEL BÁSICO", "EXCEL COMPLETO", "EXCEL AVANÇADO", "INFORMÁTICA BÁSICA", 
        "PYTHON PARA ANÁLISE DE DADOS", "FUNDAMENTOS EM PYTHON", "POWER BI (DASHBOARDS)",
        "IMPLANTAÇÃO DE SERVIÇOS DE INTELIGÊNCIA ARTIFICIAL GENERATIVA EM NUVEM – GOOGLE CLOUD", 
        "INTELIGÊNCIA ARTIFICIAL APLICADO À DETECÇÃO DE ANOMALIAS EM MÁQUINAS", 
        "INTELIGÊNCIA ARTIFICIAL NA PROGRAMAÇÃO CNC", 
        "INTELIGÊNCIA ARTIFICIAL NO MONITORAMENTO DA MANUTENÇÃO PREDITIVA", 
        "INTELIGÊNCIAS ARTIFICIAIS GENERATIVAS APLICADA A PROGRAMAÇÃO - CHATGPT", 
        "MARKETING DIGITAL COM INTELIGÊNCIA ARTIFICIAL", 
        "PROGRAMAÇÃO EM INTELIGÊNCIA ARTIFICIAL GENERATIVA"
    ],
    "Metalmecânica": ["MECÂNICO DE USINAGEM", "PROGRAMADOR CNC", "SOLDADOR MAG/TIG"],
    "Eletroeletrônica": ["ELETRICISTA INSTALADOR", "COMANDOS ELÉTRICOS", "SISTEMAS FOTOVOLTAICOS"],
    "Gestão e Logística": [
        "ALMOXARIFE", "ASSISTENTE ADMINISTRATIVO", "LOGÍSTICA INTEGRADA",
        "ASSISTENTE DE RECURSOS HUMANOS", "ASSSISTENTE FINANCEIRO",
        "GESTÃO DE PESSOAS E LIDERANÇA", "GESTÃO EM ENGENHARIA DE PRODUÇÃO"
    ]
}

# --- FUNÇÕES GOOGLE SHEETS ---
def conectar_google_sheets():
    try:
        s = st.secrets["connections"]["gsheets"]
        info = {
            "type": "service_account",
            "project_id": s["project_id"],
            "private_key_id": s["private_key_id"],
            "private_key": s["private_key"].replace("\\n", "\n").strip(),
            "client_email": s["client_email"],
            "client_id": s["client_id"],
            "auth_uri": s["auth_uri"],
            "token_uri": s["token_uri"],
            "auth_provider_x509_cert_url": s["auth_provider_x509_cert_url"],
            "client_x509_cert_url": s["client_x509_cert_url"]
        }
        creds = service_account.Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
        return build("sheets", "v4", credentials=creds, cache_discovery=False)
    except:
        return None

def salvar_novo_lead(lista_dados):
    try:
        service = conectar_google_sheets()
        if not service: return False
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_id = url.split("/d/")[1].split("/")[0]
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id, range="A1", valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS", body={"values": [lista_dados]}
        ).execute()
        st.cache_data.clear()
        return True
    except:
        return False

def ler_todos_leads():
    try:
        service = conectar_google_sheets()
        if not service: return pd.DataFrame()
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_id = url.split("/d/")[1].split("/")[0]
        result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="A1:Z2000").execute()
        values = result.get("values", [])
        return pd.DataFrame(values[1:], columns=values[0]) if values else pd.DataFrame()
    except:
        return pd.DataFrame()

# --- INTERFACE PRINCIPAL ---
path_logo = os.path.join("imagens", "logo.png")
path_fachada = os.path.join("imagens", "fachada.jpg")

logo_base = get_base64_of_bin_file(path_logo)
if logo_base:
    st.markdown(f'<div class="logo-container"><div class="moldura-3d-ajustada" style="width:150px; margin: 0 auto;"><img src="data:image/png;base64,{logo_base}"></div></div>', unsafe_allow_html=True)

st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 1
