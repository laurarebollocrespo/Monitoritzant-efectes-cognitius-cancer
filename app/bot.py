# bot.py
import streamlit as st
import openai

# Configurar tu API key
API_KEY = "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"
client = openai.OpenAI(api_key=API_KEY)

# Inicializa estado de sesión
if "bot_open" not in st.session_state:
    st.session_state.bot_open = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "bot_mode" not in st.session_state:
    st.session_state.bot_mode = None  # Se seleccionará después del primer mensaje

if "bot_initialized" not in st.session_state:
    st.session_state.bot_initialized = False

GENERIC_WELCOME = """
Hola, soc OncoBot, el teu assistent de suport cognitiu. Puc ajudar-te avui de diverses formes:

1. Entendre millor com funcionen la teva memòria, atenció, velocitat de processament i *fluencia, i respondre als teus dubtes sobre aquests temes.
2. Registrar petits incidents o dificultats que notis en el teu dia a dia, com a oblits o problemes de concentració.
3. Guiar-te per a escriure el teu diari diari, amb preguntes obertes que t'ajudin a expressar com t'has sentit.
4. Preparar-te per a les teves pròximes visites mèdiques, recordant-te incidències importants o ajudant-te a organitzar preguntes per al teu metge.

Explica'm el que vulguis o fes-me qualsevol pregunta, i junts veurem com puc ajudar-te avui.
"""

def detect_mode(user_message: str):
    msg_lower = user_message.lower()
    if any(word in msg_lower for word in ["significa", "explica", "memòria", "atenció", "fluïdesa", "velocitat", "cognitiu"]):
        return "psicoeducativo"
    elif any(word in msg_lower for word in ["oblidar", "desorientat", "confós", "recordo", "perdre"]):
        return "incidencias"
    elif any(word in msg_lower for word in ["diari", "escriure", "avui", "dia", "explicar", "sentit"]):
        return "ayudar_diario"
    else:
        return "recordatorio"


# Función para enviar mensaje al bot
def send_message_to_bot(user_message):
    # Guardar mensaje del usuario
    st.session_state.chat_history.append({"role": "user", "content": user_message})

    # Construir prompt base según el modo
    if st.session_state.bot_mode == "psicoeducativo":
        system_prompt = """
        Eres OncoBot, un asistente psicoeducativo para pacientes con cáncer que explica conceptos de manera sencilla y no alarmista. 
        Tu función es responder preguntas sobre procesos cognitivos o dificultades que los pacientes pueden experimentar durante su tratamiento, especialmente relacionadas con: 
        - Atención sostenida
        - Memoria de trabajo
        - Fluencia alternante
        - Velocidad de procesamiento
        - Fatiga cognitiva y dificultades de concentración

        No des diagnósticos ni interpretes resultados específicos del paciente. Solo ofrece información general y consejos de comprensión cognitiva.

        Ejemplos de preguntas:
        - "¿Qué significa tener problemas de memoria de trabajo?"
        - "¿Por qué me cuesta concentrarme algunos días?"
        - "¿Qué es la fluencia alternante?"
        Responde de forma clara, corta y empática.
        """
    elif st.session_state.bot_mode == "incidencias":
        system_prompt = """
        Ets OncoBot, un assistent que detecta possibles incidències cognitives en llenguatge natural per a ajudar el pacient a registrar-les en l'app. 
        Només reconeixes problemes relacionats amb les quatre capacitats que monitorem: 
        - Atenció sostinguda
        - Memòria de treball
        - Fluencia alternant
        - Velocitat de processament

        Quan l'usuari escriu alguna cosa que indica un problema en el seu dia a dia (oblits, desorientació, dificultat per a concentrar-se, lentitud mental), *proponle amablement registrar-ho com a incidència.

        Exemple d'interacció:
        Usuari: "Em vaig oblidar de prendre la medicina avui"
        Bot: "Sembla que has tingut un petit oblit avui. Vols que ho apuntem com a incidència en el teu registre?"
        """
    elif st.session_state.bot_mode == "ayudar_diario":
        system_prompt = """
        Ets OncoBot, un assistent que ajuda al pacient a escriure el seu diari diari de manera guiada. 
        Si l'usuari té dificultat per a expressar el seu dia, fes-li preguntes obertes i empàtiques centrades en com ha funcionat la seva atenció, memòria, fluencia i velocitat mental, o com s'ha sentit cognitivament.

        Exemples de preguntes:
        - "Què ha estat el més difícil avui per a concentrar-te?"
        - "Has notat algun moment en què la teva memòria et va jugar una mala passada?"
        - "En quin moment t'has sentit més lent mentalment avui?"
        - "Quin assoliment petit has tingut avui malgrat la fatiga?"

        Ofereix ajuda per a redactar l'entrada, però deixa que l'usuari la revisi abans de guardar.
        """
    else:
        system_prompt = """
        Ets OncoBot, un assistent empàtic que recorda check-ins diaris i registres pendents de manera amable. 
        Usa un to flexible i motivador:
        - Normalitza dies difícils
        - Reforça constància sense pressió
        - Evita frases intrusives o culpabilitzadores

        Exemples:
        - "Vols fer el teu check-in d'avui per a mantenir el teu seguiment al dia?"
        - "Si avui no pots, demà seguim sense problema"
        - "Has registrat diverses incidències aquesta setmana, recorda que és normal tenir dies complicats"

        Tens com a dades els check-ins de l'usuari en format python dict[str, int] que representa[fecha_str: mood_int (1-5)]
        """ + str(st.session_state.user.daily_check_in)

    # Llamada básica a OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt}
            ] + st.session_state.chat_history
        )
        bot_message = response.choices[0].message.content.strip()
    except Exception as e:
        bot_message = f"Error al contactar con el bot: {e}"

    # Guardar respuesta del bot
    st.session_state.chat_history.append({"role": "assistant", "content": bot_message})

    return bot_message

# -----------------------------
# Función para renderizar el chat en Streamlit
# -----------------------------
def render_bot():
    # Inicializar con mensaje genérico si no se ha mostrado
    if not st.session_state.bot_initialized:
        st.session_state.chat_history.append({"role": "assistant", "content": GENERIC_WELCOME})
        st.session_state.bot_initialized = True

    # Mostrar historial
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**Tú:** {msg['content']}")
        else:
            st.markdown(f"**Bot:** {msg['content']}")

    # Entrada de usuario
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Escriu un missatge...")
        submit_button = st.form_submit_button("Enviar")
        if submit_button and user_input:
            bot_reply = send_message_to_bot(user_input)
            st.rerun()
