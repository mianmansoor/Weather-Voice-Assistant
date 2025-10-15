import streamlit as st
import tempfile
from weather_chat import handle_input  # Your chatbot logic

from gtts import gTTS
from pydub import AudioSegment
import os

# Function to convert text to speech and return a WAV file path
def speak_text(text):
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tts.save(tmp_file.name)
        audio = AudioSegment.from_mp3(tmp_file.name)
        wav_path = tmp_file.name.replace(".mp3", ".wav")
        audio.export(wav_path, format="wav")
        return wav_path

# Streamlit UI
st.set_page_config(page_title="Weather Voice Assistant", page_icon="🌦️")

st.title("🌦️ Weather Assistant (Text + Voice Output)")
st.write("Type your query and get a spoken + text response.")

# Chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display past chat
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Text input
user_input = st.text_input("Type your message:")

if st.button("Send") and user_input:
    # Save user message
    st.session_state["messages"].append({"role": "user", "content": user_input})
    
    # Get response
    response = handle_input(user_input)
    st.session_state["messages"].append({"role": "assistant", "content": response})

    # Voice output using gTTS
    wav_path = speak_text(response)
    st.audio(wav_path)  # Play response

    st.experimental_rerun()

# Clear history
if st.button("Clear Chat"):
    st.session_state["messages"] = []
    st.experimental_rerun()