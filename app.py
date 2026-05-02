import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- CONEXÃO COM GOOGLE SHEETS: MÉTODO MANUAL DIRETO ---
def obter_conexao():
    try:
        # Buscamos os valores brutos dos Secrets
        secrets_dict = st.secrets["connections"]["gsheets"]
        
        # Criamos a conexão passando APENAS o necessário, sem desempacotar o dicionário inteiro
        # Isso evita que argumentos inesperados como 'spreadsheet' ou 'type' quebrem a função
        return st.connection(
            "gsheets",
            type=GSheetsConnection,
            spreadsheet=secrets_dict.get("spreadsheet"),
            project_id=secrets_dict.get("project_id"),
            private_key_id=secrets_dict.get("private_key_id"),
            private_key=secrets_dict.get("private_key"),
            client_email=secrets_dict.get("client_email"),
            client_id=secrets_dict.get("client_id"),
            auth_uri=secrets_dict.get("auth_uri"),
            token_uri=secrets_dict.get("token_uri"),
            auth_provider_x509_cert_url=secrets_dict.get("auth_provider_x509_cert_url"),
            client_x509_cert_url=secrets_dict.get("client_x509_cert_url")
        )
    except Exception as e:
        st.error(f"Erro na conexão manual: {e}")
        return st.connection("gsheets", type=GSheetsConnection)

conn = obter_conexao()

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

# --- IMAGENS (Logo e Fachada) ---
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
        try:
            # Operação de I/O na planilha
            df_atual = conn.read()
            novo_lead = pd.DataFrame([{
                "nome": nome, "email": email, "whatsapp": whats,
                "area": area_sel, "curso": curso_sel, "sugestao": sugestao,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }])
            df_final = pd.concat([df_atual, novo_lead], ignore_index=True)
            conn.update(data=df_final)
            
            st.success(f"Sucesso, {nome}! Seu interesse foi registrado.")
            st.balloons()
        except Exception as e:
            st.error(f"Erro ao salvar na planilha: {str(e)}")
    else:
        st.error("Por favor, preencha nome, área e curso.")

# --- PAINEL ADMINISTRATIVO ---
st.sidebar.title("🔒 Admin")
senha_adm = st.sidebar.text_input("Senha", type="password")
if senha_adm == "senai122":
    try:
        df_leads = conn.read()
        if not df_leads.empty:
            if st.sidebar.checkbox("Ver Interessados"):
                st.write("### 📊 Relatório")
                st.dataframe(df_leads)
            
            csv_data = df_leads.to_csv(index=False).encode('utf-8-sig')
            st.sidebar.download_button("📥 Baixar Planilha", csv_data, "leads_senai.csv", "text/csv")
    except Exception as e:
        st.sidebar.warning(f"Aguardando dados... ({e})")
