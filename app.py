import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- CONEXÃO RAIZ COM GOOGLE SHEETS (GOOGLE-AUTH) ---
@st.cache_resource
def conectar_google_sheets():
    try:
        # 1. Pegamos os dados do Secrets
        s = st.secrets["connections"]["gsheets"]
        
        # 2. Higienização manual da chave para remover qualquer caractere estranho (como o underline 95)
        # e garantir que as quebras de linha sejam convertidas corretamente
        private_key = s["private_key"].replace("\\n", "\n")
        
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
        
        # 3. Escopos de acesso
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
        service = build("sheets", "v4", credentials=creds)
        return service
    except Exception as e:
        st.error(f"Erro Crítico de Autenticação: {e}")
        return None

# Instancia o serviço
service = conectar_google_sheets()

# --- FUNÇÕES DE MANIPULAÇÃO (SUBSTITUEM O CONN.READ/UPDATE) ---
def extrair_id_planilha(url):
    # Extrai o ID entre /d/ e /edit
    return url.split("/d/")[1].split("/")[0]

def ler_dados():
    try:
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_id = extrair_id_planilha(url)
        # Lendo a aba "Página1" (ajuste se o nome for diferente)
        result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="A1:Z1000").execute()
        values = result.get("values", [])
        if not values:
            return pd.DataFrame()
        return pd.DataFrame(values[1:], columns=values[0])
    except Exception as e:
        st.error(f"Erro ao ler: {e}")
        return pd.DataFrame()

def salvar_dados(df):
    try:
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_id = extrair_id_planilha(url)
        # Converte DataFrame para lista de listas
        valores = [df.columns.values.tolist()] + df.values.tolist()
        body = {"values": valores}
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id, range="A1",
            valueInputOption="RAW", body=body
        ).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False

# --- INTERFACE (CURSOS E ESTILO) ---
# [O código de mapeamento de cursos e CSS permanece o mesmo para não perdermos o trabalho visual]
dados_cursos = {
    "Administração e Gestão": ["Almoxarife", "Assistente Administrativo", "Assistente de RH", "Logística"],
    "Eletroeletrônica": ["Eletricista Instalador", "Comandos Elétricos", "CLP"],
    "Metalmecânica": ["Mecânico de Usinagem", "Soldador", "Programador e Operador de CNC"],
    "Tecnologia da Informação": ["Excel Avançado", "IA Generativa", "Power BI", "Desenvolvimento de Sistemas"],
    "Automobilística": ["Mecânico de Automóveis", "Eletricista Veicular"],
    "Outras Áreas": ["Segurança do Trabalho", "Alimentos"]
}

# --- CABEÇALHO ---
st.markdown('<h1 style="text-align: center; color: red;">SENAI GUARULHOS</h1>', unsafe_allow_html=True)
st.write("---")

# --- FORMULÁRIO ---
with st.form("form_interesse", clear_on_submit=True):
    nome = st.text_input("Nome Completo")
    email = st.text_input("E-mail")
    whats = st.text_input("WhatsApp")
    area_sel = st.selectbox("Área:", list(dados_cursos.keys()))
    curso_sel = st.selectbox("Curso:", dados_cursos[area_sel])
    btn = st.form_submit_button("REGISTRAR INTERESSE")

if btn:
    if nome and service:
        df_atual = ler_dados()
        novo = pd.DataFrame([{
            "nome": nome, "email": email, "whatsapp": whats,
            "area": area_sel, "curso": curso_sel, "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }])
        df_final = pd.concat([df_atual, novo], ignore_index=True)
        if salvar_dados(df_final):
            st.success("Registrado com sucesso!")
            st.balloons()
