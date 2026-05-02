import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- CSS AVANÇADO: O TOQUE DE ARTE UI/UX ---
st.markdown("""
    <style>
    /* Fundo estilo "Gelo" (Ice Blue/Grey Gradient) */
    .stApp {
        background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
    }
    
    /* Cabeçalho SENAI moderno com sombra e degradê */
    .header-senai { 
        background: linear-gradient(90deg, #e3000f 0%, #ff4b4b 100%); 
        padding: 25px; 
        border-radius: 15px; 
        color: white; 
        text-align: center; 
        box-shadow: 0 10px 15px -3px rgba(227, 0, 15, 0.3);
        margin-bottom: 30px;
    }
    .header-senai h1 { margin: 0; font-size: 2.8rem; font-weight: 800; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
    .header-senai p { margin: 5px 0 0 0; font-size: 1.2rem; opacity: 0.95; }

    /* Efeito Glassmorphism no Formulário (Container) */
    [data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(12px);
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.6);
    }

    /* Botão de Envio com efeito Hover */
    div.stButton > button { 
        background: linear-gradient(90deg, #1e1e1e 0%, #333333 100%) !important; 
        color: white !important; 
        font-weight: 800 !important; 
        letter-spacing: 1px;
        width: 100% !important; 
        border-radius: 12px !important; 
        border: none !important;
        height: 55px;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(227, 0, 15, 0.3);
        background: linear-gradient(90deg, #e3000f 0%, #cc0000 100%) !important; 
        color: white !important;
    }

    /* Ajuste dos textos e labels para ficarem mais elegantes */
    label {
        font-weight: 700 !important;
        color: #2d3748 !important;
        font-size: 1.05rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BLOCO INTOCÁVEL: CONEXÃO GOOGLE SHEETS ---
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

# --- MAPEAMENTO DE CURSOS ---
dados_cursos = {
    "Administração e Gestão": ["Almoxarife", "Assistente Administrativo", "Assistente de RH", "Logística"],
    "Eletroeletrônica": ["Eletricista Instalador", "Comandos Elétricos", "CLP"],
    "Metalmecânica": ["Mecânico de Usinagem", "Soldador", "Programador e Operador de CNC"],
    "Tecnologia da Informação": ["Excel Avançado", "IA Generativa", "Power BI", "Técnico em Desenvolvimento de Sistemas"],
    "Automobilística": ["Mecânico de Automóveis", "Eletricista Veicular"]
}

# --- IMAGENS E CABEÇALHO ---
path_logo = os.path.join("imagens", "logo.png")
if os.path.exists(path_logo):
    c1, c2, c3 = st.columns([2, 1, 2])
    with c2: st.image(Image.open(path_logo), width=150)

st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Hermenegildo Campos de Almeida</p></div>', unsafe_allow_html=True)

path_fachada = os.path.join("imagens", "fachada.jpg")
if os.path.exists(path_fachada):
    st.write("")
    f1, f2, f3 = st.columns([1, 6, 1])
    with f2: st.image(Image.open(path_fachada), use_container_width=True)

st.write("---")

# --- FORMULÁRIO ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<h3 style='text-align: center; color: #1e1e1e; margin-bottom: 20px;'>📋 Ficha de Interesse</h3>", unsafe_allow_html=True)
    area_sel = st.selectbox("1. Selecione a Área:", ["Selecione..."] + sorted(list(dados_cursos.keys())))
    lista_cursos = ["Selecione..."] + sorted(dados_cursos[area_sel]) if area_sel != "Selecione..." else ["Selecione a área"]
    curso_sel = st.selectbox("2. Selecione o Curso:", lista_cursos)

    with st.form("form_final", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp")
        sugestao = st.text_area("Sugestões ou dúvidas (Opcional)")
        st.write("") # Pequeno espaço para respirar antes do botão
        btn = st.form_submit_button("REGISTRAR INTERESSE")

# --- LÓGICA DE ENVIO ---
if btn:
    if nome and email and area_sel != "Selecione..." and service:
        df_atual = ler_dados()
        novo = pd.DataFrame([{"nome": nome, "email": email, "whatsapp": whats, "area": area_sel, "curso": curso_sel, "sugestao": sugestao, "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}])
        if salvar_dados(pd.concat([df_atual, novo], ignore_index=True)):
            st.success(f"### ✅ Sucesso, {nome}!")
            st.info("Seu interesse foi registrado. **Assim que o curso for aberto, a equipe do SENAI Guarulhos 122 entrará em contato.**")
            st.balloons()
    else:
        st.warning("Preencha os campos obrigatórios (Nome, E-mail e Curso).")

# --- PAINEL ADMINISTRATIVO ---
st.sidebar.title("🔒 Área Administrativa")
acesso = st.sidebar.text_input("Senha", type="password")
if acesso == "senai122":
    st.sidebar.success("Acesso Liberado")
    df_adm = ler_dados()
    if not df_adm.empty:
        if st.sidebar.checkbox("Ver Leads"):
            st.write("### 📊 Relatório de Leads")
            st.dataframe(df_adm, use_container_width=True)
        csv = df_adm.to_csv(index=False).encode('utf-8-sig')
        st.sidebar.download_button("📥 Exportar CSV", csv, "leads.csv", "text/csv")
