import streamlit as st
from datetime import datetime, timedelta
import sys, os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
import test_fluencia

if 'user' not in st.session_state: st.switch_page("app/login.py")
user = st.session_state.user

last_test_played = user.last_test_date("Fluencia")
if last_test_played:
    try:
        last_date = datetime.strptime(last_test_played, "%Y-%m-%d").date()
        if (datetime.now().date() - last_date).days < 180:
            st.info("⏳ Test disponible en 6 mesos.")
            if st.button("Tornar"): st.switch_page("app/homepage.py")
            st.stop()
    except: pass

test_fluencia.run_fluencia()