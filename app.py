import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

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

# --- ESTILO E IMAGENS ---
st.markdown('<style>.header-senai { background-color: #ff0000; padding: 15px; border-radius: 12px; color: white; text-align: center; }</style>', unsafe_allow_html=True)

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

# --- FORMULÁRIO (Onde o 'btn' é definido) ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.write("### 📋 Ficha de Interesse")
    area_sel = st.selectbox("1. Selecione a Área:", ["Selecione..."] + sorted(list(dados_cursos.keys())))
    lista_cursos = ["Selecione..."] + sorted(dados_cursos[area_sel]) if area_sel != "Selecione..." else ["Selecione a área"]
    curso_sel = st.selectbox("2. Selecione o Curso:", lista_cursos)

    with st.form("form_final", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp")
        sugestao = st.text_area("Sugestões ou dúvidas")
        btn = st.form_submit_button("REGISTRAR INTERESSE")

# --- LÓGICA DE ENVIO (Sempre depois da definição do 'btn') ---
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
            st.dataframe(df_adm)
        csv = df_adm.to_csv(index=False).encode('utf-8-sig')
        st.sidebar.download_button("📥 Exportar CSV", csv, "leads.csv", "text/csv")
