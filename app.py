import streamlit as st
import tempfile
from weather_chat import handle_input  # Your chatbot logic

from gtts import gTTS
import os

# Function to convert text to speech and return a WAV or MP3 path
def speak_text(text):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tts = gTTS(text=text, lang='en')
        tts.save(tmp_file.name)
        return tmp_file.name  # return mp3 path directly

# Streamlit UI
st.set_page_config(page_title="Weather Voice Assistant", page_icon="🌦️")

st.title("🌦️ Weather Assistant (Text + Voice Output)")
st.write("Type your message and receive a voice + text response.")

# Chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display previous chat
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Text input
user_input = st.text_input("Type your message:")

if st.button("Send") and user_input:
    # Save user's message
    st.session_state["messages"].append({"role": "user", "content": user_input})

    # Get chatbot reply
    response = handle_input(user_input)
    st.session_state["messages"].append({"role": "assistant", "content": response})

    # Convert response to speech
    audio_path = speak_text(response)
    st.audio(audio_path)  # Play MP3 directly

    st.experimental_rerun()

# Clear chat button
if st.button("Clear Chat"):
    st.session_state["messages"] = []
    st.experimental_rerun()