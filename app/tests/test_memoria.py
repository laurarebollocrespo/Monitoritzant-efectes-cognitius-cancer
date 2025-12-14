import streamlit as st
import random
import time

NIVELL_FINAL = 9

user = st.session_state.user

def test_memoria():
    st.title("Test de Memòria")

    if "app_state" not in st.session_state:
        st.session_state.app_state = "instructions"
    if "level" not in st.session_state:
        st.session_state.level = 4
    if "numbers" not in st.session_state:
        st.session_state.numbers = []
    if "start_time" not in st.session_state:
        st.session_state.start_time = None
    if "memoria_saved" not in st.session_state:
        st.session_state.memoria_saved = False
    
    # Variables de control d'errors i intents
    if "fails_in_level" not in st.session_state: st.session_state.fails_in_level = 0
    if "tries_in_level" not in st.session_state: st.session_state.tries_in_level = 0
    if "game_over" not in st.session_state: st.session_state.game_over = False
    if "result" not in st.session_state: st.session_state.result = None

    if st.session_state.app_state == "instructions":
        st.write("Memoritza i escriu en **ordre invers**.")
        if st.button("Començar test"):
            st.session_state.app_state = "test"
            st.session_state.numbers = []
            st.session_state.level = 4
            st.session_state.memoria_saved = False
            st.session_state.fails_in_level = 0
            st.session_state.game_over = False
            st.rerun()

    elif st.session_state.app_state == "test":
        if not st.session_state.numbers:
            st.session_state.numbers = [random.randint(0, 9) for _ in range(st.session_state.level)]
            st.session_state.start_time = time.time()

        elapsed = time.time() - st.session_state.start_time
        if elapsed < st.session_state.level:
            st.progress((st.session_state.level - elapsed) / st.session_state.level)
            cols = st.columns(len(st.session_state.numbers))
            for i, n in enumerate(st.session_state.numbers):
                cols[i].markdown(f"<h1 style='text-align: center;'>{n}</h1>", unsafe_allow_html=True)
            time.sleep(0.2)
            st.rerun()
        else:
            with st.form("respuesta"):
                user_input = st.text_input("Números separats per espais")
                submitted = st.form_submit_button("Verificar")

            if submitted:
                try: user_nums = list(map(int, user_input.split()))
                except: return

                correct_reversed = list(reversed(st.session_state.numbers))
                if user_nums == correct_reversed:
                    st.session_state.result = "ok"
                    st.session_state.level += 1
                    st.session_state.fails_in_level = 0
                    st.session_state.tries_in_level = 0
                else:
                    st.session_state.result = "fail"
                    st.session_state.fails_in_level += 1
                    if st.session_state.fails_in_level >= 2:
                        st.session_state.game_over = True
                    else:
                        st.session_state.tries_in_level = 1
                
                st.session_state.start_time = None
                st.session_state.app_state = "results"
                st.rerun()

    elif st.session_state.app_state == "results":
        # --- MODIFICACIÓ: GUARDAR RESULTATS ---
        if (st.session_state.game_over or st.session_state.level > NIVELL_FINAL) and not st.session_state.memoria_saved:
            final_score = st.session_state.level if st.session_state.result == "fail" else st.session_state.level - 1
            st.session_state.user.actualiza_punt_memoria(final_score)
            user.mark_game_played(2) # Index 2 = Memoria
            st.session_state.memoria_saved = True
            st.toast("Resultat guardat!")
        # --------------------------------------

        if st.session_state.result == "ok":
            st.success("✅ Correcte!")
        else:
            st.error("❌ Incorrecte!")
            st.write(f"Revés correcte: {list(reversed(st.session_state.numbers))}")

        if st.session_state.game_over:
            st.error("Test finalitzat.")
            if st.button("Sortir"):
                st.switch_page("app/homepage.py")
        elif st.session_state.level > NIVELL_FINAL:
            st.success("🏆 Test completat!")
            if st.button("Sortir"):
                st.switch_page("app/homepage.py")
        else:
            if st.button("Següent"):
                st.session_state.numbers = []
                st.session_state.app_state = "test"
                st.rerun()