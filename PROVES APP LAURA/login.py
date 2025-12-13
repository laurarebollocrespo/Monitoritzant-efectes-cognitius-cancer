import streamlit as st
import database as db
import time
import base64
import os

# --- INICIALITZAR DB ---
db.init_db()

# --- CONFIGURACIÓ DE LA PÀGINA ---
st.set_page_config(
    page_title="OncoConnect - Login",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- FUNCIÓ PER LLEGIR IMATGE A BASE64 ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

# Ruta de la imatge de fons
img_file = "images/background_login.png"
img_base64 = get_base64_of_bin_file(img_file)

# --- CSS PERSONALITZAT ---
# 1. FONS DE PANTALLA
if img_base64:
    page_bg_img = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """
else:
    page_bg_img = """
    <style>
    .stApp { background: linear-gradient(135deg, #A8E6CF 0%, #DCEDC1 100%); }
    </style>
    """
st.markdown(page_bg_img, unsafe_allow_html=True)

# 2. ESTILS DEL FORMULARI I TARGETA
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Open Sans', sans-serif; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .block-container { padding-top: 2rem; padding-bottom: 0rem; }

    /* Títol */
    .header-title {
        font-size: 40px;
        font-weight: 800;
        color: black;
        margin-left: 10px;
        vertical-align: middle;
    }

    /* --- EL TRUC MÀGIC PER A LA CAIXA --- */
    /* Apuntem a la segona columna (la del mig) i li donem estil de targeta */
    div[data-testid="column"]:nth-of-type(2) > div {
        background-color: #F3EFEA; /* El color beix de la imatge */
        padding: 40px;
        border-radius: 5px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    }

    /* Inputs */
    .stTextInput > div > div > input {
        border: 2px solid #A8E6CF;
        border-radius: 25px;
        background-color: #FFF5F5;
        color: #333;
        padding: 10px 15px;
    }
    
    .stTextInput > label {
        color: #333 !important;
        font-weight: 500;
        margin-bottom: 5px;
    }

    /* Botó */
    .stButton > button {
        background-color: #98D8C1;
        color: black;
        border-radius: 25px;
        border: none;
        width: 100%;
        padding: 12px;
        font-weight: bold;
        font-size: 18px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
        transition: 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #7BC4A8;
        color: black;
        border: none;
    }
    
    /* Centrar verticalment */
    div[data-testid="column"] {
        display: flex;
        flex-direction: column;
        justify_content: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- GESTIÓ DE L'ESTAT ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    st.switch_page("main.py")

# --- LAYOUT DE LA PÀGINA ---

# 1. ENCAPÇALAMENT
head_col1, head_col2 = st.columns([0.08, 0.92])
with head_col1:
    st.markdown("<div style='font-size: 50px; line-height: 1;'>🌸</div>", unsafe_allow_html=True)
with head_col2:
    st.markdown("<div class='header-title'>OncoConnect</div>", unsafe_allow_html=True)

st.write("") # Espai vertical
st.write("") 

# 2. ESPAI CENTRAL (TARGETA LOGIN)
# Definim les columnes: la del mig (1) serà la que tindrà el fons beix gràcies al CSS
col_left, col_center, col_right = st.columns([1, 1, 1])

with col_center:
    # Ja no necessitem st.markdown obrint i tancant divs.
    # El CSS s'aplica automàticament a tot el contingut d'aquesta columna.
    
    username = st.text_input("Usuari", placeholder="Introdueix el teu usuari")
    password = st.text_input("Contrasenya", type="password", placeholder="********")
    
    st.write("") # Espaiador visual
    
    if st.button("Entrar", use_container_width=True):
        user_data = db.check_login(username, password)

        if user_data:
            st.success(f"Hola, {user_data[2]}!")
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.session_state['real_name'] = user_data[2]
            time.sleep(0.5)
            st.switch_page("main.py")
        elif username == "" or password == "":
            st.warning("Introdueix usuari i contrasenya")
        else:
            st.error("Credencials incorrectes")

# Footer
st.markdown("""
    <div style='position: fixed; bottom: 10px; width: 100%; text-align: center; color: #555; font-size: 12px;'>
    Hackathon BitsxLaMarató 2025
    </div>
""", unsafe_allow_html=True)