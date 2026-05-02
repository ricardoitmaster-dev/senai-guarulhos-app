import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- CONEXÃO COM GOOGLE SHEETS ---
# Puxa o link limpo que você acabou de salvar nos Secrets
url_planilha = st.secrets["connections"]["gsheets"]["spreadsheet"]
conn = st.connection("gsheets", type=GSheetsConnection)

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

# --- IMAGENS (CAMINHO RELATIVO GITHUB) ---
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

    with st.form("form_gsheets", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        whats = st.text_input("WhatsApp (com DDD)")
        sugestao = st.text_area("Sugestão de curso ou observação:")
        btn_enviar = st.form_submit_button("REGISTRAR INTERESSE")
        
        if btn_enviar:
            if nome and area_sel != "Selecione..." and curso_sel != "Selecione...":
                # Lendo dados atuais para anexar
                df_atual = conn.read(spreadsheet=url_planilha)
                novo_lead = pd.DataFrame([{
                    "nome": nome, "email": email, "whatsapp": whats,
                    "area": area_sel, "curso": curso_sel, "sugestao": sugestao,
                    "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                }])
                df_final = pd.concat([df_atual, novo_lead], ignore_index=True)
                
                # Salvando na planilha
                conn.update(spreadsheet=url_planilha, data=df_final)
                
                st.success(f"Obrigado, {nome}! Seu interesse foi registrado no Google Sheets!")
                st.balloons()
            else:
                st.error("Preencha todos os campos obrigatórios.")

# --- PAINEL ADMINISTRATIVO ---
st.sidebar.title("🔒 Admin")
senha_adm = st.sidebar.text_input("Senha", type="password")
if senha_adm == "senai122":
    # Lendo e ordenando pela data mais recente
    df_leads = conn.read(spreadsheet=url_planilha)
    if not df_leads.empty:
        df_leads['data_dt'] = pd.to_datetime(df_leads['data'], format="%d/%m/%Y %H:%M:%S", errors='coerce')
        df_leads = df_leads.sort_values(by='data_dt', ascending=False).drop(columns=['data_dt'])
        
    if st.sidebar.checkbox("Ver Interessados"):
        st.write("### 📊 Relatório (Ordenado por Data)")
        st.dataframe(df_leads)
    
    csv_data = df_leads.to_csv(index=False).encode('utf-8-sig')
    st.sidebar.download_button("📥 Baixar Planilha", csv_data, "leads_senai.csv", "text/csv")
