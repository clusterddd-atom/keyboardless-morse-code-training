import pyttsx3

MORSE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..'
}

engine = pyttsx3.init()

def speak(text):
    """Speak text using TTS engine in a separate thread."""
    engine.say(text)
    engine.runAndWait()

def morse_to_letter(sequence):
    for letter, code in MORSE_DICT.items():
        if code == sequence:
            return letter
    return None
