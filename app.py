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

# --- CSS: ESTILO PROFISSIONAL ---
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
    .sucesso-msg {
        background-color: #d4edda;
        color: #155724;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #c3e6cb;
        text-align: center;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SCRAPING DINÂMICO ---
@st.cache_data(ttl=43200)
def buscar_cursos_dinamicos():
    api_key = "3e14f4393c5a034104b37c071a0d021f" 
    url_alvo = "https://www.sp.senai.br/cursos?unidade=122"
    
    mapa_fallback = {
        "Tecnologia da Informação": ["Excel Avançado", "IA Generativa", "Python", "Power BI"],
        "Eletroeletrônica": ["Eletricista Instalador", "Comandos Elétricos"],
        "Gestão e Logística": ["Almoxarife", "Assistente Administrativo"]
    }

    try:
        params = {'api_key': api_key, 'url': url_alvo, 'render': 'true'}
        response = requests.get('http://api.scraperapi.com', params=params, timeout=60)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            cards = soup.find_all(class_='card-curso')
            if not cards: return mapa_fallback
            
            mapa_real = {}
            for card in cards:
                try:
                    area = card.find(class_='area-tematica').get_text(strip=True)
                    titulo = card.find(class_='titulo-curso').get_text(strip=True)
                    if area not in mapa_real: mapa_real[area] = []
                    if titulo not in mapa_real[area]: mapa_real[area].append(titulo)
                except: continue
            return mapa_real if mapa_real else mapa_fallback
        return mapa_fallback
    except:
        return mapa_fallback

# --- INTEGRAÇÃO GOOGLE SHEETS ---
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
    except: return None

def salvar_novo_lead(lista_dados):
    try:
        service = conectar_google_sheets()
        if service is None: return False
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_id = url.split("/d/")[1].split("/")[0]
        
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range="A1", 
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
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

# --- INTERFACE: LOGO E CABEÇALHO ---
path_logo = os.path.join("imagens", "logo.png")
try:
    if os.path.exists(path_logo):
        c_logo1, c_logo2, c_logo3 = st.columns([2, 1, 2])
        with c_logo2: st.image(Image.open(path_logo), width=160)
except: pass

st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Registro de Interesse</p></div>', unsafe_allow_html=True)

# --- IMAGEM DA FACHADA (REINSERIDA COM TRATAMENTO DE ERRO) ---
path_fachada = os.path.join("imagens", "fachada.jpg")
try:
    if os.path.exists(path_fachada):
        c_fac1, c_fac2, c_fac3 = st.columns([1, 6, 1]) # Coluna central maior para a fachada
        with c_fac2: 
            img_fachada = Image.open(path_fachada)
            st.image(img_fachada, use_container_width=True, caption="SENAI Hermenegildo Parente - Guarulhos")
except Exception as e:
    # Se der erro, não exibe nada e não quebra o app
    pass

with st.spinner("Sincronizando cursos..."):
    dados_cursos = buscar_cursos_dinamicos()

col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
with col_f2:
    st.markdown("<h3 style='text-align: center;'>📋 Formulário de Inscrição</h3>", unsafe_allow_html=True)
    
    area_escolhida = st.selectbox("Área Profissional:", ["Selecione..."] + sorted(list(dados_cursos.keys())))
    opcoes_cursos = sorted(dados_cursos[area_escolhida]) if area_escolhida != "Selecione..." else []
    curso_escolhido = st.selectbox("Curso de Interesse:", ["Aguardando área..."] + opcoes_cursos, disabled=(area_escolhida == "Selecione..."))

    with st.form("form_interessado", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp")
        sugestao = st.text_area("Sugestão de outro curso ou comentário:")
        btn_enviar = st.form_submit_button("REGISTRAR INTERESSE")

    if btn_enviar:
        if area_escolhida != "Selecione..." and nome and email:
            data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            if salvar_novo_lead([nome, email, whats, area_escolhida, curso_escolhido, sugestao, data_atual]):
                st.markdown(f"""
                    <div class="sucesso-msg">
                        <h3>Obrigado, {nome}!</h3>
                        <p>Seu interesse no curso <b>{curso_escolhido}</b> foi registrado com sucesso.</p>
                        <p>Assim que este curso for aberto, entraremos em contato imediatamente!</p>
                    </div>
                """, unsafe_allow_html=True)
                st.balloons()
        else: st.warning("Por favor, preencha o nome, e-mail e selecione a área de interesse.")

# --- ADMINISTRAÇÃO ---
st.sidebar.markdown("## 🔒 Admin")
senha = st.sidebar.text_input("Senha", type="password")
if senha == "Celina2610$$":
    if st.sidebar.checkbox("Ver Leads"):
        df = ler_todos_leads()
        if not df.empty: st.dataframe(df)
