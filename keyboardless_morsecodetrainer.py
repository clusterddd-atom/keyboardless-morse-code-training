import cv2
import mediapipe as mp
import pyttsx3
import random
import time
import threading


mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Could not open webcam.")

engine = pyttsx3.init()


MORSE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
    'Z': '--..'
}


with open("words.txt") as f:  
    DICTIONARY = [line.strip().upper() for line in f if line.strip().isalpha()]


level = "words"  
current_target = None
current_morse = ""
sequence = ""
current_gesture = None
gesture_start_time = None
cooldown_active = False
HOLD_TIME = 1.0
COOLDOWN_TIME = 0.6

import pyttsx3
import threading

import pyttsx3
import threading

def speak(text):
    def _speak():
        try:
            # Always create a fresh engine instance
            engine = pyttsx3.init()
            engine.setProperty('rate', 175)  # Optional: adjust speed
            engine.setProperty('volume', 1.0)  # Optional: max volume
            engine.say(text)
            engine.runAndWait()
            del engine  # Clean up engine after use
        except Exception as e:
            print(f"[Speech Error] {e}")
    threading.Thread(target=_speak, daemon=True).start()

def text_to_morse(text):
    return " ".join(MORSE_DICT.get(ch.upper(), "") for ch in text if ch != " ")

def reset_target():
    global current_target, current_morse, sequence
    sequence = ""
    if level == "letters":
        current_target = random.choice(list(MORSE_DICT.keys()))
    else:  
        current_target = random.choice(DICTIONARY)
    current_morse = MORSE_DICT.get(current_target, "") if level=="letters" else text_to_morse(current_target)
    speak(f"New target: {current_target}")

def handle_gesture(gesture):
    global sequence, cooldown_active
    if not cooldown_active:
        sequence += gesture
        speak(gesture)
        cooldown_active = True
        threading.Timer(COOLDOWN_TIME, release_cooldown).start()

def release_cooldown():
    global cooldown_active
    cooldown_active = False

reset_target()
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            wrist = hand_landmarks.landmark[0]
            index_tip = hand_landmarks.landmark[8]

            dist = ((index_tip.x - wrist.x)**2 + (index_tip.y - wrist.y)**2)**0.5
            gesture = '.' if dist > 0.25 else '-'

            if gesture != current_gesture:
                current_gesture = gesture
                gesture_start_time = time.time()
            else:
                if gesture_start_time and (time.time() - gesture_start_time) > HOLD_TIME:
                    handle_gesture(gesture)
                    gesture_start_time = None


        cv2.putText(frame, f"Level: {level}", (20,30), cv2.FONT_HERSHEY_SIMPLEX,1.0,(0,200,200),2)
        cv2.putText(frame, f"Target: {current_target}", (20,70), cv2.FONT_HERSHEY_SIMPLEX,0.9,(50,200,50),2)
        cv2.putText(frame, f"Your Input: {sequence}", (20,110), cv2.FONT_HERSHEY_SIMPLEX,0.9,(50,50,255),2)

        cv2.imshow("Morse Code Learning", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("1"):
            level = "letters"
            reset_target()
        elif key == ord("2"):
            level = "words"
            reset_target()
        elif key == 13:  
            if sequence.strip() == current_morse.strip():
                speak("Correct!")
            else:
                speak(f"Incorrect. Morse was {current_morse}")
            reset_target()

except KeyboardInterrupt:
    pass
finally:
    cap.release()
    cv2.destroyAllWindows()
