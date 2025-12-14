import streamlit as st
from app.bot import render_bot  # el teu bot real

st.title("Xats")

# -------------------------
# Inicialització de xats amb professionals
# -------------------------
if "professional_chats" not in st.session_state:
    st.session_state.professional_chats = {
        "Dr. Josep Maria": [
            ("doctor", "Hola, com t'has trobat aquests últims dies?"),
        ],
        "Dra. Laura Sánchez": [
            ("doctor", "Hola, com portes la concentració últimament?"),
        ]
    }

# -------------------------
# Selector de conversa
# -------------------------
chat_option = st.radio(
    "Selecciona una conversa",
    [
        "OncoBot (assistent)",
        "Dr. Josep Maria (oncologia)",
        "Dra. Laura Sánchez (psicooncologia)"
    ]
)

st.divider()

if chat_option == "OncoBot (assistent)":
    st.subheader("OncoBot")
    st.caption("Assistent de suport cognitiu i seguiment diari")

    render_bot()
else:
    if "Josep" in chat_option:
        name = "Dr. Josep Maria"
        role = "Oncologia"
    else:
        name = "Dra. Laura Sánchez"
        role = "Psicooncologia"

    st.subheader(f"{name}")
    st.caption(role)

    # Mostrar historial de missatges
    for sender, text in st.session_state.professional_chats[name]:
        if sender == "user":
            st.markdown(f"**Tu:** {text}")
        else:
            st.markdown(f"**{name}:** {text}")

    # Formulari per enviar missatge
    with st.form(key=f"chat_form_{name}", clear_on_submit=True):
        user_message = st.text_input("Escriu un missatge:")
        send = st.form_submit_button("Enviar")

        if send and user_message:
            st.session_state.professional_chats[name].append(
                ("user", user_message)
            )
            st.rerun()
