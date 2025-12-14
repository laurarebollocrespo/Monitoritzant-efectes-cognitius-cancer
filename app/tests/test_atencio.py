import streamlit as st
import random
import time

NIVELL_FINAL = 10

user = st.session_state.user

def teclat_numeric_atencio():
    """Genera un teclat numèric per que l'usuari pugui escriure l'input."""
    if "input_atencio" not in st.session_state:
        st.session_state.input_atencio = []

    st.markdown("### Introdueix els números")

    # Mostrar el que escriu l'usuari
    st.text_input(
        "Entrada",
        " ".join(st.session_state.input_atencio),
        disabled=True,
        key="display_atencio",
    )

    cols = st.columns(3)
    buttons = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "←", "0", "✔"]

    submitted = False

    for i, label in enumerate(buttons):
        with cols[i % 3]:
            if st.button(label, key=f"key_atencio_{label}_{i}"):
                if label.isdigit():
                    st.session_state.input_atencio.append(label)
                elif label == "←" and st.session_state.input_atencio:
                    st.session_state.input_atencio.pop()
                elif label == "✔":
                    submitted = True

    return submitted


def test_atencio():
    st.title("Test d'Atenció")

    if "app_state_atencio" not in st.session_state:
        st.session_state.app_state_atencio = "instructions"
    if "level_atencio" not in st.session_state:
        st.session_state.level_atencio = 4
    if "numbers_atencio" not in st.session_state:
        st.session_state.numbers_atencio = []
    if "start_time_atencio" not in st.session_state:
        st.session_state.start_time_atencio = None
    if "result_atencio" not in st.session_state:
        st.session_state.result_atencio = None
    if "fails_in_level_atencio" not in st.session_state:
        st.session_state.fails_in_level_atencio = 0
    if "game_over_atencio" not in st.session_state:
        st.session_state.game_over_atencio = False
    if "tries_in_level_atencio" not in st.session_state:
        st.session_state.tries_in_level_atencio = 0

    # Flag per assegurar que només guardem una vegada
    if "atencio_saved" not in st.session_state:
        st.session_state.atencio_saved = False

    if st.session_state.app_state_atencio == "instructions":
        st.subheader("Instruccions")
        st.write(
            "- Memoritza els números.\n- Escriu-los amb el mateix ordre.\n- 2 errades al mateix nivell acaben el test."
        )
        if st.button("Començar test"):
            st.session_state.app_state_atencio = "test"
            st.session_state.numbers_atencio = []
            st.session_state.level_atencio = 4
            st.session_state.fails_in_level_atencio = 0
            st.session_state.game_over_atencio = False
            st.session_state.atencio_saved = False
            st.rerun()

    elif st.session_state.app_state_atencio == "test":
        if not st.session_state.numbers_atencio:
            st.session_state.numbers_atencio = [
                random.randint(0, 9) for _ in range(st.session_state.level_atencio)
            ]
            st.session_state.start_time_atencio = time.time()

        elapsed = time.time() - st.session_state.start_time_atencio
        if elapsed < st.session_state.level_atencio:
            st.progress(
                (st.session_state.level_atencio - elapsed)
                / st.session_state.level_atencio
            )
            cols = st.columns(len(st.session_state.numbers_atencio))
            for i, n in enumerate(st.session_state.numbers_atencio):
                cols[i].markdown(
                    f"<h1 style='text-align: center;'>{n}</h1>", unsafe_allow_html=True
                )
            time.sleep(0.2)
            st.rerun()
        else:
            submitted = teclat_numeric_atencio()
            if submitted:
                try:
                    user_nums = list(map(int, st.session_state.input_atencio))
                except:
                    return

            if submitted:
                try:
                    user_nums = list(map(int, user_input.split()))
                except:
                    return

                st.session_state.user_number_str_atencio = " ".join(map(str, user_nums))
                correct = user_nums == st.session_state.numbers_atencio

                if correct:
                    st.session_state.result_atencio = "ok"
                    st.session_state.level_atencio += 1
                    st.session_state.fails_in_level_atencio = 0
                    st.session_state.tries_in_level_atencio = 0
                else:
                    st.session_state.result_atencio = "fail"
                    st.session_state.fails_in_level_atencio += 1
                    if st.session_state.fails_in_level_atencio >= 2:
                        st.session_state.game_over_atencio = True
                    else:
                        st.session_state.tries_in_level_atencio = 1

                st.session_state.start_time_atencio = None
                st.session_state.app_state_atencio = "results"
                st.rerun()

    elif st.session_state.app_state_atencio == "results":
        # --- GUARDAR RESULTATS ---
        if (
            st.session_state.game_over_atencio
            or st.session_state.level_atencio > NIVELL_FINAL
        ) and not st.session_state.atencio_saved:
            final_score = (
                st.session_state.level_atencio
                if st.session_state.result_atencio == "fail"
                else st.session_state.level_atencio - 1
            )
            st.session_state.user.actualiza_punt_atencio(final_score)
            user.mark_game_played(1)  # Index 1 = Atenció
            st.session_state.atencio_saved = True
            st.toast("Resultat guardat a la base de dades!")
        # -------------------------

        if st.session_state.result_atencio == "ok":
            st.success("✅ Correcte!")
        else:
            st.error("❌ Incorrecte!")
            st.write(f"Era: {st.session_state.numbers_atencio}")

        if st.session_state.game_over_atencio:
            st.error("Joc Acabat!")
            if st.button("Tornar a l'inici"):
                st.switch_page("app/homepage.py")
        elif st.session_state.level_atencio > NIVELL_FINAL:
            st.success("🏆 Has completat el test!")
            if st.button("Tornar a l'inici"):
                st.switch_page("app/homepage.py")
        else:
            if st.button("Següent Nivell"):
                st.session_state.numbers_atencio = []
                st.session_state.app_state_atencio = "test"
                st.rerun()