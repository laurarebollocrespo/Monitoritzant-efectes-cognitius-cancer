import streamlit as st
import database as db
import time


db.init_db() #inicialitzar base de dades


# --- CONFIGURACIÓ DE LA PÀGINA ---
st.set_page_config(
    page_title="OncoConnect - Login",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    /* Fons general de l'app en un verd molt suau */
    .stApp {
        background-color: #F1F8E9; /* Verd molt clar (Green 50) */
    }
    
    /* Títol principal */
    h1 {
        color: #2E7D32; /* Verd fosc per contrast */
        text-align: center;
        font-family: 'Helvetica', sans-serif;
    }
    
    /* Subtítol */
    h3 {
        color: #558B2F;
        text-align: center;
        font-weight: 300;
    }

    /* Camps de text (Inputs) */
    .stTextInput > div > div > input {
        border: 2px solid #A5D6A7; /* Vora verd pastel */
        border-radius: 10px;
        color: #1B5E20;
    }
    
    /* Botó d'acció principal */
    .stButton > button {
        background-color: #81C784; /* Verd pastel intens */
        color: white;
        border-radius: 12px;
        border: none;
        width: 100%;
        padding: 10px;
        font-weight: bold;
        transition: 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #66BB6A; /* Verd una mica més fosc al passar el ratolí */
        border: none;
        color: white;
    }

    /* Amagar elements per defecte de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Caixa del login */
    .login-container {
        background-color: white;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- GESTIÓ DE L'ESTAT (SESSION STATE) ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- LOGICA DE REDIRECCIÓ SI JA ESTÀ LOGINAT ---
if st.session_state['logged_in']:
    st.switch_page("pages/main.py")

# --- INTERFÍCIE GRÀFICA ---

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.write("") 
    st.write("") 
    
    # Logo
    st.markdown("<h1 style='font-size: 60px;'>🌿</h1>", unsafe_allow_html=True)
    st.title("OncoConnect")
    st.markdown("<h3>El teu company en el camí</h3>", unsafe_allow_html=True)
    st.divider()

    # Formulari de Login
    username = st.text_input("Usuari", placeholder="Introdueix el teu usuari")
    password = st.text_input("Contrasenya", type="password", placeholder="••••••••")

    st.write("") # Espai

    if st.button("Entrar", use_container_width=True):
    # ÚS DE LA BASE DE DADES REAL
        user_data = db.check_login(username, password)

        if user_data:
            st.success(f"Benvingut de nou, {user_data[2]}!") # user_data[2] és el nom real

            # Guardem l'estat
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.session_state['real_name'] = user_data[2]

            time.sleep(1)
            st.switch_page("pages/main.py")

        elif username == "" or password == "":
            st.warning("Si us plau, omple tots els camps.")

        else:
            st.error("Usuari o contrasenya incorrectes.")

    st.markdown("""
        <div style='text-align: center; margin-top: 20px; color: #888;'>
        <small>Hackathon BitsxLaMarató 2025</small>
        </div>
    """, unsafe_allow_html=True)