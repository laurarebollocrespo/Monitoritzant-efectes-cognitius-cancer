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

    games_played: list[int]  # Estat dels jocs jugats [Fluencia, Atencio, Memoria, Velocitat]

    def __init__(self, username):
        self.username = username
        
        # Inicialitzem contenidors buits per seguretat
        self.test_results = {"Fluencia": [], "Atencio": [], "Memoria": [], "Velocitat": []}
        self.daily_check_in = {}
        self.logs = []
        self.games_played = [0, 0, 0, 0]

        # 1. Carregar dades de la DB
        user_info = db.get_user_info(username)
        
        if user_info:
            self.name = user_info[0]
            self.streak = user_info[1] if user_info[1] is not None else 0
            self.last_login = user_info[2] # String YYYY-MM-DD
            # Capturem el flag d'admin (1 = True, 0 = False)
            self.admin = True if user_info[3] else False
        else:
            self.name = "Unknown"
            self.streak = 0
            self.last_login = None
            self.admin = False

        # Si és admin, no cal calcular streak ni carregar tests seus
        if not self.admin:
            self._calculate_streak()
            
            # Carregar dades només si és pacient
            self.test_results = {
                "Fluencia": db.get_test_history(username, "Fluencia") or [],
                "Atencio": db.get_test_history(username, "Atencio") or [],
                "Memoria": db.get_test_history(username, "Memoria") or [],
                "Velocitat": db.get_test_history(username, "Velocitat") or []
            }
            self.daily_check_in = db.get_checkin_history(username) or {}
            self.logs = db.get_logs(username) or []

            # Calculem quins jocs estan "actius" (fets fa menys de 6 mesos)
            self.current_games_played()

        # Registrem el login actual
        self.registrar_login()
        self.actualitza_last_login()
        

    def _calculate_streak(self):
        """Calcula la ratxa basant-se en l'última connexió."""
        today_date = datetime.now().date()
        today_str = today_date.strftime("%Y-%m-%d")

        # Si és la primera vegada o no hi ha data
        if not self.last_login:
            self.streak = 1
            self.last_login = today_str
            db.update_streak(self.username, self.streak)
            return

        # Convertir string last_login a objecte date
        try:
            # Intentem format curt (el que sol guardar SQLite CURRENT_DATE)
            last_login_date = datetime.strptime(self.last_login, "%Y-%m-%d").date()
        except ValueError:
            try:
                # Intentem format llarg per si de cas
                last_login_date = datetime.strptime(self.last_login, "%Y-%m-%d %H:%M:%S").date()
            except ValueError:
                # Si falla tot, resetegem
                self.streak = 1
                self.last_login = today_str
                db.update_streak(self.username, self.streak)
                return
        
        delta = (today_date - last_login_date).days

        if delta == 0:
            pass # Ja s'ha connectat avui
        elif delta == 1:
            self.streak += 1 # Es va connectar ahir
            db.update_streak(self.username, self.streak)
        else:
            self.streak = 1 # Ratxa trencada
            db.update_streak(self.username, self.streak)

    # --- MÈTODES D'ACTUALITZACIÓ ---

    def actualiza_punt_fluencia(self, paraules: int):
        self.test_results["Fluencia"].append(paraules)
        db.save_test_result(self.username, "Fluencia", float(paraules))
        self.mark_game_played(0)  # Fluencia és el joc 0

    def actualiza_punt_atencio(self, nivel: int):
        self.test_results["Atencio"].append(nivel)
        db.save_test_result(self.username, "Atencio", float(nivel))
        self.mark_game_played(1)  # Atencio és el joc 1

    def actualiza_punt_memoria(self, nivel: int):
        self.test_results["Memoria"].append(nivel)
        db.save_test_result(self.username, "Memoria", float(nivel))
        self.mark_game_played(2)  # Memoria és el joc 2

    def actualiza_punt_velocitat(self, t: float, num_errors: int):
        score_final = t + (num_errors * 2)
        self.test_results["Velocitat"].append(score_final)
        db.save_test_result(self.username, "Velocitat", score_final)
        self.mark_game_played(3)  # Velocitat és el joc 3

    def registrar_checkin(self, face: int):
        avui = datetime.now().strftime("%Y-%m-%d")
        self.daily_check_in[avui] = face
        db.save_daily_checkin(self.username, face)

    def registrar_incidencia(self, incidencia_id: int):
        db.save_incidency(self.username, incidencia_id)
        
    def registrar_log(self, text: str):
        db.save_log(self.username, text)
    
    def registrar_login(self):
        db.add_login_history(self.username)
    
    def actualitza_last_login(self):
        db.save_last_login(self.username)

    def last_test_date(self, test_type: str) -> str | None:
        return db.get_last_test(self.username, test_type)
    
    def current_games_played(self):
        # Indexs: 0:Fluencia, 1:Atencio, 2:Memoria, 3:Velocitat
        for i, test in enumerate(["Fluencia", "Atencio", "Memoria", "Velocitat"]):
            last = self.last_test_date(test)
            if last:
                # --- CORRECCIÓ DE L'ERROR ---
                try:
                    # La DB guarda "YYYY-MM-DD", no té hores/minuts
                    last_date = datetime.strptime(last, "%Y-%m-%d").date()
                except ValueError:
                    # Fallback per si alguna vegada es guarda amb hores
                    try:
                        last_date = datetime.strptime(last, "%Y-%m-%d %H:%M:%S").date()
                    except ValueError:
                        continue # Si la data està corrupta, ignorem

                today = datetime.now().date()
                if (today - last_date).days < 180:
                    self.games_played[i] = 1
                    
    def mark_game_played(self, game_index: int):
        self.games_played[game_index] = 1