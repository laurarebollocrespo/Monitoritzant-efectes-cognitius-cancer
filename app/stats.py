# fitxer: app.py
import streamlit as st
import sqlite3
import matplotlib.pyplot as plt

# Connexió a la base de dades
DB_PATH = "onco_connect.db"
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

st.title("Evolució dels tests del pacient")

# Llistar pacients
c.execute("SELECT username, name FROM users ORDER BY username")
pacients = c.fetchall()
pacient_dict = {f"{name} ({username})": username for username, name in pacients}

# Selector de pacient
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
    dates = [row[0] for row in dades]
    scores = [row[1] for row in dades]
    evolucio[test] = (dates, scores)

# Tancar connexió
conn.close()

# Crear gràfic
fig, ax = plt.subplots(figsize=(10, 5))
for test in tests:
    dates, scores = evolucio[test]
    ax.plot(dates, scores, marker="o", label=test)

ax.set_title(f"Evolució dels tests de {seleccio}")
ax.set_xlabel("Data")
ax.set_ylabel("Score")
ax.set_ylim(0, 10)
ax.legend()
ax.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

# Mostrar gràfic a Streamlit
st.pyplot(fig)
