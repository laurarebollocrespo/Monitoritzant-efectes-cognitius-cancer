import streamlit as st
import time
from datetime import datetime
import random
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import database as db

today = datetime.now().date()

# --- CONFIGURACIÓ DE LA PÀGINA ---
st.set_page_config(
    page_title="OncoConnect - Inici",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- LOGIN ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Si us plau, inicia sessió primer.")
    st.stop()

st.markdown("""
    <style>
    .stApp { background-color: #F1F8E9; }
    
    /* Pestanyes personalitzades */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 10px;
        color: #558B2F;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #81C784;
        color: white;
    }
    
    /* Targetes de contingut */
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* Botons grans per a dits */
    .stButton > button {
        height: 50px;
        border-radius: 10px;
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)

# --- GESTIÓ D'ESTAT DELS TESTS ---
if 'test_active' not in st.session_state: st.session_state['test_active'] = False
if 'test_phase' not in st.session_state: st.session_state['test_phase'] = 'intro'
if 'sequence' not in st.session_state: st.session_state['sequence'] = []
if 'user_input_seq' not in st.session_state: st.session_state['user_input_seq'] = ""
if 'speed_numbers' not in st.session_state: st.session_state['speed_numbers'] = []
if 'next_number' not in st.session_state: st.session_state['next_number'] = 1
if 'start_time' not in st.session_state: st.session_state['start_time'] = 0

# --- FUNCIONS AUXILIARS ---
def reset_test_state():
    st.session_state['test_active'] = False
    st.session_state['test_phase'] = 'intro'
    st.session_state['sequence'] = []
    st.session_state['speed_numbers'] = []
    st.session_state['next_number'] = 1

# --- INTERFÍCIE PRINCIPAL ---

# Capçalera amb nom usuari
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown(f"<h2 style='color:#2E7D32;'>Hola, {st.session_state.get('real_name', 'Pacient')}! 👋</h2>", unsafe_allow_html=True)
with col_h2:
    if st.button("Sortir", key="logout_btn"):
        st.session_state['logged_in'] = False
        st.switch_page("login.py")

# Navegació per Tabs
tab_avui, tab_progres, tab_recursos = st.tabs(["🏠 Avui", "📈 El meu Progrés", "🧘 Recursos"])

# ==============================================================================
# PESTANYA 1: AVUI (CHECK-IN I TESTS)
# ==============================================================================
with tab_avui:
    
    # 1. CHECK-IN DIARI
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 📝 Com et sents avui?")
    
    symptom_options = [
        "Avui em sento bé",
        "He anat a una habitació i no recordava què hi anava a fer (Atenció)",
        "He trigat més del normal a fer una activitat (Velocitat)",
        "Volia dir una paraula i no m'ha sortit (Fluència)",
        "He perdut el fil de la conversa (Atenció)",
        "No recordo informació recent (Memòria)",
        "Em sento amb 'nebulosa mental' (Funcions Executives)"
    ]
    
    selected_symptom = st.selectbox("Selecciona una opció:", symptom_options, label_visibility="collapsed")
    
    if st.button("Guardar Check-in", type="primary", use_container_width=True):
        db.save_daily_checkin(st.session_state['username'], selected_symptom)
        st.success("Registrat! Gràcies per compartir-ho.")
        # Lògica de recomanació immediata
        if "Atenció" in selected_symptom:
            st.info("💡 Recomanació: Intenta fer una tasca cada vegada. Avui et recomanem el test d'Atenció.")
        elif "Velocitat" in selected_symptom:
            st.info("💡 Recomanació: No et pressionis. Fes el test de Velocitat per activar-te.")
    
    st.markdown("</div>", unsafe_allow_html=True)

    # 2. REPTE DEL DIA (TESTS)
    st.markdown("### 🧠 Entrena el teu cervell")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if st.button("🔢 Atenció", use_container_width=True):
            st.session_state['test_active'] = True
            st.session_state['current_test'] = 'atencio'
            st.session_state['test_phase'] = 'intro'
            st.rerun()
            
    with col_t2:
        if st.button("⚡ Velocitat", use_container_width=True):
            st.session_state['test_active'] = True
            st.session_state['current_test'] = 'velocitat'
            st.session_state['test_phase'] = 'intro'
            st.rerun()

    # --- ÀREA D'EXECUCIÓ DELS TESTS ---
    if st.session_state['test_active']:
        st.markdown("---")
        
        # === TEST D'ATENCIÓ (DIGIT SPAN) ===
        if st.session_state['current_test'] == 'atencio':
            st.markdown("#### Test d'Atenció: Repeteix els números")
            
            if st.session_state['test_phase'] == 'intro':
                st.write("Apareixeran uns números. Memoritza'ls i escriu-los.")
                if st.button("COMENÇAR", type="primary", use_container_width=True):
                    # Generar seqüència
                    st.session_state['sequence'] = [str(random.randint(0, 9)) for _ in range(5)] # Comencem amb 5
                    st.session_state['test_phase'] = 'show'
                    st.rerun()
            
            elif st.session_state['test_phase'] == 'show':
                # Mostrar números amb un placeholder
                placeholder = st.empty()
                placeholder.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{' '.join(st.session_state['sequence'])}</h1>", unsafe_allow_html=True)
                time.sleep(2) # Temps per memoritzar
                placeholder.empty() # Esborrar
                st.session_state['test_phase'] = 'input'
                st.rerun()
                
            elif st.session_state['test_phase'] == 'input':
                with st.form("input_form"):
                    user_ans = st.text_input("Quins eren els números? (Ex: 12345)", autocomplete="off")
                    submitted = st.form_submit_button("COMPROVAR", use_container_width=True)
                    if submitted:
                        seq_str = "".join(st.session_state['sequence'])
                        if user_ans == seq_str:
                            st.balloons()
                            st.success("Correcte! 🎉")
                            db.save_test_result(st.session_state['username'], "Atenció", 10)
                        else:
                            st.error(f"Oh! Era {seq_str}. No passa res, segueix practicant!")
                            db.save_test_result(st.session_state['username'], "Atenció", 5)
                        
                        time.sleep(2)
                        reset_test_state()
                        st.rerun()

        # === TEST DE VELOCITAT (ORDERED TAPPING) ===
        elif st.session_state['current_test'] == 'velocitat':
            st.markdown("#### Test de Velocitat: Prem en ordre (1-10)")
            
            if st.session_state['test_phase'] == 'intro':
                if st.button("COMENÇAR CRONÒMETRE", type="primary", use_container_width=True):
                    st.session_state['speed_numbers'] = random.sample(range(1, 11), 10) # Números 1 a 10 desordenats
                    st.session_state['next_number'] = 1
                    st.session_state['start_time'] = time.time()
                    st.session_state['test_phase'] = 'playing'
                    st.rerun()
            
            elif st.session_state['test_phase'] == 'playing':
                st.write(f"Busca el número: **{st.session_state['next_number']}**")
                
                # Crear graella de botons (Grid 4x3)
                cols = st.columns(4)
                for i, num in enumerate(st.session_state['speed_numbers']):
                    # Si el número ja s'ha clicat (és menor que el següent), no el mostrem o el mostrem desactivat
                    if num < st.session_state['next_number']:
                        cols[i % 4].button("✅", key=f"btn_{num}", disabled=True)
                    else:
                        if cols[i % 4].button(str(num), key=f"btn_{num}", use_container_width=True):
                            if num == st.session_state['next_number']:
                                st.session_state['next_number'] += 1
                                if st.session_state['next_number'] > 10:
                                    end_time = time.time()
                                    total_time = round(end_time - st.session_state['start_time'], 2)
                                    st.success(f"Acabat en {total_time} segons!")
                                    db.save_test_result(st.session_state['username'], "Velocitat", total_time)
                                    time.sleep(2)
                                    reset_test_state()
                                st.rerun()
                            else:
                                st.toast("❌ Incorrecte! Segueix l'ordre.")

        if st.button("Cancel·lar Test", type="secondary"):
            reset_test_state()
            st.rerun()

# ==============================================================================
# PESTANYA 2: PROGRÉS
# ==============================================================================
with tab_progres:
    st.markdown("### 📊 La teva evolució")
    
    # Recuperar dades reals de la DB
    conn = db.sqlite3.connect(db.DB_NAME)
    
    # Gràfic de resultats objectius
    df_tests = pd.read_sql_query(f"SELECT * FROM test_results WHERE username='{st.session_state['username']}'", conn)
    
    if not df_tests.empty:
        st.markdown("#### Rendiment Cognitiu")
        fig = px.line(df_tests, x='date', y='score', color='test_type', markers=True, 
                      color_discrete_sequence=['#81C784', '#2E7D32'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Encara no has fet cap test. Fes el teu primer repte a la pestanya 'Avui'!")

    # Historial de símptomes
    df_symptoms = pd.read_sql_query(f"SELECT * FROM daily_checkin WHERE username='{st.session_state['username']}'", conn)
    if not df_symptoms.empty:
        st.markdown("#### Diari de Símptomes")
        st.dataframe(df_symptoms[['date', 'symptom_category']], use_container_width=True)
    
    conn.close()

# ==============================================================================
# PESTANYA 3: RECURSOS
# ==============================================================================
with tab_recursos:
    st.markdown("### 🧘 El Racó de la Calma")
    
    with st.expander("🌱 Mindfulness Bàsic (3 min)"):
        st.write("Asseu-te en una posició còmoda. Tanca els ulls. Centra la teva atenció només en la respiració...")
        st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3") # Àudio placeholder
    
    with st.expander("📅 Estratègies per a la Memòria"):
        st.write("""
        * **L'Agenda:** És el teu "disc dur extern". Apunta-ho tot.
        * **Associació:** Vincula noms nous amb imatges mentals divertides.
        * **Routines:** Deixa les claus sempre al mateix lloc.
        """)
    
    with st.expander("⚡ Activació Mental"):
        st.write("Quan et sentis lent, prova de fer una caminada ràpida de 10 minuts. L'oxigenació ajuda a la velocitat de processament.")