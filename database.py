import sqlite3
import hashlib

DB_NAME = "oncoconnect.db"
type_user = tuple[str, str, str, int] #username, password, name, strike

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
            strike INTEGER DEFAULT 0,
            
        )
    ''')
    
    # TAULA: test_results
    c.execute('''
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            test_type TEXT,
            score REAL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')

    # TAULA: daily_checkin
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_checkin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            symptom_category TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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

# --- Funcions per guardar dades de l'app ---

def save_test_result(username, test_type, score)-> None:
    """Guarda la puntuació d'un test."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO test_results (username, test_type, score) VALUES (?, ?, ?)',
              (username, test_type, score))
    conn.commit()
    conn.close()

def save_daily_checkin(username, symptom)-> None:
    """Guarda el símptoma del dia."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO daily_checkin (username, symptom_category) VALUES (?, ?)',
              (username, symptom))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    if create_user("pacient", "1234", "Joan Garcia"): # Usuari de prova
        print("Usuari 'pacient' creat correctament.")
    else:
        print("L'usuari ja existeix.")