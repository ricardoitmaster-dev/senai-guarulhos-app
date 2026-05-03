import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Importações para o Scraping
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- CSS: ESTILO VITRIFICADO ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%); }
    .header-senai { 
        background: linear-gradient(90deg, #e3000f 0%, #ff4b4b 100%); 
        padding: 30px; border-radius: 20px; color: white; text-align: center; 
        box-shadow: 0 15px 25px -5px rgba(227, 0, 15, 0.4); margin-bottom: 20px;
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

# --- FUNÇÃO DE WEB SCRAPING COM TRATAMENTO DE ERRO MELHORADO ---
@st.cache_data(ttl=43200)
def buscar_cursos_dinamicos():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # Mapa reserva caso a conexão falhe
    mapa_fallback = {
        "Tecnologia da Informação": ["Excel Avançado", "IA Generativa", "Python", "Power BI"],
        "Eletroeletrônica": ["Eletricista Instalador", "Comandos Elétricos"],
        "Gestão": ["Assistente Administrativo", "Logística"]
    }
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get("https://www.sp.senai.br/cursos?unidade=122")
        
        # Espera curta para garantir que o conteúdo carregou
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Tenta localizar os cards ou nomes dos cursos no HTML
        # Ajustado para pegar o texto de forma mais ampla se as classes mudarem
        elementos_cursos = driver.find_elements(By.XPATH, "//div[contains(@class, 'card')]")
        
        mapa_real = {}
        for el in elementos_cursos:
            try:
                texto = el.text.split('\n')
                if len(texto) >= 2:
                    # Tenta identificar Área e Curso pela estrutura comum do SENAI
                    area = "Cursos SENAI" # Valor padrão se não identificar área
                    curso = texto[0]
                    
                    if area not in mapa_real: mapa_real[area] = []
                    if curso not in mapa_real[area]: mapa_real[area].append(curso)
            except: continue
            
        driver.quit()
        return mapa_real if mapa_real else mapa_fallback
    except:
        return mapa_fallback

# --- FUNÇÕES DE CONEXÃO GOOGLE (PRESERVADAS) ---
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

def ler_todos_leads():
    try:
        service = conectar_google_sheets()
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_id = url.split("/d/")[1].split("/")[0]
        result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="A1:Z2000").execute()
        values = result.get("values", [])
        return pd.DataFrame(values[1:], columns=values[0]) if values else pd.DataFrame()
    except: return pd.DataFrame()

# --- INTERFACE VISUAL ---
path_logo = os.path.join("imagens", "logo.png")
if os.path.exists(path_logo):
    c_logo1, c_logo2, c_logo3 = st.columns([2, 1, 2])
    with c_logo2: st.image(Image.open(path_logo), width=160)

st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Registro de Interesse</p></div>', unsafe_allow_html=True)

path_fachada = os.path.join("imagens", "fachada.jpg")
if os.path.exists(path_fachada):
    c_fac1, c_fac2, c_fac3 = st.columns([1, 4, 1])
    with c_fac2: st.image(Image.open(path_fachada), use_container_width=True)

# --- CARREGAMENTO DOS CURSOS ---
with st.spinner("Sincronizando cursos..."):
    dados_cursos = buscar_cursos_dinamicos()

col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
with col_f2:
    st.markdown("<h3 style='text-align: center;'>📋 Escolha seu Curso</h3>", unsafe_allow_html=True)
    area_escolhida = st.selectbox("1. Selecione a Área Profissional:", ["Selecione..."] + sorted(list(dados_cursos.keys())))
    opcoes_cursos = sorted(dados_cursos[area_escolhida]) if area_escolhida != "Selecione..." else []
    curso_escolhido = st.selectbox("2. Selecione o Curso:", ["Aguardando área..."] + opcoes_cursos, disabled=(area_escolhida == "Selecione..."))

    with st.form("form_interessado", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("Seu E-mail")
        whats = st.text_input("Seu WhatsApp")
        btn_enviar = st.form_submit_button("REGISTRAR MEU INTERESSE")

    if btn_enviar:
        if area_escolhida != "Selecione..." and curso_escolhido != "Aguardando área..." and nome and email:
            data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            if salvar_novo_lead([nome, email, whats, area_escolhida, curso_escolhido, data_atual]):
                st.success(f"✅ Olá {nome}! Registro concluído.")
                st.balloons()
            else: st.error("Erro ao salvar os dados.")
        else: st.warning("⚠️ Preencha todos os campos.")

# --- ADM ---
st.sidebar.markdown("## 🔒 Área Administrativa")
senha = st.sidebar.text_input("Senha", type="password")
if senha == "Celina2610$$":
    st.sidebar.success("Acesso Liberado")
    if st.sidebar.checkbox("Visualizar Interessados"):
        df_leads = ler_todos_leads()
        if not df_leads.empty:
            st.write("### Relatório de Leads")
            st.dataframe(df_leads)
            csv = df_leads.to_csv(index=False).encode('utf-8-sig')
            st.sidebar.download_button("📥 Baixar CSV", csv, "leads_senai.csv", "text/csv")
