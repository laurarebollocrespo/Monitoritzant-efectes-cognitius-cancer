import streamlit as st
import random
import time

NIVELL_FINAL = 9  # mirar si es 9 u 8

def score(lvl:int)->float:
    """Asigna un float de puntuación en función del nivel en el que se acaba el test"""
    return (lvl-4)/5*100

def test_memoria():
    st.title("Test de Memòria")

    # -------------------------
    # ESTADO GLOBAL DE LA APP
    # -------------------------
    if "app_state" not in st.session_state:
        st.session_state.app_state = "instructions"

    # Variables del test
    if "level" not in st.session_state:
        st.session_state.level = 4
    if "numbers" not in st.session_state:
        st.session_state.numbers = []
    if "start_time" not in st.session_state:
        st.session_state.start_time = None
    if "result" not in st.session_state:
        st.session_state.result = None
    if "fails_in_level" not in st.session_state:
        st.session_state.fails_in_level = 0
    if "game_over" not in st.session_state:
        st.session_state.game_over = False
    if "tries_in_level" not in st.session_state:
        st.session_state.tries_in_level = 0

    # -------------------------
    # ESTADO 1: INSTRUCCIONES
    # -------------------------
    if st.session_state.app_state == "instructions":
        st.subheader("Instruccions")
        st.write(
            """
        - Memoritza els números mostrats.
        - Escriu-los amb l'ordre invers.
        - Si falles dues vegades seguides al mateix nivell, el test acaba.
        """
        )

        if st.button("Començar test"):
            st.session_state.app_state = "test"
            st.session_state.numbers = []
            st.session_state.level = 4
            st.session_state.fails_in_level = 0
            st.session_state.game_over = False
            st.rerun()

    # -------------------------
    # ESTADO 2: TEST
    # -------------------------
    elif st.session_state.app_state == "test":

        if not st.session_state.numbers:
            st.session_state.numbers = [
                random.randint(0, 9) for _ in range(st.session_state.level)
            ]
            st.session_state.start_time = time.time()

        elapsed = time.time() - st.session_state.start_time
        remaining_time = max(st.session_state.level - elapsed, 0)
        progress = remaining_time / st.session_state.level  # valor entre 0 y 1

        # Mostrar barra de progreso
        st.progress(progress)

        if elapsed < st.session_state.level:
            st.write("Memoritza aquests números:")
            cols = st.columns(len(st.session_state.numbers))
            for i, n in enumerate(st.session_state.numbers):
                cols[i].markdown(
                    f"<h1 style='text-align: center;'>{n}</h1>", unsafe_allow_html=True
                )
            time.sleep(0.2)
            st.rerun()
        else:
            with st.form("respuesta"):
                user_input = st.text_input(
                    "Introduce los números separados por espacios"
                )
                submitted = st.form_submit_button("Verificar")

            if submitted:
                try:
                    user_nums = list(map(int, user_input.split()))
                except:
                    st.warning("Formato incorrecto")
                    return

                st.session_state.user_number_str = " ".join(map(str, user_nums))

                if st.session_state.tries_in_level == 0:
                    if user_nums == list(reversed(st.session_state.numbers)):
                        st.session_state.result = "ok"
                        st.session_state.level += (
                            1  # acierta en primer intento → sube de nivel
                        )
                        st.session_state.fails_in_level = 0
                        st.session_state.tries_in_level = 0
                    else:
                        st.session_state.result = "fail"
                        st.session_state.fails_in_level = 1
                        st.session_state.tries_in_level = 1  # pasa a segundo intento
                # Segundo intento
                elif st.session_state.tries_in_level == 1:
                    if user_nums == list(reversed(st.session_state.numbers)):
                        st.session_state.result = "ok"
                        st.session_state.level += (
                            1  # acierta en segundo intento → sube de nivel
                        )
                        st.session_state.fails_in_level = 0
                    else:
                        st.session_state.result = "fail"
                        st.session_state.game_over = (
                            True  # falla segundo intento → termina test
                        )
                    st.session_state.tries_in_level = 0  # reset para siguiente nivel
                # Si aún no son dos pruebas, repetimos el mismo nivel
                st.session_state.start_time = None
                st.session_state.app_state = "results"
                st.rerun()
    # -------------------------
    # ESTADO 3: RESULTADOS
    # -------------------------
    elif st.session_state.app_state == "results":
        bg_color = "#FFFFFF"  # blanco por defecto
        title = ""
        if st.session_state.result == "ok":
            bg_color = "#4CAF50"  # verde
            title = "✅ Correcte!"
        else:
            bg_color = "#F44336"  # rojo
            title = "❌ Incorrecte!"

        user_number_str = st.session_state.get("user_number_str", "")
        correct_number_str = " ".join(map(str, st.session_state.numbers))
        correct_reversed_number_str = " ".join(
            map(str, list(reversed(st.session_state.numbers)))
        )

        # Mostrar resultado con fondo coloreado
        st.markdown(
            f"""
            <div style="
                background-color: {bg_color};
                padding: 50px;
                border-radius: 15px;
                text-align: center;
                color: white;
            ">
                <h1 style="font-size: 48px;">{title}</h1>
                <h2>Número: {correct_number_str}</h2>
                <h2>Número revés: {correct_reversed_number_str}</h2>
                <h2>El teu número: {user_number_str}</h2>
                <h3>Nivell #{(st.session_state.level - 1) if st.session_state.result == "ok" else (st.session_state.level)}</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not st.session_state.game_over:
            if st.button("Continuar"):
                st.session_state.numbers = []
                st.session_state.start_time = None
                st.session_state.app_state = "test"
                st.rerun()
        else:
            if st.session_state.level == NIVELL_FINAL:
                st.error("✅ Has completat tots els nivells. El test ha finalitzat.")
            else:
                st.error(
                "❌ Has fallat dues vegades seguides a aquest nivell. El test ha finalitzat."
                )   
            result = score(st.session_state.level)
            st.session_state.user.actualiza_punt_memoria(result)
            
            if st.button("Tornar a l'inici"):
                st.session_state.app_state = "instructions"
                st.session_state.numbers = []
                st.session_state.game_over = False
                st.session_state.tries_in_level = 0
                st.session_state.fails_in_level = 0
                st.rerun()


test_memoria()
