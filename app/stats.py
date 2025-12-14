from pathlib import Path
from datetime import datetime, timedelta
import streamlit as st
import sqlite3
import matplotlib.pyplot as plt
import numpy as np

# Connexió a la BD
REPO_PATH = Path(__file__).resolve().parent.parent
DB_PATH = REPO_PATH / "onco_connect.db"
conn = sqlite3.connect(str(DB_PATH))
c = conn.cursor()

st.title("Evolució del pacient")

############################################
# Evolució tests objectius de cada pacient #
############################################

st.header("Evolució dels tests del pacient")

# Llistar pacients
c.execute("SELECT username, name FROM users ORDER BY username")
pacients = c.fetchall()
pacient_dict = {f"{name} ({username})": username for username, name in pacients}

# Sel·lecciona pacient
seleccio = st.selectbox("Selecciona un pacient:", list(pacient_dict.keys()))
pacient = pacient_dict[seleccio]

# Tipus de tests
tests = ["fluencia", "atencio", "memoria", "velocitat"]

# Agafar dades
evolucio = {}
for test in tests:
    c.execute(
        "SELECT date, score FROM test_results WHERE username=? AND test_type=? ORDER BY date",
        (pacient, test),
    )
    dades = c.fetchall()
    # Dict {date: score}
    evolucio[test] = {row[0]: row[1] for row in dades}

# Dates ordenades
all_dates = sorted({d for test_scores in evolucio.values() for d in test_scores.keys()})

# GRÀFIC 1: Evolució en línies
fig1, ax1 = plt.subplots(figsize=(10, 5))
for test in tests:
    scores = [evolucio[test].get(d, 0) for d in all_dates]
    ax1.plot(all_dates, scores, marker="o", label=test)

ax1.set_title(f"Evolució dels tests de {seleccio}")
ax1.set_xlabel("Data")
ax1.set_ylabel("Score")
ax1.set_ylim(0, 10)
ax1.legend()
ax1.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig1)

# GRÀFIC 2: Diagrama de barres per dia
import numpy as np

fig2, ax2 = plt.subplots(figsize=(12, 6))
width = 0.2
x = np.arange(len(all_dates))

for i, test in enumerate(tests):
    scores = [evolucio[test].get(d, 0) for d in all_dates]
    ax2.bar(x + i * width, scores, width=width, label=test)

ax2.set_title(f"Puntuacions per test de {seleccio}")
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

st.header("Evolució de l'estat d'ànim del pacient")

# Agafar dades de daily_checkin
c.execute(
    "SELECT username, date, face FROM daily_checkin WHERE username=? ORDER BY date",
    (pacient,),
)
dades_checkin = c.fetchall()
conn.close()

scores_dict = {date: face for username, date, face in dades_checkin}
all_dates = sorted(list(scores_dict.keys()))

# GRÀFIC 3: Línia evolució estat d'ànim
fig2, ax2 = plt.subplots(figsize=(12, 6))
scores = [scores_dict.get(d, np.nan) for d in all_dates]  # NaN si no hi ha dada
ax2.plot(all_dates, scores, marker="o", label=seleccio, color="tab:blue")

ax2.set_title(f"Estat d'ànim de {seleccio}")
ax2.set_xlabel("Data")
ax2.set_ylabel("Face (1=trist, 5=feliç)")
ax2.set_ylim(0, 6)
ax2.set_xticks(all_dates)
ax2.set_xticklabels(all_dates, rotation=45)
ax2.legend()
ax2.grid(True)
plt.tight_layout()
st.pyplot(fig2)

############################################
# Evolució del Què m'ha passat del pacient #
############################################

st.header("Evolució del - Què m'ha passat? - del pacient")

dies_enrere = st.number_input(
    "Mostra incidències dels últims dies:", min_value=1, max_value=365, value=7
)


def grafic_incidents(pacient, dies_enrere):
    """Elabora el gràfic de barres dels incidents d'un pacient (agrupats per tipus) fins fa dies_enrere."""

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
        (pacient, data_min.strftime("%Y-%m-%d"), data_max.strftime("%Y-%m-%d")),
    )
    dades_incidencies = c.fetchall()
    conn.close()

    comptador = [0] * 10
    for incidencia, count in dades_incidencies:
        comptador[incidencia] = count

    # GRÀFIC 4: Gràfic de barres - Què m'ha passat? -

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(range(10), comptador, color=plt.cm.tab10.colors)
    ax.set_xticks(range(10))
    ax.set_xticklabels([str(i) for i in range(10)])
    ax.set_xlabel("Tipus d'incidència")
    ax.set_ylabel("Nombre de vegades")
    ax.set_title(f"Incidències dels últims {dies_enrere} dies per {seleccio}")
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    st.pyplot(fig)


grafic_incidents(pacient, dies_enrere)
