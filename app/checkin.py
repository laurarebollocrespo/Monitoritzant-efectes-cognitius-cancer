import streamlit as st
import time
from datetime import datetime

# --- CONFIGURACIÓ DE PÀGINA (Només si s'executa sol, però main.py ja ho gestiona) ---
# st.set_page_config(page_title="Check-in Diari", page_icon="😊")

# --- RECUPERAR L'USUARI ACTUAL ---
if 'user' not in st.session_state:
    st.error("No s'ha trobat l'usuari. Si us plau, torna a fer login.")
    st.stop()

user = st.session_state['user']

# --- CSS PERSONALITZAT PER AL CHECK-IN ---
st.markdown("""
    <style>
    .checkin-container {
        background-color: #F0FFF4;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
    }
    .checkin-title {
        color: #2E7D32;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .checkin-subtitle {
        color: #558B2F;
        font-size: 18px;
        margin-bottom: 30px;
    }
    
    /* Estilitzar el slider per fer-lo més amable (limitat en Streamlit pur, però ho intentem) */
    .stSlider > div > div > div > div {
        background-color: #81C784;
    }
    </style>
""", unsafe_allow_html=True)

# --- CAPÇALERA ---
st.markdown("<div class='checkin-container'>", unsafe_allow_html=True)
st.markdown(f"<div class='checkin-title'>Bon dia, {user.name}! ☀️</div>", unsafe_allow_html=True)
st.markdown("<div class='checkin-subtitle'>Com sents el teu cap avui?</div>", unsafe_allow_html=True)

# --- LÒGICA DEL CHECK-IN ---

# Comprovar si ja ha fet check-in avui
avui = datetime.now().strftime("%Y-%m-%d")
valor_anterior = user.daily_check_in.get(avui, 3) # Per defecte 3 si no hi és

# Definició de les cares/estats
cares = {
    1: "😫 Molt boirós/Lent",
    2: "😕 Una mica espès",
    3: "😐 Normal / Regular",
    4: "🙂 Bastant bé",
    5: "😁 Molt clar i àgil"
}

# Utilitzem un select_slider perquè és més visual que un slider numèric
estat_anim = st.select_slider(
    "Selecciona el teu estat:",
    options=[1, 2, 3, 4, 5],
    value=valor_anterior,
    format_func=lambda x: cares[x]
)

# Visualització gran de l'emoji seleccionat
emojis_grans = {
    1: "😫", 2: "😕", 3: "😐", 4: "🙂", 5: "😁"
}
st.markdown(f"<div style='font-size: 80px; margin: 20px 0;'>{emojis_grans[estat_anim]}</div>", unsafe_allow_html=True)

# Botó de guardar
if st.button("Guardar el meu estat", use_container_width=True, type="primary"):
    # Guardar a través de l'objecte User (que guarda a DB)
    user.registrar_checkin(estat_anim)
    
    st.balloons()
    st.success("Registrat correctament! Gràcies per compartir-ho.")
    
    # Feedback personalitzat segons la puntuació
    if estat_anim <= 2:
        st.info("💡 Avui sembla un dia difícil. No et forcis. Prova el recurs de **Mindfulness** a la secció d'Eines.")
    elif estat_anim >= 4:
        st.info("🌟 Fantàstic! És un bon moment per provar un test de **Velocitat** o **Memòria**.")
    
    time.sleep(3)
    st.switch_page("app/homepage.py")

st.markdown("</div>", unsafe_allow_html=True)

# --- MOSTRAR HISTÒRIC RECENT (OPCIONAL) ---
with st.expander("Veure els meus últims dies"):
    if user.daily_check_in:
        # Convertir a llista per mostrar
        dates = list(user.daily_check_in.keys())[-7:] # Últims 7 dies
        valors = [user.daily_check_in[d] for d in dates]
        
        # Petit gràfic de línies simple
        st.line_chart(valors)
    else:
        st.write("Encara no tens registres anteriors.")