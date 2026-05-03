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

# --- FUNÇÃO DO ROBÔ: BUSCA E EXTRAÇÃO DE DADOS ---
def buscar_detalhes_no_site(nome_curso):
    url_unidade = "https://www.sp.senai.br/unidade/guarulhos/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        response = requests.get(url_unidade, headers=headers, timeout=12)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            texto_pagina = soup.get_text()
            
            if nome_curso.lower() in texto_pagina.lower():
                # Tenta localizar a data no formato DD/MM/AAAA próximo ao nome do curso
                datas = re.findall(r'\d{2}/\d{2}/\d{4}', texto_pagina)
                data_ini = datas[0] if datas else "Consulte na Secretaria"
                
                # Lógica simplificada para valor (busca por R$ ou a palavra Gratuito)
                if "gratuito" in texto_pagina.lower() or "sem custo" in texto_pagina.lower():
                    valor = "Gratuito"
                else:
                    precos = re.findall(r'R\$\s?\d+\.?\d*,?\d*', texto_pagina)
                    valor = precos[0] if precos else "Consulte valores na Secretaria"
                
                return {"status": "aberto", "nome": nome_curso, "data": data_ini, "valor": valor}
        return {"status": "fechado"}
    except:
        return {"status": "erro"}

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

# --- INTERFACE ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.write("### 📋 Ficha de Interesse")
    area_sel = st.selectbox("1. Selecione a Área:", ["Selecione..."] + sorted(list(dados_cursos.keys())))
    lista_cursos = ["Selecione..."] + sorted(dados_cursos[area_sel]) if area_sel != "Selecione..." else ["Selecione a área"]
    curso_sel = st.selectbox("2. Selecione o Curso:", lista_cursos)

    info_vaga = None

    if curso_sel not in ["Selecione...", "Selecione a área"]:
        with st.spinner('Consultando dados oficiais no site do SENAI...'):
            info_vaga = buscar_detalhes_no_site(curso_sel)
            
            if info_vaga["status"] == "aberto":
                st.success(f"📌 **CURSO ENCONTRADO!**")
                # Mostra os detalhes capturados do site
                c_inf1, c_inf2 = st.columns(2)
                c_inf1.metric("Data de Início", info_vaga["data"])
                c_inf2.metric("Valor do Investimento", info_vaga["valor"])
                st.info("Preencha o restante do formulário para registrar seu interesse.")
            else:
                st.warning("ℹ️ **Curso sem turmas abertas no momento.**")
                st.write("Ainda não temos uma data definida para este curso. Preencha seus dados e avisaremos você assim que abrir!")

    # FORMULÁRIO DE DADOS
    with st.form("form_final", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp")
        sugestao = st.text_area("Comentários")
        btn = st.form_submit_button("REGISTRAR INTERESSE")

# --- LÓGICA FINAL DE ENVIO ---
if btn:
    if nome and email and area_sel != "Selecione..." and service:
        df_atual = ler_dados()
        novo = pd.DataFrame([{
            "nome": nome, "email": email, "whatsapp": whats, 
            "area": area_sel, "curso": curso_sel, "sugestao": sugestao, 
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }])
        
        if salvar_dados(pd.concat([df_atual, novo], ignore_index=True)):
            st.balloons()
            
            if info_vaga and info_vaga["status"] == "aberto":
                st.success(f"### Excelente escolha, {nome}!")
                st.markdown(f"""
                ✅ **Interesse Registrado.**  
                Como este curso possui turmas previstas para **{info_vaga['data']}**, pedimos que você:
                
                👉 **Dirija-se à secretaria da escola para efetivar sua matrícula.**
                
                **📍 Endereço:** Rua Saquaquara, 150 - Pres. Dutra, Guarulhos - SP (Unidade 122)  
                **⏰ Atendimento:** Seg a Sex: 08h às 20h | Sáb: 08h às 12h.
                """)
            else:
                st.info(f"### Tudo pronto, {nome}!")
                st.write("Registramos seu nome em nossa **Lista de Espera**. Assim que o curso de " + curso_sel + " for aberto, entraremos em contato via E-mail ou WhatsApp!")
        else:
            st.error("Erro técnico ao salvar dados. Tente novamente.")
    else:
        st.warning("Preencha Nome e E-mail para continuar.")
