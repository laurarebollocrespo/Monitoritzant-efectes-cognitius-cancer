import streamlit as st
import time
from datetime import datetime
import base64

# --- FUNCIÓ PER LLEGIR IMATGES (Mantenim la teva lògica) ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

def img_base64_html(base64_str, width=100):
    if base64_str is None: return ""
    return f'<img src="data:image/png;base64,{base64_str}" style="width:{width}px; display:block; margin:auto;">'

# --- CARREGAR IMATGES ---
# Assegura't que les rutes són correctes
FACE1 = img_base64_html(get_base64_of_bin_file("images/1.png"))
FACE2 = img_base64_html(get_base64_of_bin_file("images/2.png"))
FACE3 = img_base64_html(get_base64_of_bin_file("images/3.png"))
FACE4 = img_base64_html(get_base64_of_bin_file("images/4.png"))
FACE5 = img_base64_html(get_base64_of_bin_file("images/5.png"))


user = st.session_state.user

# --- CSS NECESSARI ---
st.markdown("""
    <style>
    /* Part de dalt de la targeta */
    .header-card {
        background-color: #F0FFF4; /* Verd molt suau */
        padding: 25px 20px 10px 20px;
        border-radius: 20px 20px 0 0; /* Arrodonit DALT */
        text-align: center;
        margin-bottom: 0px;
    }
    
    /* Part de baix de la targeta */
    .footer-card {
        background-color: #F0FFF4; /* Mateix verd */
        padding: 10px 20px 25px 20px;
        border-radius: 0 0 20px 20px; /* Arrodonit BAIX */
        text-align: center;
        margin-top: 0px;
    }

    /* Targeta completa (quan ja ha votat) */
    .full-card {
        background-color: #F0FFF4;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }

    .title-text { color: #2E7D32; font-size: 24px; font-weight: bold; }
    .subtitle-text { color: #558B2F; font-size: 16px; margin-bottom: 10px; }
    .result-text { font-size: 22px; font-weight: 600; color: #2E7D32; margin-top: 10px; }
    
    /* Truc visual: treure marge al slider perquè s'enganxi visualment */
    div[data-testid="stSlider"] {
        margin-top: -20px;
        padding-bottom: 0px;
    }
    </style>
""", unsafe_allow_html=True)

# --- LÒGICA PRINCIPAL ---
avui = datetime.now().strftime("%Y-%m-%d")
valor_anterior = user.daily_check_in.get(avui)

cares = {
    1: (FACE1, "Molt boirós / Lent"),
    2: (FACE2, "Una mica espès"),
    3: (FACE3, "Normal / Regular"),
    4: (FACE4, "Bastant bé"),
    5: (FACE5, "Molt clar i àgil")
}

# -----------------------------------------------
# CAS 1: JA HA REGISTRAT AVUI (Targeta única)
# -----------------------------------------------
if valor_anterior is not None:
    face_html, label = cares[valor_anterior]
    
    st.markdown(f"""
        <div class="full-card">
            <div class="title-text">Bon dia, {user.name}! ☀️</div>
            <div class="subtitle-text">Avui has registrat:</div>
            <div style="margin: 20px 0;">{face_html}</div>
            <div class="result-text">{label}</div>
        </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------
# CAS 2: ENCARA NO HA REGISTRAT (Targeta Partida)
# -----------------------------------------------
else:
    # 1. BLOC SUPERIOR (HTML PUR)
    st.markdown(f"""
        <div class="header-card">
            <div class="title-text">Bon dia, {user.name}! ☀️</div>
            <div class="subtitle-text">Com sents el teu cap avui?</div>
        </div>
    """, unsafe_allow_html=True)

    # 2. SLIDER (WIDGET STREAMLIT)
    # Està fora del div, però visualment semblarà a dins pel CSS
    valor_defecte = 3
    estat_anim = st.select_slider(
        "Selecciona el teu estat", # Label invisible per accessibilitat
        options=[1, 2, 3, 4, 5],
        value=valor_defecte,
        format_func=lambda x: "", # No mostrem text al slider, només els punts
        label_visibility="collapsed"
    )
    
    # Calculem què mostrar segons el slider
    face_html, label = cares[estat_anim]

    # 3. BLOC INFERIOR (HTML PUR)
    st.markdown(f"""
        <div class="footer-card">
            <div style="margin-top: 0px; margin-bottom: 15px;">
                <div style="transform: scale(1.2);">
                    {face_html}
                </div>
            </div>
            <div class="result-text">{label}</div>
        </div>
    """, unsafe_allow_html=True)

    # 4. BOTÓ (Natiu Streamlit)
    if st.button("Guardar el meu estat", type="primary", use_container_width=True):
        user.registrar_checkin(estat_anim)
        # Feedback personalitzat segons la puntuació
        if estat_anim <= 2:
            st.info("💡 Avui sembla un dia difícil. No et forcis. Prova el recurs de **Mindfulness** a la secció d'Eines.")
        elif estat_anim >= 4:
            st.info("🌟 Fantàstic! És un bon moment per provar un test de **Velocitat** o **Memòria**.")
            st.balloons()

st.write("") # Espai

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