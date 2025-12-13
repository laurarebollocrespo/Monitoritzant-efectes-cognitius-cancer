import sys
import os
from datetime import datetime, timedelta

# Importem database des del mateix paquet
from app import database as db

class User:
    name: str
    username: str
    streak: int
    admin: bool
    last_login: str  # Data en format string "YYYY-MM-DD"
    test_results: dict[str, list[float]]  # Resultats per tipus de test
    daily_check_in: dict[str, int]  # Historial de check-ins diaris {data: face}
    logs: list[tuple[str, str]]  # Historial de logs (date, text)

    def __init__(self, username):
        self.username = username
        
        # 1. Carregar dades de la DB
        user_info = db.get_user_info(username)
        print(user_info)
        if user_info:
            self.name = user_info[0]
            self.streak = user_info[1] if user_info[1] is not None else 0
            self.last_login = user_info[2] # String YYYY-MM-DD
            self.admin = True if user_info[3] else False

        else:
            self.name = "Unknown"
            self.streak = 0
            self.last_login = None
        if user_info:
            self.name = user_info[0]
            self.streak = user_info[1] if user_info[1] is not None else 0
            self.last_login = user_info[2]
            # Capturem el flag d'admin (1 = True, 0 = False)
            self.is_admin = True if user_info[3] == 1 else False
        else:
            self.name = "Unknown"
            self.streak = 0
            self.last_login = None
            self.is_admin = False

        # Si és admin, no cal calcular streak ni carregar tests seus
        if not self.is_admin:
            self._calculate_streak()
            # Carregar dades només si és pacient
            self.test_results = {
                "Fluencia": db.get_test_history(username, "Fluencia"),
                "Atencio": db.get_test_history(username, "Atencio"),
                "Memoria": db.get_test_history(username, "Memoria"),
                "Velocitat": db.get_test_history(username, "Velocitat")
            }
            self.daily_check_in = db.get_checkin_history(username)

            self.test_results = {
            "Fluencia": db.get_test_history(username, "Fluencia"),
            "Atencio": db.get_test_history(username, "Atencio"),
            "Memoria": db.get_test_history(username, "Memoria"),
            "Velocitat": db.get_test_history(username, "Velocitat")
            }
            self.daily_check_in = db.get_checkin_history(username)
            self.logs = db.get_logs(username)

        self.registrar_login()
           
        

    def _calculate_streak(self):
        """Calcula la ratxa basant-se en l'última connexió."""
        today_date = datetime.now().date()
        today_str = today_date.strftime("%Y-%m-%d")

        # Si és la primera vegada o no hi ha data
        if not self.last_login:
            self.streak = 1
            self.last_login = today_str
            db.update_streak(self.username, self.streak, self.last_login)
            db.add_login_history(self.username)
            return

        # Convertir string last_login a objecte date
        try:
            last_login_date = datetime.strptime(self.last_login, "%Y-%m-%d").date()
        except ValueError:
            # Si el format fos incorrecte, resetegem
            self.streak = 1
            self.last_login = today_str
            db.update_streak(self.username, self.streak, self.last_login)
            return

        delta = (today_date - last_login_date).days

        if delta == 0:
            # Ja s'ha connectat avui, no fem res
            pass
        elif delta == 1:
            # Es va connectar ahir, sumem ratxa!
            self.streak += 1
            self.last_login = today_str
            db.update_streak(self.username, self.streak, self.last_login)
            db.add_login_history(self.username)
        else:
            # Ha passat més d'un dia, resetegem ratxa
            self.streak = 1
            self.last_login = today_str
            db.update_streak(self.username, self.streak, self.last_login)
            db.add_login_history(self.username)

    # --- MÈTODES D'ACTUALITZACIÓ ---

    def actualiza_punt_fluencia(self, paraules: int):
        self.test_results["Fluencia"].append(paraules)
        db.save_test_result(self.username, "Fluencia", float(paraules))

    def actualiza_punt_atencio(self, nivel: int):
        self.test_results["Atencio"].append(nivel)
        db.save_test_result(self.username, "Atencio", float(nivel))

    def actualiza_punt_memoria(self, nivel: int):
        self.test_results["Memoria"].append(nivel)
        db.save_test_result(self.username, "Memoria", float(nivel))

    def actualiza_punt_velocitat(self, t: float, num_errors: int):
        
        # Score final pot ser temps + penalització
        score_final = t + (num_errors * 2)
        self.test_results["Velocitat"].append(score_final)
        db.save_test_result(self.username, "Velocitat", score_final)

    def registrar_checkin(self, face: int):
        """Registra un nou check-in diari a la DB."""
        avui = datetime.now().strftime("%Y-%m-%d")
        self.daily_check_in[avui] = face
        db.save_daily_checkin(self.username, face)

    def registrar_incidencia(self, incidencia_id: int):
        """Registra una nova incidència a la DB."""
        db.save_incidency(self.username, incidencia_id)
        
    def registrar_log(self, text: str):
        """Registra una nova entrada de diari a la DB."""
        db.save_log(self.username, text)
    
    def registrar_login(self):
        """Registra un nou login a la DB."""
        db.add_login_history(self.username)
