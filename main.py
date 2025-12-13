import streamlit as st
import sys
import os
import base64

# Afegim el directori actual al path per poder importar 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import database as db

# --- FUNCIÓ ICONA ---
def get_base64_logo():
    try:
        with open("images/logo.png", "rb") as f:
            data = f.read()
        return f"data:image/png;base64,{base64.b64encode(data).decode()}"
    except:
        return "🌸"

# --- CONFIGURACIÓ GLOBAL ---
st.set_page_config(
    page_title="OncoConnect",
    page_icon=get_base64_logo(), # Icona del navegador
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- INICIALITZACIÓ ---
db.init_db() # Crea taules si no existeixen

#--- GESTIÓ SESSIÓ ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- DEFINICIÓ PÀGINES ---
login_page = st.Page("app/login.py", title="Accés")
home_page = st.Page("app/homepage.py", title="Inici")
admin_home_page = st.Page("app/homepage_admin.py", title="Panell Mèdic")

# TESTS
test_fluencia = st.Page("app/tests/fluencia.py", title="Fluència Verbal")
test_atencio = st.Page("app/tests/atencio.py", title="Atenció")
test_memoria = st.Page("app/tests/memoria.py", title="Memòria")
test_velocitat = st.Page("app/tests/velocitat.py", title="Velocitat")

# EINES
checkin_page = st.Page("app/checkin.py", title="Check-in Diari")
incidencies_page = st.Page("app/incidencies.py", title="Incidències")
log_page = st.Page("app/log.py", title="Diari")
stats_page = st.Page("app/stats.py", title="Estadístiques")
eines_page = st.Page("app/eines.py", title="Recursos")


# --- NAVEGACIÓ ---
if st.session_state.logged_in:
    # Sidebar amb botó de sortir
    with st.sidebar:
        user = st.session_state.get('user')
        if user:
            st.write(f"Usuari: **{user.name}**")
        
        if st.button("Tancar Sessió", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()

    if user and user.is_admin:
        # --- MENÚ DE METGE ---
        pg = st.navigation({
            "Admin": [admin_home_page]
        })

    else:
        # Menú PACIENT
        pg = st.navigation({
            "Principal": [home_page],
            "Tests Cognitius": [test_fluencia, test_atencio, test_memoria, test_velocitat],
            "El meu Seguiment": [checkin_page, stats_page, log_page, incidencies_page],
            "Eines": [eines_page]
        })

else:
    # Només Login
    pg = st.navigation([login_page])

pg.run()