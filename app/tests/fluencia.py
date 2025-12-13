import streamlit as st
import random
import time
from difflib import get_close_matches
import openai
import threading

# -----------------------------
# Dataset de palabras
# -----------------------------
fields = {  
    "frutas": [
        "manzana", "pera", "plátano", "naranja", "fresa", "melón", "sandía", "kiwi", "mango", "cereza",
        "limón", "piña", "mandarina", "arándano", "coco", "papaya", "maracuyá", "guayaba", "higo", "ciruela",
        "frambuesa", "mora", "lichi", "caqui", "granada", "pomelo", "nectarina", "albaricoque", "uva", "plumón"
    ],
    "animales": [
        "gato", "perro", "elefante", "tigre", "león", "jirafa", "caballo", "oveja", "conejo", "mono",
        "tiburón", "colibrí", "cerdo", "lobo", "oso", "zorro", "pingüino", "delfín", "ballena", "águila",
        "águila calva", "búho", "halcón", "lince", "camello", "cabra", "vaca", "pollo", "gallina", "pato",
        "ganso", "tortuga", "rana", "serpiente", "iguana", "murciélago", "orca", "foca", "nutria", "canguro"
    ],
    "colores": [
        "rojo", "azul", "verde", "amarillo", "negro", "blanco", "morado", "rosa", "naranja", "gris",
        "cian", "magenta", "lila", "turquesa", "beige", "ocre", "fucsia", "lavanda", "marfil", "bronce",
        "esmeralda", "salmón", "carmesí", "añil", "granate", "púrpura", "azafrán", "marrón", "mostaza", "verde oliva"
    ],
    "transportes": [
        "coche", "autobús", "bicicleta", "moto", "avión", "tren", "barco", "metro", "tranvía", "patinete",
        "camión", "helicóptero", "ferry", "submarino", "globlo aerostático", "monopatín", "velero", "yate", "trineo", "caravana"
    ],
    "ropa": [
        "camisa", "pantalón", "falda", "vestido", "chaqueta", "abrigo", "zapato", "bota", "sandalia", "gorra",
        "sombrero", "bufanda", "guantes", "calcetines", "cinturón", "traje", "camiseta", "jersey", "chaquetón", "chaleco"
    ]
}

field_representatives = {
    "frutas": "fruta",
    "animales": "animal",
    "colores": "color",
    "transportes": "vehículo",
    "ropa": "prenda de ropa"
}

# -----------------------------
# Letras válidas
# -----------------------------
valid_letters = [l for l in "abcdefghijklmnopqrstuvwxyz" if l not in "wxyzhkgq"]

all_words = set()
all_words_list = []

with open("noms-fdic.txt", "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            word = line.split("=")[0].strip()  # tomamos la palabra antes del '='
            all_words.add(word.lower())
            all_words_list.append(word.lower())  # para get_close_matches

TEST_DURATION = 60
# -----------------------------
# Configuración OpenAI
# -----------------------------
API_KEY = "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"
client = openai.OpenAI(api_key=API_KEY)

# -----------------------------
# Validaciones
# -----------------------------
def validar_letra(word, letter):
    w = word.lower().strip()

    if w in st.session_state.used_words:
        return "incorrect"

    if not w.startswith(letter):
        return "incorrect"

    if w in all_words or get_close_matches(w, all_words, cutoff=0.8):
        return "correct"

    return "pending"


def validar_campo(word, field):
    w = word.lower().strip()

    if w in st.session_state.used_words:
        return "incorrect"

    if w in fields[field] or get_close_matches(w, fields[field], cutoff=0.8):
        return "correct"

    return "pending"

def validar_campo_gpt(word, field, idx, pending_results):
    try:
        prompt = (
            f"Responde solo con SI o NO.\n"
            f"¿La palabra '{word}' es un/una {field_representatives[field]}?"
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        answer = response.choices[0].message.content.strip().upper()
        result = "correct" if answer == "SI" else "incorrect"

    except Exception:
        result = "incorrect"

    # ✅ NO tocamos st.session_state.words
    pending_results['state'] = result

# -----------------------------
# Inicialización session_state
# -----------------------------
if "screen" not in st.session_state:
    st.session_state.screen = "instructions"

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "words" not in st.session_state:
    st.session_state.words = []  # {word, state}

if "used_words" not in st.session_state:
    st.session_state.used_words = set()

if "current_type" not in st.session_state:
    st.session_state.current_type = "letter"

if "current_letter" not in st.session_state:
    st.session_state.current_letter = random.choice(valid_letters)

if "current_field" not in st.session_state:
    st.session_state.current_field = random.choice(list(fields.keys()))

if "last_tick" not in st.session_state:
    st.session_state.last_tick = time.time()


# -----------------------------
# Instrucciones
# -----------------------------
if st.session_state.screen == "instructions":
    st.title("Fluencia verbal alternante")
    st.write(
        "Escribe palabras alternando entre:\n"
        "- Palabras que empiecen por una letra\n"
        "- Palabras de un campo semántico\n\n"
        "⏱️ Duración: 60 segundos"
    )
    if st.button("Comenzar"):
        st.session_state.start_time = time.time()
        st.session_state.screen = "test"
        st.rerun()

# -----------------------------
# Test
# -----------------------------
elif st.session_state.screen == "test":
    # Tiempo transcurrido
    elapsed = time.time() - st.session_state.start_time
    time_left = max(TEST_DURATION - elapsed, 0)

    st.title("Test en curso")
    st.progress(time_left / TEST_DURATION)

    # Mostrar consigna
    if st.session_state.current_type == "letter":
        st.subheader(f"Palabra que empiece por: **{st.session_state.current_letter.upper()}**")
    else:
        st.subheader(f"Palabra del campo: **{st.session_state.current_field}**")

    # Formulario de entrada
    with st.form("fluencia_form", clear_on_submit=True):
        word = st.text_input("Escribe una palabra")
        submitted = st.form_submit_button("Enviar")

    if submitted and word:
        if st.session_state.current_type == "letter":
            state = validar_letra(word, st.session_state.current_letter)
        else:
            state = validar_campo(word, st.session_state.current_field)

        st.session_state.used_words.add(word.lower())

        idx = len(st.session_state.words)
        st.session_state.words.append({
            "word": word,
            "state": state,
            "field": st.session_state.current_field if st.session_state.current_type == "field" else None
        })

        if state == "pending" and st.session_state.current_type == "field":
            # Validación en segundo plano con GPT
            thread = threading.Thread(
                target=validar_campo_gpt,
                args=(word, st.session_state.current_field, idx, st.session_state.words[idx]),
                daemon=True
            )
            thread.start()

        # Alternar tipo de palabra
        st.session_state.current_type = (
            "field" if st.session_state.current_type == "letter" else "letter"
        )

    # Mostrar palabras con estado
    for w in st.session_state.words:
        color = {
            "correct": "lightgreen",
            "incorrect": "lightcoral",
            "pending": "#f7f7a0"
        }[w["state"]]

        symbol = {
            "correct": "✅",
            "incorrect": "❌",
        }[w["state"]]

        st.markdown(
            f"<div style='background:{color}; padding:6px; margin:4px'>"
            f"{symbol} {w['word']}</div>",
            unsafe_allow_html=True
        )

    all_processed = all(w["state"] != "pending" for w in st.session_state.words)
    if time_left <= 0 and all_processed:
        st.session_state.screen = "results"
        st.rerun()

    # Si no ha terminado, forzamos actualización cada segundo
    time.sleep(1)
    st.rerun()

# -----------------------------
# Resultados
# -----------------------------
elif st.session_state.screen == "results":
    st.title("Resultados")

    correct = sum(1 for w in st.session_state.words if w["state"] == "correct")
    incorrect = sum(1 for w in st.session_state.words if w["state"] == "incorrect")
    pending = sum(1 for w in st.session_state.words if w["state"] == "pending")

    st.write(f"✅ Correctas: {correct}")
    st.write(f"❌ Incorrectas: {incorrect}")
    st.write(f"⏳ Pendientes: {pending}")

    if st.button("Reiniciar"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
