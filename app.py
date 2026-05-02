import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- CSS: O TOQUE VITRIFICADO (GLASSMORPHISM) ---
st.markdown("""
    <style>
    /* Fundo degradê estilo Gelo */
    .stApp {
        background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
    }
    
    /* Cabeçalho SENAI com profundidade */
    .header-senai { 
        background: linear-gradient(90deg, #e3000f 0%, #ff4b4b 100%); 
        padding: 30px; 
        border-radius: 20px; 
        color: white; 
        text-align: center; 
        box-shadow: 0 15px 25px -5px rgba(227, 0, 15, 0.4);
        margin-bottom: 40px;
    }
    .header-senai h1 { margin: 0; font-size: 3rem; font-weight: 900; }

    /* EFEITO VITRIFICADO NO FORMULÁRIO */
    [data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.4) !important; /* Transparência do vidro */
        backdrop-filter: blur(15px) saturate(180%) !important; /* O desfoque essencial */
        -webkit-backdrop-filter: blur(15px) saturate(180%);
        border-radius: 25px !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important; /* Borda brilhante */
        padding: 3rem !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1) !important;
    }

    /* Botão de Envio Estilizado */
    div.stButton > button { 
        background: linear-gradient(90deg, #232526 0%, #414345 100%) !important;
        color: white !important; 
        font-weight: 700 !important;
        height: 60px !important;
        border-radius: 15px !important;
        transition: 0.4s !important;
    }
    div.stButton > button:hover {
        background: #e3000f !important;
        transform: scale(1.02);
        box-shadow: 0 10px 20px rgba(227, 0, 15, 0.3);
    }

    /* Estilo dos inputs para combinar com o vidro */
    input, textarea, .stSelectbox {
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO GOOGLE SHEETS (MANTIDA IGUAL) ---
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

# --- DADOS ---
dados_cursos = {
    "Administração e Gestão": ["Almoxarife", "Assistente Administrativo", "Assistente de RH", "Logística"],
    "Eletroeletrônica": ["Eletricista Instalador", "Comandos Elétricos", "CLP"],
    "Metalmecânica": ["Mecânico de Usinagem", "Soldador", "Programador e Operador de CNC"],
    "Tecnologia da Informação": ["Excel Avançado", "IA Generativa", "Power BI", "Técnico em Desenvolvimento de Sistemas"],
    "Automobilística": ["Mecânico de Automóveis", "Eletricista Veicular"]
}

# --- INTERFACE ---
path_logo = os.path.join("imagens", "logo.png")
if os.path.exists(path_logo):
    c1, c2, c3 = st.columns([2, 1, 2])
    with c2: st.image(Image.open(path_logo), width=150)

st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Hermenegildo Campos de Almeida</p></div>', unsafe_allow_html=True)

st.write("") # Espaçador

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<h3 style='text-align: center; color: #1e1e1e;'>✨ Interessado em um Curso?</h3>", unsafe_allow_html=True)
    area_sel = st.selectbox("Selecione a Área:", ["Selecione..."] + sorted(list(dados_cursos.keys())))
    lista_cursos = ["Selecione..."] + sorted(dados_cursos[area_sel]) if area_sel != "Selecione..." else ["Selecione a área"]
    curso_sel = st.selectbox("Selecione o Curso:", lista_cursos)

    with st.form("form_vitrificado", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("Seu melhor E-mail")
        whats = st.text_input("WhatsApp")
        sugestao = st.text_area("Mensagem Adicional")
        btn = st.form_submit_button("ENVIAR MEU INTERESSE")

if btn:
    if nome and email and area_sel != "Selecione..." and service:
        df_atual = ler_dados()
        novo = pd.DataFrame([{"nome": nome, "email": email, "whatsapp": whats, "area": area_sel, "curso": curso_sel, "sugestao": sugestao, "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}])
        if salvar_dados(pd.concat([df_atual, novo], ignore_index=True)):
            st.success(f"Excelente, {nome}! Seus dados foram salvos no Google Sheets.")
            st.balloons()
    else:
        st.warning("Por favor, preencha todos os campos obrigatórios.")

# --- ADMIN ---
st.sidebar.title("🔒 ADM")
acesso = st.sidebar.text_input("Senha", type="password")
if acesso == "senai122":
    st.sidebar.success("Conectado")
    df_adm = ler_dados()
    if not df_adm.empty:
        if st.sidebar.checkbox("Visualizar Leads"):
            st.write("### Leads Captados")
            st.dataframe(df_adm, use_container_width=True)
        csv = df_adm.to_csv(index=False).encode('utf-8-sig')
        st.sidebar.download_button("Exportar CSV", csv, "leads_senai122.csv")
