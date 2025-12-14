import streamlit as st
import random
import time
from difflib import get_close_matches
import openai
import threading
import os 
import pyaudio
from vosk import Model, KaldiRecognizer
from queue import Queue
from threading import Thread
import speech_recognition as sr  # Alternativa para simplificar

# -----------------------------
# Configuración de reconocimiento de voz
# -----------------------------

class VoiceRecognition:
    def __init__(self, model_path=os.path.join(os.path.dirname(__file__), "model/vosk-model-small-ca-0.4")):
        self.model_path = model_path
        self.recognizer = None
        self.audio_queue = Queue()
        self.is_listening = False
        self.current_transcription = ""
        self.last_word = ""
        
    def initialize_model(self):
        """Inicializa el modelo de reconocimiento"""
        try:
            self.model = Model(self.model_path)
            self.recognizer = KaldiRecognizer(self.model, 16000)
            self.recognizer.SetWords(True)
            return True
        except Exception as e:
            st.error(f"Error inicializando modelo: {e}")
            return False
    
    def listen_microphone(self):
        """Escucha el micrófono y transcribe en tiempo real"""
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=4000
        )
        
        self.is_listening = True
        
        try:
            while self.is_listening:
                data = stream.read(2000, exception_on_overflow=False)
                
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    if 'text' in result and result['text']:
                        new_text = result['text'].strip()
                        if new_text:
                            # Extraer la última palabra
                            words = new_text.split()
                            if words:
                                last_word = words[-1].lower()
                                # Solo enviar si es diferente a la última palabra detectada
                                if last_word != self.last_word and len(last_word) > 2:
                                    self.last_word = last_word
                                    self.current_transcription = last_word
                                    # Poner en la cola para procesar
                                    self.audio_queue.put(last_word)
                else:
                    # Procesamiento parcial para obtener texto en tiempo real
                    partial = json.loads(self.recognizer.PartialResult())
                    if 'partial' in partial and partial['partial']:
                        partial_text = partial['partial'].strip()
                        if partial_text:
                            # Actualizar visualización en tiempo real
                            st.session_state.partial_text = partial_text
        except Exception as e:
            st.error(f"Error en reconocimiento: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
    
    def start_listening(self):
        """Inicia el reconocimiento en un hilo separado"""
        if self.initialize_model():
            thread = Thread(target=self.listen_microphone, daemon=True)
            thread.start()
            return True
        return False
    
    def stop_listening(self):
        """Detiene el reconocimiento"""
        self.is_listening = False


user = st.session_state.user

# -----------------------------
# Dataset de palabras
# -----------------------------
fields = {
    "fruites": [
        "poma", "pera", "plàtan", "taronja", "maduixa", "meló", "síndria", "kiwi", "mango", "cirera",
        "llimona", "pinya", "mandarina", "nabiu", "coco", "papaia", "maracujà", "guaiaba", "figa", "pruna",
        "gerd", "móra", "litxi", "caqui", "magrana", "aranja", "nectarina", "albercoc", "raïm", "plomissol"
    ],
    "animals": [
        "gat", "gos", "elefant", "tigre", "lleó", "girafa", "cavall", "ovella", "conill", "mico",
        "tauró", "colibrí", "porc", "llop", "ós", "guineu", "pingüí", "dofí", "balena", "àguila",
        "àguila calba", "mussol", "falcó", "linx", "camell", "cabra", "vaca", "pollastre", "gallina", "ànec",
        "oca", "tortuga", "granota", "serp", "iguana", "ratpenat", "orca", "foca", "llúdriga", "cangur"
    ],
    "colors": [
        "vermell", "blau", "verd", "groc", "negre", "blanc", "morat", "rosa", "taronja", "gris",
        "cian", "magenta", "lila", "turquesa", "beix", "ocre", "fúcsia", "lavanda", "ivori", "bronze",
        "maragda", "salmó", "carmesí", "anyil", "grana", "porpra", "safrà", "marró", "mostassa", "verd oliva"
    ],
    "transports": [
        "cotxe", "autobús", "bicicleta", "moto", "avió", "tren", "vaixell", "metro", "tramvia", "patinet",
        "camió", "helicòpter", "ferri", "submarí", "globus aerostàtic", "monopatí", "veler", "iot", "trineu", "caravana"
    ],
    "roba": [
        "camisa", "pantalons", "faldilla", "vestit", "jaqueta", "abric", "sabata", "bota", "sandàlia", "gorra",
        "barret", "bufanda", "guants", "mitjons", "cinturó", "vestit (traje)", "samarreta", "jersei", "jaquetó", "armilla"
    ]
}

field_representatives = {
    "fruites": "fruita",
    "animals": "animal",
    "colors": "color",
    "transports": "vehicle",
    "roba": "prenda de roba"
}

# -----------------------------
# Letras válidas
# -----------------------------
valid_letters = [l for l in "abcdefghijklmnopqrstuvwxyz" if l not in "wxyzhkgq"]

# Càrrega del fitxer amb ruta absoluta per evitar errors
all_words = set()
all_words_list = []

current_dir = os.path.dirname(os.path.abspath(__file__))
txt_path = os.path.join(current_dir, "noms-fdic.txt")

if os.path.exists(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                word = line.split("=")[0].strip()
                all_words.add(word.lower())
                all_words_list.append(word.lower())
else:
    # Fallback si no troba el fitxer per evitar crash
    all_words = set(["hola", "prova"]) 

TEST_DURATION = 60

# -----------------------------
# Configuración OpenAI
# -----------------------------
API_KEY = "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"
client = openai.OpenAI(api_key=API_KEY)

# -----------------------------
# Validaciones
# -----------------------------
def validar_letra(word, letter):
    w = word.lower().strip()
    if w in st.session_state.used_words: return "incorrect"
    if not w.startswith(letter): return "incorrect"
    if w in all_words or get_close_matches(w, all_words, cutoff=0.8): return "correct"
    return "pending"

def validar_campo(word, field):
    w = word.lower().strip()
    if w in st.session_state.used_words: return "incorrect"
    if w in fields[field] or get_close_matches(w, fields[field], cutoff=0.8): return "correct"
    return "pending"

def validar_campo_gpt(word, field, idx, pending_results):
    try:
        prompt = (f"Respon només amb SI o NO.\nLa paraula '{word}' és un/una {field_representatives[field]}?")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        answer = response.choices[0].message.content.strip().upper()
        result = "correct" if answer == "SI" or answer == "SI." else "incorrect"
    except Exception:
        result = "incorrect"
    pending_results['state'] = result

# ==========================================
# FUNCIÓ PRINCIPAL (WRAPPER)
# ==========================================
def run_fluencia():
    # -----------------------------
    # Inicialización session_state
    # -----------------------------
    if "screen" not in st.session_state: st.session_state.screen = "instructions"
    if "start_time" not in st.session_state: st.session_state.start_time = None
    if "words" not in st.session_state: st.session_state.words = []
    if "used_words" not in st.session_state: st.session_state.used_words = set()
    if "current_type" not in st.session_state: st.session_state.current_type = "letter"
    if "current_letter" not in st.session_state: st.session_state.current_letter = random.choice(valid_letters)
    if "current_field" not in st.session_state: st.session_state.current_field = random.choice(list(fields.keys()))
    if "fluencia_saved" not in st.session_state: st.session_state.fluencia_saved = False

    # -----------------------------
    # Instrucciones
    # -----------------------------
    if st.session_state.screen == "instructions":
        st.title("Fluència Verbal")
        st.write(
            "Escriu paraules alternant entre:\n"
            "- Paraules que comencin per una lletra\n"
            "- Paraules d'un camp semàntic\n\n"
            "⏱️ Durada: 60 segons"
        )
        if st.button("Començar"):
            st.session_state.start_time = time.time()
            st.session_state.screen = "test"
            st.session_state.fluencia_saved = False
            st.rerun()

    # -----------------------------
    # Test
    # -----------------------------
    elif st.session_state.screen == "test":
        elapsed = time.time() - st.session_state.start_time
        time_left = max(TEST_DURATION - elapsed, 0)

        st.title("Test en curs")
        st.progress(time_left / TEST_DURATION)
        st.caption(f"Temps restant: {int(time_left)}s")

        if st.session_state.current_type == "letter":
            st.subheader(f"Paraula que comenci per: **{st.session_state.current_letter.upper()}**")
        else:
            st.subheader(f"Paraula del camp: **{st.session_state.current_field}**")

        with st.form("fluencia_form", clear_on_submit=True):
            word = st.text_input("Escriu una paraula")
            submitted = st.form_submit_button("Enviar")

        if submitted and word:
            if st.session_state.current_type == "letter":
                state = validar_letra(word, st.session_state.current_letter)
            else:
                state = validar_campo(word, st.session_state.current_field)

            st.session_state.used_words.add(word.lower())
            idx = len(st.session_state.words)
            st.session_state.words.append({
                "word": word,
                "state": state,
                "field": st.session_state.current_field if st.session_state.current_type == "field" else None
            })

            if state == "pending" and st.session_state.current_type == "field":
                thread = threading.Thread(
                    target=validar_campo_gpt,
                    args=(word, st.session_state.current_field, idx, st.session_state.words[idx]),
                    daemon=True
                )
                thread.start()

            st.session_state.current_type = ("field" if st.session_state.current_type == "letter" else "letter")
            st.rerun()

        # Mostrar palabras
        for w in st.session_state.words:
            color = {"correct": "lightgreen", "incorrect": "lightcoral", "pending": "#f7f7a0"}[w["state"]]
            symbol = {"correct": "✅", "incorrect": "❌", "pending": "⏳"}.get(w["state"], "")
            st.markdown(f"<div style='background:{color}; padding:6px; margin:4px; border-radius:5px;'>{symbol} {w['word']}</div>", unsafe_allow_html=True)

        all_processed = all(w["state"] != "pending" for w in st.session_state.words)
        if time_left <= 0 and all_processed:
            st.session_state.screen = "results"
            st.rerun()

        time.sleep(1)
        st.rerun()

    # -----------------------------
    # Resultados
    # -----------------------------
    elif st.session_state.screen == "results":
        st.title("Resultats")

        correct = sum(1 for w in st.session_state.words if w["state"] == "correct")
        incorrect = sum(1 for w in st.session_state.words if w["state"] == "incorrect")
        pending = sum(1 for w in st.session_state.words if w["state"] == "pending")

        # --- GUARDAR A BASE DE DADES ---
        if not st.session_state.fluencia_saved:
            st.session_state.user.actualiza_punt_fluencia(correct)
            user.mark_game_played(0)
            st.session_state.fluencia_saved = True
            st.toast("Resultats guardats correctament!", icon="💾")
        # -------------------------------

        st.metric("✅ Correctes", correct)
        st.metric("❌ Incorrectes", incorrect)
        if pending > 0: st.write(f"⏳ Pendents de validació: {pending}")

        if st.button("Tornar a l'Inici"):
            # Neteja de variables clau per la pròxima vegada
            keys_to_clear = ["screen", "words", "used_words", "start_time", "fluencia_saved"]
            for k in keys_to_clear:
                if k in st.session_state: del st.session_state[k]
            st.switch_page("app/homepage.py")


#### PELAYO VOICE ####
# fluencia.py
import streamlit as st
import random
import time
from difflib import get_close_matches
import openai
import threading
import os
import json
import pyaudio
from vosk import Model, KaldiRecognizer
from queue import Queue
from threading import Thread
import speech_recognition as sr  # Alternativa para simplificar
# -----------------------------
# Configuración de reconocimiento de voz
# -----------------------------
class VoiceRecognition:
    def __init__(self, model_path=os.path.join(os.path.dirname(__file__), "model/vosk-model-small-ca-0.4")):
        self.model_path = model_path
        self.recognizer = None
        self.audio_queue = Queue()
        self.is_listening = False
        self.current_transcription = ""
        self.last_word = ""
        
    def initialize_model(self):
        """Inicializa el modelo de reconocimiento"""
        try:
            self.model = Model(self.model_path)
            self.recognizer = KaldiRecognizer(self.model, 16000)
            self.recognizer.SetWords(True)
            return True
        except Exception as e:
            st.error(f"Error inicializando modelo: {e}")
            return False
    
    def listen_microphone(self):
        """Escucha el micrófono y transcribe en tiempo real"""
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=4000
        )
        
        self.is_listening = True
        
        try:
            while self.is_listening:
                data = stream.read(2000, exception_on_overflow=False)
                
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    if 'text' in result and result['text']:
                        new_text = result['text'].strip()
                        if new_text:
                            # Extraer la última palabra
                            words = new_text.split()
                            if words:
                                last_word = words[-1].lower()
                                # Solo enviar si es diferente a la última palabra detectada
                                if last_word != self.last_word and len(last_word) > 2:
                                    self.last_word = last_word
                                    self.current_transcription = last_word
                                    # Poner en la cola para procesar
                                    self.audio_queue.put(last_word)
                else:
                    # Procesamiento parcial para obtener texto en tiempo real
                    partial = json.loads(self.recognizer.PartialResult())
                    if 'partial' in partial and partial['partial']:
                        partial_text = partial['partial'].strip()
                        if partial_text:
                            # Actualizar visualización en tiempo real
                            st.session_state.partial_text = partial_text
        except Exception as e:
            st.error(f"Error en reconocimiento: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
    
    def start_listening(self):
        """Inicia el reconocimiento en un hilo separado"""
        if self.initialize_model():
            thread = Thread(target=self.listen_microphone, daemon=True)
            thread.start()
            return True
        return False
    
    def stop_listening(self):
        """Detiene el reconocimiento"""
        self.is_listening = False
# -----------------------------
# Dataset de palabras
# -----------------------------
fields = {
    "fruites": [
        "poma", "pera", "plàtan", "taronja", "maduixa", "meló", "síndria", "kiwi", "mango", "cirera",
        "llimona", "pinya", "mandarina", "nabiu", "coco", "papaia", "maracujà", "guaiaba", "figa", "pruna",
        "gerd", "móra", "litxi", "caqui", "magrana", "aranja", "nectarina", "albercoc", "raïm", "plomissol"
    ],
    "animals": [
        "gat", "gos", "elefant", "tigre", "lleó", "girafa", "cavall", "ovella", "conill", "mico",
        "tauró", "colibrí", "porc", "llop", "ós", "guineu", "pingüí", "dofí", "balena", "àguila",
        "àguila calba", "mussol", "falcó", "linx", "camell", "cabra", "vaca", "pollastre", "gallina", "ànec",
        "oca", "tortuga", "granota", "serp", "iguana", "ratpenat", "orca", "foca", "llúdriga", "cangur"
    ],
    "colors": [
        "vermell", "blau", "verd", "groc", "negre", "blanc", "morat", "rosa", "taronja", "gris",
        "cian", "magenta", "lila", "turquesa", "beix", "ocre", "fúcsia", "lavanda", "ivori", "bronze",
        "maragda", "salmó", "carmesí", "anyil", "grana", "porpra", "safrà", "marró", "mostassa", "verd oliva"
    ],
    "transports": [
        "cotxe", "autobús", "bicicleta", "moto", "avió", "tren", "vaixell", "metro", "tramvia", "patinet",
        "camió", "helicòpter", "ferri", "submarí", "globus aerostàtic", "monopatí", "veler", "iot", "trineu", "caravana"
    ],
    "roba": [
        "camisa", "pantalons", "faldilla", "vestit", "jaqueta", "abric", "sabata", "bota", "sandàlia", "gorra",
        "barret", "bufanda", "guants", "mitjons", "cinturó", "vestit (traje)", "samarreta", "jersei", "jaquetó", "armilla"
    ]
}
field_representatives = {
    "fruites": "fruita",
    "animals": "animal",
    "colors": "color",
    "transports": "vehicle",
    "roba": "prenda de roba"
}
# -----------------------------
# Letras válidas
# -----------------------------
valid_letters = [l for l in "abcdefghijklmnopqrstuvwxyz" if l not in "wxyzhkgq"]
all_words = set()
all_words_list = []
FILE_PATH = os.path.join(os.path.dirname(__file__), "noms-fdic.txt")
with open(FILE_PATH, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            word = line.split("=")[0].strip()
            all_words.add(word.lower())
            all_words_list.append(word.lower())
TEST_DURATION = 60
# -----------------------------
# Configuración OpenAI
# -----------------------------
API_KEY = "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"
client = openai.OpenAI(api_key=API_KEY)
# -----------------------------
# Validaciones
# -----------------------------
def validar_letra(word, letter):
    w = word.lower().strip()
    if w in st.session_state.used_words:
        return "incorrect"
    if not w.startswith(letter):
        return "incorrect"
    if w in all_words or get_close_matches(w, all_words, cutoff=0.8):
        return "correct"
    return "pending"
def validar_campo(word, field):
    w = word.lower().strip()
    if w in st.session_state.used_words:
        return "incorrect"
    if w in fields[field] or get_close_matches(w, fields[field], cutoff=0.8):
        return "correct"
    return "pending"
def validar_campo_gpt(word, field, idx, pending_results):
    try:
        prompt = (
            f"Respon només amb SI o NO.\n"
            f"La paraula '{word}' és un/una {field_representatives[field]}?"
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        answer = response.choices[0].message.content.strip().upper()
        result = "correct" if answer == "SI" or answer == "SI." else "incorrect"
    except Exception:
        result = "incorrect"
    pending_results['state'] = result
# -----------------------------
# Inicialización session_state
# -----------------------------
if "screen" not in st.session_state:
    st.session_state.screen = "instructions"
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "words" not in st.session_state:
    st.session_state.words = []
if "used_words" not in st.session_state:
    st.session_state.used_words = set()
if "current_type" not in st.session_state:
    st.session_state.current_type = "letter"
if "current_letter" not in st.session_state:
    st.session_state.current_letter = random.choice(valid_letters)
if "current_field" not in st.session_state:
    st.session_state.current_field = random.choice(list(fields.keys()))
if "last_tick" not in st.session_state:
    st.session_state.last_tick = time.time()
if "voice_recognition" not in st.session_state:
    st.session_state.voice_recognition = VoiceRecognition()
if "is_listening" not in st.session_state:
    st.session_state.is_listening = False
if "partial_text" not in st.session_state:
    st.session_state.partial_text = ""
if "last_processed_word" not in st.session_state:
    st.session_state.last_processed_word = ""
# -----------------------------
# Instrucciones
# -----------------------------
if st.session_state.screen == "instructions":
    st.title("Fluencia verbal alternante")
    st.write(
        "Escribe palabras alternando entre:\n"
        "- Palabras que empiecen por una letra\n"
        "- Palabras de un campo semántico\n\n"
        "⏱️ Duración: 60 segundos\n\n"
        "🔊 Ahora con reconocimiento de voz!"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Comenzar"):
            st.session_state.start_time = time.time()
            st.session_state.screen = "test"
            st.rerun()
    
    with col2:
        if st.button("Probar micrófono"):
            st.session_state.screen = "mic_test"
            st.rerun()
# -----------------------------
# Prueba de micrófono
# -----------------------------
elif st.session_state.screen == "mic_test":
    st.title("Prueba de micrófono")
    
    if st.button("Iniciar prueba"):
        if st.session_state.voice_recognition.start_listening():
            st.session_state.is_listening = True
            st.success("Micrófono activado. Habla ahora...")
    
    if st.button("Detener prueba"):
        st.session_state.voice_recognition.stop_listening()
        st.session_state.is_listening = False
        st.info("Micrófono detenido")
    
    if st.button("Volver a instrucciones"):
        st.session_state.screen = "instructions"
        st.rerun()
    
    # Mostrar texto reconocido en tiempo real
    if st.session_state.partial_text:
        st.text_area("Texto reconocido:", st.session_state.partial_text, height=100)
# -----------------------------
# Test
# -----------------------------
elif st.session_state.screen == "test":
    # Tiempo transcurrido
    elapsed = time.time() - st.session_state.start_time
    time_left = max(TEST_DURATION - elapsed, 0)
    st.title("Test en curso")
    
    # Barra de progreso y tiempo
    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(time_left / TEST_DURATION)
    with col2:
        st.metric("Tiempo restante", f"{int(time_left)}s")
    # Mostrar consigna
    if st.session_state.current_type == "letter":
        st.subheader(f"Palabra que empiece por: **{st.session_state.current_letter.upper()}**")
    else:
        st.subheader(f"Palabra del campo: **{st.session_state.current_field}**")
    # Controles de voz
    col_voice1, col_voice2 = st.columns(2)
    with col_voice1:
        if not st.session_state.is_listening:
            if st.button("🎤 Activar voz", type="primary"):
                if st.session_state.voice_recognition.start_listening():
                    st.session_state.is_listening = True
                    st.rerun()
    with col_voice2:
        if st.session_state.is_listening:
            if st.button("⏹️ Detener voz", type="secondary"):
                st.session_state.voice_recognition.stop_listening()
                st.session_state.is_listening = False
                st.rerun()
    # Mostrar estado de voz
    if st.session_state.is_listening:
        st.info("🎤 Escuchando... Habla ahora")
        # Mostrar texto parcial
        if st.session_state.partial_text:
            st.caption(f"Reconociendo: {st.session_state.partial_text}")
    else:
        st.warning("Micrófono desactivado - Usa entrada manual")
    # Formulario de entrada manual (como respaldo)
    with st.form("fluencia_form", clear_on_submit=True):
        word = st.text_input("O escribe manualmente:")
        submitted = st.form_submit_button("Enviar manualmente")
    # Procesar entrada de voz
    voice_word = None
    if st.session_state.is_listening and not st.session_state.voice_recognition.audio_queue.empty():
        voice_word = st.session_state.voice_recognition.audio_queue.get()
    
    # Procesar palabra (de voz o manual)
    word_to_process = None
    if voice_word:
        word_to_process = voice_word
        st.success(f"🎤 Palabra detectada: {voice_word}")
    elif submitted and word:
        word_to_process = word
    
    if word_to_process:
        # Validar y procesar la palabra
        if st.session_state.current_type == "letter":
            state = validar_letra(word_to_process, st.session_state.current_letter)
        else:
            state = validar_campo(word_to_process, st.session_state.current_field)
        st.session_state.used_words.add(word_to_process.lower())
        idx = len(st.session_state.words)
        st.session_state.words.append({
            "word": word_to_process,
            "state": state,
            "field": st.session_state.current_field if st.session_state.current_type == "field" else None,
            "source": "voz" if voice_word else "manual"
        })
        if state == "pending" and st.session_state.current_type == "field":
            thread = threading.Thread(
                target=validar_campo_gpt,
                args=(word_to_process, st.session_state.current_field, idx, st.session_state.words[idx]),
                daemon=True
            )
            thread.start()
        # Alternar tipo de palabra
        st.session_state.current_type = (
            "field" if st.session_state.current_type == "letter" else "letter"
        )
        # Actualizar última palabra procesada
        st.session_state.last_processed_word = word_to_process
        
        st.rerun()
    # Mostrar palabras con estado
    st.subheader("Palabras ingresadas:")
    for w in st.session_state.words:
        color = {
            "correct": "lightgreen",
            "incorrect": "lightcoral",
            "pending": "#f7f7a0"
        }[w["state"]]
        symbol = {
            "correct": "✅",
            "incorrect": "❌",
            "pending": "⏳"
        }.get(w["state"], "⏳")
        source_icon = "🎤" if w.get("source") == "voz" else "✍️"
        
        st.markdown(
            f"<div style='background:{color}; padding:8px; margin:4px; border-radius:5px'>"
            f"{symbol} {source_icon} {w['word']}</div>",
            unsafe_allow_html=True
        )
    # Verificar si el test ha terminado
    all_processed = all(w["state"] != "pending" for w in st.session_state.words)
    if time_left <= 0 and all_processed:
        st.session_state.voice_recognition.stop_listening()
        st.session_state.is_listening = False
        st.session_state.screen = "results"
        st.rerun()
    # Actualización automática
    time.sleep(0.5)
    st.rerun()
# -----------------------------
# Resultados
# -----------------------------
elif st.session_state.screen == "results":
    st.title("Resultados")
    correct = sum(1 for w in st.session_state.words if w["state"] == "correct")
    incorrect = sum(1 for w in st.session_state.words if w["state"] == "incorrect")
    pending = sum(1 for w in st.session_state.words if w["state"] == "pending")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("✅ Correctas", correct)
    with col2:
        st.metric("❌ Incorrectas", incorrect)
    with col3:
        st.metric("⏳ Pendientes", pending)
    # Detalles por tipo de entrada
    st.subheader("Detalles:")
    voz_words = [w for w in st.session_state.words if w.get("source") == "voz"]
    manual_words = [w for w in st.session_state.words if w.get("source") == "manual"]
    
    st.write(f"Palabras por voz: {len(voz_words)}")
    st.write(f"Palabras manuales: {len(manual_words)}")
    if st.button("Reiniciar test"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()