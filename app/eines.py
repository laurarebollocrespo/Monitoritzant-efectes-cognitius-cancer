import streamlit as st
import streamlit.components.v1 as components
from user import User

# Asignación de valores del usuario y constantes

IDS:dict[int, list[str]] = {
        0: ['hcBaJisV1Wo', 'sB6u7ZhNrHk', '24P5B6L0IgQ'],
        1: ['B_M8eFq2GCA', '_5HCl5CDA94', 'fXDHm8PP6qo', 'OlyIT2zIimw', 'zXqljYzFb3w'],
        2: ['B_M8eFq2GCA', '_5HCl5CDA94', 'fXDHm8PP6qo', 'OlyIT2zIimw', 'zXqljYzFb3w'],
        3: ['RExO6edCQYk', 'FJIy-R3Gze4', 'iGTnb1YeRNw'],
        4: ['RExO6edCQYk', 'FJIy-R3Gze4']
       
    }
CAPTIONS:dict[int, list[str]] = {
    0: ["La congición y sus funciones", "Déficits cognitivos y cáncer", "Déficits cognitivos en el día a día"],
    1: ['Mindfulness', 'Preparación para la práctica', 'Postura', 'Amabilidad ante fallos cognitivos', 'Aceptación ante los fallos cognitivos'],
    2: ['Mindfulness', 'Preparación para la práctica', 'Postura', 'Amabilidad ante fallos cognitivos', 'Aceptación ante los fallos cognitivos'],
    3: ['Estimulación', 'Estrategias de compensación', 'Uso de agenda'],
    4: ['Estimulación', 'Estrategias de compensación']
}

# funciones para la página
def embed_youtube(video_id:str, width_percent=100)->str:
    """Enventana un video de youtube a partir de su id"""
    # Calculate height based on 16:9 aspect ratio
    html_code = f'''
    <div style="position: relative; padding-bottom: 56.25%; /* 16:9 aspect ratio */ 
                height: 0; overflow: hidden; width: {width_percent}%;">
        <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
                src="https://www.youtube.com/embed/{video_id}"
                frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen>
        </iframe>
    </div>
    '''
    return html_code

def column_organizer(deficit: int, ids:dict[int, list[str]], captions:dict[int, list[str]])->None:
    """Coloca en columnas los vídeos que correspondan al déficit. 0 si existe deficit y 
    1-4 fluencia - atención - memoria de trabajo - velocidad"""
    n = len(ids[deficit])
    col1, col2 = st.columns(2)
    for i in range(n):
        if i % 2 == 0:
            with col1:
                components.html(
                    embed_youtube(ids[deficit][i]),
                    height=200
                )
                st.caption(captions[deficit][i])
        else:
            with col2:
                components.html(
                    embed_youtube(ids[deficit][i]),
                    height=200
                )
                st.caption(captions[deficit][i])

def deficit_materiel(defic:int, ids:dict[int, list[str]], captions:dict[int, list[str]]):
    """Añade flavor text a cada déficit"""
    if defic == 0: # existencia de déficits en general
        st.subheader("Dèficits")
        st.write("Recomanem els següents vídeos per comprendre millor la teva situació")
        # embed de vídeos

    elif defic == 1: #Fluencia
        st.subheader("Dificultats de fluència verbal")
        st.write("Sovint els pacients experimenten alguns problemes en evocar paraules",)
        st.markdown("* Avui és un bon dia per fer una mica d'esport, potser anar a caminar una estona o alguna altra activitat que et vingui de gust.")
        st.markdown("* Avui durant 5 minuts enuncia en veu alta els objectes que veus al teu voltant.")
        st.markdown("* Pensa durant uns minuts quantes fruites i verdures hi ha d'un cert color.")
        
        st.write("Podeu consultar els següents vídeos educacionals per més suggerències:")

    elif defic == 2: # atención
        st.subheader("Problemes atencionals")
        st.write("Les dificultats en la concentració i mantenir l'atenció són habituals en els pacients.",)
        st.markdown("* Avui és un bon dia per fer una mica d'esport, potser anar a caminar una estona o alguna altra activitat que et vingui de gust. ")
        st.markdown("* Aquesta setmana és ideal per fer tornar a fer aquella recepta que has deixat de fer i et sortia tan bé... ")
        st.markdown("* Si tens una estona, llegeix un text curt (una notícia, un paràgraf d’un llibre) i intenta comprendre’l detenidament. Pots subratllar mentalment les idees importants per mantenir-te concentrat.")
        
        st.write("Us oferim els següents vídeos educacionals al respecte:")
        
    elif defic == 3: #Memoria
        st.subheader("Problemes amb la memòria de treball")
        st.write("No és fora del comú que els qui pateixen càncer tenir dificultats en la memòria de treball i curt termini")
        st.markdown("* Avui és un bon dia per fer una mica d'esport, potser anar a caminar una estona o alguna altra activitat que et vingui de gust. ")
        st.markdown("* Aquesta setmana és ideal per fer tornar a fer aquella recepta que has deixat de fer i et sortia tan bé... ")
        st.markdown("* Prova d'aprendre algunes paraules d'un nou idioma, potser un idioma que ja en sàpigues una mica o un completament nou.")        
        st.write("Consulteu els vídeos de sota per més idees o informació:")

    elif defic == 4: #Velocidad
        st.subheader("Dificultat per processar ràpid la informació")
        st.write("Sovint els pacients de càncer experimenten poca traça per respondre amb rapidesa als estímuls")
        st.markdown("* Avui és un bon dia per fer una mica d'esport, potser anar a caminar una estona o alguna altra activitat que et vingui de gust")
        st.markdown("* Avui és el dia de les decisions ràpides: no pots trigar més de 15 segons en escollir la roba que et posaràs.")
        st.markdown("* Dia d'anar al supermercat! Prova a trobar lo més ràpid possible on són les galetes Maria al teu supermercat de confiança.")
        st.write("A continuació u spresentem uns vídeos sobre el tema:")
    column_organizer(defic, ids, captions)

    st.divider()

def ponder(user: User) -> list[int]:
    """Valora las deficiencias cognitivas del usuario basándose en los últimos tests"""
    # Define thresholds (adjust based on your test scoring)
    # These are example thresholds - you'll need to calibrate them
    THRESHOLDS = {
        'Fluencia': {'severe': 40, 'moderate': 55, 'mild': 70},
        'Atencio': {'severe': 35, 'moderate': 50, 'mild': 65},
        'Memoria': {'severe': 30, 'moderate': 45, 'mild': 60},
        'Velocitat': {'severe': 25, 'moderate': 40, 'mild': 55}
    }
    
    deficits = []
    test_types = ['Fluencia', 'Atencio', 'Memoria', 'Velocitat']
    
    for test_type in test_types:
        results = user.test_results.get(test_type, [])
        
        if not results:
            deficits.append(0)  # No data
            continue
        
        # Use last 5-10 results
        recent_results = results[-10:] if len(results) >= 10 else results
        
        # Calculate average of recent results
        avg_score = sum(recent_results) / len(recent_results)
        thresholds = THRESHOLDS[test_type]
        
        # Determine deficit level
        if avg_score < thresholds['severe']:
            deficits.append(3)  # Severe deficit
        elif avg_score < thresholds['moderate']:
            deficits.append(2)  # Moderate deficit
        elif avg_score < thresholds['mild']:
            deficits.append(1)  # Mild deficit
        else:
            deficits.append(0)  # Within normal range
    
    return deficits

def master(user:User)->None:
    """Inicializa la página y valora los déficits del usuario"""
    deficits = ponder(user)

    ids = IDS
    captions = CAPTIONS

    st.title("Finestra d'eines")

    st.header("En aquesta finestra podràs accedir a eines que t'ajudaran a entendre i millorar la teva condició")

    if deficits: # comprobar la presencia de problemas cognitivos
        deficit_materiel(0, ids, captions)
        for defic in deficits:
            deficit_materiel(defic, ids, captions)
    else:
        st.subheader("Tot en orde!")
        st.write("Enhorabona! Les teves respostes indiquen que actualment no presentes problemes cognitius, és important però mantenir un estil de vida saludable per ajudar a prevenir-ho, t'animem a:")
        st.markdown("* Fer esport")
        st.markdown("* Cuidar l'alimentació")
        st.markdown("* Aprendre coses noves")
        st.markdown("* Sociabilitzar")
        st.markdown("* Fer Mindfulness")

if __name__ == '__main__':
    user = User('pe', 'pito', 0, 'ahir', {}, {})
    master(user)