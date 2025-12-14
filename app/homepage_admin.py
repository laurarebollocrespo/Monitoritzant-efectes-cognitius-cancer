import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Importem database
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import database as db

# --- VERIFICACIÓ DE SEGURETAT ---
if 'user' not in st.session_state or not st.session_state.user.is_admin:
    st.error("Accés denegat. Només per a personal mèdic.")
    st.stop()

st.title(f"👨‍⚕️ Panell Mèdic: {st.session_state.user.name}")
st.markdown("---")

# 1. SELECTOR DE PACIENT
patients = db.get_all_patients() # Retorna [(user, nom), ...]
patient_dict = {f"{p[1]} ({p[0]})": p[0] for p in patients}

selected_label = st.selectbox("🔍 Buscar Pacient:", ["Selecciona un pacient..."] + list(patient_dict.keys()))

if selected_label != "Selecciona un pacient...":
    target_username = patient_dict[selected_label]
    
    # Recuperar dades del pacient seleccionat
    # Nota: Podem usar les funcions get_... de database.py directament
    
    tab_overview, tab_tests, tab_logs = st.tabs(["Visió General", "Tests Cognitius", "Diari i Incidències"])
    
    # --- TAB 1: VISIÓ GENERAL ---
    with tab_overview:
        col1, col2 = st.columns(2)
        
        # Dades bàsiques
        info = db.get_user_info(target_username)
        with col1:
            st.info(f"**Nom:** {info[0]}")
            st.write(f"**Última connexió:** {info[2]}")
            st.metric("Ratxa Actual (Dies)", info[1])
            
        # Historial de Check-ins (Cares)
        checkins = db.get_checkin_history(target_username)
        if checkins:
            df_check = pd.DataFrame(list(checkins.items()), columns=['Data', 'Estat'])
            df_check['Data'] = pd.to_datetime(df_check['Data'])
            
            with col2:
                st.write("**Evolució de l'Estat d'Ànim:**")
                fig = px.line(df_check, x='Data', y='Estat', markers=True, range_y=[0, 6])
                st.plotly_chart(fig, use_container_width=True)
        else:
            with col2:
                st.warning("Aquest pacient no ha registrat estats d'ànim.")

    # --- TAB 2: TESTS COGNITIUS ---
    with tab_tests:
        test_types = ["Fluencia", "Atencio", "Memoria", "Velocitat"]
        
        # Grid de gràfics
        c1, c2 = st.columns(2)
        
        conn = db.sqlite3.connect(db.DB_PATH) # Connexió directa per fer query complexa ràpida
        df_all_tests = pd.read_sql_query(f"SELECT test_type, date, score FROM test_results WHERE username='{target_username}'", conn)
        conn.close()
        
        if not df_all_tests.empty:
            for i, test in enumerate(test_types):
                # Filtrat per tipus
                df_t = df_all_tests[df_all_tests['test_type'] == test]
                
                # Assignar columna (esquerra o dreta)
                col = c1 if i % 2 == 0 else c2
                
                with col:
                    st.subheader(test)
                    if not df_t.empty:
                        fig = px.bar(df_t, x='date', y='score', color_discrete_sequence=['#81C784'])
                        st.plotly_chart(fig, use_container_width=True, key=f"plot_{test}")
                    else:
                        st.caption("Sense dades.")
        else:
            st.info("El pacient encara no ha realitzat cap test.")

    # --- TAB 3: DIARI I INCIDÈNCIES ---
    with tab_logs:
        col_inc, col_diari = st.columns(2)
        
        conn = db.sqlite3.connect(db.DB_PATH)
        
        with col_inc:
            st.subheader("⚠️ Incidències Reportades")
            df_inc = pd.read_sql_query(f"SELECT date, incidencia FROM incidencies WHERE username='{target_username}' ORDER BY date DESC", conn)
            
            # Mapeig invers manual per mostrar text (idealment importar INCIDENCIES_MAP)
            # Per hackathon mostrem l'ID o fem un join simple si cal
            if not df_inc.empty:
                st.dataframe(df_inc, use_container_width=True)
            else:
                st.write("Cap incidència.")
                
        with col_diari:
            st.subheader("📔 Entrades al Diari")
            df_log = pd.read_sql_query(f"SELECT date, text FROM logs WHERE username='{target_username}' ORDER BY date DESC", conn)
            
            if not df_log.empty:
                for index, row in df_log.iterrows():
                    with st.expander(f"{row['date']}"):
                        st.write(row['text'])
            else:
                st.write("Diari buit.")
        
        conn.close()

else:
    st.info("Selecciona un pacient del menú superior per veure les seves dades.")
    st.image("images/logo.png", width=100) # Decoració