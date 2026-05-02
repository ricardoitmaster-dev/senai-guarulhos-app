import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

@st.cache_resource
def conectar_google_sheets():
    try:
        s = st.secrets["connections"]["gsheets"]
        pk = s["private_key"].replace("\\n", "\n").strip()
        
        info = {
            "type": "service_account",
            "project_id": s["project_id"],
            "private_key_id": s["private_key_id"],
            "private_key": pk,
            "client_email": s["client_email"],
            "client_id": s["client_id"],
            "auth_uri": s["auth_uri"],
            "token_uri": s["token_uri"],
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

def extrair_id(url):
    return url.split("/d/")[1].split("/")[0]

def ler_dados():
    try:
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        res = service.spreadsheets().values().get(spreadsheetId=extrair_id(url), range="A1:Z1000").execute()
        v = res.get("values", [])
        return pd.DataFrame(v[1:], columns=v[0]) if v else pd.DataFrame()
    except: return pd.DataFrame()

def salvar_dados(df):
    try:
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        valores = [df.columns.tolist()] + df.values.tolist()
        service.spreadsheets().values().update(
            spreadsheetId=extrair_id(url), range="A1",
            valueInputOption="RAW", body={"values": valores}
        ).execute()
        return True
    except: return False

# --- INTERFACE ---
dados_cursos = {
    "TI": ["Excel Avançado", "IA Generativa", "Power BI"],
    "Gestão": ["Logística", "Assistente de RH"],
    "Eletro": ["Comandos Elétricos", "CLP"]
}

st.markdown('<h1 style="text-align: center; color: red;">SENAI GUARULHOS</h1>', unsafe_allow_html=True)

with st.form("form_leads", clear_on_submit=True):
    nome = st.text_input("Nome Completo")
    email = st.text_input("E-mail")
    whats = st.text_input("WhatsApp")
    area = st.selectbox("Área", list(dados_cursos.keys()))
    curso = st.selectbox("Curso", dados_cursos[area])
    enviar = st.form_submit_button("REGISTRAR")

if enviar and nome and service:
    df = ler_dados()
    novo = pd.DataFrame([{"nome": nome, "email": email, "whatsapp": whats, "area": area, "curso": curso, "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}])
    if salvar_dados(pd.concat([df, novo], ignore_index=True)):
        st.success("Interesse registrado!")
        st.balloons()
