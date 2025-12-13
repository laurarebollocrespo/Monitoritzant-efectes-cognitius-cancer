import sqlite3
import hashlib

DB_NAME = "oncoconnect.db"
type_user = tuple[str, str, str, str, int]  # username, password, name, last_login, strike


def init_db() -> None:
    """Inicialitza la base de dades si no existeix."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # TAULA: users
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            name TEXT,
            last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            streak INTEGER DEFAULT 0 
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
            date DATE DEFAULT CURRENT_DATE,
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

def create_user(username, password, name) -> bool:
    """Crea un nou usuari amb la contrasenya hashada (seguretat bàsica)."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Hash password per seguretat (fins i tot en hackathons queda bé fer-ho)
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        c.execute('INSERT INTO users (username, password, name) VALUES (?, ?, ?)', 
                  (username, hashed_pw, name))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # L'usuari ja existeix
    finally:
        conn.close()

def check_login(username, password) -> type_user | None:
    """Verifica si l'usuari i contrasenya són correctes."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_pw))
    data = c.fetchone()
    conn.close()
    
    return data # Retorna None si no el troba

def add_login_history(username) -> None:
    """Afegeix una entrada a l'historial de logins."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO login_history (username) VALUES (?)', (username,))
    conn.commit()
    conn.close()

# --- Funcions per guardar dades de l'app ---

def save_test_result(username, test_type, score)-> None:
    """Guarda la puntuació d'un test."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO test_results (username, test_type, score) VALUES (?, ?, ?)',
              (username, test_type, score))
    conn.commit()
    conn.close()

def save_daily_checkin(username, face)-> None:
    """Guarda com se sent avui."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO daily_checkin (username, face) VALUES (?, ?)',
              (username, face))
    conn.commit()
    conn.close()

def save_incidency(username, incidencia)-> None:
    """Guarda una incidència reportada."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO incidencies (username, incidencia) VALUES (?, ?)',
              (username, incidencia))
    conn.commit()
    conn.close()

def save_log(username, text)-> None:
    """Guarda un log de text."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO logs (username, text) VALUES (?, ?)',
              (username, text))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    if create_user("pacient", "1234", "Joan Garcia"): # Usuari de prova
        print("Usuari 'pacient' creat correctament.")
    else:
        print("L'usuari ja existeix.")