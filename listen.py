"""
listen.py — Converts microphone speech into text for Omu.
"""
import speech_recognition as sr

recognizer = sr.Recognizer()

def listen_for_speech(timeout=5, phrase_time_limit=15):
    """
    Listens on the default microphone and returns recognized text.
    Returns None if nothing was understood or on timeout.
    """
    with sr.Microphone() as source:
        print("Listening... (speak now)")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            print("No speech detected.")
            return None

    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand that.")
        return None
    except sr.RequestError as e:
        print(f"Speech recognition service error: {e}")
        return None