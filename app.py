import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- CONEXÃO COM GOOGLE SHEETS (VERSÃO ESTÁVEL) ---
@st.cache_resource
def conectar_google_sheets():
    try:
        # Recupera os segredos do Streamlit Cloud
        s = st.secrets["connections"]["gsheets"]
        
        # O segredo do sucesso: Tratar as quebras de linha sem corromper a chave
        # Isso resolve o erro de 'short data' e 'ASN.1 parsing'
        private_key = s["private_key"].replace("\\n", "\n")
        
        # Garante que os cabeçalhos PEM existam
        if not private_key.startswith("-----BEGIN"):
             private_key = f"-----BEGIN PRIVATE KEY-----\n{private_key}\n-----END PRIVATE KEY-----\n"

        info = {
            "type": s["type"],
            "project_id": s["project_id"],
            "private_key_id": s["private_key_id"],
            "private_key": private_key,
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
        st.error(f"Erro Crítico de Autenticação: {e}")
        return None

# Instancia o serviço globalmente
service = conectar_google_sheets()

# --- FUNÇÕES DE MANIPULAÇÃO DE DADOS ---
def extrair_id_planilha(url):
    return url.split("/d/")[1].split("/")[0]

def ler_dados():
    try:
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_id = extrair_id_planilha(url)
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, 
            range="A1:Z1000"
        ).execute()
        values = result.get("values", [])
        if not values:
            return pd.DataFrame()
        return pd.DataFrame(values[1:], columns=values[0])
    except Exception as e:
        st.error(f"Erro ao ler dados: {e}")
        return pd.DataFrame()

def salvar_dados(df):
    try:
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_id = extrair_id_planilha(url)
        valores = [df.columns.values.tolist()] + df.values.tolist()
        body = {"values": valores}
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id, 
            range="A1",
            valueInputOption="RAW", 
            body=body
        ).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar dados: {e}")
        return False

# --- DADOS E ESTILIZAÇÃO ---
dados_cursos = {
    "Administração e Gestão": ["Almoxarife", "Assistente Administrativo", "Assistente de RH", "Logística"],
    "Eletroeletrônica": ["Eletricista Instalador", "Comandos Elétricos", "CLP"],
    "Metalmecânica": ["Mecânico de Usinagem", "Soldador", "Programador e Operador de CNC"],
    "Tecnologia da Informação": ["Excel Avançado", "IA Generativa", "Power BI", "Desenvolvimento de Sistemas"],
    "Automobilística": ["Mecânico de Automóveis", "Eletricista Veicular"],
    "Outras Áreas": ["Segurança do Trabalho", "Alimentos"]
}

st.markdown("""
    <style>
    .header-senai { background-color: #ff0000; padding: 15px; border-radius: 12px; color: white; text-align: center; margin: 20px 0; }
    div.stButton > button { background-color: #000000 !important; color: white !important; font-weight: bold !important; width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Inscrição de Interesse em Cursos</p></div>', unsafe_allow_html=True)

# --- FORMULÁRIO ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    with st.form("meu_form", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp")
        area = st.selectbox("Área de Interesse", list(dados_cursos.keys()))
        curso = st.selectbox("Curso", dados_cursos[area])
        enviar = st.form_submit_button("REGISTRAR")

if enviar:
    if nome and service:
        df_atual = ler_dados()
        novo = pd.DataFrame([{
            "nome": nome, "email": email, "whatsapp": whats,
            "area": area, "curso": curso, "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }])
        df_final = pd.concat([df_atual, novo], ignore_index=True)
        if salvar_dados(df_final):
            st.success("Sucesso! Aguarde nosso contato.")
            st.balloons()
