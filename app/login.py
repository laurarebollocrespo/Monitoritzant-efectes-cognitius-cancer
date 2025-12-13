import streamlit as st
import time
import base64
from app.user import User
from app import database as db

# --- PAGE CONFIG ---
st.set_page_config(page_title="OncoConnect", layout="wide")

# --- UTILS ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

# Load Images
BACKGROUND_PATH = "images/background_login.png"
LOGO_PATH = "images/logo.png"

bg_base64 = get_base64_of_bin_file(BACKGROUND_PATH)
logo_base64 = get_base64_of_bin_file(LOGO_PATH)

# --- CSS STYLING ---
# We inject CSS to handle the background, the font, and the specific "Card" look
st.markdown(f"""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
    /* 1. GLOBAL FONT */
    html, body, [class*="css"] {{
        font-family: 'Poppins', sans-serif;
    }}

    /* 2. BACKGROUND IMAGE */
    .stApp {{
        background-image: url("data:image/png;base64,{bg_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    /* 3. REMOVE DEFAULT STREAMLIT PADDING (To move logo up) */
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 0rem;
    }}
    
    /* 4. HIDE STREAMLIT ELEMENTS */
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    [data-testid="stSidebar"] {{display: none;}}

    /* 5. THE LOGIN CARD (GREY RECTANGLE) 
       This targets the middle column (col2) specifically.
    */
    div[data-testid="column"]:nth-of-type(2) {{
        background-color: #f4f4f4; /* Light Grey/Beige background */
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1); /* Soft shadow for depth */
        border: 1px solid rgba(0,0,0,0.05);
    }}

    /* 6. INPUT FIELDS */
    .stTextInput input {{
        border: 2px solid #A8E6CF !important; /* Green border */
        border-radius: 12px !important;
        padding: 10px 15px !important;
        background-color: #FFF !important;
        color: #333 !important;
    }}
    
    /* Labels (Usuari / Contrasenya) */
    .stTextInput label {{
        font-size: 14px !important;
        color: #555 !important;
        margin-bottom: 5px !important;
    }}

    /* 7. BUTTON */
    .stButton button {{
        background-color: #98D8C1 !important; /* Green button */
        color: black !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 12px !important;
        font-weight: 600 !important;
        width: 100% !important;
        margin-top: 10px;
    }}
    .stButton button:hover {{
        background-color: #86C1AD !important;
    }}
    
    </style>
""", unsafe_allow_html=True)

# --- HEADER SECTION (Logo + Name) ---
# We use HTML/Flexbox to position it exactly where we want (Upper Left)
logo_img_tag = f'<img src="data:image/png;base64,{logo_base64}" width="50" style="margin-right: 15px;">' if logo_base64 else "🌸"

st.markdown(f"""
    <div style="
        display: flex; 
        align-items: center; 
        justify-content: flex-start; /* Change to flex-end if you really want it on the right */
        margin-bottom: 40px; 
        margin-left: 10px;">
        {logo_img_tag}
        <span style="font-size: 32px; font-weight: 600; color: #1a1a1a; letter-spacing: -0.5px;">
            OncoConnect
        </span>
    </div>
""", unsafe_allow_html=True)


# --- LOGIN FORM SECTION ---
# We use 3 columns. The middle one (col2) gets the "Grey Rectangle" style from the CSS above.
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    # Inputs
    username = st.text_input("Usuari", placeholder="Introdueix el teu usuari")
    password = st.text_input("Contrasenya", type="password", placeholder="********")
    
    st.write("") # Spacer
    
    # Button
    if st.button("Entrar"):
        user_data = db.check_login(username, password)

        if user_data:
            st.session_state.logged_in = True
            st.session_state.games_played = [False]*4  # Reset games played
            current_user = User(username)
            st.session_state.admin = current_user.admin
            st.session_state.user = current_user
            st.success(f"Benvingut {current_user.name}!")
            st.rerun()
            
        elif username == "" or password == "":
            st.warning("Omple tots els camps.")
        else:
            st.error("Dades incorrectes.")