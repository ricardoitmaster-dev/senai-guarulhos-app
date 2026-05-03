import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- BLOCO: CONEXÃO GOOGLE SHEETS ---
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
        if not values: 
            return pd.DataFrame(columns=["nome", "email", "whatsapp", "area", "curso", "sugestao", "data"])
        return pd.DataFrame(values[1:], columns=values[0])
    except: 
        return pd.DataFrame(columns=["nome", "email", "whatsapp", "area", "curso", "sugestao", "data"])

def salvar_dados(df):
    try:
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_id = extrair_id_planilha(url)
        # Prepara os dados: cabeçalho + valores
        valores = [df.columns.values.tolist()] + df.values.tolist()
        body = {"values": valores}
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id, 
            range="A1", 
            valueInputOption="RAW", 
            body=body
        ).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False

# --- PAINEL ADMINISTRATIVO (BARRA LATERAL) ---
with st.sidebar:
    st.header("🔐 Painel Adm")
    senha = st.text_input("Senha de acesso:", type="password")
    
    if senha == "senai122":
        st.success("Acesso Autorizado")
        if st.button("📊 Ver Lista de Interessados"):
            df_leads = ler_dados()
            st.write("### Candidatos Registrados")
            st.dataframe(df_leads)
            
            csv = df_leads.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Baixar Planilha (CSV)", data=csv, file_name="interessados_senai.csv", mime="text/csv")

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

# Logo
path_logo = os.path.join("imagens", "logo.png")
if os.path.exists(path_logo):
    c1, c2, c3 = st.columns([2, 1, 2])
    with c2: st.image(Image.open(path_logo), width=150)

st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Hermenegildo Campos de Almeida</p></div>', unsafe_allow_html=True)

# Fachada
path_fachada = os.path.join("imagens", "fachada.jpg")
if os.path.exists(path_fachada):
    st.write("")
    f1, f2, f3 = st.columns([1, 6, 1])
    with f2: st.image(Image.open(path_fachada), use_container_width=True)

st.write("---")

# --- INTERFACE DO FORMULÁRIO ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.write("### 📋 Ficha de Interesse")
    area_sel = st.selectbox("1. Selecione a Área:", ["Selecione..."] + sorted(list(dados_cursos.keys())))
    
    if area_sel != "Selecione...":
        lista_cursos = ["Selecione..."] + sorted(dados_cursos[area_sel])
    else:
        lista_cursos = ["Selecione a área"]
        
    curso_sel = st.selectbox("2. Selecione o Curso:", lista_cursos)

    # O formulário propriamente dito
    with st.form("form_registro", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp")
        sugestao = st.text_area("Sugestões ou dúvidas")
        submit_btn = st.form_submit_button("REGISTRAR INTERESSE")

    # Lógica de processamento após o clique
    if submit_btn:
        if nome and email and area_sel != "Selecione..." and curso_sel != "Selecione...":
            if service:
                # 1. Busca os dados atuais
                df_atual = ler_dados()
                
                # 2. Cria o novo registro
                novo_registro = {
                    "nome": nome, 
                    "email": email, 
                    "whatsapp": whats, 
                    "area": area_sel, 
                    "curso": curso_sel, 
                    "sugestao": sugestao, 
                    "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                }
                df_novo = pd.DataFrame([novo_registro])
                
                # 3. Une e Salva
                df_final = pd.concat([df_atual, df_novo], ignore_index=True)
                
                if salvar_dados(df_final):
                    st.success(f"### ✅ Sucesso, {nome}!")
                    st.info("Seu interesse foi registrado. A equipe do SENAI Guarulhos 122 entrará em contato em breve.")
                    st.balloons()
            else:
                st.error("Falha na conexão com o banco de dados. Tente mais tarde.")
        else:
            st.warning("Por favor, preencha todos os campos obrigatórios.")
