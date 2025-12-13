import streamlit as st
import streamlit.components.v1 as components

def embed_youtube(video_id, width_percent=100):
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

# Usage with 2 videos in one row
st.title("Finestra d'eines")

st.header("En aquesta finestra podràs accedir a eines que t'ajudaran a entendre i millorar la teva condició")

## Establecer los déficits del usuario

if ...: # comprobar la presencia de problemas cognitivos
    st.subheader("Dèficits")

    st.write("Recomanem els següents vídeos per comprendre millor la teva situació")
    # Embed de los vídeos de psicoeducación
    st.markdown(f"### La cognició i les seves funcions")

    # Crear las dos columnas iguales
    col1, col2 = st.columns(2)
    with col1:
        components.html(
            embed_youtube("hcBaJisV1Wo"),
            height=200
        )
        st.caption("La congición y sus funciones")

    with col2:
        components.html(
            embed_youtube("sB6u7ZhNrHk"),
            height=200
        )

    with col1:
        components.html(
            embed_youtube("24P5B6L0IgQ"),
            height=200
        )
        st.caption("Déficits cognitivos en el día a día")

st.divider()