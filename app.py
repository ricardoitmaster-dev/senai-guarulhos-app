import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64
import urllib.parse
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- FUNÇÃO DE LIMPEZA TOTAL ---
def reset_geral_callback():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# Função para converter imagem local em base64
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

# --- CSS: ESTILO 3D E RODAPÉ OFICIAL ---
st.markdown("""
    <style>
    .stApp { background-color: #e0e5ec; }
    .logo-container { position: relative; z-index: 10; margin-bottom: -20px; display: flex; justify-content: center; padding-top: 10px; }
    .moldura-3d-ajustada { display: block; border-radius: 25px; box-shadow: 10px 10px 20px #bebebe, -10px -10px 20px #ffffff; border: 4px solid #e0e5ec; overflow: hidden; margin: 25px auto; width: 100%; }
    .moldura-3d-ajustada img { border-radius: 20px; display: block; width: 100%; height: auto; }
    .header-senai { background: #ff0000; padding: 40px 0px 25px 0px; color: white; text-align: center; width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; z-index: 5; box-shadow: 0px 10px 15px rgba(0,0,0,0.1); border-bottom: 4px solid #cc0000; }
    .header-senai h1 { font-size: 28px !important; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); font-weight: 800; color: white !important; }
    
    .btn-whatsapp {
        display: inline-flex; align-items: center; justify-content: center;
        background-color: #25D366 !important; color: white !important;
        padding: 15px 25px; border-radius: 12px; text-decoration: none;
        font-weight: bold; font-size: 18px; box-shadow: 4px 4px 10px rgba(0,0,0,0.2);
        margin-top: 15px; width: 100%; transition: 0.3s;
    }
    .btn-whatsapp:hover { background-color: #128C7E !important; transform: scale(1.02); }

    .footer-container { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; margin-top: 50px; font-family: sans-serif; }
    .footer-container a { text-decoration: none !important; color: inherit !important; }
    .footer-container a:hover { opacity: 0.8 !important; }
    .footer-top { background-color: #f4f4f4; padding: 15px 0; text-align: center; display: flex; justify-content: center; gap: 20px; font-size: 12px; font-weight: bold; color: #444; }
    .footer-social { background-color: #ff0000; padding: 15px 0; text-align: center; color: white; display: flex; justify-content: center; gap: 25px; font-size: 20px; }
    .footer-content { background-color: #b5121b; padding: 40px 10% 20px 10%; color: white; display: grid; grid-template-columns: 1fr 1fr; gap: 50px; }
    .footer-bottom { background-color: #b5121b; padding: 20px 0; border-top: 1px solid rgba(255,255,255,0.2); display: flex; justify-content: center; gap: 30px; font-size: 13px; font-weight: bold; color: white !important; }
    
    label, [data-testid="stWidgetLabel"] p { color: #000000 !important; font-weight: 600 !important; }
    div.stButton > button { background-color: #ff0000 !important; color: #ffffff !important; font-weight: bold !important; height: 55px !important; border-radius: 15px !important; width: 100% !important; border: none !important; box-shadow: 6px 6px 12px #b8b9be, -6px -6px 12px #ffffff !important; }
    [data-testid="stForm"] { background-color: #e0e5ec !important; border-radius: 30px !important; padding: 2rem !important; box-shadow: inset 8px 8px 16px #bebebe, inset -8px -8px 16px #ffffff !important; border: none !important; }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    """, unsafe_allow_html=True)

# --- DADOS ATUALIZADOS ---
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
    "Gestão e Logística": ["ALMOXARIFE", "ASSISTENTE ADMINISTRATIVO", "LOGÍSTICA INTEGRADA"]
}

# --- FUNÇÕES GOOGLE SHEETS ---
def conectar_google_sheets():
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
    except Exception: return None

def salvar_novo_lead(lista_dados):
    try:
        service = conectar_google_sheets()
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_id = url.split("/d/")[1].split("/")[0]
        service.spreadsheets().values().append(spreadsheetId=sheet_id, range="A1", valueInputOption="RAW", insertDataOption="INSERT_ROWS", body={"values": [lista_dados]}).execute()
        return True
    except Exception: return False

def ler_todos_leads():
    try:
        service = conectar_google_sheets()
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_id = url.split("/d/")[1].split("/")[0]
        result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="A1:Z2000").execute()
        values = result.get("values", [])
        return pd.DataFrame(values[1:], columns=values[0]) if values else pd.DataFrame()
    except Exception: return pd.DataFrame()

# --- INTERFACE ---
path_logo = os.path.join("imagens", "logo.png")
path_fachada = os.path.join("imagens", "fachada.jpg")

if os.path.exists(path_logo):
    logo_base = get_base64_of_bin_file(path_logo)
    st.markdown(f'<div class="logo-container"><div class="moldura-3d-ajustada" style="width:150px;"><img src="data:image/png;base64,{logo_base}"></div></div>', unsafe_allow_html=True)

st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Registro de Interesse Profissional</p></div>', unsafe_allow_html=True)

if os.path.exists(path_fachada):
    fachada_base = get_base64_of_bin_file(path_fachada)
    st.markdown(f'<div class="moldura-3d-ajustada"><img src="data:image/jpeg;base64,{fachada_base}"></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Reset amigável para selectbox
    area_sel = st.selectbox("Área Profissional:", ["Selecione..."] + sorted(list(DADOS_CURSOS.keys())), key="area_input")
    opcoes = sorted(DADOS_CURSOS[area_sel]) if area_sel != "Selecione..." else []
    curso_sel = st.selectbox("Curso:", ["Aguardando área..."] + opcoes, disabled=(area_sel == "Selecione..."), key="curso_input")

    with st.form("form_registro", clear_on_submit=True):
        nome = st.text_input("Nome Completo", key="nome_input")
        email = st.text_input("E-mail", key="email_input")
        whats = st.text_input("WhatsApp", key="whats_input")
        obs = st.text_area("Observações", key="obs_input")
        enviar = st.form_submit_button("REGISTRAR AGORA")

        if enviar:
            if area_sel != "Selecione..." and nome and email:
                data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                if salvar_novo_lead([nome, email, f"'{whats}", area_sel, curso_sel, obs, data_atual]):
                    st.success(f"Excelente, {nome}! Registramos seu interesse.")
                    st.balloons()
                    
                    # Lógica do WhatsApp Mantida
                    numero_destino = "551133220050" 
                    mensagem_texto = f"Olá! Acabei de registrar interesse no curso de *{curso_sel}*. Meu nome é *{nome}*."
                    texto_url = urllib.parse.quote(mensagem_texto)
                    link_wa = f"https://wa.me/{numero_destino}?text={texto_url}"
                    st.markdown(f'<a href="{link_wa}" target="_blank" class="btn-whatsapp"><i class="fab fa-whatsapp" style="margin-right:10px;"></i> ENVIAR PELO WHATSAPP</a>', unsafe_allow_html=True)
                else: st.error("Erro ao salvar.")
            else: st.error("Preencha os campos obrigatórios.")

# --- RODAPÉ ORIGINAL (VOLTOU!) ---
footer_html = """
<div class="footer-container">
    <div class="footer-top">
        <a href="https://www.sp.senai.br/fale-conosco" target="_blank">FALE CONOSCO</a>
        <a href="https://www.sp.senai.br/trabalhe-conosco" target="_blank">TRABALHE CONOSCO</a>
        <a href="https://www.sp.senai.br/ouvidoria" target="_blank">OUVIDORIA</a>
        <a href="https://www.sp.senai.br/institucional/politica-de-privacidade" target="_blank">POLÍTICA DE PRIVACIDADE</a>
        <a href="https://www.sp.senai.br/a-lgpd-no-senai-sp" target="_blank">A LGPD NO SENAI-SP</a>
    </div>
    <div class="footer-social">
        <a href="https://www.facebook.com/senaisp" target="_blank"><i class="fab fa-facebook-f"></i></a>
        <a href="https://twitter.com/senaisp" target="_blank"><i class="fab fa-twitter"></i></a>
        <a href="https://www.youtube.com/senaisp" target="_blank"><i class="fab fa-youtube"></i></a>
        <a href="https://www.linkedin.com/school/senai-sp/" target="_blank"><i class="fab fa-linkedin-in"></i></a>
        <a href="https://www.instagram.com/senaisp/" target="_blank"><i class="fab fa-instagram"></i></a>
        <a href="https://api.whatsapp.com/send?phone=551133220050" target="_blank"><i class="fab fa-whatsapp"></i></a>
    </div>
    <div class="footer-content">
        <div>
            <h4>EDIFÍCIO SEDE FIESP</h4>
            <p>Av. Paulista, 1313, São Paulo/SP</p>
            <p>CEP 01311-923</p>
        </div>
        <div>
            <h4>CENTRAL DE RELACIONAMENTO</h4>
            <p><a href="tel:1133220050">(11) 3322-0050</a> (Telefone/WhatsApp)</p>
            <p><a href="tel:08000551000">0800-055-1000</a> (Interior de SP, somente fixo)</p>
        </div>
    </div>
    <div class="footer-bottom">
        <a href="https://www.sp.senai.br/o-senai" target="_blank">O SENAI</a>
        <a href="https://www.sp.senai.br/perguntas-frequentes" target="_blank">PERGUNTAS FREQUENTES</a>
        <a href="https://www.sp.senai.br/fale-conosco" target="_blank">FALE CONOSCO</a>
        <a href="https://transparencia.sp.senai.br/" target="_blank">TRANSPARÊNCIA</a>
        <a href="https://www.sp.senai.br/para-a-sua-empresa" target="_blank">PARA A SUA EMPRESA</a>
    </div>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)

# --- ÁREA ADMINISTRATIVA ---
with st.sidebar:
    st.markdown("---")
    st.subheader("🔒 Área Administrativa")
    senha_mestra = st.secrets["auth"]["admin_password"] if "auth" in st.secrets else ""
    senha_digitada = st.text_input("Senha", type="password", key="senha_admin_input")

    if senha_digitada == senha_mestra and senha_mestra != "":
        st.success("Acesso Liberado")
        if st.checkbox("Ver Leads"):
            st.dataframe(ler_todos_leads())
        
        if st.button("Sair / Limpar Tudo", on_click=reset_geral_callback):
            pass # O rerun está dentro da função de callback agora
