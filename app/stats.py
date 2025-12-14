from pathlib import Path
from datetime import datetime, timedelta
from user import User
import database as db


import streamlit as st
import sqlite3
import matplotlib.pyplot as plt
import numpy as np


st.session_state = {
    "username": "pacient"
}

usuari_loggejat = st.session_state["username"]
pacient = User(usuari_loggejat)

############################################
# Evolució tests objectius de cada pacient #
############################################

st.header("Evolució dels tests del pacient")

tests = ["Fluencia", "Atencio", "Memoria", "Velocitat"]
all_dates = sorted({date for test in tests for date in pacient.test_results[test]})

# GRÀFIC 1: Evolució en línies
fig1, ax1 = plt.subplots(figsize=(10, 5))
for test in tests:
    scores = [pacient.test_results[test].get(d, np.nan) for d in all_dates]
    ax1.plot(all_dates, scores, marker="o", label=test)

ax1.set_title(f"Evolució dels tests de {pacient.name}")
ax1.set_xlabel("Data")
ax1.set_ylabel("Score")
ax1.set_ylim(0, 10)
ax1.legend()
ax1.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig1)

# GRÀFIC 2: Diagrama de barres per dia

fig2, ax2 = plt.subplots(figsize=(12, 6))
width = 0.2
x = np.arange(len(all_dates))

for i, test in enumerate(tests):
    # Agafar puntuacions del pacient loggejat, posar NaN si no hi ha dada
    scores = [pacient.test_results[test].get(d, 0) for d in all_dates]
    ax2.bar(x + i * width, scores, width=width, label=test)

ax2.set_title(f"Puntuacions per test de {pacient.name}")
ax2.set_xlabel("Data")
ax2.set_ylabel("Score")
ax2.set_ylim(0, 10)
ax2.set_xticks(x + width * 1.5)
ax2.set_xticklabels(all_dates, rotation=45)
ax2.legend()
plt.tight_layout()
st.pyplot(fig2)

#############################################
# Evolució de l'estat d'ànim del pacient #
#############################################

REPO_PATH = Path(__file__).resolve().parent.parent
DB_PATH = REPO_PATH / "onco_connect.db"
conn = sqlite3.connect(str(DB_PATH))
c = conn.cursor()

st.header("Evolució de l'estat d'ànim del pacient")

# Agafar dades de daily_checkin
c.execute(
    "SELECT username, date, face FROM daily_checkin WHERE username=? ORDER BY date",
    (pacient.username,),
)
dades_checkin = c.fetchall()
conn.close()

# Organitzar dades del pacient seleccionat
scores_dict = {date: face for username, date, face in dades_checkin}
all_dates = sorted(list(scores_dict.keys()))

# GRÀFIC 3: Línia evolució estat d'ànim
fig3, ax3 = plt.subplots(figsize=(12, 6))
scores = [scores_dict.get(d, np.nan) for d in all_dates]  # NaN si no hi ha dada
ax3.plot(all_dates, scores, marker="o", label=pacient.name, color="tab:blue")

ax3.set_title(f"Estat d'ànim de {pacient.name}")
ax3.set_xlabel("Data")
ax3.set_ylabel("Face (1=trist, 5=feliç)")
ax3.set_ylim(0, 6)
ax3.set_xticks(all_dates)
ax3.set_xticklabels(all_dates, rotation=45)
ax3.legend()
ax3.grid(True)
plt.tight_layout()
st.pyplot(fig3)

############################################
# Evolució del Què m'ha passat del pacient #
############################################

st.header("Evolució del - Què m'ha passat? - del pacient")

dies_enrere = st.number_input(
    "Mostra incidències dels últims dies:", min_value=1, max_value=365, value=7
)


def graf_incidents(pacient_name, dies_enrere):
    from datetime import datetime, timedelta
    import matplotlib.pyplot as plt
    import sqlite3

    data_max = datetime.today()
    data_min = data_max - timedelta(days=int(dies_enrere))

    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute(
        """
        SELECT incidencia, COUNT(*)
        FROM incidencies
        WHERE username=? AND date BETWEEN ? AND ?
        GROUP BY incidencia
        ORDER BY incidencia
        """,
        (pacient.username, data_min.strftime("%Y-%m-%d"), data_max.strftime("%Y-%m-%d")),
    )
    dades_incidencies = c.fetchall()
    conn.close()

    comptador = [0] * 10
    for incidencia, count in dades_incidencies:
        comptador[incidencia] = count

    fig4, ax4 = plt.subplots(figsize=(10, 5))
    ax4.bar(range(10), comptador, color=plt.cm.tab10.colors)
    ax4.set_xticks(range(10))
    ax4.set_xticklabels([str(i) for i in range(10)])
    ax4.set_xlabel("Tipus d'incidència")
    ax4.set_ylabel("Nombre de vegades")
    ax4.set_title(f"Incidències dels últims {dies_enrere} dies per {pacient.name}")
    ax4.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    st.pyplot(fig4)


# Cridar la funció amb el pacient seleccionat i dies_enrere actual
graf_incidents(pacient.name, dies_enrere)