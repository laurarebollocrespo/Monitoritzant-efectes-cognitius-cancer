import streamlit as st
import random
import time

def run_test():
    # --- CONFIGURACIÓ ---
    N_NUMBERS = 15
    BOARD_COLS = 5
    COUNTDOWN = 3

    # --- ESTAT ---
    if "screen" not in st.session_state:
        st.session_state.screen = "instructions"
    if "velocitat_saved" not in st.session_state:
        st.session_state.velocitat_saved = False

    # --- INSTRUCCIONS ---
    if st.session_state.screen == "instructions":
        st.title("Test de Velocitat")
        st.write("Prem els números en ordre creixent (1, 2, 3...) tan ràpid com puguis.")
        if st.button("Començar"):
            st.session_state.numbers_velocitat = random.sample(range(1, 100), N_NUMBERS)
            st.session_state.expected = min(st.session_state.numbers_velocitat)
            st.session_state.positions = []
            for n in st.session_state.numbers_velocitat:
                st.session_state.positions.append({
                    "number": n, "col": random.randint(0, BOARD_COLS-1), 
                    "top": random.randint(0, 2), "color": "lightgrey"
                })
            st.session_state.start_time = None
            st.session_state.click_times = []
            st.session_state.errors = 0
            st.session_state.finished = False
            st.session_state.velocitat_saved = False
            st.session_state.screen = "countdown"
            st.rerun()

    # --- COMPTE ENRERE ---
    elif st.session_state.screen == "countdown":
        t = st.empty()
        for i in range(COUNTDOWN, 0, -1):
            t.markdown(f"<h1 style='text-align:center'>{i}</h1>", unsafe_allow_html=True)
            time.sleep(1)
        t.empty()
        st.session_state.screen = "test"
        st.rerun()

    # --- JOC ---
    elif st.session_state.screen == "test":
        st.write(f"Busca el: **{st.session_state.expected}**")
        cols = st.columns(BOARD_COLS)

        def handle_click(n):
            if st.session_state.start_time is None:
                st.session_state.start_time = time.time()
            
            for p in st.session_state.positions:
                if p["number"] == n:
                    if n == st.session_state.expected:
                        p["color"] = "#A5D6A7" # Verd
                        st.session_state.click_times.append(time.time())
                        remaining = sorted([x for x in st.session_state.numbers_velocitat if x > n])
                        if remaining:
                            st.session_state.expected = remaining[0]
                        else:
                            st.session_state.finished = True
                            st.session_state.screen = "results"
                    else:
                        p["color"] = "#EF9A9A" # Vermell
                        st.session_state.errors += 1

        for p in st.session_state.positions:
            with cols[p["col"]]:
                for _ in range(p["top"]): st.write("")
                st.button(str(p["number"]), key=f"btn_{p['number']}", 
                          on_click=handle_click, args=(p["number"],),
                          disabled=st.session_state.finished or p["color"]=="#A5D6A7")
                st.markdown(f"<div style='height:5px;background-color:{p['color']}'></div>", unsafe_allow_html=True)

    # --- RESULTATS ---
    elif st.session_state.screen == "results":
        total_time = st.session_state.click_times[-1] - st.session_state.start_time
        
        # --- MODIFICACIÓ: GUARDAR ---
        if not st.session_state.velocitat_saved:
            st.session_state.user.actualiza_punt_velocitat(total_time, st.session_state.errors)
            st.session_state.games_played[3] = True # Index 3
            st.session_state.velocitat_saved = True
            st.toast("Resultat guardat!")
        # ----------------------------

        st.success("¡Prueba completada!")
        st.metric("Temps", f"{total_time:.2f} s")
        st.metric("Errors", st.session_state.errors)
        
        if st.button("Tornar a l'Inici"):
            st.switch_page("app/homepage.py")

if __name__ == "__main__":
    run_test()