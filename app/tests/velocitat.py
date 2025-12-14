import streamlit as st
from datetime import datetime, timedelta
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
import test_velocitat

if 'user' not in st.session_state:
    st.switch_page("app/login.py")

user = st.session_state.user
# DB key: Velocitat
last_test_played = user.last_test_date("Velocitat")

if last_test_played:
    try:
        last_date = datetime.strptime(last_test_played, "%Y-%m-%d").date()
        if (datetime.now().date() - last_date).days < 180:
            st.info(f"⏳ Test disponible en 6 mesos.")
            if st.button("Tornar"): st.switch_page("app/homepage.py")
            st.stop()
    except: pass

# Important: Netejar estat si venim de nou
if 'screen' in st.session_state and st.session_state.screen == 'results':
     del st.session_state['screen']

test_velocitat.run_test() # Asumim que poses el codi en una funció o executa l'script