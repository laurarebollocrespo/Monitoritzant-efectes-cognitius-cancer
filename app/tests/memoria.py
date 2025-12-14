import streamlit as st
from datetime import datetime, timedelta
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
import test_memoria

if 'user' not in st.session_state:
    st.switch_page("app/login.py")

user = st.session_state.user
last_test_played = user.last_test_date("Memoria")

# --- LÒGICA 6 MESOS ---
last_test_played = user.last_test_date("Memoria") # Nom exacte a la DB

if last_test_played:
    try:
        last_date = datetime.strptime(last_test_played, "%Y-%m-%d").date()
        today = datetime.now().date()
        if (today - last_date).days < 180:
            next_date = last_date + timedelta(days=180)
            st.info(f"⏳ Aquest test només es pot realitzar cada 6 mesos.\n\nData disponible: **{next_date.strftime('%d/%m/%Y')}**")
            if st.button("Tornar a l'Inici"):
                st.switch_page("app/homepage.py")
            st.stop()
    except ValueError:
        pass # Si hi ha error de format, deixem passar

# Executar el test
test_memoria.test_memoria()