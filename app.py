"""
Sagitario.ai - Chatbot con personalidad honesta y directa
Powered by Google Gemini API + Streamlit
"""

import streamlit as st
import google.generativeai as genai

# ---------------------------------------------------------------------------
# Configuración de la página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Sagitario.ai",
    page_icon="🏹",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Personalidad del bot
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """
Eres Sagitario.ai, un asistente conversacional con una personalidad honesta,
directa y sin rodeos. Tus características son:

- Dices la verdad aunque no sea cómoda, siempre con respeto.
- Vas al grano: evitas relleno innecesario y respuestas vagas.
- No endulzas las cosas solo para quedar bien; prefieres ser útil de verdad.
- Tienes un toque de humor seco y franqueza, como el arquero de Sagitario:
  apuntas directo al punto.
- Si no sabes algo, lo admites en vez de inventar.
- Eres cercano y claro, no arrogante: directo no significa grosero.

Responde siempre en el idioma en que te escriba el usuario.
"""

# ---------------------------------------------------------------------------
# Sidebar: configuración de API Key
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("🏹 Sagitario.ai")
    st.caption("Honesto. Directo. Sin rodeos.")

    api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        help="Consigue tu API key en https://aistudio.google.com/app/apikey",
    )

    model_name = st.selectbox(
        "Modelo",
        options=["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
        index=0,
    )

    st.divider()

    if st.button("🗑️ Reiniciar conversación"):
        st.session_state.messages = []
        st.session_state.message_count = 0
        st.rerun()

    st.divider()
    st.caption(
        f"Mensajes enviados: {st.session_state.get('message_count', 0)}"
    )

# ---------------------------------------------------------------------------
# Estado de sesión
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "message_count" not in st.session_state:
    st.session_state.message_count = 0

# ---------------------------------------------------------------------------
# Encabezado
# ---------------------------------------------------------------------------
st.title("🏹 Sagitario.ai")
st.caption("Tu chatbot honesto y directo, sin filtros innecesarios.")

if not api_key:
    st.info(
        "👈 Ingresa tu API Key de Google Gemini en la barra lateral para "
        "empezar a chatear."
    )
    st.stop()

# Configurar Gemini con la API key proporcionada
genai.configure(api_key=api_key)

# ---------------------------------------------------------------------------
# Mostrar historial de mensajes (incluyendo los "anuncios")
# ---------------------------------------------------------------------------
for msg in st.session_state.messages:
    if msg["role"] == "ad":
        st.info("📢 **Espacio Publicitario**")
    else:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ---------------------------------------------------------------------------
# Input del usuario
# ---------------------------------------------------------------------------
user_input = st.chat_input("Escribe tu mensaje a Sagitario.ai...")

if user_input:
    # 1. Mostrar y guardar el mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Incrementar el contador de mensajes
    st.session_state.message_count += 1

    # 3. Construir el historial para Gemini (system prompt + turnos previos)
    try:
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=SYSTEM_PROMPT,
        )

        # Convertir historial al formato que espera Gemini, ignorando
        # los marcadores de "ad" que insertamos nosotros
        gemini_history = []
        for msg in st.session_state.messages[:-1]:  # todo menos el último (recién enviado)
            if msg["role"] == "ad":
                continue
            role = "model" if msg["role"] == "assistant" else "user"
            gemini_history.append({"role": role, "parts": [msg["content"]]})

        chat = model.start_chat(history=gemini_history)

        with st.chat_message("assistant"):
            with st.spinner("Sagitario.ai está pensando..."):
                response = chat.send_message(user_input)
                reply = response.text

            st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})

    except Exception as e:
        st.error(f"Ocurrió un error al contactar a Gemini: {e}")

    # 4. Cada 10 mensajes, insertar el "Espacio Publicitario"
    if st.session_state.message_count % 10 == 0:
        st.session_state.messages.append({"role": "ad"})
        st.info("📢 **Espacio Publicitario**")

    # Refrescar para actualizar el contador en la sidebar
    st.rerun()
