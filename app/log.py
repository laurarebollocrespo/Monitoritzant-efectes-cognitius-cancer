import streamlit as st
import time
from datetime import datetime
import sys
import os

# --- GESTIÓ DE SESSIÓ ---
if 'user' not in st.session_state:
    st.warning("No s'ha trobat l'usuari. Torna a fer login.")
    st.stop()

user = st.session_state.user

# Importem la DB per llegir l'historial (ja que user.py només té el mètode de guardar)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- CSS PERSONALITZAT ---
st.markdown("""
    <style>
    /* Estil de la caixa d'escriptura */
    .stTextArea textarea {
        background-color: #FFF9C4; /* Groc pàl·lid tipus pòsit/paper antic */
        color: #333;
        border: 1px solid #FBC02D;
        border-radius: 10px;
        font-family: 'Courier New', Courier, monospace; /* Tipus màquina d'escriure */
    }
    
    /* Estil de les entrades antigues */
    .log-entry {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #81C784;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .log-date {
        color: #666;
        font-size: 12px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    
    .log-text {
        font-size: 16px;
        color: #2E7D32;
        white-space: pre-wrap; /* Mantenir salts de línia */
    }
    </style>
""", unsafe_allow_html=True)

# --- CAPÇALERA ---
st.title("El teu Diari Personal")
st.write("Un espai segur per escriure com et sents, els teus dubtes o els teus èxits.")

# --- ÀREA D'ESCRIPTURA ---
with st.container():
    nou_text = st.text_area("Escriu aquí el que vulguis...", height=150, placeholder="Avui m'he sentit...")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Guardar Entrada", type="primary", use_container_width=True):
            if nou_text.strip():
                user.registrar_log(nou_text)
                st.success("Guardat al teu diari!")
                st.rerun() # Recarregar per mostrar-ho a l'historial a sota
            else:
                st.warning("El diari està buit.")

st.divider()

# --- HISTORIAL D'ENTRADES ---
st.subheader("Entrades Anteriors")

logs = user.logs

if logs:
    for data, text in logs:
        # Formatar la data perquè sigui més llegible (ex: 2023-10-27 10:30)
        try:
            data_obj = datetime.strptime(data, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            # Fallback si el format és diferent (ex: sense microsegons)
            try:
                data_obj = datetime.strptime(data, "%Y-%m-%d %H:%M:%S")
            except:
                data_obj = datetime.now() # Fallback total
                
        data_bonica = data_obj.strftime("%d/%m/%Y a les %H:%M")
        
        st.markdown(f"""
            <div class="log-entry">
                <div class="log-date">📅 {data_bonica}</div>
                <div class="log-text">{text}</div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("Encara no has escrit res al teu diari. Comença avui!")
