import streamlit as st
import tempfile
from weather_chat import handle_input  # Import your chatbot logic

import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import soundfile as sf
import os

# Function to convert text to speech and play it
def speak_text(text):
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tts.save(tmp_file.name)
        audio = AudioSegment.from_mp3(tmp_file.name)
        # Convert to wav because streamlit only supports wav playback
        wav_path = tmp_file.name.replace(".mp3", ".wav")
        audio.export(wav_path, format="wav")
        return wav_path

# Function for speech recognition input
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak now.")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        st.success(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        st.error("Sorry, I could not understand your speech.")
    except sr.RequestError:
        st.error("Speech recognition service is unavailable.")

    return None

# --- Streamlit UI ---
st.set_page_config(page_title="Weather Voice Assistant", page_icon="🌦️")

st.title("🌦️ Weather Voice Assistant")
st.write("Ask about the weather via voice or text.")

# Chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display previous messages
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Input options (voice or text)
col1, col2 = st.columns(2)

with col1:
    if st.button("🎤 Speak"):
        user_text = recognize_speech()
        if user_text:
            st.session_state["messages"].append({"role": "user", "content": user_text})
            response = handle_input(user_text)
            st.session_state["messages"].append({"role": "assistant", "content": response})

            # TTS for response
            wav_path = speak_text(response)
            st.audio(wav_path)  # Play the generated audio

with col2:
    user_input = st.text_input("Or type your message here:")
    if st.button("Send") and user_input:
        st.session_state["messages"].append({"role": "user", "content": user_input})
        response = handle_input(user_input)
        st.session_state["messages"].append({"role": "assistant", "content": response})

        # TTS for response
        wav_path = speak_text(response)
        st.audio(wav_path)

# Clear chat button
if st.button("Clear Chat"):
    st.session_state["messages"] = []
    st.experimental_rerun()
