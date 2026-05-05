import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
from google.oauth2 import service_account
from googleapiclient.discovery import build
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# Função para converter imagem local em base64
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

# --- DICIONÁRIO DE CURSOS ATUALIZADO (INCORPORANDO SEUS NOVOS PEDIDOS) ---
DADOS_CURSOS_LOCAL = {
    "Metalmecânica": [
        "MECÂNICO DE USINAGEM", 
        "PROGRAMADOR E OPERADOR DE CNC",
        "SOLDADOR MAG",
        "SOLDADOR TIG",
        "MECÂNICO DE MANUTENÇÃO",
        "CALDEIRARIA BÁSICA",
        "METROLOGIA APLICADA",
        "INTELIGÊNCIA ARTIFICIAL NA PROGRAMAÇÃO CNC"
    ],
    "Tecnologia da Informação": [
        "EXCEL BÁSICO",
        "EXCEL AVANÇADO",
        "EXCEL COMPLETO",
        "INFORMÁTICA BÁSICA",
        "IA GENERATIVA PARA PRODUTIVIDADE",
        "Desenvolvimento de soluções em inteligencia artificial - Microsoft Al-102",
        "Implantação de Serviços de Inteligência Artificial em Nuvem - Microsoft AI-900",
        "Fundamentos de Inteligência Artificial Generativa - Google Cloud",
        "Implantação de Serviços de Inteligência Artificial em Nuvem - Google Cloud AI Foundations",
        "Implantação de Serviços de Inteligência Artificial Generativa em Nuvem - Google Cloud",
        "Inteligências Artificiais Generativas Aplicada A Programação - Chatgpt",
        "Administração de Sistemas ServiceNow - CSA",
        "Desenvolvimento de Aplicações com IA Generativa utilizando Google Antigravity",
        "Criação de Agentes de IA com o Microsoft AI Foundry",
        "Criação de Aplicativos com Google Firebase e Gemini (PC disponível em Abril)",
        "Programação em Inteligência Artificial Generativa",
        "MARKETING DIGITAL COM INTELIGÊNCIA ARTIFICIAL",
        "PYTHON PARA ANÁLISE DE DADOS", 
        "POWER BI (DASHBOARDS)",
        "TÉCNICO EM DESENVOLVIMENTO DE SISTEMAS"
    ],
    "Eletroeletrônica": [
        "ELETRICISTA INSTALADOR", 
        "COMANDOS ELÉTRICOS",
        "CLP - CONTROLADORES LÓGICOS PROGRAMÁVEIS",
        "INSTALAÇÕES ELÉTRICAS RESIDENCIAIS",
        "MANUTENÇÃO DE SISTEMAS FOTOVOLTAICOS",
        "INTELIGÊNCIA ARTIFICIAL APLICADO À DETECÇÃO DE ANOMALIAS EM MÁQUINAS"
    ],
    "Gestão e Logística": [
        "QUALIDADE",
        "ALMOXARIFE", 
        "ASSISTENTE ADMINISTRATIVO",
        "ASSISTENTE DE RECURSOS HUMANOS",
        "LOGÍSTICA INTEGRADA",
        "GESTÃO DE ESTOQUES"
    ],
    "Automobilística": [
        "MECÂNICO DE AUTOMÓVEIS LEVES",
        "ELETRICISTA VEICULAR",
        "SISTEMAS DE INJEÇÃO ELETRÔNICA"
    ],
    "Manutenção e Lubrificação Industrial": [
        "INTELIGÊNCIA ARTIFICIAL NO MONITORAMENTO DA MANUTENÇÃO PREDITIVA",
        "DETECÇÃO A LASER E INTELIGÊNCIA ARTIFICIAL PARA LUBRIFICAÇÃO INDUSTRIAL"
    ]
}

# --- CSS: ESTILO 3D E FAIXA TOTAL (Design Original Preservado) ---
st.markdown("""
    <style>
    .stApp { background-color: #e0e5ec; }
    .logo-container { position: relative; z-index: 10; margin-bottom: -20px; display: flex; justify-content: center; padding-top: 10px; }
    .header-senai { 
        background: #ff0000; padding: 40px 0px 25px 0px; color: white; text-align: center; 
        width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw;
        z-index: 5; box-shadow: 0px 10px 15px rgba(0,0,0,0.1); border-bottom: 4px solid #cc0000;
    }
    .header-senai h1 { font-size: 28px !important; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); font-weight: 800; color: white !important; }
    .header-senai p { font-size: 16px !important; margin: 5px 0 0 0; opacity: 0.9; color: white !important; }
    label, [data-testid="stWidgetLabel"] p { color: #000000 !important; font-weight: 600 !important; }
    div.stButton > button { 
        background-color: #ff0000 !important; color: #ffffff !important; font-weight: bold !important; 
        height: 55px !important; border-radius: 15px !important; width: 100% !important;
        box-shadow: 6px 6px 12px #b8b9be, -6px -6px 12px #ffffff !important;
    }
    [data-testid="stForm"] { background-color: #e0e5ec !important; border-radius: 30px !important; padding: 2rem !important; box-shadow: inset 8px 8px 16px #bebebe, inset -8px -8px 16px #ffffff !important; border: none !important; }
    .footer-container { background-color: #b91d1d; color: white; padding: 40px 20px; margin-top: 50px; width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; }
    .footer-bottom { text-align: center; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 20px; margin-top: 20px; font-size: 12px; background-color: #ff0000; width: 100vw; padding-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- GOOGLE SHEETS ---
def salvar_novo_lead(lista_dados):
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
        service = build("sheets", "v4", credentials=creds, cache_discovery=False)
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_id = url.split("/d/")[1].split("/")[0]
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id, range="A1", valueInputOption="RAW",
            insertDataOption="INSERT_ROWS", body={"values": [lista_dados]}
        ).execute()
        return True
    except: return False

# --- INTERFACE ---
path_logo = os.path.join("imagens", "logo.png")
if os.path.exists(path_logo):
    logo_64 = get_base64_of_bin_file(path_logo)
    st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{logo_64}" width="150"></div>', unsafe_allow_html=True)

st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Registro de Interesse Profissional</p></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<h3 style='text-align: center; margin-top: 20px; color: #000000;'>📋 Cadastro de Interesse</h3>", unsafe_allow_html=True)
    
    # Seleção de Área e Curso baseada na nova lista local
    area_sel = st.selectbox("Área Profissional:", ["Selecione..."] + sorted(list(DADOS_CURSOS_LOCAL.keys())))
    opcoes_cursos = sorted(DADOS_CURSOS_LOCAL[area_sel]) if area_sel != "Selecione..." else []
    curso_sel = st.selectbox("Curso:", ["Aguardando área..."] + opcoes_cursos, disabled=(area_sel == "Selecione..."))

    with st.form("form_3d", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp")
        obs = st.text_area("Observações")
        enviar = st.form_submit_button("REGISTRAR AGORA")

        if enviar:
            if area_sel != "Selecione..." and nome and email and curso_sel != "Aguardando área...":
                data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                if salvar_novo_lead([nome, email, f"'{whats}", area_sel, curso_sel, obs, data_atual]):
                    st.success(f"Excelente, {nome}! Seu interesse foi registrado.")
                    st.balloons()
                else: st.error("Erro ao salvar. Verifique sua conexão.")
            else: st.error("Por favor, preencha os campos obrigatórios.")

st.markdown('<div class="footer-container"><div class="footer-bottom">Copyright 2026 © SENAI Guarulhos 122</div></div>', unsafe_allow_html=True)
