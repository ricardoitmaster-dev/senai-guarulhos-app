import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
from google.oauth2 import service_account
from googleapiclient.discovery import build
import textwrap

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- CONEXÃO RAIZ COM GOOGLE SHEETS (HIGIENIZAÇÃO AGRESSIVA) ---
@st.cache_resource
def conectar_google_sheets():
    try:
        # 1. Recupera os segredos do Streamlit Cloud
        s = st.secrets["connections"]["gsheets"]
        
        # 2. Limpeza profunda da chave privada
        # Removemos cabeçalhos, espaços, quebras de linha e o caractere '_' (ASCII 95)
        pk = s["private_key"]
        pk = pk.replace("-----BEGIN PRIVATE KEY-----", "")
        pk = pk.replace("-----END PRIVATE KEY-----", "")
        pk = pk.replace("\n", "").replace("\r", "").replace(" ", "").replace("_", "").replace("\\n", "")
        
        # 3. Reconstrói o formato PEM estrito (64 caracteres por linha)
        pk_limpa = "\n".join(textwrap.wrap(pk, 64))
        private_key_final = f"-----BEGIN PRIVATE KEY-----\n{pk_limpa}\n-----END PRIVATE KEY-----\n"
        
        info = {
            "type": s["type"],
            "project_id": s["project_id"],
            "private_key_id": s["private_key_id"],
            "private_key": private_key_final,
            "client_email": s["client_email"],
            "client_id": s["client_id"],
            "auth_uri": s["auth_uri"],
            "token_uri": s["token_uri"],
            "auth_provider_x509_cert_url": s["auth_provider_x509_cert_url"],
            "client_x509_cert_url": s["client_x509_cert_url"]
        }
        
        # 4. Escopos de acesso e criação do serviço
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
        return build("sheets", "v4", credentials=creds)
    except Exception as e:
        st.error(f"Erro Crítico de Autenticação: {e}")
        return None

# Instancia o serviço globalmente
service = conectar_google_sheets()

# --- FUNÇÕES DE UTILITÁRIO ---
def extrair_id_planilha(url):
    return url.split("/d/")[1].split("/")[0]

def ler_dados():
    try:
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_id = extrair_id_planilha(url)
        # Lemos um range amplo da primeira página
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, 
            range="A1:Z1000"
        ).execute()
        values = result.get("values", [])
        if not values:
            return pd.DataFrame()
        # Transforma em DataFrame usando a primeira linha como cabeçalho
        return pd.DataFrame(values[1:], columns=values[0])
    except Exception as e:
        st.error(f"Erro ao ler dados: {e}")
        return pd.DataFrame()

def salvar_dados(df):
    try:
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_id = extrair_id_planilha(url)
        # Prepara os dados para o Google (lista de listas)
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
        st.error(f"Erro ao salvar dados: {e}")
        return False

# --- MAPEAMENTO DE CURSOS ---
dados_cursos = {
    "Administração e Gestão": ["Almoxarife", "Assistente Administrativo", "Assistente de RH", "Logística"],
    "Eletroeletrônica": ["Eletricista Instalador", "Comandos Elétricos", "CLP"],
    "Metalmecânica": ["Mecânico de Usinagem", "Soldador", "Programador e Operador de CNC"],
    "Tecnologia da Informação": [
        "Excel Avançado", "IA Generativa: ChatGPT", "IA Generativa: Google Gemini",
        "IA Generativa: Microsoft Copilot", "Power BI", "Técnico em Desenvolvimento de Sistemas"
    ],
    "Automobilística": ["Mecânico de Automóveis", "Eletricista Veicular"],
    "Outras Áreas": ["Segurança do Trabalho", "Alimentos"]
}

# --- ESTILO CSS ---
st.markdown("""
    <style>
    [data-testid="stImage"] { display: flex; justify-content: center; margin: auto; width: 100%; }
    .header-senai { background-color: #ff0000; padding: 15px; border-radius: 12px; color: white; text-align: center; margin: 20px 0; }
    div.stButton > button { background-color: #000000 !important; color: white !important; font-weight: bold !important; width: 100% !important; border-radius: 8px !important; }
    label { font-weight: bold !important; color: #1e1e1e !important; }
    </style>
    """, unsafe_allow_html=True)

# --- IMAGENS E CABEÇALHO ---
path_logo = os.path.join("imagens", "logo.png")
if os.path.exists(path_logo):
    col_l1, col_l2, col_l3 = st.columns([2, 1, 2])
    with col_l2: st.image(Image.open(path_logo), width=150)

st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Hermenegildo Campos de Almeida</p></div>', unsafe_allow_html=True)

path_fachada = os.path.join("imagens", "fachada.jpg")
if os.path.exists(path_fachada):
    f_col1, f_col2, f_col3 = st.columns([1, 6, 1]) 
    with f_col2: st.image(Image.open(path_fachada), use_container_width=True)

st.write("---")

# --- INTERFACE DE CADASTRO ---
col_f1, col_f2, col_f3 = st.columns([1, 2, 1])

with col_f2:
    st.write("### 📋 Ficha de Interesse")
    opcoes_areas = ["Selecione..."] + sorted(list(dados_cursos.keys()))
    area_sel = st.selectbox("1. Selecione a Área:", opcoes_areas)
    
    lista_cursos = ["Selecione..."] + sorted(dados_cursos[area_sel]) if area_sel != "Selecione..." else ["Selecione..."]
    curso_sel = st.selectbox("2. Selecione o Curso:", lista_cursos)

    with st.form("form_registro", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp (com DDD)")
        sugestao = st.text_area("Sugestão de curso ou observação:")
        btn_enviar = st.form_submit_button("REGISTRAR INTERESSE")

if btn_enviar:
    if nome and area_sel != "Selecione..." and curso_sel != "Selecione..." and service:
        try:
            # 1. Busca dados atuais
            df_atual = ler_dados()
            
            # 2. Cria novo registro
            novo_lead = pd.DataFrame([{
                "nome": nome, "email": email, "whatsapp": whats,
                "area": area_sel, "curso": curso_sel, "sugestao": sugestao,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }])
            
            # 3. Junta e salva
            df_final = pd.concat([df_atual, novo_lead], ignore_index=True)
            if salvar_dados(df_final):
                st.success(f"Sucesso, {nome}! Seu interesse foi registrado.")
                st.balloons()
        except Exception as e:
            st.error(f"Erro no processamento: {e}")
    else:
        st.error("Por favor, preencha os campos obrigatórios e verifique a conexão.")

# --- PAINEL ADMINISTRATIVO ---
st.sidebar.title("🔒 Admin")
senha_adm = st.sidebar.text_input("Senha", type="password")
if senha_adm == "senai122" and service:
    try:
        df_leads = ler_dados()
        if not df_leads.empty:
            if st.sidebar.checkbox("Ver Interessados"):
                st.write("### 📊 Relatório de Leads")
                st.dataframe(df_leads)
            
            csv_data = df_leads.to_csv(index=False).encode('utf-8-sig')
            st.sidebar.download_button("📥 Baixar Planilha", csv_data, "leads_senai.csv", "text/csv")
    except:
        st.sidebar.warning("Aguardando registros na planilha...")
