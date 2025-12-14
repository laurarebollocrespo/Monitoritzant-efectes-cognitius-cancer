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

if last_test_played:
    try:
        last_date = datetime.strptime(last_test_played, "%Y-%m-%d").date()
        today = datetime.now().date()
        if (today - last_date).days < 180:
            next_date = last_date + timedelta(days=180)
            st.info(f"⏳ Test disponible el: **{next_date.strftime('%d/%m/%Y')}**")
            if st.button("Tornar a l'Inici"):
                st.switch_page("app/homepage.py")
            st.stop()
    except ValueError: pass

test_memoria.test_memoria()