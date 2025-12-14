import streamlit as st
import random
import time

NIVELL_FINAL = 10 

def test_atencio():
    st.title("Test d'Atenció")

    if "app_state" not in st.session_state:
        st.session_state.app_state = "instructions"
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
    
    # Flag per assegurar que només guardem una vegada
    if "atencio_saved" not in st.session_state:
        st.session_state.atencio_saved = False

    if st.session_state.app_state == "instructions":
        st.subheader("Instruccions")
        st.write("- Memoritza els números.\n- Escriu-los amb el mateix ordre.\n- 2 errades al mateix nivell acaben el test.")
        if st.button("Començar test"):
            st.session_state.app_state = "test"
            st.session_state.numbers = []
            st.session_state.level = 4
            st.session_state.fails_in_level = 0
            st.session_state.game_over = False
            st.session_state.atencio_saved = False
            st.rerun()

    elif st.session_state.app_state == "test":
        if not st.session_state.numbers:
            st.session_state.numbers = [random.randint(0, 9) for _ in range(st.session_state.level)]
            st.session_state.start_time = time.time()

        elapsed = time.time() - st.session_state.start_time
        if elapsed < st.session_state.level: # Temps per memoritzar = nivell (4s per 4 nums)
            st.progress((st.session_state.level - elapsed) / st.session_state.level)
            cols = st.columns(len(st.session_state.numbers))
            for i, n in enumerate(st.session_state.numbers):
                cols[i].markdown(f"<h1 style='text-align: center;'>{n}</h1>", unsafe_allow_html=True)
            time.sleep(0.2)
            st.rerun()
        else:
            with st.form("respuesta"):
                user_input = st.text_input("Escriu els números (espaiats)")
                submitted = st.form_submit_button("Verificar")

            if submitted:
                try: user_nums = list(map(int, user_input.split()))
                except: return
                
                st.session_state.user_number_str = " ".join(map(str, user_nums))
                correct = (user_nums == st.session_state.numbers)
                
                if correct:
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
        # --- MODIFICACIÓ: GUARDARRESULTATS ---
        if (st.session_state.game_over or st.session_state.level > NIVELL_FINAL) and not st.session_state.atencio_saved:
            # Guardem el nivell assolit
            final_score = st.session_state.level if st.session_state.result == "fail" else st.session_state.level - 1
            st.session_state.user.actualiza_punt_atencio(final_score)
            st.session_state.games_played[1] = True # Index 1 = Atenció
            st.session_state.atencio_saved = True
            st.toast("Resultat guardat a la base de dades!")
        # -------------------------------------

        if st.session_state.result == "ok":
            st.success("✅ Correcte!")
        else:
            st.error("❌ Incorrecte!")
            st.write(f"Era: {st.session_state.numbers}")

        if st.session_state.game_over:
            st.error("Joc Acabat!")
            if st.button("Tornar a l'inici"):
                st.switch_page("app/homepage.py")
        elif st.session_state.level > NIVELL_FINAL:
            st.success("🏆 Has completat el test!")
            if st.button("Tornar a l'inici"):
                st.switch_page("app/homepage.py")
        else:
            if st.button("Següent Nivell"):
                st.session_state.numbers = []
                st.session_state.app_state = "test"
                st.rerun()