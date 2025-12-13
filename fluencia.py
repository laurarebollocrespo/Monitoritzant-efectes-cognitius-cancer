import streamlit as st
import time

# -----------------------------
# Configuración
# -----------------------------
DURATION = 60   # duración del test en segundos
COUNTDOWN = 3

# -----------------------------
# Inicialización session_state
# -----------------------------
if "screen" not in st.session_state:
    st.session_state.screen = "instructions"

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "words" not in st.session_state:
    # Cada palabra se guarda como dict: palabra, turno, validación estructural, score semántico (None por ahora)
    st.session_state.words = []

if "finished" not in st.session_state:
    st.session_state.finished = False

# -----------------------------
# Pantalla de instrucciones
# -----------------------------
if st.session_state.screen == "instructions":
    st.title("Prueba de Fluencia Verbal Alternante")
    st.write(
        """
        Durante **60 segundos**, escribe palabras **alternando** entre:

        - Una palabra que empiece por la letra **P**
        - Una **fruta o verdura** (evaluación semántica futura)

        Ejemplo correcto:
        - **Pera → Manzana → Pan → Tomate**
        """
    )

    if st.button("Comenzar prueba"):
        st.session_state.screen = "countdown"
        st.rerun()

# -----------------------------
# Cuenta atrás
# -----------------------------
elif st.session_state.screen == "countdown":
    placeholder = st.empty()
    for i in range(COUNTDOWN, 0, -1):
        placeholder.markdown(
            f"<h1 style='text-align:center'>{i}</h1>",
            unsafe_allow_html=True
        )
        time.sleep(1)

    st.session_state.start_time = time.time()
    st.session_state.screen = "test"
    st.rerun()

# -----------------------------
# Función para agregar palabra
# -----------------------------
def add_word():
    word = st.session_state.fluency_input.strip()
    if not word:
        return

    index = len(st.session_state.words)
    expected_type = "P" if index % 2 == 0 else "FOOD"

    # Check estructura: letra P
    valid_structure = True
    if expected_type == "P" and not word.lower().startswith("p"):
        valid_structure = False

    # Check repetición
    previous_words = [w["word"].lower() for w in st.session_state.words]
    if word.lower() in previous_words:
        valid_structure = False

    # Guardar palabra
    st.session_state.words.append({
        "word": word,
        "turn": index + 1,
        "expected_type": expected_type,
        "valid_structure": valid_structure,
        "semantic_score": None  # preparado para embeddings futuros
    })

    # Limpiar input
    st.session_state.fluency_input = ""

# -----------------------------
# Pantalla de test
# -----------------------------
elif st.session_state.screen == "test":
    st.title("Fluencia Verbal")
    elapsed = time.time() - st.session_state.start_time
    remaining = max(0, DURATION - int(elapsed))
    st.write(f"⏳ Tiempo restante: **{remaining} s**")

    # Input del usuario con callback
    st.text_input(
        "Escribe una palabra y pulsa Enter",
        key="fluency_input",
        on_change=add_word,
        disabled=remaining <= 0
    )

    # Mostrar palabras previas con colores
    st.write("### Palabras escritas:")
    for w in st.session_state.words:
        color = "green" if w["valid_structure"] else "red"
        st.markdown(
            f"<span style='color:{color}; font-weight:bold'>{w['word']}</span>",
            unsafe_allow_html=True
        )

    if remaining <= 0:
        st.session_state.finished = True
        st.session_state.screen = "results"
        st.rerun()

# -----------------------------
# Resultados
# -----------------------------
elif st.session_state.screen == "results":
    st.title("Resultados – Fluencia Verbal")

    total_words = len(st.session_state.words)
    correct_words = sum(1 for w in st.session_state.words if w["valid_structure"])

    # Mostrar palabras con colores
    st.write("### Palabras:")
    for w in st.session_state.words:
        color = "green" if w["valid_structure"] else "red"
        st.markdown(
            f"<span style='color:{color}; font-weight:bold'>{w['word']}</span>",
            unsafe_allow_html=True
        )

    st.write(f"📝 Total de palabras introducidas: **{total_words}**")
    st.write(f"✅ Correctas según estructura: **{correct_words}**")
    st.write("💡 La evaluación semántica se añadirá posteriormente usando embeddings.")

    if st.button("Reiniciar prueba"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
