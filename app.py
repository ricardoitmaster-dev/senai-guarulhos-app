import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64
import urllib.parse
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="SENAI Guarulhos 122", page_icon="⚙️", layout="wide")

# --- FUNÇÃO DE LIMPEZA TOTAL ---
def reset_geral_callback():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

def get_base64_of_bin_file(bin_file):
    try:
        if os.path.exists(bin_file):
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()
    except:
        return ""
    return ""

# --- FUNÇÃO PARA LIMPAR NÚMERO DO WHATSAPP ---
def limpar_whatsapp(numero):
    return re.sub(r'\D', '', numero)

# --- CSS: ESTILO 3D E RODAPÉ ---
st.markdown("""
    <style>
    .stApp { background-color: #e0e5ec; }
    .logo-container { position: relative; z-index: 10; margin-bottom: -20px; display: flex; justify-content: center; padding-top: 10px; }
    .moldura-3d-ajustada { display: block; border-radius: 25px; box-shadow: 10px 10px 20px #bebebe, -10px -10px 20px #ffffff; border: 4px solid #e0e5ec; overflow: hidden; margin: 25px auto; }
    .moldura-3d-ajustada img { border-radius: 20px; display: block; width: 100%; height: auto; }
    .header-senai { background: #ff0000; padding: 40px 0px 25px 0px; color: white; text-align: center; width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; z-index: 5; box-shadow: 0px 10px 15px rgba(0,0,0,0.1); border-bottom: 4px solid #cc0000; }
    .header-senai h1 { font-size: 28px !important; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); font-weight: 800; color: white !important; }
    .btn-whatsapp { display: inline-flex; align-items: center; justify-content: center; background-color: #25D366 !important; color: white !important; padding: 15px 25px; border-radius: 12px; text-decoration: none; font-weight: bold; font-size: 18px; box-shadow: 4px 4px 10px rgba(0,0,0,0.2); margin-top: 15px; width: 100%; transition: 0.3s; }
    .btn-whatsapp:hover { background-color: #128C7E !important; transform: scale(1.02); }
    .footer-container { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; margin-top: 50px; font-family: sans-serif; }
    .footer-container a { text-decoration: none !important; color: inherit !important; }
    .footer-top { background-color: #f4f4f4; padding: 15px 0; text-align: center; display: flex; justify-content: center; gap: 20px; font-size: 12px; font-weight: bold; color: #444; }
    .footer-social { background-color: #ff0000; padding: 15px 0; text-align: center; color: white; display: flex; justify-content: center; gap: 25px; font-size: 20px; }
    .footer-content { background-color: #b5121b; padding: 40px 10% 20px 10%; color: white; display: grid; grid-template-columns: 1fr 1fr; gap: 50px; }
    .footer-bottom { background-color: #b5121b; padding: 20px 0; border-top: 1px solid rgba(255,255,255,0.2); display: flex; justify-content: center; gap: 30px; font-size: 13px; font-weight: bold; color: white !important; }
    label, [data-testid="stWidgetLabel"] p { color: #000000 !important; font-weight: 600 !important; }
    div.stButton > button { background-color: #ff0000 !important; color: #ffffff !important; font-weight: bold !important; height: 55px !important; border-radius: 15px !important; width: 100% !important; border: none !important; box-shadow
