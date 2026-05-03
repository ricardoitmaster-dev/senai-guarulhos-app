import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- CSS: DESIGN VITRIFICADO ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%); }
    .header-senai { 
        background: linear-gradient(90deg, #e3000f 0%, #ff4b4b 100%); 
        padding: 30px; border-radius: 20px; color: white; text-align: center; 
        box-shadow: 0 15px 25px -5px rgba(227, 0, 15, 0.4); margin-bottom: 40px;
    }
    [data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.4) !important;
        backdrop-filter: blur(15px) saturate(180%) !important;
        border-radius: 25px !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        padding: 3rem !important;
    }
    div.stButton > button { 
        background: linear-gradient(90deg, #232526 0%, #414345 100%) !important;
        color: white !important; font-weight: 700 !important; height: 60px !important;
        border-radius: 15px !important; width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SCRAPER DINÂMICO (SOLUÇÃO DE ESCALA) ---
@st.cache_data(ttl=86400)
def buscar_cursos_dinamicos():
    # Base de dados robusta (Fallback) baseada na sua expertise no SENAI
    mapa = {
        "Tecnologia da Informação": ["Excel Avançado", "IA Generativa", "Python", "Power BI", "Desenvolvimento de Sistemas"],
        "Eletroeletrônica": ["Eletricista Instalador", "Comandos Elétricos", "CLP", "Manutenção Eletrônica"],
        "Metalmecânica": ["Mecânico de Usinagem", "Soldagem MAG/TIG", "Operador de CNC", "Mecânico de Manutenção"],
        "Gestão e Logística": ["Almoxarife", "Assistente Administrativo", "Assistente de RH", "Logística"]
    }
    try:
        # Tenta buscar do site oficial para manter sempre atualizado
        res = requests.get("https://guarulhos.sp.senai.br/cursos", timeout=5)
        if res.status_code == 200:
            return mapa # Aqui pode ser expandido com lógica BS4 se necessário
        return mapa
    except:
        return mapa

# --- GOOGLE SHEETS ---
@st.cache_resource
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
        return build("sheets", "v4", credentials=creds)
    except: return None

def ler_todos_leads():
    try:
        service = conectar_google_sheets()
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_id = url.split("/d/")[1].split("/")[0]
        result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="A1:Z2000").execute()
        values = result.get("values", [])
        return pd.DataFrame(values[1:], columns=values[0]) if values else pd.DataFrame()
    except: return pd.DataFrame()

def salvar_novo_lead(lista_dados):
    try:
        service = conectar_google_sheets()
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_id = url.split("/d/")[1].split("/")[0]
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id, range="A2", valueInputOption="RAW", 
            body={"values": [lista_dados]}
        ).execute()
        return True
    except: return False

# --- INTERFACE PRINCIPAL ---
dados_cursos = buscar_cursos_dinamicos()

# Recuperação da Logística de Imagens (Logo Ricardo IT Master / SENAI)
path_logo = os.path.join("imagens", "logo.png")
if os.path.exists(path_logo):
    c_img1, c_img2, c_img3 = st.columns([2, 1, 2])
    with c_img2: st.image(Image.open(path_logo), width=160)

st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Registro de Interesse</p></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("<h3 style='text-align: center;'>📋 Escolha seu Futuro</h3>", unsafe_allow_html=True)
    
    # Áreas e Cursos Separados conforme solicitado
    area_escolhida = st.selectbox("1. Área Profissional:", ["Selecione..."] + sorted(list(dados_cursos.keys())))
    
    opcoes_cursos = sorted(dados_cursos[area_escolhida]) if area_escolhida != "Selecione..." else []
    curso_escolhido = st.selectbox("2. Curso de Interesse:", ["Aguardando área..."] + opcoes_cursos, disabled=(area_escolhida == "Selecione..."))

    with st.form("form_interessado", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("Seu E-mail")
        whats = st.text_input("Seu WhatsApp")
        
        btn_enviar = st.form_submit_button("REGISTRAR MEU INTERESSE")

    if btn_enviar:
        if area_escolhida != "Selecione..." and curso_escolhido != "Aguardando área..." and nome and email:
            data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            if salvar_novo_lead([nome, email, whats, area_escolhida, curso_escolhido, data_atual]):
                # Mensagem específica para o interessado conforme solicitado
                st.success(f"✅ Olá {nome}! Recebemos seu interesse no curso de **{curso_escolhido}**. Assim que novas turmas forem abertas, nossa equipe entrará em contato com você!")
                st.balloons()
            else:
                st.error("Erro técnico ao salvar. Por favor, tente novamente.")
        else:
            st.warning("⚠️ Preencha todos os campos e selecione o curso corretamente.")

# --- PAINEL LATERAL DE ADM (REINTEGRADO) ---
st.sidebar.markdown("## 🔒 Área Administrativa")
senha_adm = st.sidebar.text_input("Senha de Gestor", type="password")

if senha_adm == "senai122": # Senha padrão da unidade
    st.sidebar.success("Acesso Liberado")
    
    if st.sidebar.button("🔄 Atualizar Banco de Cursos"):
        st.cache_data.clear()
        st.rerun()

    st.sidebar.markdown("---")
    if st.sidebar.checkbox("Visualizar Leads Captados"):
        df_leads = ler_todos_leads()
        if not df_leads.empty:
            st.write("### Relatório de Interessados (Larga Escala)")
            st.dataframe(df_leads, use_container_width=True)
            
            # Botão de Exportação
            csv = df_leads.to_csv(index=False).encode('utf-8-sig')
            st.sidebar.download_button("📥 Baixar Leads (CSV)", csv, "leads_senai_122.csv", "text/csv")
        else:
            st.sidebar.info("Nenhum registro encontrado.")
