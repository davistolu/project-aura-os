import os
import sys
import tempfile
import speech_recognition as sr
from gtts import gTTS

def recognize_from_wav(wav_path):
    r = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = r.record(source)
    try:
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        return f"__GOOGLE_API_ERROR__: {e}"

def synthesize_google_tts(text, output_mp3):
    tts = gTTS(text=text, lang='en', tld='com')
    tts.save(output_mp3)
    return output_mp3

if __name__ == "__main__":
    print("Google Speech & TTS module loaded successfully.")
