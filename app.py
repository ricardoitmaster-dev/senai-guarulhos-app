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

# --- DICIONÁRIO DE CURSOS (Sua Lista Atualizada e Fixa) ---
DADOS_CURSOS_LOCAL = {
    "Metalmecânica": [
        "MECÂNICO DE USINAGEM", "PROGRAMADOR E OPERADOR DE CNC", "SOLDADOR MAG",
        "SOLDADOR TIG", "MECÂNICO DE MANUTENÇÃO", "CALDEIRARIA BÁSICA",
        "METROLOGIA APLICADA", "INTELIGÊNCIA ARTIFICIAL NA PROGRAMAÇÃO CNC"
    ],
    "Tecnologia da Informação": [
        "EXCEL BÁSICO", "EXCEL AVANÇADO", "EXCEL COMPLETO", "INFORMÁTICA BÁSICA",
        "IA GENERATIVA PARA PRODUTIVIDADE", "Microsoft Al-102 - Soluções em IA",
        "Microsoft AI-900 - Serviços de IA em Nuvem", "Google Cloud - Fundamentos de IA Generativa",
        "Google Cloud AI Foundations", "Google Cloud - IA Generativa em Nuvem",
        "ChatGPT - IA Aplicada à Programação", "Administração de Sistemas ServiceNow - CSA",
        "Google Antigravity - IA Generativa", "Microsoft AI Foundry - Agentes de IA",
        "Google Firebase e Gemini", "Programação em IA Generativa",
        "MARKETING DIGITAL COM IA", "PYTHON PARA ANÁLISE DE DADOS", 
        "POWER BI (DASHBOARDS)", "TÉCNICO EM DESENVOLVIMENTO DE SISTEMAS"
    ],
    "Eletroeletrônica": [
        "ELETRICISTA INSTALADOR", "COMANDOS ELÉTRICOS", "CLP - CONTROLADORES LÓGICOS",
        "INSTALAÇÕES ELÉTRICAS RESIDENCIAIS", "MANUTENÇÃO DE SISTEMAS FOTOVOLTAICOS",
        "IA APLICADA À DETECÇÃO DE ANOMALIAS EM MÁQUINAS"
    ],
    "Gestão e Logística": [
        "QUALIDADE", "ALMOXARIFE", "ASSISTENTE ADMINISTRATIVO",
        "ASSISTENTE DE RECURSOS HUMANOS", "LOGÍSTICA INTEGRADA", "GESTÃO DE ESTOQUES"
    ],
    "Automobilística": [
        "MECÂNICO DE AUTOMÓVEIS LEVES", "ELETRICISTA VEICULAR", "SISTEMAS DE INJEÇÃO ELETRÔNICA"
    ],
    "Manutenção e Lubrificação Industrial": [
        "IA NO MONITORAMENTO DA MANUTENÇÃO PREDITIVA",
        "DETECÇÃO A LASER E IA PARA LUBRIFICAÇÃO INDUSTRIAL"
    ]
}

# --- ESTILO CSS (Neumorfismo e Design 122) ---
st.markdown("""
    <style>
    .stApp { background-color: #e0e5ec; }
    .header-senai { 
        background: #ff0000; padding: 40px 0px; color: white; text-align: center; 
        width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw;
        box-shadow: 0px 10px 15px rgba(0,0,0,0.1); border-bottom: 4px solid #cc0000;
    }
    .header-senai h1 { font-size: 28px !important; margin: 0; font-weight: 800; color: white !important; }
    div.stButton > button { 
        background-color: #ff0000 !important; color: white !important; font-weight: bold !important; 
        height: 50px; border-radius: 15px; width: 100%; border: none;
        box-shadow: 6px 6px 12px #b8b9be, -6px -6px 12px #ffffff !important;
    }
    [data-testid="stForm"] { 
        background-color: #e0e5ec !important; border-radius: 30px !important; padding: 2rem !important; 
        box-shadow: 8px 8px 16px #bebebe, -8px -8px 16px #ffffff !important; border: none !important; 
    }
    .footer-custom { background-color: #ff0000; color: white; text-align: center; padding: 20px; margin-top: 50px; width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; }
    </style>
    """, unsafe_allow_html=True)

# --- GOOGLE SHEETS (Funções de Dados) ---
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
        return build("sheets", "v4", credentials=creds, cache_discovery=False)
    except: return None

def salvar_lead(dados):
    service = conectar_sheets()
    if service:
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        id_planilha = url.split("/d/")[1].split("/")[0]
        service.spreadsheets().values().append(
            spreadsheetId=id_planilha, range="A1", valueInputOption="RAW",
            insertDataOption="INSERT_ROWS", body={"values": [dados]}
        ).execute()
        return True
    return False

# --- BARRA LATERAL (Fachada e Info) ---
with st.sidebar:
    path_fachada = os.path.join("imagens", "fachada.png")
    if os.path.exists(path_fachada):
        st.image(path_fachada, caption="SENAI Guarulhos - Unidade 122")
    
    st.markdown("---")
    st.markdown("### 🏢 Sobre a Unidade")
    st.info("O SENAI 122 é referência em Metalmecânica e Tecnologia da Informação na região de Guarulhos.")
    
    # --- PAINEL ADM (Restaurado) ---
    st.markdown("---")
    with st.expander("🔐 Área Administrativa"):
        senha = st.text_input("Senha", type="password")
        if senha == st.secrets.get("admin_password", "senai122"):
            st.success("Acesso Liberado")
            if st.button("Visualizar Leads"):
                st.write("Conectando à base de dados...")
                # Aqui você pode adicionar a lógica de carregar o DataFrame da planilha

# --- CABEÇALHO ---
path_logo = os.path.join("imagens", "logo.png")
if os.path.exists(path_logo):
    logo_64 = get_base64_of_bin_file(path_logo)
    st.markdown(f'<div style="text-align: center; margin-bottom: -20px;"><img src="data:image/png;base64,{logo_64}" width="150"></div>', unsafe_allow_html=True)

st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS - UNIDADE 122</h1><p>Excelência em Formação Profissional</p></div>', unsafe_allow_html=True)

# --- FORMULÁRIO DE INTERESSE ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<br><h4 style='text-align: center; color: #333;'>Manifestação de Interesse em Cursos</h4>", unsafe_allow_html=True)
    
    area_sel = st.selectbox("Escolha a Área de Interesse:", ["Selecione..."] + sorted(list(DADOS_CURSOS_LOCAL.keys())))
    lista_cursos = sorted(DADOS_CURSOS_LOCAL[area_sel]) if area_sel != "Selecione..." else []
    curso_sel = st.selectbox("Escolha o Curso:", ["Aguardando Área..."] + lista_cursos, disabled=(area_sel == "Selecione..."))

    with st.form("form_registro", clear_on_submit=True):
        nome = st.text_input("Seu Nome Completo")
        email = st.text_input("Seu melhor E-mail")
        whats = st.text_input("WhatsApp para contato")
        obs = st.text_area("Alguma dúvida ou observação?")
        btn_enviar = st.form_submit_button("REGISTRAR MEU INTERESSE")

        if btn_enviar:
            if area_sel != "Selecione..." and nome and email and curso_sel != "Aguardando Área...":
                data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                if salvar_lead([nome, email, f"'{whats}", area_sel, curso_sel, obs, data_hora]):
                    st.success(f"Obrigado pelo interesse, {nome}!")
                    # --- MENSAGEM RESTAURADA ---
                    st.info("✅ Entraremos em contato com você assim que houver turmas abertas para o curso selecionado.")
                    st.balloons()
                else:
                    st.error("Erro técnico ao salvar. Tente novamente em instantes.")
            else:
                st.warning("Por favor, preencha todos os campos obrigatórios.")

# --- RODAPÉ ---
st.markdown('<div class="footer-custom">Copyright 2026 © SENAI Guarulhos 122 - Gestão Ricardo IT Master</div>', unsafe_allow_html=True)
