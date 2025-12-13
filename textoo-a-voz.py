# Python ejemplo (backend si usas arquitectura cliente-servidor)
from vosk import Model, KaldiRecognizer
import wave
import json

# Cargar modelo catalán
model = Model("model/vosk-model-small-ca-0.4")
rec = KaldiRecognizer(model, 16000)

# Procesar audio
with wave.open("Audio.wav", "rb") as wf:
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            print(result["text"])