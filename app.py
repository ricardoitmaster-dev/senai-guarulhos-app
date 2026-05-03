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

# --- CSS: ESTILO VITRIFICADO ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%); }
    .header-senai { 
        background: linear-gradient(90deg, #e3000f 0%, #ff4b4b 100%); 
        padding: 30px; border-radius: 20px; color: white; text-align: center; 
        box-shadow: 0 15px 25px -5px rgba(227, 0, 15, 0.4); margin-bottom: 20px;
    }
    .img-escola {
        border-radius: 15px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        margin-bottom: 30px;
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

# --- FUNÇÕES DE DADOS ---
@st.cache_data(ttl=86400)
def buscar_cursos_dinamicos():
    return {
        "Tecnologia da Informação": ["Excel Avançado", "IA Generativa", "Python", "Power BI", "Desenvolvimento de Sistemas"],
        "Eletroeletrônica": ["Eletricista Instalador", "Comandos Elétricos", "CLP", "Manutenção Eletrônica"],
        "Metalmecânica": ["Mecânico de Usinagem", "Soldagem MAG/TIG", "Operador de CNC", "Mecânico de Manutenção"],
        "Gestão e Logística": ["Almoxarife", "Assistente Administrativo", "Assistente de RH", "Logística"]
    }

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

# --- CABEÇALHO ---
st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Registro de Interesse</p></div>', unsafe_allow_html=True)

# --- EXIBIÇÃO DA IMAGEM DA ESCOLA (CORRIGIDA) ---
c_img1, c_img2, c_img3 = st.columns([1, 4, 1])
with c_img2:
    # Tentativa 1: Arquivo local (imagens/frente_escola.png)
    path_escola = os.path.join("imagens", "frente_escola.png")
    if os.path.exists(path_escola):
        st.image(Image.open(path_escola), use_container_width=True, caption="Unidade SENAI Guarulhos 122")
    else:
        # Tentativa 2: URL Direta (Substitua este link pela URL da foto da escola se tiver uma)
        # Usei uma imagem padrão do SENAI como exemplo caso a sua suma
        st.image("https://guarulhos.sp.senai.br/institucional/3611/0/unidade-guarulhos", use_container_width=True, caption="SENAI Guarulhos - Unidade 122")

# --- INTERFACE PRINCIPAL ---
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
                st.success(f"✅ Olá {nome}! Registro concluído para o curso de {curso_escolhido}. Entraremos em contato em breve!")
                st.balloons()
            else:
                st.error("Erro ao salvar os dados.")
        else:
            st.warning("⚠️ Preencha todos os campos corretamente.")

# --- PAINEL LATERAL ADM ---
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
