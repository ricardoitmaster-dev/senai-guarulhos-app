import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
from google.oauth2 import service_account
from googleapiclient.discovery import build
import requests
from bs4 import BeautifulSoup
import re

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

# --- FUNÇÃO DO ROBÔ REFORMULADA ---
def buscar_detalhes_reais(nome_curso):
    url_unidade = "https://www.sp.senai.br/unidade/guarulhos/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url_unidade, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Procura o curso na lista
        curso_found = soup.find(string=re.compile(nome_curso, re.IGNORECASE))
        
        if curso_found:
            # Tenta pegar a data próxima ao nome do curso no HTML
            # Se não achar data clara, retornamos vazio para não exibir informação errada
            parent = curso_found.find_parent()
            texto_contexto = parent.get_text() if parent else ""
            
            data_match = re.search(r'\d{2}/\d{2}/\d{4}', texto_contexto)
            data_str = data_match.group() if data_match else "A definir"
            
            valor_str = "Gratuito" if "gratuito" in texto_contexto.lower() else "Sob consulta"
            
            return {"status": "aberto", "data": data_str, "valor": valor_str}
        return {"status": "lista_espera"}
    except:
        return {"status": "erro"}

# --- MAPEAMENTO ---
dados_cursos = {
   "Administração e Gestão": ["Almoxarife", "Assistente Administrativo", "Assistente de RH", "Logística"],
   "Eletroeletrônica": ["Eletricista Instalador", "Comandos Elétricos", "CLP"],
   "Metalmecânica": ["Mecânico de Usinagem", "Soldador", "Programador e Operador de CNC"],
   "Tecnologia da Informação": ["Excel Avançado", "IA Generativa", "Power BI", "Técnico em Desenvolvimento de Sistemas"],
   "Automobilística": ["Mecânico de Automóveis", "Eletricista Veicular"]
}

# --- HEADER ---
st.markdown('<style>.header-senai { background-color: #ff0000; padding: 15px; border-radius: 12px; color: white; text-align: center; }</style>', unsafe_allow_html=True)
st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Hermenegildo Campos de Almeida</p></div>', unsafe_allow_html=True)

# --- FORMULÁRIO ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.write("### 📋 Ficha de Interesse")
    area_sel = st.selectbox("1. Selecione a Área:", ["Selecione..."] + sorted(list(dados_cursos.keys())))
    lista_cursos = ["Selecione..."] + sorted(dados_cursos[area_sel]) if area_sel != "Selecione..." else ["Selecione a área"]
    curso_sel = st.selectbox("2. Selecione o Curso:", lista_cursos)

    info_vaga = None
    if curso_sel not in ["Selecione...", "Selecione a área"]:
        with st.spinner('Consultando disponibilidade...'):
            info_vaga = buscar_detalhes_reais(curso_sel)
            
            if info_vaga["status"] == "aberto":
                st.success(f"✅ **Curso com Turmas Abertas/Previstas!**")
                # Só mostra se a data for real
                st.write(f"📅 **Data de Início:** {info_vaga['data']}")
                st.write(f"💰 **Investimento:** {info_vaga['valor']}")
            else:
                st.warning("ℹ️ **No momento este curso está em Lista de Espera.**")

    with st.form("form_final", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp")
        sugestao = st.text_area("Comentários")
        btn = st.form_submit_button("REGISTRAR INTERESSE")

if btn:
    if nome and email and area_sel != "Selecione...":
        df_atual = ler_dados()
        novo = pd.DataFrame([{"nome": nome, "email": email, "whatsapp": whats, "area": area_sel, "curso": curso_sel, "sugestao": sugestao, "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}])
        
        if salvar_dados(pd.concat([df_atual, novo], ignore_index=True)):
            st.balloons()
            if info_vaga and info_vaga["status"] == "aberto":
                st.success(f"### Sucesso, {nome}!")
                st.markdown(f"""
                **PRÓXIMO PASSO:**  
                Como o curso de **{curso_sel}** está ativo, você deve comparecer à secretaria para garantir sua vaga.
                
                **📍 Endereço:** Rua Saquaquara, 150 - Pres. Dutra, Guarulhos - SP (Unidade 122)  
                **⏰ Secretaria:** Seg a Sex (08h às 20h) e Sáb (08h às 12h).
                """)
            else:
                st.info(f"### {nome}, você está na lista!")
                st.write("Assim que abrirmos novas turmas para este curso, entraremos em contato imediatamente.")
