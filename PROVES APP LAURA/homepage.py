import streamlit as st
import sys
import os
import base64
from streamlit_image_coordinates import streamstreamlit_image_coordinates

# --- IMPORTAR BASE DE DADES ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pages.database as db

# --- CONFIGURACIÓ DE PÀGINA ---
st.set_page_config(
    page_title="OncoConnect - Panell",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- VERIFICAR LOGIN ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.switch_page("login.py")

# --- FUNCIÓ PER LLEGIR IMATGES EN BASE64 (Per al Header) ---
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

flower_icon = get_img_as_base64("imatges/flower_icon.png") # Assegura't que existeix

# --- CSS PERSONALITZAT (ESTIL EXACTE A LA IMATGE) ---
st.markdown(f"""
    <style>
    /* Importar fonts */
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Open Sans', sans-serif;
    }}

    /* Amagar elements per defecte */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* HEADER PERSONALITZAT (Barra verda de dalt) */
    .custom-header {{
        background-color: #98D8C1; /* Verd fosc de la imatge */
        padding: 10px 30px;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        z-index: 999;
        display: flex;
        justify_content: space-between;
        align-items: center;
        height: 60px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
    }}
    
    .header-logo img {{
        height: 40px;
    }}
    
    .header-user {{
        font-size: 18px;
        color: #333;
        display: flex;
        gap: 20px;
        align-items: center;
    }}
    
    .logout-btn {{
        cursor: pointer;
        font-weight: bold;
    }}

    /* FONS DE LA PÀGINA PRINCIPAL (Verd molt clar) */
    .stApp {{
        background-color: #F0FFF4; /* Verd molt molt suau */
        margin-top: 40px; /* Espai pel header fix */
    }}

    /* CAIXA DE BENVINGUDA */
    .welcome-box {{
        padding: 20px 0px;
        margin-bottom: 20px;
    }}
    
    .streak-badge {{
        display: inline-flex;
        align-items: center;
        background-color: #FFF;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        color: #555;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }}

    /* BOTONS DRETA */
    .action-button {{
        display: block;
        width: 100%;
        background-color: #98D8C1;
        color: black;
        text-align: center;
        padding: 15px;
        border-radius: 30px;
        font-weight: bold;
        text-decoration: none;
        margin-bottom: 15px;
        border: none;
        transition: 0.3s;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }}
    .action-button:hover {{
        background-color: #7BC4A8;
        color: black;
    }}

    /* TITOL EINES */
    .tools-title {{
        text-align: right;
        font-size: 30px;
        font-weight: 300; /* Lletra fina */
        margin-top: 50px;
        letter-spacing: 2px;
    }}
    
    /* Separador vertical */
    .vertical-line {{
        border-left: 1px solid #ccc;
        height: 100%;
        position: absolute;
        left: 50%;
    }}

    </style>
    
    <div class="custom-header">
        <div class="header-logo">
            <img src="data:image/png;base64,{flower_icon}" alt="Logo">
        </div>
        <div class="header-user">
            <span>{st.session_state.get('username', 'Usuari')}</span>
            <span class="logout-btn">Sortir</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- BENVINGUDA ---
st.markdown("<div class='welcome-box'>", unsafe_allow_html=True)
st.markdown(f"## Hola,")
st.markdown(f"# {st.session_state.get('real_name', 'Nom Cognom')}")
st.markdown("""
    <div class="streak-badge">
        🔥 15 dies
    </div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)


# --- LAYOUT PRINCIPAL (2 COLUMNES) ---
col_brain, col_sep, col_actions = st.columns([1.5, 0.1, 1])

# --- COLUMNA ESQUERRA: CERVELL CLICABLE ---
with col_brain:
    st.write("") # Espaiat
    
    # RUTA DE LA IMATGE DEL CERVELL
    brain_image_path = "imatges/brain_areas.png" 
    
    # CALIBRATGE DE COORDENADES (IMPORTANT!)
    # Quan tinguis la imatge final, clica a les zones i mira la terminal per veure les coordenades X i Y.
    # Després ajusta els números dels 'if' de sota.
    
    # Renderitzar la imatge clicable
    coords = streamlit_image_coordinates(
        brain_image_path,
        key="brain_click",
        width=500 # Ajusta l'amplada segons la teva imatge
    )
    
    # LÒGICA DE REDIRECCIÓ SEGONS EL CLICK
    if coords:
        x = coords['x']
        y = coords['y']
        
        # Exemple de lògica (HAS D'AJUSTAR ELS NÚMEROS A LA TEVA IMATGE REAL):
        # Imagina que la imatge fa 500x400 píxels
        
        # 1. Zona FLUÈNCIA (Superior Esquerra - Groc)
        if x < 250 and y < 200:
            st.session_state['current_test'] = 'fluencia'
            st.switch_page("pages/fluencia.py") # Crea aquest fitxer!
            
        # 2. Zona ATENCIÓ (Superior Dreta - Blau)
        elif x > 250 and y < 200:
            st.session_state['current_test'] = 'atencio'
            st.switch_page("pages/atencio.py") # Crea aquest fitxer!
            
        # 3. Zona MEMÒRIA (Inferior Esquerra - Verd)
        elif x < 250 and y > 200:
            st.session_state['current_test'] = 'memoria'
            st.switch_page("pages/memoria.py") # Crea aquest fitxer!
            
        # 4. Zona AGILITAT/VELOCITAT (Inferior Dreta - Rosa)
        elif x > 250 and y > 200:
            st.session_state['current_test'] = 'velocitat'
            st.switch_page("pages/velocitat.py") # Crea aquest fitxer!

# --- SEPARADOR VISUAL ---
with col_sep:
    # Línia vertical dibuixada amb CSS/HTML o buida
    st.markdown("""
        <div style="border-left: 2px solid #ccc; height: 400px; margin: auto;"></div>
    """, unsafe_allow_html=True)

# --- COLUMNA DRETA: BOTONS D'ACCIÓ ---
with col_actions:
    st.write("")
    st.write("")
    
    # Botons fets amb HTML per tenir el control total de l'estil (rounded corners, colors)
    # Nota: Per fer-los funcionals en Streamlit pur, utilitzem st.button però injectem estil,
    # o utilitzem callbacks. Aquí usarem st.button estàndard amb l'estil CSS definit a dalt.
    
    # Per aplicar l'estil CSS definit a dalt als st.button, hem de fer un petit truc o usar els botons natius
    # que ja hem estilitzat parcialment. Per clavar el disseny rodó de la imatge:
    
    if st.button("Com em sento avui?", key="btn_feel", use_container_width=True):
        # Obrir modal o anar a pàgina de check-in
        pass # Aquí posaries la lògica
        
    st.write("") # Espai
    
    if st.button("Què m'ha passat?", key="btn_what", use_container_width=True):
        # Obrir modal de símptomes
        pass 

    st.markdown("<div class='tools-title'>EINES</div>", unsafe_allow_html=True)

# --- GESTIÓ DEL LOGOUT ---
# Com que el botó de sortida és HTML pur al header, no podem detectar el click directament amb Python fàcilment.
# PER LA HACKATHON: Podeu posar un botó de 'Sortir' petit al final de la pàgina o a la barra lateral
# com a funcionalitat real, i deixar el del header com a decoratiu, O fer servir st.components.v1.html amb retorn (més complex).
# Opció senzilla:
with st.sidebar:
    if st.button("Tancar Sessió"):
        st.session_state['logged_in'] = False
        st.switch_page("login.py")