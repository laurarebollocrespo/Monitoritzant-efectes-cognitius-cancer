import streamlit as st
import time

st.title("Pruebas desde el móvil")

st.write("Esta es una prueba sencilla hecha solo con Python.")

# Botón 1
if st.button("Prueba 1"):
    st.success("Has pulsado la Prueba 1")

# Botón 2 con temporizador simple
if st.button("Prueba de tiempo de reacción"):
    st.write("Espera...")
    time.sleep(1)
    start = time.time()
    st.write("¡Pulsa ahora!")
    if st.button("PULSA"): 
        rt = time.time() - start
        st.write(f"Tu tiempo de reacción es: {rt:.3f} segundos")

# Input simple
n = st.number_input("Introduce un número:", 0, 999)
if st.button("Enviar número"):
    st.write(f"Número recibido: {n}")