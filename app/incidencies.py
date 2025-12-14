import streamlit as st
import time

# --- GESTIÓ DE SESSIÓ ---
if 'user' not in st.session_state:
    st.warning("No s'ha trobat l'usuari. Torna a fer login.")
    st.stop()

user = st.session_state.user

# --- DADES: LES 10 AFIRMACIONS DEL REPTE ---
INCIDENCIES_MAP = {
    0: {"text": "He anat a un lloc i no recordava què hi anava a fer", "tipus": "Atenció"},
    1: {"text": "He trigat més del normal a fer una activitat rutinària", "tipus": "Velocitat"},
    2: {"text": "Volia dir una paraula i no m'ha sortit (punta de la llengua)", "tipus": "Fluència"},
    3: {"text": "He perdut el fil de la conversa mentre parlava", "tipus": "Atenció"},
    4: {"text": "No he recordat una cosa que m'acabaven de dir", "tipus": "Memòria"},
    5: {"text": "He oblidat informació que ja sabia d'abans", "tipus": "Memòria"},
    6: {"text": "M'ha costat molt prendre una decisió senzilla", "tipus": "Funcions Executives"},
    7: {"text": "He tingut dificultats per planificar el meu dia", "tipus": "Funcions Executives"},
    8: {"text": "Tinc sensació de 'nebulosa mental' (cap espès)", "tipus": "Fatiga"},
    9: {"text": "Sento que penso molt més a poc a poc avui", "tipus": "Velocitat"}
}

# --- CONSELLS PER CATEGORIA ---
CONSELLS = {
    "Atenció": "**No et frustris.** Atura't un moment. Respira fons 3 vegades i intenta fer només UNA cosa a la vegada. La multitasca és l'enemic ara mateix.",
    "Velocitat": "**Pren-t'ho amb calma.** És normal anar més lent. Dona't permís per trigar més. Si pots, surt a caminar 5 minuts per oxigenar el cervell.",
    "Fluència": "**Busca un sinònim.** Si no surt la paraula, intenta explicar-la amb altres paraules o descriure-la. No et bloquegis intentant forçar la memòria.",
    "Memòria": "**Utilitza ajudes externes.** No confiïs només en el teu cap avui. Apunta-ho tot a l'agenda o posa't una alarma al mòbil immediatament.",
    "Funcions Executives": "**Divideix i venceràs.** Si una tasca sembla massa gran o confusa, divideix-la en passos molt petits i fes només el primer.",
    "Fatiga": "**Descansa.** El teu cervell t'està demanant una pausa. Tanca els ulls 5 minuts en silenci."
}

# --- CSS PERSONALITZAT ---
st.markdown("""
    <style>
    .incidencia-card {
        background-color: #FFF3E0; /* Taronja molt suau */
        padding: 30px;
        border-radius: 15px;
        border-left: 5px solid #FFB74D;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Estil personalitzat per als checkboxes per fer-los més grans */
    .stCheckbox label {
        font-size: 16px;
        padding: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- INTERFÍCIE ---

st.markdown("<div class='incidencia-card'>", unsafe_allow_html=True)
st.title("Què t'ha passat?")
st.write("Selecciona totes les situacions que hagis viscut avui. Això ens ajuda a personalitzar el teu tractament.")

st.write("") # Espai

# --- SELECCIÓ MÚLTIPLE (CHECKBOXES) ---
# Creem un diccionari per guardar l'estat de cada checkbox
seleccions = []

# Iterem per crear els checkboxes
for id_inc, data in INCIDENCIES_MAP.items():
    # El key ha de ser únic per cada checkbox
    if st.checkbox(data["text"], key=f"inc_{id_inc}"):
        seleccions.append(id_inc)

st.write("") # Espai
st.markdown("---")

if st.button("Registrar Incidències", use_container_width=True, type="primary"):
    if len(seleccions) > 0:

        tipus_detectats = set()
        
        for id_inc in seleccions:
            # Guardem a la DB
            user.registrar_incidencia(id_inc)
            # Guardem el tipus per donar consell després
            tipus_detectats.add(INCIDENCIES_MAP[id_inc]["tipus"])
        
        # 2. Feedback
        st.success(f"S'han registrat {len(seleccions)} incidències correctament.")
        
        st.markdown("### Consells per a ara mateix:")
        
        for tipus in tipus_detectats:
            consell = CONSELLS.get(tipus, "Pren-t'ho amb calma.")
            st.info(f"**Per a problemes de {tipus}:** {consell}")

        # Retorn automàtic a casa
        time.sleep(8) # Donem temps per llegir els consells
        st.switch_page("app/homepage.py")
        
    else:
        st.error("Si us plau, selecciona almenys una opció abans de registrar.")

st.markdown("</div>", unsafe_allow_html=True)