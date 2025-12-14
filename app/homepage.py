import streamlit as st
import base64
import os
from streamlit_image_coordinates import streamlit_image_coordinates

# --- GESTIÓ DE SESSIÓ ---
if 'user' not in st.session_state:
    print('HOLAAAAAAA ')
    st.switch_page("app/login.py")


user = st.session_state.user
games_state = user.games_played

def get_dynamic_brain_image(games_state):
    """
    Converteix l'estat [0, 1, 0, 1] en el nom del fitxer.
    """
    # Convertim booleans a string binari (ex: "1010")
    binary_suffix = "".join([str(x) for x in games_state])
    
    # Ruta esperada (assegura't que el nom del fitxer coincideix amb el que tens a la carpeta)
    expected_path = f"images/brain_{binary_suffix}-removebg-preview.png"
    
    # FALLBACK
    if os.path.exists(expected_path):
        return expected_path
    else:
        # Si no troba la imatge exacta, lògica de seguretat:
        if any(games_state):
             # Si tens una imatge genèrica acolorida, posa-la aquí:
             return "images/brain_areas.png" 
        else:
             # Imatge per defecte (tot gris)
             return "images/brain_0000.png" 

# --- CARREGAR IMATGES (PER AL LOGO HTML) ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

# 1. Calculem quina imatge del cervell toca (RUTA)
BRAIN_PATH = get_dynamic_brain_image(games_state)

# 2. Carreguem el logo en Base64 (per al HTML/CSS)
LOGO_B64 = get_base64_image("images/logo.png")

# --- CSS PERSONALITZAT ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Poppins', sans-serif;
    }}

    /* HEADER PERSONALITZAT */
    .custom-header {{
        background-color: #A8E6CF;
        padding: 10px 30px;
        display: flex;
        justify_content: space-between;
        align-items: center;
        border-bottom: 3px solid #8FD9BF;
        margin-bottom: 20px;
        color: #333;
    }}
    
    .logo-img {{ height: 40px; margin-right: 10px; vertical-align: middle; }}
    
    .header-right {{ font-size: 18px; display: flex; gap: 30px; align-items: center; }}
    
    .logout-text {{ font-weight: bold; cursor: pointer; }}

    /* BENVINGUDA */
    .welcome-container {{
        background-color: #E0F7FA;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 30px;
    }}
    
    h1 {{ color: black; font-size: 32px; font-weight: 800; margin: 0; padding: 0; }}
    h2 {{ color: #333; font-size: 20px; font-weight: 400; margin: 0; margin-bottom: 5px; }}
    
    .streak {{ font-size: 16px; color: #555; display: flex; align-items: center; gap: 5px; margin-top: 10px; }}

    /* BOTONS D'ACCIÓ */
    .stButton button {{
        background-color: #98D8C1 !important; color: black !important; border: none !important;
        border-radius: 30px !important; padding: 15px 20px !important; font-weight: bold !important;
        font-size: 16px !important; box-shadow: 0px 4px 6px rgba(0,0,0,0.1) !important;
        width: 100%; transition: transform 0.1s;
    }}
    .stButton button:hover {{ background-color: #86C9B5 !important; transform: translateY(-2px); }}
    
    .eines-title {{ text-align: right; font-size: 36px; margin-top: 50px; font-weight: 300; color: black; letter-spacing: 1px; }}
    
    .vertical-line {{ border-left: 1px solid #ccc; height: 100%; margin: 0 auto; }}
    </style>
""", unsafe_allow_html=True)

# --- ZONA BENVINGUDA ---
st.markdown(f"""
    <div class="welcome-container">
        <h2>Hola,</h2>
        <h1>{user.name}</h1>
        <div class="streak">
            🔥 {user.streak} dies seguits
        </div>
    </div>
""", unsafe_allow_html=True)


# --- LAYOUT CENTRAL ---
col_brain, col_sep, col_actions = st.columns([1.5, 0.1, 1])

# 1. CERVELL INTERACTIU (ESQUERRA)
with col_brain:
    st.write("") # Espai
    
    # CORRECCIÓ PRINCIPAL AQUÍ:
    if os.path.exists(BRAIN_PATH):
        # Passem la RUTA (BRAIN_PATH), no el base64
        coords = streamlit_image_coordinates(
            BRAIN_PATH,
            width=350,
            key="brain_nav"
        )
        
        # LÒGICA DE NAVEGACIÓ
        if coords:
            x, y = coords['x'], coords['y']
            
            # Quadrant Superior Esquerre: Fluència
            if x < 250 and y < 200:
                st.switch_page("app/tests/fluencia.py")
            # Quadrant Superior Dret: Atenció
            elif x > 250 and y < 200:
                st.switch_page("app/tests/atencio.py")
            # Quadrant Inferior Esquerre: Memòria
            elif x < 250 and y > 200:
                st.switch_page("app/tests/memoria.py")
            # Quadrant Inferior Dret: Velocitat
            elif x > 250 and y > 200:
                st.switch_page("app/tests/velocitat.py")
    else:
        st.error(f"No s'ha trobat la imatge: {BRAIN_PATH}")
        st.info("Assegura't que les imatges existeixen a la carpeta 'images/'")

# 2. SEPARADOR (CENTRE)
with col_sep:
    st.markdown('<div style="border-left: 2px solid #ddd; height: 400px; margin: auto;"></div>', unsafe_allow_html=True)

# 3. ACCIONS RÀPIDES (DRETA)
with col_actions:
    st.write("")
    st.write("")
    
    if st.button("Com em sento avui?"):
        st.switch_page("app/checkin.py")
        
    st.write("")
    
    if st.button("Què m'ha passat?"):
        st.switch_page("app/incidencies.py")
            
    if st.button("Veure totes les eines ->", key="btn_eines", use_container_width=True):
        st.switch_page("app/eines.py")