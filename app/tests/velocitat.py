import streamlit as st
import random
import time

# -----------------------------
# Configuración
# -----------------------------
N_NUMBERS = 9   
BOARD_COLS = 6
COUNTDOWN = 3

# -----------------------------
# Inicialización session_state
# -----------------------------
if "screen" not in st.session_state:
    st.session_state.screen = "instructions"
if "numbers_velocitat" not in st.session_state:
    st.session_state.numbers_velocitat = random.sample(range(1, 100), N_NUMBERS)
if "expected" not in st.session_state:
    st.session_state.expected = min(st.session_state.numbers_velocitat)
if "positions" not in st.session_state:
    st.session_state.positions = []
    for n in st.session_state.numbers_velocitat:
        st.session_state.positions.append({
            "number": n,
            "col": random.randint(0, BOARD_COLS-1),
            "top_padding": random.randint(0, 3),
            "color": "lightgrey"
        })
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "click_times" not in st.session_state:
    st.session_state.click_times = []
if "errors" not in st.session_state:
    st.session_state.errors = 0
if "finished" not in st.session_state:
    st.session_state.finished = False

# -----------------------------
# Pantalla de instrucciones
# -----------------------------
if st.session_state.screen == "instructions":
    st.title("Instrucciones del Test")
    st.write("Pulsa los números en orden creciente lo más rápido posible. Si aciertas, el botón se pondrá verde; si fallas, rojo. ¡Intenta hacerlo lo mejor posible!")
    if st.button("Comenzar prueba"):
        st.session_state.screen = "countdown"
        st.rerun()

# -----------------------------
# Cuenta atrás antes del test
# -----------------------------
elif st.session_state.screen == "countdown":
    st.title("Preparándote...")
    countdown_placeholder = st.empty()
    for i in range(COUNTDOWN, 0, -1):
        countdown_placeholder.markdown(f"<h1 style='text-align:center'>{i}</h1>", unsafe_allow_html=True)
        time.sleep(1)
    st.session_state.screen = "test"

    st.rerun()

# -----------------------------
# Pantalla de test
# -----------------------------
elif st.session_state.screen == "test":
    st.title("Test de Velocidad de Procesamiento")
    st.write("Pulsa los números en orden creciente.")
    cols = st.columns(BOARD_COLS)

    def handle_click(n):
        if st.session_state.start_time is None:
            st.session_state.start_time = time.time()

        for item in st.session_state.positions:
            if item["number"] == n:
                if n == st.session_state.expected:
                    item["color"] = "lightgreen"
                    st.session_state.click_times.append(time.time())
                    remaining = sorted(st.session_state.numbers_velocitat)
                    idx = remaining.index(n)
                    if idx + 1 < len(remaining):
                        st.session_state.expected = remaining[idx+1]
                    else:
                        st.session_state.finished = True
                        st.session_state.screen = "results"
                else:
                    item["color"] = "lightcoral"
                    st.session_state.errors += 1

    for item in st.session_state.positions:
        with cols[item["col"]]:
            for _ in range(item["top_padding"]):
                st.write("")
            st.button(
                str(item["number"]),
                key=f"btn_{item['number']}",
                on_click=handle_click,
                args=(item["number"],),
                disabled=st.session_state.finished or item["color"] == "lightgreen"
            )
            st.markdown(f"<div style='height:20px;background-color:{item['color']}'></div>", unsafe_allow_html=True)

# -----------------------------
# Pantalla de resultados
# -----------------------------
elif st.session_state.screen == "results":
    total_time = st.session_state.click_times[-1] - st.session_state.start_time
    aciertos = len(st.session_state.click_times)
    st.success("¡Prueba completada!")
    st.write(f"⏱️ Tiempo total: {total_time:.2f} s")
    st.write(f"✅ Aciertos: {aciertos}")
    st.write(f"⚠️ Errores: {st.session_state.errors}")

    if st.button("Reiniciar prueba", disabled=False):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()