# app.py — Streamlit front-end for your Weather Voice Assistant
import streamlit as st
import base64
import tempfile
import uuid
import os
import io
from pathlib import Path
import speech_recognition as sr
from TTS.api import TTS
from weather_chat import handle_input  # your existing function

# ---------- Config ----------
st.set_page_config(page_title="Weather Voice Assistant", layout="centered")
st.title("🌤️ Weather Voice Assistant — Voice + Text Demo")

# Initialize TTS model once (adjust model_name if you use a different model)
@st.cache_resource(show_spinner=False)
def load_tts():
    try:
        tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False)
        return tts
    except Exception as e:
        st.warning("TTS model could not be loaded here. Text responses will still work. "
                   "If you want TTS, ensure the host has resources & internet access to download the model.")
        return None

tts_model = load_tts()

# Utilities
def save_wav_bytes(wav_bytes: bytes) -> str:
    """Save bytes to a temporary wav file and return its path."""
    tmp_dir = tempfile.gettempdir()
    filename = os.path.join(tmp_dir, f"upload_{uuid.uuid4().hex}.wav")
    with open(filename, "wb") as f:
        f.write(wav_bytes)
    return filename

def transcribe_audio_file(wav_path: str) -> str:
    """Use SpeechRecognition to transcribe a wav file (recognize_google)."""
    r = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = r.record(source)
    try:
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        st.error(f"Speech recognition request failed: {e}")
        return ""

def synthesize_to_audio_bytes(text: str, tts_model) -> bytes:
    """Synthesize text into wav bytes using Coqui TTS (TTS.api)."""
    if not tts_model:
        return b""
    tmp_path = os.path.join(tempfile.gettempdir(), f"tts_{uuid.uuid4().hex}.wav")
    # Clean the text slightly to improve pronunciation (optional)
    safe_text = text.replace("°C", " degrees Celsius")
    tts_model.tts_to_file(text=safe_text, file_path=tmp_path)
    with open(tmp_path, "rb") as f:
        data = f.read()
    try:
        os.remove(tmp_path)
    except Exception:
        pass
    return data

# ---------- UI Layout ----------
st.markdown("Click **Record**, speak (city, intent or name), then click **Stop**. Or type your message below and press Send.")
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Voice Input")
    # JS recorder widget embedded via components.html
    RECORD_HTML = """
    <style>
    .stButton>button { width:100%;}
    </style>
    <div>
      <button id="recordButton">Record</button>
      <button id="stopButton" disabled>Stop</button>
      <p id="status">Idle</p>
    </div>
    <script>
    const recordButton = document.getElementById("recordButton");
    const stopButton = document.getElementById("stopButton");
    const status = document.getElementById("status");
    let mediaRecorder;
    let audioChunks = [];

    recordButton.onclick = async () => {
      if (!navigator.mediaDevices) {
        alert("Your browser does not support audio recording.");
        return;
      }
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
      mediaRecorder.onstop = async () => {
        const blob = new Blob(audioChunks, { type: 'audio/wav' });
        const reader = new FileReader();
        reader.onloadend = () => {
          const base64data = reader.result.split(',')[1];
          // send base64 to Streamlit via a new file input
          const el = document.createElement("input");
          el.type = "hidden";
          el.id = "audio-base64";
          el.value = base64data;
          document.body.appendChild(el);
        };
        reader.readAsDataURL(blob);
        audioChunks = [];
      };
      mediaRecorder.start();
      status.innerText = "Recording...";
      recordButton.disabled = true;
      stopButton.disabled = false;
    };

    stopButton.onclick = () => {
      if (mediaRecorder && mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
        status.innerText = "Recording stopped. Click 'Process voice' below.";
        recordButton.disabled = false;
        stopButton.disabled = true;
      }
    };
    </script>
    """
    import streamlit.components.v1 as components
    components.html(RECORD_HTML, height=160)

    # The "Process voice" button reads the hidden input and uploads to Streamlit
    if st.button("Process voice"):
        # Read hidden DOM element using JS -> Streamlit can't directly read DOM, but Streamlit sets
        # a special placeholder: we ask the user to paste base64 if the hidden field doesn't exist.
        st.info("If your browser blocked automatic upload, paste the base64 audio string below (from browser console / hidden field).")
        base64_input = st.text_area("Paste base64 audio here (optional)", value="", height=120)
        if base64_input.strip() == "":
            st.warning("No audio base64 pasted. If you recorded, check the page and copy the base64 value from the hidden element with id 'audio-base64'.")
        else:
            try:
                wav_bytes = base64.b64decode(base64_input.strip())
                wav_path = save_wav_bytes(wav_bytes)
                st.success("Audio received. Transcribing...")
                transcribed = transcribe_audio_file(wav_path)
                if transcribed:
                    st.markdown(f"**You said:** {transcribed}")
                    response = handle_input(transcribed)
                    st.markdown(f"**Assistant:** {response}")
                    # TTS
                    if tts_model:
                        audio_bytes = synthesize_to_audio_bytes(response, tts_model)
                        if audio_bytes:
                            st.audio(audio_bytes, format="audio/wav")
                        else:
                            st.warning("TTS could not produce audio here.")
                else:
                    st.warning("Could not transcribe the audio. Try again or use text input.")
            except Exception as e:
                st.error(f"Error processing audio: {e}")

with col2:
    st.subheader("Text Input")
    text_msg = st.text_input("Type your message (e.g., 'lahore ka mosam aaj' or 'kal karachi')", "")
    if st.button("Send Text"):
        if text_msg.strip() == "":
            st.warning("Type something first.")
        else:
            response = handle_input(text_msg)
            st.markdown(f"**Assistant:** {response}")
            if tts_model:
                audio_bytes = synthesize_to_audio_bytes(response, tts_model)
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/wav")

st.markdown("---")
st.caption("If voice recording directly in your browser is difficult on the host, you can record locally (phone/recorder) and paste base64 or use the file uploader below.")

# Optional file uploader fallback
uploaded_file = st.file_uploader("Or upload a WAV audio file (mono/16-bit preferred)", type=["wav", "mp3", "m4a", "ogg"])
if uploaded_file is not None:
    temp_path = save_wav_bytes(uploaded_file.read())
    st.success("File uploaded. Transcribing...")
    text = transcribe_audio_file(temp_path)
    if text:
        st.markdown(f"**You said:** {text}")
        response = handle_input(text)
        st.markdown(f"**Assistant:** {response}")
        if tts_model:
            audio_bytes = synthesize_to_audio_bytes(response, tts_model)
            if audio_bytes:
                st.audio(audio_bytes, format="audio/wav")
    else:
        st.warning("Could not transcribe uploaded file.")

# Small housekeeping: show link to repo / instructions
st.markdown("---")
st.markdown("**Developer notes:** Make sure `weather_chat.py` (with `handle_input`) is present in the same repo. "
            "If you want to hide the model download and heavy TTS from Streamlit Cloud, remove the `TTS` usage and serve text-only responses.")
