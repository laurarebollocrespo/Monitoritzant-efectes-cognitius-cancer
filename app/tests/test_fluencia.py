import streamlit as st
import random
import time
import json
import threading
import os
import pyaudio
from vosk import Model, KaldiRecognizer
from queue import Queue
from threading import Thread
from difflib import get_close_matches
import openai

# ======================================================
# RECONOCIMIENTO DE VOZ
# ======================================================

class VoiceRecognition:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = os.path.join(
                os.path.dirname(__file__),
                "model/vosk-model-small-ca-0.4"
            )
        self.model_path = model_path
        self.model = None
        self.recognizer = None
        self.audio_queue = Queue()
        self.is_listening = False
        self.last_word = ""

    def initialize_model(self):
        try:
            self.model = Model(self.model_path)
            self.recognizer = KaldiRecognizer(self.model, 16000)
            self.recognizer.SetWords(True)
            return True
        except Exception as e:
            st.error(f"Error inicializando modelo: {e}")
            return False

    def listen_microphone(self):
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
                    text = result.get("text", "").strip()

                    if text:
                        words = text.split()
                        last_word = words[-1].lower()

                        if last_word != self.last_word and len(last_word) > 2:
                            self.last_word = last_word
                            self.audio_queue.put(last_word)

                else:
                    partial = json.loads(self.recognizer.PartialResult())
                    st.session_state.partial_text = partial.get("partial", "")

        except Exception as e:
            st.error(f"Error en reconocimiento: {e}")

        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    def start_listening(self):
        if self.initialize_model():
            Thread(target=self.listen_microphone, daemon=True).start()
            return True
        return False

    def stop_listening(self):
        self.is_listening = False


# ======================================================
# DATASETS
# ======================================================

fields = {
    "fruites": ["poma", "pera", "plàtan", "taronja"],
    "animals": ["gat", "gos", "elefant", "lleó"],
    "colors": ["vermell", "blau", "verd", "groc"],
    "transports": ["cotxe", "tren", "avió"],
    "roba": ["camisa", "pantalons", "vestit"]
}

field_representatives = {
    "fruites": "fruita",
    "animals": "animal",
    "colors": "color",
    "transports": "vehicle",
    "roba": "peça de roba"
}

valid_letters = [l for l in "abcdefghijklmnopqrstuvwxyz" if l not in "wxyzhkgq"]

TEST_DURATION = 60

# -----------------------------
# Configuración OpenAI
# -----------------------------
API_KEY = "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"
client = openai.OpenAI(api_key=API_KEY)


# ======================================================
# VALIDACIONES
# ======================================================

def validar_letra(word, letter):
    w = word.lower().strip()
    if w in st.session_state.used_words:
        return "incorrect"
    if not w.startswith(letter):
        return "incorrect"
    return "correct"

def validar_campo(word, field):
    w = word.lower().strip()
    if w in st.session_state.used_words:
        return "incorrect"
    if w in fields[field]:
        return "correct"
    return "pending"

def validar_campo_gpt(word, field, result_dict):
    try:
        prompt = f"Responde solo SI o NO. ¿'{word}' es un {field_representatives[field]}?"
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        answer = response.choices[0].message.content.strip().upper()
        result_dict["state"] = "correct" if answer.startswith("SI") else "incorrect"
    except Exception:
        result_dict["state"] = "incorrect"


# ======================================================
# TEST DE FLUENCIA
# ======================================================

def run_fluencia():

    # ---------- SESSION STATE ----------
    defaults = {
        "screen": "instructions",
        "start_time": None,
        "words": [],
        "used_words": set(),
        "current_type": "letter",
        "current_letter": random.choice(valid_letters),
        "current_field": random.choice(list(fields.keys())),
        "voice_recognition": VoiceRecognition(),
        "is_listening": False,
        "partial_text": "",
        "fluencia_saved": False
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # ---------- INSTRUCCIONES ----------
    if st.session_state.screen == "instructions":
        st.title("Fluencia verbal alternante")
        st.write("Alterna entre letra y categoría. Duración: 60s")

        if st.button("Comenzar"):
            st.session_state.start_time = time.time()
            st.session_state.screen = "test"
            st.rerun()

    # ---------- TEST ----------
    elif st.session_state.screen == "test":

        elapsed = time.time() - st.session_state.start_time
        time_left = max(TEST_DURATION - elapsed, 0)

        st.progress(time_left / TEST_DURATION)
        st.metric("Tiempo restante", f"{int(time_left)}s")

        if st.session_state.current_type == "letter":
            st.subheader(f"Letra: {st.session_state.current_letter.upper()}")
        else:
            st.subheader(f"Campo: {st.session_state.current_field}")

        # Voz
        if not st.session_state.is_listening:
            if st.button("🎤 Activar voz"):
                if st.session_state.voice_recognition.start_listening():
                    st.session_state.is_listening = True
                    st.rerun()
        else:
            if st.button("⏹ Detener voz"):
                st.session_state.voice_recognition.stop_listening()
                st.session_state.is_listening = False
                st.rerun()

        if st.session_state.partial_text:
            st.caption(f"Reconociendo: {st.session_state.partial_text}")

        # Entrada manual
        with st.form("input_form", clear_on_submit=True):
            word = st.text_input("Escribe palabra")
            submit = st.form_submit_button("Enviar")

        voice_word = None
        if st.session_state.is_listening and not st.session_state.voice_recognition.audio_queue.empty():
            voice_word = st.session_state.voice_recognition.audio_queue.get()

        word_to_process = voice_word or (word if submit else None)

        if word_to_process:
            if st.session_state.current_type == "letter":
                state = validar_letra(word_to_process, st.session_state.current_letter)
            else:
                state = validar_campo(word_to_process, st.session_state.current_field)

            entry = {
                "word": word_to_process,
                "state": state,
                "source": "voz" if voice_word else "manual"
            }

            st.session_state.used_words.add(word_to_process.lower())
            st.session_state.words.append(entry)

            if state == "pending":
                threading.Thread(
                    target=validar_campo_gpt,
                    args=(word_to_process, st.session_state.current_field, entry),
                    daemon=True
                ).start()

            st.session_state.current_type = (
                "field" if st.session_state.current_type == "letter" else "letter"
            )

            st.rerun()

        # Mostrar palabras
        for w in st.session_state.words:
            st.write(f"{w['word']} — {w['state']} ({w['source']})")

        if time_left <= 0:
            st.session_state.screen = "results"
            st.rerun()

    # ---------- RESULTADOS ----------
    elif st.session_state.screen == "results":
        st.title("Resultados")

        correct = sum(w["state"] == "correct" for w in st.session_state.words)
        incorrect = sum(w["state"] == "incorrect" for w in st.session_state.words)

        st.metric("Correctas", correct)
        st.metric("Incorrectas", incorrect)

        if st.button("Volver al inicio"):
            st.session_state.clear()
            st.rerun()