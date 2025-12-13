# Python ejemplo (backend si usas arquitectura cliente-servidor)
import wave
import json
import sys
from vosk import Model, KaldiRecognizer, SetLogLevel

# Opcional: Reducir logs (0=silencioso, -1=verbose)
SetLogLevel(-1)  # O usa 0 para menos logs

def transcribir_audio(ruta_audio, ruta_modelo="model/vosk-model-small-es-0.42"):
    """
    Transcribe un archivo de audio WAV a texto usando Vosk
    """
    try:
        # 1. Cargar modelo
        print("Cargando modelo Vosk...")
        model = Model(ruta_modelo)
        
        # 2. Abrir archivo de audio
        wf = wave.open(ruta_audio, "rb")
        
        # Verificar formato de audio
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
            print("Audio debe ser mono (1 canal) y 16-bit PCM")
            wf.close()
            return None
        
        # 3. Crear reconocedor
        recognizer = KaldiRecognizer(model, wf.getframerate())
        recognizer.SetWords(True)  # Para obtener palabras con timestamps
        
        # 4. Procesar audio en chunks
        print("Procesando audio...")
        results = []
        
        while True:
            data = wf.readframes(4000)  # Leer chunk de audio
            if len(data) == 0:
                break
            
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                if 'text' in result and result['text']:
                    results.append(result['text'])
                    print(f"Fragmento reconocido: {result['text']}")
        
        # Obtener resultado final
        final_result = json.loads(recognizer.FinalResult())
        if 'text' in final_result and final_result['text']:
            results.append(final_result['text'])
        
        wf.close()
        
        # 5. Unir todos los fragmentos
        texto_completo = " ".join(results)
        
        if texto_completo:
            print(f"\n✅ Transcripción completa:")
            print(f"Texto: {texto_completo}")
            return texto_completo
        else:
            print("❌ No se pudo transcribir audio")
            return None
            
    except FileNotFoundError as e:
        print(f"❌ Error: Archivo no encontrado - {e}")
        print(f"Modelo buscado en: {ruta_modelo}")
        print(f"Audio buscado en: {ruta_audio}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
    
    return None

# Versión para procesar en tiempo real desde micrófono
def transcribir_microfono(ruta_modelo="model/vosk-model-small-es-0.42"):
    """
    Transcripción en tiempo real desde micrófono
    """
    import pyaudio
    
    model = Model(ruta_modelo)
    recognizer = KaldiRecognizer(model, 16000)
    
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=8000)
    stream.start_stream()
    
    print("🎤 Escuchando... Habla ahora (Ctrl+C para detener)")
    
    try:
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if len(data) == 0:
                break
                
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                if 'text' in result and result['text']:
                    print(f"\n📝 Reconocido: {result['text']}")
                    
    except KeyboardInterrupt:
        print("\n⏹️  Deteniendo...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Resultado final
        final = json.loads(recognizer.FinalResult())
        if 'text' in final and final['text']:
            print(f"\n✅ Transcripción final: {final['text']}")
            return final['text']
    
    return None

# Función principal con menú
def main():
    print("=" * 50)
    print("TRANSCRIPCIÓN DE VOZ A TEXTO - VOSK CATALÁN")
    print("=" * 50)
    
    print("\nOpciones:")
    print("1. Transcribir archivo de audio WAV")
    print("2. Transcribir desde micrófono en tiempo real")
    print("3. Salir")
    
    opcion = input("\nSelecciona opción (1-3): ").strip()
    
    if opcion == "1":
        # Pedir ruta del archivo
        ruta_audio = input("Ruta del archivo WAV (ej: audio/ejemplo.wav): ").strip()
        
        # Verificar si es .wav
        if not ruta_audio.lower().endswith('.wav'):
            print("⚠️  Solo archivos .wav son soportados")
            # Opcional: convertir de otros formatos
            convertir = input("¿Tienes ffmpeg para convertir? (s/n): ")
            if convertir.lower() == 's':
                import subprocess
                salida_wav = ruta_audio.rsplit('.', 1)[0] + '.wav'
                subprocess.run(['ffmpeg', '-i', ruta_audio, '-ar', '16000', 
                              '-ac', '1', '-f', 'wav', salida_wav])
                ruta_audio = salida_wav
        
        # Transcribir
        texto = transcribir_audio(ruta_audio)
        
        # Guardar resultado
        if texto:
            guardar = input("\n¿Guardar resultado en archivo? (s/n): ")
            if guardar.lower() == 's':
                nombre_archivo = "transcripcion.txt"
                with open(nombre_archivo, "w", encoding="utf-8") as f:
                    f.write(texto)
                print(f"✅ Resultado guardado en {nombre_archivo}")
    
    elif opcion == "2":
        # Verificar pyaudio instalado
        try:
            import pyaudio
            texto = transcribir_microfono()
            
            if texto:
                guardar = input("\n¿Guardar resultado? (s/n): ")
                if guardar.lower() == 's':
                    with open("transcripcion_microfono.txt", "w", encoding="utf-8") as f:
                        f.write(texto)
                    print("✅ Transcripción guardada")
        except ImportError:
            print("❌ PyAudio no instalado. Instala con:")
            print("pip install pyaudio")
            print("En Windows quizás necesites:")
            print("pip install pipwin")
            print("pipwin install pyaudio")
    
    elif opcion == "3":
        print("👋 ¡Hasta luego!")
    else:
        print("❌ Opción no válida")

if __name__ == "__main__":
    main()