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

# --- CSS: IDENTIDADE VISUAL SENAI (CORES INSTITUCIONAIS) ---
st.markdown("""
    <style>
    /* Fundo cinza bem claro, padrão do portal */
    .stApp { background-color: #f4f4f4; }
    
    /* Cabeçalho com o Vermelho SENAI exato */
    .header-senai { 
        background-color: #ff0000; 
        padding: 40px; border-radius: 0px 0px 20px 20px; color: white; text-align: center; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 30px;
        font-family: 'Arial Black', Gadget, sans-serif;
    }
    
    /* Formulário com bordas e cores limpas */
    [data-testid="stForm"] {
        background-color: #ffffff !important;
        border-radius: 8px !important;
        border: 1px solid #ddd !important;
        padding: 2.5rem !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
    }
    
    /* Botão Vermelho SENAI com hover escurecido */
    div.stButton > button { 
        background-color: #ff0000 !important;
        color: white !important; 
        font-weight: bold !important; 
        height: 55px !important;
        border-radius: 4px !important; 
        width: 100% !important;
        border: none !important;
        text-transform: uppercase;
    }
    div.stButton > button:hover {
        background-color: #cc0000 !important;
        border: none !important;
    }

    /* Mensagem de sucesso acompanhando o padrão */
    .sucesso-msg {
        background-color: #ffffff;
        color: #333;
        padding: 25px;
        border-radius: 8px;
        border-left: 10px solid #ff0000;
        text-align: center;
        margin-top: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Ajuste de labels */
    label { color: #333 !important; font-weight: 600 !important; }
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
        params = {'api_key': api_key, 'url': url_alvo, 'render': 'true', 'wait_until': 'networkidle'}
        response = requests.get('http://api.scraperapi.com', params=params, timeout=90)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            cards = soup.select('div[class*="card-curso"]') or soup.select('.item-lista-curso')
            
            if not cards: return mapa_fallback
            
            mapa_real = {}
            for card in cards:
                try:
                    area_elem = card.select_one('.area-tematica, .txt-area, .tag-area')
                    titulo_elem = card.select_one('.titulo-curso, h2, .nome-curso')
                    
                    if area_elem and titulo_elem:
                        area = area_elem.get_text(strip=True).title()
                        titulo = titulo_elem.get_text(strip=True).upper()
                        if area not in mapa_real: mapa_real[area] = []
                        if titulo not in mapa_real[area]: mapa_real[area].append(titulo)
                except: continue
            return mapa_real if len(mapa_real) > 0 else mapa_fallback
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
            spreadsheetId=sheet_id, range="A1", valueInputOption="RAW",
            insertDataOption="INSERT_ROWS", body={"values": [lista_dados]}
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

# --- INTERFACE ---
# Logo no topo
path_logo = os.path.join("imagens", "logo.png")
try:
    if os.path.exists(path_logo):
        c_logo1, c_logo2, c_logo3 = st.columns([2, 1, 2])
        with c_logo2: st.image(Image.open(path_logo), width=180)
except: pass

# Cabeçalho Vermelho
st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Registro de Interesse</p></div>', unsafe_allow_html=True)

# Fachada tratada para evitar erro de imagem quebrada
path_fachada = os.path.join("imagens", "fachada.jpg")
try:
    if os.path.exists(path_fachada):
        c_fac1, c_fac2, c_fac3 = st.columns([1, 6, 1])
        with c_fac2: st.image(Image.open(path_fachada), use_container_width=True)
except: pass

with st.spinner("Carregando cursos..."):
    dados_cursos = buscar_cursos_dinamicos()

# Layout do Formulário
col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
with col_f2:
    st.markdown("<h3 style='text-align: center; color: #333;'>📋 Formulário de Inscrição</h3>", unsafe_allow_html=True)
    
    area_escolhida = st.selectbox("Selecione a Área Profissional:", ["Selecione..."] + sorted(list(dados_cursos.keys())))
    opcoes_cursos = sorted(dados_cursos[area_escolhida]) if area_escolhida != "Selecione..." else []
    curso_escolhido = st.selectbox("Selecione o Curso de Interesse:", ["Aguardando área..."] + opcoes_cursos, disabled=(area_escolhida == "Selecione..."))

    with st.form("form_interessado", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp (com DDD)")
        sugestao = st.text_area("Sugestão de outro curso ou comentário:")
        btn_enviar = st.form_submit_button("ENVIAR INTERESSE")

    if btn_enviar:
        if area_escolhida != "Selecione..." and nome and email:
            data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            if salvar_novo_lead([nome, email, whats, area_escolhida, curso_escolhido, sugestao, data_atual]):
                st.markdown(f"""
                    <div class="sucesso-msg">
                        <h3>Olá, {nome}!</h3>
                        <p>Seu interesse no curso <b>{curso_escolhido}</b> foi registrado.</p>
                        <p>Entraremos em contato assim que as vagas forem abertas.</p>
                    </div>
                """, unsafe_allow_html=True)
                st.balloons()
        else: st.warning("Por favor, preencha todos os campos obrigatórios.")

# --- ADMIN ---
st.sidebar.markdown("## 🔒 Painel Administrativo")
senha = st.sidebar.text_input("Senha de Acesso", type="password")
if senha == "Celina2610$$":
    if st.sidebar.checkbox("Visualizar Interessados"):
        df = ler_todos_leads()
        if not df.empty: st.dataframe(df)
