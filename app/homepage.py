import streamlit as st
import base64
import os
from streamlit_image_coordinates import streamlit_image_coordinates

# --- GESTIÓ DE SESSIÓ ---
if 'user' not in st.session_state:
    st.switch_page("app/login.py")

# Inicialitzar estat dels jocs si no existeix (per seguretat)
if 'games_played' not in st.session_state:
    # Indexs: 0:Fluencia, 1:Atencio, 2:Memoria, 3:Velocitat
    st.session_state.games_played = [False, False, False, False]
user = st.session_state.user


def get_dynamic_brain_image(games_state):
    """
    Converteix l'estat [True, False, True, False] en el nom del fitxer "brain_1010.png"
    """
    # Convertim booleans a string binari (ex: "1010")
    binary_suffix = "".join(["1" if game else "0" for game in games_state])
    
    # Ruta esperada
    expected_path = f"images/brain_states/brain_{binary_suffix}.png"
    
    # FALLBACK: Si la imatge exacta no existeix (per si no heu tingut temps de fer les 16),
    # mostrem la imatge totalment acolorida o la totalment grisa com a seguretat.
    if os.path.exists(expected_path):
        return expected_path
    else:
        # Si han jugat alguna cosa, mostrem el full color, sino el gris.
        if any(games_state):
             return "images/brain_areas.png" # La imatge original (tota color)
        else:
             return "images/brain_states/brain_0000.png" # Assegura't de tenir almenys la 0000 feta!
        

# --- CARREGAR IMATGES ---
def get_base64_image(image_path):
    # Busquem la imatge des de l'arrel del projecte
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

# Rutes a les imatges (des de l'arrel on s'executa main.py)
LOGO_B64 = get_base64_image("images/logo.png")
BRAIN_B64 = get_base64_image(get_dynamic_brain_image(st.session_state.games_played))

# --- CSS PERSONALITZAT (ESTIL EXACTE REFERÈNCIA) ---
st.markdown(f"""
    <style>
    /* Importar font neta */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Poppins', sans-serif;
    }}

    /* 1. HEADER PERSONALITZAT */
    .custom-header {{
        background-color: #A8E6CF; /* Verd fons capçalera */
        padding: 10px 30px;
        display: flex;
        justify_content: space-between;
        align-items: center;
        border-bottom: 3px solid #8FD9BF;
        margin-bottom: 20px;
        color: #333;
    }}
    
    .logo-img {{
        height: 40px;
        margin-right: 10px;
        vertical-align: middle;
    }}
    
    .header-right {{
        font-size: 18px;
        display: flex;
        gap: 30px;
        align-items: center;
    }}
    
    .logout-text {{
        font-weight: bold;
        cursor: pointer; /* Visualment sembla clicable */
    }}

    /* 2. BENVINGUDA */
    .welcome-container {{
        background-color: #E0F7FA; /* Blau/Verd molt clar de fons */
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 30px;
    }}
    
    h1 {{
        color: black;
        font-size: 32px;
        font-weight: 800;
        margin: 0;
        padding: 0;
    }}
    
    h2 {{
        color: #333;
        font-size: 20px;
        font-weight: 400;
        margin: 0;
        margin-bottom: 5px;
    }}
    
    .streak {{
        font-size: 16px;
        color: #555;
        display: flex;
        align-items: center;
        gap: 5px;
        margin-top: 10px;
    }}

    /* 3. BOTONS D'ACCIÓ (DRETA) */
    .stButton button {{
        background-color: #98D8C1 !important;
        color: black !important;
        border: none !important;
        border-radius: 30px !important; /* Molt rodons */
        padding: 15px 20px !important;
        font-weight: bold !important;
        font-size: 16px !important;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1) !important;
        width: 100%;
        transition: transform 0.1s;
    }}
    
    .stButton button:hover {{
        background-color: #86C9B5 !important;
        transform: translateY(-2px);
    }}
    
    .eines-title {{
        text-align: right;
        font-size: 36px;
        margin-top: 50px;
        font-weight: 300;
        color: black;
        letter-spacing: 1px;
    }}
    
    /* Separador vertical */
    .vertical-line {{
        border-left: 1px solid #ccc;
        height: 100%;
        margin: 0 auto;
    }}
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
    
    if os.path.exists(BRAIN_PATH):
        # Renderitzar imatge i capturar click
        coords = streamlit_image_coordinates(
            BRAIN_PATH,
            width=500, # Amplada fixa per calibrar bé els clicks
            key="brain_nav"
        )
        
        # LÒGICA DE NAVAGACIÓ SEGONS COORDENADES
        # (Ajusta aquests valors segons la teva imatge de 500px d'ample)
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
                
            # Quadrant Inferior Dret: Velocitat (Agilitat)
            elif x > 250 and y > 200:
                st.switch_page("app/tests/velocitat.py")
    else:
        st.error(f"No s'ha trobat la imatge: {BRAIN_PATH}. Assegura't que està a la carpeta images/")

# 2. SEPARADOR (CENTRE)
with col_sep:
    st.markdown('<div style="border-left: 2px solid #ddd; height: 400px; margin: auto;"></div>', unsafe_allow_html=True)

# 3. ACCIONS RÀPIDES (DRETA)
with col_actions:
    st.write("")
    st.write("")
    
    if st.button("Com em sento avui?"):
        st.switch_page("app/checkin.py")
        
    st.write("") # Espai
    
    if st.button("Què m'ha passat?"):
        st.switch_page("app/incidencies.py")
            
    # Àrea clicable per anar a Eines (com a botó invisible o botó text)
    if st.button("Veure totes les eines ->", key="btn_eines", use_container_width=True):
        st.switch_page("app/eines.py")
