===============================
Weather Voice Assistant Setup
===============================

This voice assistant fetches live weather updates and responds with spoken Urdu replies. It uses speech recognition and gTTS (Google Text-to-Speech).

----------------------------------------------------
🛠️ Prerequisites
----------------------------------------------------

1. Python 3.8 or higher installed on your system
2. Internet connection (for API & speech recognition)

----------------------------------------------------
📁 Project Structure
----------------------------------------------------

weather_voice_bot.py       <-- Main file to run the assistant  
weather_chat.py            <-- Contains logic to handle weather queries  
readme.txt                 <-- You're reading it!  
requirements.txt           <-- Dependencies to install  
.gitignore                 <-- Ignore unnecessary files in GitHub repo  
__pycache__/               <-- Will be auto-created by Python

----------------------------------------------------
📦 Step 1: Install Required Python Packages
----------------------------------------------------

Open Command Prompt or Terminal and run:

    pip install -r requirements.txt

If you don’t have `requirements.txt`, create one using:

    pip freeze > requirements.txt

Required packages:
    - speechrecognition
    - pyttsx3
    - gtts
    - playsound
    - pyaudio
    - requests
    - re

To install manually:

    pip install SpeechRecognition pyttsx3 gTTS playsound pyaudio requests

⚠️ If PyAudio gives error, download `.whl` file from:
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

Then run:

    pip install path\to\PyAudio‑0.2.11‑cp39‑cp39‑win_amd64.whl

----------------------------------------------------
🧠 Step 2: Add Your OpenWeatherMap API Key
----------------------------------------------------

Open `weather_chat.py` and replace:

    API_KEY = "your_api_key_here"

with your actual API key.  
Get it for free from: https://openweathermap.org/api

----------------------------------------------------
💻 Step 3: Run the Program
----------------------------------------------------

Use this command to start the bot:

    python weather_voice_bot.py

You’ll hear:
    "Assalamualaikum! Weather Voice Assistant aapki madad ke liye haazir hai..."

Then speak your query, like:
    - "Lahore ka weather"
    - "Kal Karachi ka temperature"
    - "Exit" (to stop the assistant)

----------------------------------------------------
🎙️ Speech Notes
----------------------------------------------------

- Bot listens to **English input** like: "Lahore weather"
- Bot **replies in Urdu**, spoken aloud with gTTS
- Make sure your **microphone is enabled** and working

----------------------------------------------------
🧼 Output Voice Cleanliness
----------------------------------------------------

- Emojis and symbols are removed before speaking
- “°C” is replaced with “degrees Celsius” for clarity

----------------------------------------------------
📌 GitHub Upload Tips (Optional)
----------------------------------------------------

- Repository name: `weather-voice-assistant`
- One-line description:
  A real-time voice-enabled weather assistant that responds in natural Urdu speech using speech recognition and gTTS.

- Use `.gitignore` to avoid uploading:
    __pycache__/
    *.pyc
    *.mp3
    *.env

----------------------------------------------------
📞 Troubleshooting
----------------------------------------------------

- Microphone not detected?
  Make sure no other app is using it.
  
- Internet issue?
  Check your connection — bot uses Google and OpenWeather APIs.

- Getting `playsound` errors?
  Try using an alternative like `pygame` or `simpleaudio` (optional)

----------------------------------------------------
👨‍💻 Developed by: Mian Mansoor
----------------------------------------------------

A fun voice project using Python and AI tools, made with ❤️

