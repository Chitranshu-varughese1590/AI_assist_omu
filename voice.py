"""
voice.py — gives Omu a spoken voice using pyttsx3.

100% free and offline — uses the voice engines already built into Windows
(SAPI5), no internet or API key needed.
"""

import pyttsx3

# Initialize once and reuse — creating a new engine every call can cause issues
_engine = pyttsx3.init()

# Optional: tweak these to taste
_engine.setProperty("rate", 175)   # words per minute (default ~200, slower = clearer)
_engine.setProperty("volume", 1.0)  # 0.0 to 1.0


def speak(text):
    """Speak the given text out loud."""
    _engine.say(text)
    _engine.runAndWait()


def list_voices():
    """Print available system voices — useful for picking a different one."""
    voices = _engine.getProperty("voices")
    for i, v in enumerate(voices):
        print(f"{i}: {v.name} ({v.languages})")


def set_voice(index):
    """Switch to a different installed voice by index (see list_voices())."""
    voices = _engine.getProperty("voices")
    _engine.setProperty("voice", voices[index].id)
