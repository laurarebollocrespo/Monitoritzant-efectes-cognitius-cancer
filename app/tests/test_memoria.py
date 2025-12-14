import streamlit as st
import random
import time

NIVELL_FINAL = 9

user = st.session_state.user


def test_memoria():
    st.title("Test de Memòria")

    if "app_state_memoria" not in st.session_state:
        st.session_state.app_state_memoria = "instructions"
    if "level_memoria" not in st.session_state:
        st.session_state.level_memoria = 4
    if "numbers_memoria" not in st.session_state:
        st.session_state.numbers_memoria = []
    if "start_time_memoria" not in st.session_state:
        st.session_state.start_time_memoria = None
    if "memoria_saved" not in st.session_state:
        st.session_state.memoria_saved = False

    # Variables de control
    if "fails_in_level_memoria" not in st.session_state:
        st.session_state.fails_in_level_memoria = 0
    if "tries_in_level_memoria" not in st.session_state:
        st.session_state.tries_in_level_memoria = 0
    if "game_over_memoria" not in st.session_state:
        st.session_state.game_over_memoria = False
    if "result_memoria" not in st.session_state:
        st.session_state.result_memoria = None

    if st.session_state.app_state_memoria == "instructions":
        st.write("Memoritza i escriu en **ordre invers**.")
        if st.button("Començar test"):
            st.session_state.app_state_memoria = "test"
            st.session_state.numbers_memoria = []
            st.session_state.level_memoria = 4
            st.session_state.memoria_saved = False
            st.session_state.fails_in_level_memoria = 0
            st.session_state.game_over_memoria = False
            st.rerun()

    elif st.session_state.app_state_memoria == "test":
        if not st.session_state.numbers_memoria:
            st.session_state.numbers_memoria = [
                random.randint(0, 9) for _ in range(st.session_state.level_memoria)
            ]
            st.session_state.start_time_memoria = time.time()

        elapsed = time.time() - st.session_state.start_time_memoria
        if elapsed < st.session_state.level_memoria:
            st.progress(
                (st.session_state.level_memoria - elapsed)
                / st.session_state.level_memoria
            )
            cols = st.columns(len(st.session_state.numbers_memoria))
            for i, n in enumerate(st.session_state.numbers_memoria):
                cols[i].markdown(
                    f"<h1 style='text-align: center;'>{n}</h1>", unsafe_allow_html=True
                )
            time.sleep(0.2)
            st.rerun()
        else:
            with st.form("respuesta"):
                user_input = st.text_input("Números separats per espais")
                submitted = st.form_submit_button("Verificar")

            if submitted:
                try:
                    user_nums = list(map(int, user_input.split()))
                except:
                    return

                correct_reversed = list(reversed(st.session_state.numbers_memoria))

                if user_nums == correct_reversed:
                    st.session_state.result_memoria = "ok"
                    st.session_state.level_memoria += 1
                    st.session_state.fails_in_level_memoria = 0
                    st.session_state.tries_in_level_memoria = 0
                else:
                    st.session_state.result_memoria = "fail"
                    st.session_state.fails_in_level_memoria += 1
                    if st.session_state.fails_in_level_memoria >= 2:
                        st.session_state.game_over_memoria = True
                    else:
                        st.session_state.tries_in_level_memoria = 1

                st.session_state.start_time_memoria = None
                st.session_state.app_state_memoria = "results"
                st.rerun()

    elif st.session_state.app_state_memoria == "results":
        # --- GUARDAR RESULTATS ---
        if (
            st.session_state.game_over_memoria
            or st.session_state.level_memoria > NIVELL_FINAL
        ) and not st.session_state.memoria_saved:
            final_score = (
                st.session_state.level_memoria
                if st.session_state.result_memoria == "fail"
                else st.session_state.level_memoria - 1
            )
            st.session_state.user.actualiza_punt_memoria(final_score)
            user.mark_game_played(2)  # Index 2 = Memòria
            st.session_state.memoria_saved = True
            st.toast("Resultat guardat!")
        # ------------------------

        if st.session_state.result_memoria == "ok":
            st.success("✅ Correcte!")
        else:
            st.error("❌ Incorrecte!")
            st.write(
                f"Revés correcte: {list(reversed(st.session_state.numbers_memoria))}"
            )

        if st.session_state.game_over_memoria:
            st.error("Test finalitzat.")
            if st.button("Sortir"):
                st.switch_page("app/homepage.py")
        elif st.session_state.level_memoria > NIVELL_FINAL:
            st.success("🏆 Test completat!")
            if st.button("Sortir"):
                st.switch_page("app/homepage.py")
        else:
            if st.button("Següent"):
                st.session_state.numbers_memoria = []
                st.session_state.app_state_memoria = "test"
                st.rerun()