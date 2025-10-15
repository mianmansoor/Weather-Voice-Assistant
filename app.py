# app.py
import streamlit as st
import base64
import tempfile
from pathlib import Path
from weather_chat import handle_input
from gtts import gTTS
from pydub import AudioSegment
import os

st.set_page_config(page_title="Weather Voice Assistant (Web Speech Demo)", layout="centered")
st.title("🌦️ Weather Voice Assistant — Voice (browser) + Text Demo")

st.markdown(
    """
    **How to use (voice):**
    1. Click **Start recording** and speak (Chrome/Edge recommended).
    2. Click **Stop recording** — the browser will attempt to transcribe using the Web Speech API.
    3. The transcript appears in the box. Edit if needed, then click **Submit transcript**.
    4. The assistant will reply and a TTS audio will be generated (gTTS).
    
    If the browser cannot transcribe, download the recorded audio (button appears) and upload it using the **Upload audio** control below.
    """
)

# --- Embedded JS recorder + Web Speech API ---
# This creates a small UI that records audio, transcribes (browser), and shows:
# - a visible transcript textarea (auto-filled)
# - a base64 blob field the user can copy/paste if needed
RECORDER_HTML = r"""
<style>
.record-btn { padding:10px 16px; margin-right:8px; font-size:14px; }
#status { margin-top:8px; font-weight:600; }
.container { display:flex; gap:12px; }
textarea { width:100%; height:90px; }
.hidden { display:none; }
</style>

<div>
  <div class="container">
    <div>
      <button id="startBtn" class="record-btn">Start recording</button>
      <button id="stopBtn" class="record-btn" disabled>Stop recording</button>
      <button id="downloadBtn" class="record-btn" disabled>Download audio</button>
    </div>
    <div>
      <p id="status">Idle</p>
    </div>
  </div>

  <p><strong>Transcript (editable):</strong></p>
  <textarea id="transcript" placeholder="Transcript will appear here..."></textarea>

  <p><strong>Base64 audio (optional, long):</strong></p>
  <textarea id="base64audio" placeholder="Base64 audio will appear here if recording finished (you can ignore)"></textarea>
</div>

<script>
let mediaRecorder;
let audioChunks = [];
let audioBlobUrl = null;

// Web Speech API setup (client-side)
let recognition;
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition || null;
if (SpeechRecognition) {
  recognition = new SpeechRecognition();
  recognition.lang = 'en-US'; // you can change this; Urdu/English mixed might be less accurate
  recognition.interimResults = true;
  recognition.continuous = true;
} else {
  recognition = null;
}

const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const downloadBtn = document.getElementById('downloadBtn');
const statusEl = document.getElementById('status');
const transcriptEl = document.getElementById('transcript');
const base64El = document.getElementById('base64audio');

startBtn.onclick = async () => {
  // start audio recording
  if (!navigator.mediaDevices) {
    alert("Your browser doesn't support audio recording.");
    return;
  }
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  audioChunks = [];
  mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
  mediaRecorder.onstop = async () => {
    const blob = new Blob(audioChunks, {type:'audio/wav'});
    // create a downloadable link
    if (audioBlobUrl) URL.revokeObjectURL(audioBlobUrl);
    audioBlobUrl = URL.createObjectURL(blob);
    downloadBtn.disabled = false;
    downloadBtn.onclick = () => {
      const a = document.createElement('a');
      a.href = audioBlobUrl;
      a.download = 'recording.wav';
      a.click();
    };

    // convert blob -> base64 and put in textarea
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64data = reader.result.split(',')[1];
      base64El.value = base64data;
    };
    reader.readAsDataURL(blob);
  };
  mediaRecorder.start();
  statusEl.innerText = "Recording...";
  startBtn.disabled = true;
  stopBtn.disabled = false;

  // start speech recognition if available
  if (recognition) {
    transcriptEl.value = ""; // clear
    recognition.start();
    recognition.onresult = (event) => {
      let interim = "";
      let final = transcriptEl.value || "";
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          final += event.results[i][0].transcript;
        } else {
          interim += event.results[i][0].transcript;
        }
      }
      transcriptEl.value = final + interim;
    };
    recognition.onend = () => {
      // do nothing — stop will call stop()
    };
    recognition.onerror = (e) => {
      console.log("Speech recognition error:", e);
    };
  } else {
    // if no speech API, inform user they can download and upload file
    transcriptEl.placeholder = "Browser does not support Web Speech API. Use Download and upload file as fallback.";
  }
};

stopBtn.onclick = () => {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
  }
  statusEl.innerText = "Stopped recording. If transcription finished it will remain above.";
  startBtn.disabled = false;
  stopBtn.disabled = true;
  if (recognition) {
    try { recognition.stop(); } catch(e) { console.log(e); }
  }
};
</script>
"""

import streamlit.components.v1 as components
components.html(RECORDER_HTML, height=480)

st.markdown("---")

# The transcript textarea created by the component is not directly accessible to Streamlit,
# so provide a visible input area where user can paste or confirm the transcript.
st.markdown("**Paste the transcript here (or edit it):**")
transcript_input = st.text_area("Transcript (paste from the box above if needed)", value="", height=120)

# If user already has base64 audio (copied from the component), allow them to paste it
st.markdown("**(Optional)** If you want to upload the recorded audio to the server, paste base64 audio here (or use Upload below).")
base64_input = st.text_area("Base64 audio (optional)", value="", height=80)

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Submit transcript"):
        user_text = transcript_input.strip()
        if not user_text:
            st.warning("Transcript empty. Please paste or type your message.")
        else:
            st.info(f"Processing: {user_text}")
            response = handle_input(user_text)
            st.markdown(f"**Assistant:** {response}")

            # TTS with gTTS
            try:
                tts = gTTS(text=response, lang="en")
                tmp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                tts.save(tmp_mp3.name)
                # convert mp3 to wav for st.audio (both work, but WAV is more compatible)
                audio = AudioSegment.from_file(tmp_mp3.name, format="mp3")
                wav_path = tmp_mp3.name.replace(".mp3", ".wav")
                audio.export(wav_path, format="wav")
                st.audio(wav_path)
                # cleanup mp3 (leave wav until process done)
                try:
                    os.unlink(tmp_mp3.name)
                except Exception:
                    pass
            except Exception as e:
                st.error(f"TTS failed: {e}")

with col2:
    user_text2 = st.text_input("Or type your message here and press Send:")
    if st.button("Send typed"):
        if not user_text2.strip():
            st.warning("Type something first.")
        else:
            response = handle_input(user_text2.strip())
            st.markdown(f"**Assistant:** {response}")
            try:
                tts = gTTS(text=response, lang="en")
                tmp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                tts.save(tmp_mp3.name)
                audio = AudioSegment.from_file(tmp_mp3.name, format="mp3")
                wav_path = tmp_mp3.name.replace(".mp3", ".wav")
                audio.export(wav_path, format="wav")
                st.audio(wav_path)
                try:
                    os.unlink(tmp_mp3.name)
                except Exception:
                    pass
            except Exception as e:
                st.error(f"TTS failed: {e}")

st.markdown("---")
st.markdown("### Fallback: Upload audio file (WAV/MP3)")
uploaded = st.file_uploader("Upload a recorded audio file (if you downloaded it earlier)", type=["wav", "mp3", "m4a", "ogg"])
if uploaded is not None:
    # save to a temp file and, if desired, the server-side speech-to-text could run here (if you add a service)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded.name).suffix)
    tmp.write(uploaded.read())
    tmp.flush()
    st.success(f"File uploaded: {uploaded.name}")

    st.markdown("You can play it back here:")
    st.audio(tmp.name)

    # If base64_input empty, populate it automatically for convenience
    if not base64_input:
        with open(tmp.name, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
            st.code("Base64 (first 200 chars): " + b64[:200] + "...")
            # give user the full base64 in a textarea if they want to copy
            st.text_area("Full base64 (copy if you want to paste into the Base64 box above)", value=b64, height=120)

st.markdown("---")
st.caption("Notes: Browser transcription uses the Web Speech API (Chrome/Edge recommended). If automatic transcription doesn't work, download the recording and upload it here or paste the transcript above.")