

class User:
    user_id: str # Nombre de usuario
    name: str # Nombre real de la persona
    log_ins: list[str] # Lista de fechas en las que el usuario ha hecho log_in
    streak: int # Racha de dias consecutivos que ha hecho log_in

    test_results: dict[str, list[float]] # dict[tipo_de_prueba: resultados]

    # Com em sento avui? (1 a 5)
    daily_check_in: dict[str, list[int]] # dict[fecha, int]

    # Que m'ha passat? (desplegable 10 opciones)
    incidencies: dict[str, list[int]]

    # Diario
    logs: dict[str, str] # dict[Timestamp, texto]

    def __init__(self, user_id, db_conn):
        self.user_id = user_id
        self.daily_logs = []
        self.test_results = {"Fluencia": [], "Atencio": [], "Memoria": [], "Velocitat": []}

    def actualiza_punt_fluencia(self, paraules: int):
        """parules: numero de palabras dichas en el test"""
        self.test_results["Fluencia"].append(paraules)

    def actualiza_punt_atencio(self, nivel: int):
        """nivel: nivel final en el que te quedas"""
        self.test_results["Atencio"].append(nivel)

    def actualiza_punt_memoria(self, nivel: int):
        """parules: nivel final el que te quedas en el test"""
        self.test_results["Memoria"].append(nivel)

    def actualiza_punt_velocitat(self, t: float, num_erorrs: int):
        """parules: numero de palabras dichas en el test"""
        self.test_results["velocitat"].append((t, num_erorrs))
    

    