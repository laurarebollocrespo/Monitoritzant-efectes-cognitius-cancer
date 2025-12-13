import sqlite3
import hashlib
import os

type_user = tuple[str, str, str, str, int]  # username, password, name, last_login, strike

# Assegurem que la DB es crea a la carpeta arrel del projecte, no dins d'app/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "onco_connect.db")

def init_db() -> None:
    """Inicialitza la base de dades si no existeix."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # TAULA: users
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            name TEXT,
            last_login DATE DEFAULT CURRENT_DATE,
            streak INTEGER DEFAULT 1,
            admin BOOL DEFAULT 0 
        )
    ''')

    # TAULA: login_history
    c.execute('''
        CREATE TABLE IF NOT EXISTS login_history (
            username TEXT,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(username, login_time),
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')

    # TAULA: test_results
    c.execute('''
        CREATE TABLE IF NOT EXISTS test_results (
            username TEXT,
            test_type TEXT,
            date DATE DEFAULT CURRENT_DATE,
            score REAL,
            PRIMARY KEY(username, test_type, date),
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')

    # TAULA: daily_checkin
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_checkin (
            username TEXT,
            date DATE DEFAULT CURRENT_DATE,
            face INTEGER CHECK(face BETWEEN 1 AND 5),
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')

    #  TAULA: incidencies
    c.execute('''
        CREATE TABLE IF NOT EXISTS incidencies (
            username TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            incidencia INTEGER CHECK(incidencia BETWEEN 0 AND 9),
            PRIMARY KEY(username, date, incidencia),
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')

    # TAULA: logs
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            username TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            text TEXT,
            PRIMARY KEY(username, date),
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_user(username, password, name, admin=0) -> bool:
    """Crea un nou usuari amb la contrasenya hashada (seguretat bàsica)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Hash password per seguretat (fins i tot en hackathons queda bé fer-ho)
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        c.execute('INSERT INTO users (username, password, name, admin) VALUES (?, ?, ?, ?)', 
                  (username, hashed_pw, name, admin))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # L'usuari ja existeix
    finally:
        conn.close()

def check_login(username, password) -> type_user | None:
    """Verifica si l'usuari i contrasenya són correctes."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_pw))
    data = c.fetchone()
    conn.close()
    print(data)
    return data # Retorna None si no el troba


# --- getters ---

def get_all_patients() -> list[tuple[str, str]]:
    """Retorna llista de tots els usuaris que NO són admins (username, name)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Seleccionem usuaris on admin és 0 o False
    c.execute('SELECT username, name FROM users WHERE admin = 0')
    data = c.fetchall()
    conn.close()
    return data

def get_user_info(username) -> tuple[str, int, str, bool] | None:
    """Retorna (name, streak, last_login, admin) de l'usuari."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT name, streak, last_login, admin FROM users WHERE username = ?', (username,))
    data = c.fetchone()
    conn.close()
    return data

def get_test_history(username, test_type) -> list[float]| None:
    """Retorna llista de puntuacions d'un test específic ordenades per data."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT score FROM test_results WHERE username = ? AND test_type = ? ORDER BY date DESC', 
              (username, test_type))
    data = c.fetchall()
    conn.close()
    return [x[0] for x in data] # Convertir llista de tuples a llista plana

def get_checkin_history(username) -> dict[str, int]| None:
    """Retorna dict {data: face}."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT date, face FROM daily_checkin WHERE username = ?', (username,))
    data = c.fetchall()
    conn.close()
    return {x[0]: x[1] for x in data}

def update_streak(username, new_streak) -> None:
    """Actualitza la ratxa a la DB."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE users SET streak = ? WHERE username = ?', (new_streak, username))
    conn.commit()
    conn.close()

def get_logs(username) -> list[tuple[str, str]]|None:
    """Retorna llista de logs (date, text) de l'usuari."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT date, text FROM logs WHERE username = ? ORDER BY date DESC', (username,))
    data = c.fetchall()
    conn.close()
    return data

# --- Funcions per guardar dades de l'app ---
def add_login_history(username) -> None:
    """Afegeix una entrada a l'historial de logins."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO login_history (username) VALUES (?)', (username,))
    conn.commit()
    conn.close()

def save_test_result(username, test_type, score)-> None:
    """Guarda la puntuació d'un test."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO test_results (username, test_type, score) VALUES (?, ?, ?)',
              (username, test_type, score))
    conn.commit()
    conn.close()

def save_daily_checkin(username, face)-> None:
    """Guarda com se sent avui."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO daily_checkin (username, face) VALUES (?, ?)',
              (username, face))
    conn.commit()
    conn.close()

def save_incidency(username, incidencia)-> None:
    """Guarda una incidència reportada."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO incidencies (username, incidencia) VALUES (?, ?)',
              (username, incidencia))
    conn.commit()
    conn.close()

def save_log(username, text)-> None:
    """Guarda un log de text."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO logs (username, text) VALUES (?, ?)',
              (username, text))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    if create_user("pacient", "1234", "Joan Garcia"): # Usuari de prova
        print("Usuari 'pacient' creat correctament.")
        create_user("admin", "1234", "Administrador", admin=1) # Usuari admin de prova
    else:
        print("L'usuari ja existeix.")