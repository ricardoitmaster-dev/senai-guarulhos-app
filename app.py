# 1. Instalação e Configuração (Rode esta célula no Colab)
!pip install -q streamlit pyngrok

import os
from pyngrok import ngrok
from google.colab import drive
import shutil
import time

# --- CONEXÃO COM O DRIVE ---
drive.mount('/content/drive')
BACKUP_PATH = '/content/drive/MyDrive/Backup_SENAI/'
if not os.path.exists(BACKUP_PATH):
    os.makedirs(BACKUP_PATH)

# --- TOKEN DO NGROK ---
TOKEN = "COLE_SEU_TOKEN_AQUI" 
ngrok.set_auth_token(TOKEN)
!pkill streamlit
!pkill ngrok

# 2. Criação do app.py
with open("app.py", "w") as f:
    f.write(f"""
import streamlit as st
import sqlite3
import pandas as pd
import time
import shutil
import re
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- BANCO DE DADOS ---
conn = sqlite3.connect('senai_database.db', check_same_thread=False)
conn.execute('CREATE TABLE IF NOT EXISTS leads (nome TEXT, email TEXT, whatsapp TEXT, area TEXT, curso TEXT, data TEXT)')

# --- DICIONÁRIO DE CURSOS (EXTRAÍDO DO SITE SENAI-SP) ---
dados_cursos = {{
    "Administração e Gestão": [
        "Assistente de Recursos Humanos", "Assistente Financeiro", 
        "Assistente de Controle da Qualidade", "Analista de Escrituração Fiscal",
        "Assistente de Escrituração Fiscal", "Auditor Interno NBR ISO 9001:2015",
        "Alinhamento Estratégico Aplicado à Gestão", "5S"
    ],
    "Fabricação Mecânica e Mecânica Industrial": [
        "Ajustador Mecânico", "Mecânico de Usinagem", "Mecânico de Manutenção Industrial",
        "Técnico de Fabricação Mecânica", "Caldeireiro", "Soldador MAG"
    ],
    "Logística e Transporte": [
        "Técnico em Logística", "Almoxarife", "Assistente de Logística",
        "Análise de Modo e Efeito de Falha - FMEA", "Operador de Empilhadeira"
    ],
    "Tecnologia da Informação e Informática": [
        "Técnico em Desenvolvimento de Sistemas", "Administrador de Servidores Linux",
        "Administração de Sistemas ServiceNow - CSA", "Excel Avançado", "Lógica de Programação"
    ],
    "Mecatrônica, Energia e Eletrônica": [
        "Acionamento Eletrônico de Máquinas Elétricas", "Eletricista Instalador",
        "Comandos Elétricos", "Técnico em Eletrotécnica", "CLP - Controlador Lógico Programável"
    ],
    "Automotiva": [
        "Mecânico de Injeção Eletrônica", "Mecânico de Suspensão e Freios",
        "Eletricista de Veículos"
    ],
    "Meio Ambiente, Saúde e Segurança": [
        "Técnico em Segurança do Trabalho", "Economia Circular", "NR-10", "NR-35"
    ]
}}

# --- ESTILO CSS (BOTÕES PRETOS / TEXTO PRETO / SIDEBAR VERMELHA) ---
st.markdown('''
    <style>
    label, p, span, h1, h2, h3 {{ color: #000000 !important; font-weight: bold !important; }}
    [data-testid="stSidebar"] {{ background-color: #FF0000 !important; }}
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {{ color: #FFFFFF !important; }}
    
    .header-senai {{
        background-color: #FF0000; padding: 20px; border-radius: 12px;
        text-align: center; margin-bottom: 25px; color: white !important;
    }}
    .header-senai h1, .header-senai p {{ color: white !important; }}

    /* Botão Registrar */
    div.stButton > button {{
        background-color: #000000 !important; color: white !important;
        font-weight: bold !important; font-size: 18px !important;
        width: 100% !important; height: 3.5em !important; border-radius: 10px !important;
    }}
    /* Botão Download CSV */
    div.stDownloadButton > button {{
        background-color: #000000 !important; color: white !important;
        width: 100% !important; border-radius: 5px !important;
    }}
    </style>
''', unsafe_allow_html=True)

# --- CABEÇALHO ---
st.image("https://logodownload.org/wp-content/uploads/2019/08/senai-logo-1.png", width=180)
st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Hermenegildo Campos de Almeida</p></div>', unsafe_allow_html=True)

# --- SIDEBAR (ADMIN) ---
st.sidebar.title("🛠️ Painel Admin")
acesso = st.sidebar.checkbox("Ver Registros")
if acesso:
    senha = st.sidebar.text_input("Senha", type="password")
    if senha == "senai122":
        df = pd.read_sql_query("SELECT * FROM leads", conn)
        st.sidebar.write(f"Total: {{len(df)}}")
        st.sidebar.download_button("Baixar CSV", df.to_csv(index=False).encode('utf-8'), "leads_senai.csv", "text/csv")
        st.write("### 📊 Relatório de Interessados")
        st.dataframe(df, use_container_width=True)

# --- FORMULÁRIO ---
if 'form_key' not in st.session_state: st.session_state.form_key = 0

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.write("### 📋 Cadastro de Reserva")
    k = st.session_state.form_key
    nome = st.text_input("Nome Completo", key=f"n{{k}}")
    email = st.text_input("E-mail", key=f"e{{k}}")
    wpp = st.text_input("WhatsApp (ex: 11988887777)", key=f"w{{k}}")
    
    area_sel = st.selectbox("Área de Interesse", list(dados_cursos.keys()), key=f"a{{k}}")
    curso_sel = st.selectbox("Curso", dados_cursos[area_sel], key=f"c{{k}}")

    if st.button("REGISTRAR INTERESSE"):
        if nome and email and wpp:
            # Validação simples de número
            num_limpo = re.sub(r'\\D', '', wpp)
            if len(num_limpo) >= 10:
                dt = datetime.now().strftime("%d/%m/%Y %H:%M")
                conn.execute("INSERT INTO leads VALUES (?,?,?,?,?,?)", (nome, email, num_limpo, area_sel, curso_sel, dt))
                conn.commit()
                
                # Backup Automático no Drive
                try: shutil.copy('senai_database.db', '{BACKUP_PATH}senai_backup.db')
                except: pass
                
                st.success("✅ Sucesso! Seus dados foram salvos.")
                st.balloons()
                time.sleep(2)
                st.session_state.form_key += 1
                st.rerun()
            else:
                st.error("❌ WhatsApp inválido. Use DDD + Número.")
        else:
            st.warning("⚠️ Preencha todos os campos.")
""")

# 3. Execução
get_ipython().system_raw('streamlit run app.py --server.port 8501 &')
time.sleep(3)
public_url = ngrok.connect(8501).public_url
print(f"\n✅ APP FINALIZADO!\n🔗 LINK DE ACESSO: {public_url}")