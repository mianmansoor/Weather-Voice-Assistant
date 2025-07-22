import speech_recognition as sr
from weather_chat import handle_input
from gtts import gTTS
from playsound import playsound
import re
import os
import uuid

# Initialize recognizer
recognizer = sr.Recognizer()

def speak(text):
    print(f"Bot: {text}")

    # Replace special symbols for better speech
    text = text.replace("°C", " degrees Celsius")

    # Remove emojis/special characters (except common punctuation)
    safe_text = re.sub(r'[^\w\s.,!?]', '', text)

    try:
        tts = gTTS(text=safe_text, lang='ur')  # Use 'en' if mostly English
        filename = f"temp_{uuid.uuid4()}.mp3"
        tts.save(filename)
        playsound(filename)
        os.remove(filename)
    except Exception as e:
        print("Voice Error:", e)

def listen():
    with sr.Microphone() as source:
        print("🎙️ Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language="en-US")
        print(f"You: {text}")
        return text.lower()
    except sr.UnknownValueError:
        speak("Maaf kijiye, mein samajh nahi paaya. Dobara boliye.")
        return ""
    except sr.RequestError:
        speak("Internet ka masla hai. Please check your connection.")
        return ""

# Startup message
speak("Assalamualaikum! Weather Voice Assistant aapki madad ke liye haazir hai. Mausam ya ehtiyaat se related koi bhi sawal poochein. Band karne ke liye exit boliye.")

# Main loop
while True:
    user_input = listen()
    if not user_input:
        continue

    response = handle_input(user_input)

    if response.lower() == "exit":
        speak("Khuda Hafiz! Aapka din acha guzray.")
        break

    speak(response)
