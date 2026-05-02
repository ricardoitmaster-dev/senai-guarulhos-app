import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- CONEXÃO COM GOOGLE SHEETS (MOTOR OFICIAL) ---
@st.cache_resource
def conectar_google_sheets():
    try:
        s = st.secrets["connections"]["gsheets"]
        # Limpeza da chave para evitar erro de ASN.1 / short data
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
        st.error(f"Erro Crítico de Autenticação: {e}")
        return None

service = conectar_google_sheets()

# --- FUNÇÕES DE APOIO ---
def extrair_id_planilha(url):
    return url.split("/d/")[1].split("/")[0]

def ler_dados():
    try:
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_id = extrair_id_planilha(url)
        result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="A1:Z1000").execute()
        values = result.get("values", [])
        if not values:
            return pd.DataFrame(columns=["nome", "email", "whatsapp", "area", "curso", "sugestao", "data"])
        return pd.DataFrame(values[1:], columns=values[0])
    except:
        return pd.DataFrame(columns=["nome", "email", "whatsapp", "area", "curso", "sugestao", "data"])

def salvar_dados(df):
    try:
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_id = extrair_id_planilha(url)
        valores = [df.columns.values.tolist()] + df.values.tolist()
        body = {"values": valores}
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id, range="A1",
            valueInputOption="RAW", body=body
        ).execute()
        return True
    except:
        return False

# --- MAPEAMENTO DE ÁREAS E CURSOS (O QUE HAVIA SUMIDO) ---
dados_cursos = {
    "Administração e Gestão": ["Almoxarife", "Assistente Administrativo", "Assistente de RH", "Logística"],
    "Eletroeletrônica": ["Eletricista Instalador", "Comandos Elétricos", "CLP"],
    "Metalmecânica": ["Mecânico de Usinagem", "Soldador", "Programador e Operador de CNC"],
    "Tecnologia da Informação": [
        "Excel Avançado", "IA Generativa: ChatGPT", "IA Generativa: Google Gemini",
        "IA Generativa: Microsoft Copilot", "Power BI", "Técnico em Desenvolvimento de Sistemas"
    ],
    "Automobilística": ["Mecânico de Automóveis", "Eletricista Veicular"],
    "Outras Áreas": ["Segurança do Trabalho", "Alimentos"]
}

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .header-senai { background-color: #ff0000; padding: 20px; border-radius: 12px; color: white; text-align: center; margin-bottom: 25px; }
    div.stButton > button { background-color: #000000 !important; color: white !important; font-weight: bold !important; width: 100% !important; border-radius: 8px !important; height: 50px; }
    label { font-weight: bold !important; color: #1e1e1e !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Hermenegildo Campos de Almeida</p></div>', unsafe_allow_html=True)

# --- FORMULÁRIO ---
col_f1, col_f2, col_f3 = st.columns([1, 2, 1])

with col_f2:
    st.write("### 📋 Ficha de Interesse")
    
    # Lógica de seleção dinâmica que você desejava:
    opcoes_areas = ["Selecione..."] + sorted(list(dados_cursos.keys()))
    area_sel = st.selectbox("1. Selecione a Área de Interesse:", opcoes_areas)
    
    if area_sel != "Selecione...":
        lista_cursos = ["Selecione..."] + sorted(dados_cursos[area_sel])
    else:
        lista_cursos = ["Selecione a área primeiro"]
        
    curso_sel = st.selectbox("2. Selecione o Curso:", lista_cursos)

    with st.form("form_final", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp (com DDD)")
        sugestao = st.text_area("Alguma dúvida ou sugestão?")
        
        btn_enviar = st.form_submit_button("REGISTRAR INTERESSE")

# --- LÓGICA DE ENVIO ---
if btn_enviar:
    if area_sel != "Selecione..." and curso_sel != "Selecione..." and nome and email:
        if service:
            df_atual = ler_dados()
            novo_lead = pd.DataFrame([{
                "nome": nome, "email": email, "whatsapp": whats,
                "area": area_sel, "curso": curso_sel, "sugestao": sugestao,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }])
            
            df_final = pd.concat([df_atual, novo_lead], ignore_index=True)
            
            if salvar_dados(df_final):
                st.success(f"Excelente, {nome}! Seu interesse em {curso_sel} foi registrado com sucesso.")
                st.balloons()
            else:
                st.error("Erro ao salvar na planilha. Verifique as permissões de Editor.")
    else:
        st.warning("Por favor, preencha todos os campos obrigatórios (Nome, E-mail, Área e Curso).")
