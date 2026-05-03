import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- CSS: DESIGN VITRIFICADO & FUNDO GELO ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
    }
    
    .header-senai { 
        background: linear-gradient(90deg, #e3000f 0%, #ff4b4b 100%); 
        padding: 30px; 
        border-radius: 20px; 
        color: white; 
        text-align: center; 
        box-shadow: 0 15px 25px -5px rgba(227, 0, 15, 0.4);
        margin-bottom: 40px;
    }

    [data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.4) !important;
        backdrop-filter: blur(15px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(15px) saturate(180%);
        border-radius: 25px !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        padding: 3rem !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1) !important;
    }

    div.stButton > button { 
        background: linear-gradient(90deg, #232526 0%, #414345 100%) !important;
        color: white !important; 
        font-weight: 700 !important;
        height: 60px !important;
        border-radius: 15px !important;
        transition: 0.4s !important;
        width: 100% !important;
    }
    div.stButton > button:hover {
        background: #e3000f !important;
        transform: scale(1.01);
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO GOOGLE SHEETS ---
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

def extrair_id_planilha(url):
    return url.split("/d/")[1].split("/")[0]

def ler_dados():
    try:
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_id = extrair_id_planilha(url)
        result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="A1:Z1000").execute()
        values = result.get("values", [])
        if not values: return pd.DataFrame(columns=["nome", "email", "whatsapp", "area", "curso", "sugestao", "data"])
        return pd.DataFrame(values[1:], columns=values[0])
    except: return pd.DataFrame(columns=["nome", "email", "whatsapp", "area", "curso", "sugestao", "data"])

def salvar_dados(df):
    try:
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_id = extrair_id_planilha(url)
        valores = [df.columns.values.tolist()] + df.values.tolist()
        body = {"values": valores}
        service.spreadsheets().values().update(spreadsheetId=sheet_id, range="A1", valueInputOption="RAW", body=body).execute()
        return True
    except: return False

# --- MAPEAMENTO DE CURSOS (ÁREAS SEPARADAS) ---
dados_cursos = {
    "Administração e Gestão": ["Almoxarife", "Assistente Administrativo", "Assistente de RH", "Logística"],
    "Eletroeletrônica": ["Eletricista Instalador", "Comandos Elétricos", "CLP"],
    "Metalmecânica": ["Mecânico de Usinagem", "Soldador", "Programador e Operador de CNC"],
    "Tecnologia da Informação": ["Excel Avançado", "IA Generativa", "Power BI", "Técnico em Desenvolvimento de Sistemas"],
    "Automobilística": ["Mecânico de Automóveis", "Eletricista Veicular"]
}

# --- INTERFACE ---
st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Hermenegildo Campos de Almeida</p></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("<h3 style='text-align: center; color: #1e1e1e;'>📋 Ficha de Interesse</h3>", unsafe_allow_html=True)
    
    # IMPORTANTE: Seleção de Área e Curso fora do st.form para permitir a atualização dinâmica
    area_selecionada = st.selectbox("1. Escolha a Área de Interesse:", ["Selecione uma área..."] + list(dados_cursos.keys()))
    
    if area_selecionada != "Selecione uma área...":
        opcoes_cursos = dados_cursos[area_selecionada]
    else:
        opcoes_cursos = []

    curso_selecionado = st.selectbox("2. Escolha o Curso:", ["Selecione o curso..."] + opcoes_cursos, disabled=(area_selecionada == "Selecione uma área..."))

    # Formulário apenas para dados pessoais e botão de envio
    with st.form("meu_form_vitrificado", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail para contato")
        whats = st.text_input("WhatsApp (com DDD)")
        sugestao = st.text_area("Dúvidas ou Comentários")
        
        submit_button = st.form_submit_button("REGISTRAR INTERESSE")

    if submit_button:
        if area_selecionada == "Selecione uma área..." or curso_selecionado == "Selecione o curso..." or not nome or not email:
            st.warning("⚠️ Por favor, selecione a Área, o Curso e preencha seus dados básicos.")
        elif service:
            df_atual = ler_dados()
            novo_registro = pd.DataFrame([{
                "nome": nome, 
                "email": email, 
                "whatsapp": whats, 
                "area": area_selecionada, 
                "curso": curso_selecionado, 
                "sugestao": sugestao, 
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }])
            
            if salvar_dados(pd.concat([df_atual, novo_registro], ignore_index=True)):
                st.success(f"✅ Muito obrigado, {nome}! Seu interesse foi registrado com sucesso.")
                st.balloons()
            else:
                st.error("❌ Erro ao salvar os dados. Verifique a conexão.")

# --- ADMINISTRAÇÃO ---
st.sidebar.title("🔒 Gestão SENAI-122")
senha = st.sidebar.text_input("Senha de acesso", type="password")
if senha == "senai122":
    st.sidebar.success("Acesso Autorizado")
    if st.sidebar.button("Atualizar Dados"):
        st.cache_resource.clear()
    
    dados_adm = ler_dados()
    if not dados_adm.empty:
        st.sidebar.write(f"Total de Leads: {len(dados_adm)}")
        if st.sidebar.checkbox("Mostrar Tabela"):
            st.write("### Relatório de Interessados")
            st.dataframe(dados_adm, use_container_width=True)
