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

# --- CSS: ESTILO PERSONALIZADO (BMW PORTINARI, PRETO E OURO) ---
st.markdown("""
    <style>
    /* Fundo em Azul BMW Portinari */
    .stApp { background-color: #003366; } 
    
    .logo-container { position: relative; z-index: 10; margin-bottom: -20px; display: flex; justify-content: center; padding-top: 10px; }
    
    .moldura-3d-ajustada { 
        display: block; 
        border-radius: 25px; 
        box-shadow: 10px 10px 20px #001a33, -5px -5px 15px #004080; 
        border: 4px solid #D4AF37; /* Borda Ouro */
        overflow: hidden; 
        margin: 25px auto; 
    }
    
    .moldura-3d-ajustada img { border-radius: 20px; display: block; width: 100%; height: auto; }
    
    /* Header em Preto Brilhante com detalhes Ouro */
    .header-senai { 
        background: #000000; 
        padding: 40px 0px 25px 0px; 
        color: #D4AF37; 
        text-align: center; 
        width: 100vw; 
        position: relative; 
        left: 50%; 
        right: 50%; 
        margin-left: -50vw; 
        margin-right: -50vw; 
        z-index: 5; 
        box-shadow: 0px 10px 15px rgba(0,0,0,0.5); 
        border-bottom: 4px solid #D4AF37; 
    }
    
    .header-senai h1 { font-size: 28px !important; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); font-weight: 800; color: #D4AF37 !important; }
    
    .btn-whatsapp { 
        display: inline-flex; 
        align-items: center; 
        justify-content: center; 
        background-color: #25D366 !important; 
        color: white !important; 
        padding: 15px 25px; 
        border-radius: 12px; 
        text-decoration: none; 
        font-weight: bold; 
        font-size: 18px; 
        box-shadow: 4px 4px 10px rgba(0,0,0,0.4); 
        margin-top: 15px; 
        width: 100%; 
        transition: 0.3s; 
    }
    
    /* Formulário Estilo Glassmorphism (Preto com Ouro) */
    [data-testid="stForm"] { 
        background-color: rgba(0, 0, 0, 0.7) !important; 
        border-radius: 30px !important; 
        padding: 2rem !important; 
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8) !important; 
        border: 2px solid #D4AF37 !important; 
    }

    label, [data-testid="stWidgetLabel"] p { color: #D4AF37 !important; font-weight:
