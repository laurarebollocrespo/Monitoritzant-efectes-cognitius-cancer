
def carrega_paraules(path: str):
    paraules: set[str] = set()
    with open(path, encoding="utf-8") as f:
        for linia in f:
            linia = linia.strip()
            if not linia or '=' not in linia:
                continue
            paraula, resta = linia.split('=', 1)
            fonts = None
            for part in resta.split(';'):
                if part.startswith('fonts:'):
                    fonts = part.replace('fonts:', '').strip()
            #afegim la paraula si no és de la font dsalut. No volem termes mèdics
            if fonts != 'dsalut':
                paraules.add(paraula.lower())
    return paraules


DICCIONARI_GENERAL = carrega_paraules("noms-fdic.txt")


