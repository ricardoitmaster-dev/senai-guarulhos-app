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

# --- DICIONÁRIO DE CURSOS (Lista Fixa e Atualizada) ---
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

# --- ESTILO CSS ---
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

# --- FUNÇÕES GOOGLE SHEETS ---
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

def carregar_dados_adm():
    service = conectar_sheets()
    if service:
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        id_planilha = url.split("/d/")[1].split("/")[0]
        result = service.spreadsheets().values().get(spreadsheetId=id_planilha, range="A1:G1000").execute()
        values = result.get('values', [])
        if values:
            return pd.DataFrame(values[1:], columns=values[0])
    return None

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

# --- BARRA LATERAL ---
with st.sidebar:
    path_logo_side = os.path.join("imagens", "logo.png")
    if os.path.exists(path_logo_side):
        st.image(path_logo_side, width=150)
    st.markdown("### 🏢 Unidade 122")
    st.info("Portal de captação de interesse para novos treinamentos.")
    
    st.markdown("---")
    with st.expander("🔐 Área Administrativa"):
        senha_input = st.text_input("Senha", type="password")
        # Comparação com o segredo criptografado nos Secrets
        if senha_input == st.secrets["admin_password"]:
            st.success("Acesso Liberado")
            ver_relatorio = st.checkbox("Visualizar Tabela de Leads")
        else:
            ver_relatorio = False

# --- TELA PRINCIPAL ---

# 1. Tarja Vermelha
st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Registro de Interesse Profissional</p></div>', unsafe_allow_html=True)

# 2. Imagem da Fachada (Abaixo da tarja)
path_fachada = os.path.join("imagens", "fachada.jpg")
if os.path.exists(path_fachada):
    st.image(path_fachada, use_column_width=True, caption="Unidade 122 - Guarulhos")

# 3. Lógica do Relatório ADM (Se ativado na lateral)
if ver_relatorio:
    st.markdown("### 📊 Relatório de Interessados")
    df = carregar_dados_adm()
    if df is not None:
        st.dataframe(df, use_container_width=True)
    else:
        st.error("Não foi possível carregar os dados da planilha.")
    st.markdown("---")

# 4. Formulário
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<br><h4 style='text-align: center; color: #333;'>Cadastro de Candidato</h4>", unsafe_allow_html=True)
    
    area_sel = st.selectbox("Área Profissional:", ["Selecione..."] + sorted(list(DADOS_CURSOS_LOCAL.keys())))
    lista_c = sorted(DADOS_CURSOS_LOCAL[area_sel]) if area_sel != "Selecione..." else []
    curso_sel = st.selectbox("Curso de Interesse:", ["Aguardando Área..."] + lista_c, disabled=(area_sel == "Selecione..."))

    with st.form("form_registro", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp")
        obs = st.text_area("Observações Adicionais")
        enviar = st.form_submit_button("REGISTRAR INTERESSE")

        if enviar:
            if area_sel != "Selecione..." and nome and email and curso_sel != "Aguardando Área...":
                data_h = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                if salvar_lead([nome, email, f"'{whats}", area_sel, curso_sel, obs, data_h]):
                    st.success(f"Registro realizado com sucesso, {nome}!")
                    st.info("✅ Entraremos em contato com você assim que houver turmas abertas para o curso selecionado.")
                    st.balloons()
                else:
                    st.error("Erro ao salvar dados. Verifique a planilha.")
            else:
                st.warning("Preencha todos os campos antes de enviar.")

# --- RODAPÉ ---
st.markdown('<div class="footer-custom">Copyright 2026 © SENAI Guarulhos 122 - Ricardo IT Master</div>', unsafe_allow_html=True)
