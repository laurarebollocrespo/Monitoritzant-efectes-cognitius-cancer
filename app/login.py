import streamlit as st
import time
import base64
import os
from app.user import User
from app import database as db

# --- FUNCIÓ PER LLEGIR IMATGES ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

# Carregar imatges (Assegura't que estan a la carpeta 'images' a l'arrel)
BACKGROUND_PATH = "images/background_login.png"
LOGO_PATH = "images/logo.png"

bg_base64 = get_base64_of_bin_file(BACKGROUND_PATH)
logo_base64 = get_base64_of_bin_file(LOGO_PATH)

# --- CSS PERSONALITZAT ---
# 1. Fons de pantalla
if bg_base64:
    page_bg = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bg_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """
else:
    page_bg = """<style>.stApp { background-color: #A8E6CF; }</style>"""

st.markdown(page_bg, unsafe_allow_html=True)

# 2. Estils de la Targeta i Inputs
st.markdown("""
    <style>
    /* Amagar elements per defecte */
    header, footer {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}

    /* Targeta Central - El truc per pintar el fons del login */
    div[data-testid="column"]:nth-of-type(2) > div {
        background-color: #F3EFEA; /* Beix suau */
        padding: 40px;
        border-radius: 10px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    }

    /* Inputs */
    .stTextInput input {
        border: 2px solid #A8E6CF;
        border-radius: 20px;
        background-color: #FFF5F5;
        color: #333;
        padding: 10px 15px;
    }
    
    .stTextInput label {
        color: #333 !important;
    }

    /* Botó */
    .stButton button {
        background-color: #98D8C1;
        color: black;
        border: none;
        border-radius: 20px;
        width: 100%;
        font-weight: bold;
        padding: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .stButton button:hover {
        background-color: #7BC4A8;
        color: black;
    }
    
    /* Logo i Títol */
    .header-container {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }
    .app-title {
        font-size: 40px;
        font-weight: 800;
        color: black;
        margin-left: 15px;
        font-family: 'Helvetica', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# --- LAYOUT VISUAL ---

# Encapçalament (Logo + Text)
col_h1, col_h2 = st.columns([0.1, 0.9])
with col_h1:
    if logo_base64:
        st.markdown(f'<img src="data:image/png;base64,{logo_base64}" width="70">', unsafe_allow_html=True)
    else:
        st.markdown("🌸", unsafe_allow_html=True) # Fallback
with col_h2:
    st.markdown('<div class="app-title">OncoConnect</div>', unsafe_allow_html=True)

st.write("") 
st.write("") 

# Zona Central (Targeta Login)
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    # Camps
    username = st.text_input("Usuari", placeholder="Introdueix el teu usuari")
    password = st.text_input("Contrasenya", type="password", placeholder="********")
    
    st.write("") 
    
    # Lògica del botó
    if st.button("Entrar"):
        user_data = db.check_login(username, password)

        if user_data:
            # Login correcte
            st.session_state.logged_in = True
            
            # Instanciem la classe User (això carrega streak, resultats, etc.)
            current_user = User(username)
            st.session_state.user = current_user
            
            st.success(f"Hola, {current_user.name}!")
            time.sleep(0.5)
            st.rerun() # Això farà que main.py carregui la Homepage
            
        elif username == "" or password == "":
            st.warning("Si us plau, introdueix usuari i contrasenya.")
        else:
            st.error("Usuari o contrasenya incorrectes.")