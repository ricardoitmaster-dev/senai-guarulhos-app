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

# --- DICIONÁRIO DE CURSOS (Sua lista incorporada) ---
DADOS_CURSOS_LOCAL = {
    "Metalmecânica": [
        "MECÂNICO DE USINAGEM", "PROGRAMADOR E OPERADOR DE CNC", "SOLDADOR MAG",
        "SOLDADOR TIG", "MECÂNICO DE MANUTENÇÃO", "CALDEIRARIA BÁSICA",
        "METROLOGIA APLICADA", "INTELIGÊNCIA ARTIFICIAL NA PROGRAMAÇÃO CNC"
    ],
    "Tecnologia da Informação": [
        "EXCEL BÁSICO", "INFORMÁTICA BÁSICA", "EXCEL COMPLETO",
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
        "PYTHON PARA ANÁLISE DE DADOS", "POWER BI (DASHBOARDS)", "TÉCNICO EM DESENVOLVIMENTO DE SISTEMAS"
    ],
    "Eletroeletrônica": [
        "ELETRICISTA INSTALADOR", "COMANDOS ELÉTRICOS", "CLP - CONTROLADORES LÓGICOS",
        "INSTALAÇÕES ELÉTRICAS RESIDENCIAIS", "MANUTENÇÃO DE SISTEMAS FOTOVOLTAICOS",
        "INTELIGÊNCIA ARTIFICIAL APLICADO À DETECÇÃO DE ANOMALIAS EM MÁQUINAS"
    ],
    "Gestão e Logística": [
        "QUALIDADE", "ALMOXARIFE", "ASSISTENTE ADMINISTRATIVO",
        "ASSISTENTE DE RECURSOS HUMANOS", "LOGÍSTICA INTEGRADA", "GESTÃO DE ESTOQUES"
    ],
    "Automobilística": [
        "MECÂNICO DE AUTOMÓVEIS LEVES", "ELETRICISTA VEICULAR", "SISTEMAS DE INJEÇÃO ELETRÔNICA"
    ],
    "Manutenção e Lubrificação Industrial": [
        "INTELIGÊNCIA ARTIFICIAL NO MONITORAMENTO DA MANUTENÇÃO PREDITIVA",
        "DETECÇÃO A LASER E INTELIGÊNCIA ARTIFICIAL PARA LUBRIFICAÇÃO INDUSTRIAL"
    ]
}

# --- ESTILO CSS (Design Original) ---
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

# --- GOOGLE SHEETS ---
def conectar_sheets():
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

def carregar_dados():
    service = conectar_sheets()
    url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    sheet_id = url.split("/d/")[1].split("/")[0]
    result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="A1:G1000").execute()
    values = result.get('values', [])
    return pd.DataFrame(values[1:], columns=values[0]) if values else None

def salvar_lead(dados):
    service = conectar_sheets()
    url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    sheet_id = url.split("/d/")[1].split("/")[0]
    service.spreadsheets().values().append(
        spreadsheetId=sheet_id, range="A1", valueInputOption="RAW",
        insertDataOption="INSERT_ROWS", body={"values": [dados]}
    ).execute()
    return True

# --- SIDEBAR (ADM e Fachada Lateral) ---
with st.sidebar:
    path_fachada_side = os.path.join("imagens", "fachada.png")
    if os.path.exists(path_fachada_side):
        st.image(path_fachada_side, caption="Unidade 122")
    
    st.markdown("---")
    with st.expander("🔐 Área Administrativa"):
        senha_input = st.text_input("Senha", type="password")
        if senha_input == st.secrets["admin_password"]:
            st.success("Acesso Liberado")
            ver_leads = st.checkbox("Visualizar Relatório de Leads")
        else:
            ver_leads = False

# --- CONTEÚDO PRINCIPAL ---

# Cabeçalho
st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Registro de Interesse Profissional</p></div>', unsafe_allow_html=True)

# Imagem da Fachada Principal (Restaurada abaixo da tarja)
path_fachada_main = os.path.join("imagens", "fachada.jpg")
if os.path.exists(path_fachada_main):
    st.image(path_fachada_main, use_container_width=True)

# Exibição do Relatório (Tabela ADM)
if ver_leads:
    st.markdown("### 📊 Relatório de Interessados")
    df = carregar_dados()
    if df is not None:
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Nenhum dado encontrado na planilha.")
    st.markdown("---")

# Formulário
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<br><h4 style='text-align: center;'>Cadastro de Interessado</h4>", unsafe_allow_html=True)
    
    area = st.selectbox("Selecione a Área:", ["Selecione..."] + sorted(list(DADOS_CURSOS_LOCAL.keys())))
    lista = sorted(DADOS_CURSOS_LOCAL[area]) if area != "Selecione..." else []
    curso = st.selectbox("Selecione o Curso:", ["Aguardando Área..."] + lista, disabled=(area == "Selecione..."))

    with st.form("registro_form", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp")
        obs = st.text_area("Dúvidas ou Observações")
        submit = st.form_submit_button("REGISTRAR INTERESSE")

        if submit:
            if area != "Selecione..." and nome and email and curso != "Aguardando Área...":
                data_h = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                if salvar_lead([nome, email, f"'{whats}", area, curso, obs, data_h]):
                    st.success(f"Obrigado pelo registro, {nome}!")
                    st.info("✅ Entraremos em contato com você assim que houver turmas abertas para o curso selecionado.")
                    st.balloons()
                else: st.error("Erro ao salvar. Tente novamente.")
            else: st.warning("Preencha todos os campos obrigatórios.")

# Rodapé
st.markdown('<div class="footer-custom">Copyright 2026 © SENAI Guarulhos 122 - Ricardo IT Master</div>', unsafe_allow_html=True)
