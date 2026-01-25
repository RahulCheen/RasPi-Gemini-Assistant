import os
import io
import json
import time
import sys
import wave
import struct
import traceback
import pyaudio
import speech_recognition as sr
import google.generativeai as genai
import numpy as np
import openwakeword
from openwakeword.model import Model
import markdown
from bs4 import BeautifulSoup

import asyncio
import tempfile
from pathlib import Path
import edge_tts
from playsound3 import playsound




def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found.")
        sys.exit(1)

CONFIG = load_config()

class WakeWordListener:
    def __init__(self, model_names=[CONFIG.get("WAKE_WORD_MODEL", "hey_jarvis")]):
        print(f"Loading Wake Word Model: {model_names}...")
        try:
            self.model = Model(wakeword_models=model_names, inference_framework="onnx")
        except Exception as e:
            print(f"Error loading Wake Word model: {e}")
            sys.exit(1)
        
        self.chunk_size = 1280
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.p = pyaudio.PyAudio()
        self.stream = None

    def start_stream(self):
        if self.stream is None:
            try:
                self.stream = self.p.open(
                    format=self.format,
                    channels=self.channels,
                    rate=self.rate,
                    input=True,
                    frames_per_buffer=self.chunk_size
                )
            except OSError as e:
                print(f"Error accessing microphone: {e}")
                print("Please ensure a microphone is connected and configured.")
                sys.exit(1)

    def stop_stream(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

    def listen_for_wake_word(self):
        self.start_stream()
        print("Listening for wake word...")
        try:
            while True:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                audio = np.frombuffer(data, dtype=np.int16)
                
                audio = np.frombuffer(data, dtype=np.int16)
                
                if len(audio) == self.chunk_size:
                    prediction = self.model.predict(audio)
                    
                    # Check for activation
                    for md in self.model.prediction_buffer.keys():
                        scores = self.model.prediction_buffer[md]
                        if scores[-1] > 0.5: # Threshold
                            print(f"Wake word detected! ({md})")
                            self.stop_stream()
                            self.model.reset()
                            return True
                

        except KeyboardInterrupt:
            self.stop_stream()
            raise
        finally:
            self.stop_stream()

class SpeechTranscriber:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def listen_and_transcribe(self):
        print("Listening for command...")
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=30)
                except sr.WaitTimeoutError:
                    print("Listening timed out.")
                    return None
            
            print("Processing audio...")
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except OSError as e:
             print(f"Microphone error during STT: {e}")
        return None

class GeminiAssistant:
    def __init__(self):
        api_key = CONFIG.get("GEMINI_API_KEY")
        if not api_key or api_key == "YOUR_API_KEY_HERE":
            print("Error: Invalid Gemini API Key in config.json")
            sys.exit(1)
        
        genai.configure(api_key=api_key)
        
        self.models = [
            "gemini-2.5-flash-lite", 
            "gemini-2.5-flash", 
            "gemini-3-flash"
        ]

    def list_available_models(self):
        print("Checking available models...")
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    print(m.name)
        except Exception as e:
            print(f"Error listing models: {e}")

    def generate_response(self, text):
        for model_name in self.models:
            print(f"Querying Gemini ({model_name})...")
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(text)
                print(f"Gemini: {response.text}")
                return response.text
                
            except Exception as e:
                print(f"Error on {model_name}: {e}. switching...")
                continue
        
        # If we exhausted all models
        print("All models failed or rate limited.")
        return "I apologize, but I need to cool down. Please wait a moment before trying again."

class EdgeTTS:
    def __init__(self):
        self.voice = "en-GB-RyanNeural"
        self.rate = "+0%"
        self.volume = "+0%"

    async def _stream_audio(self, text):
        """
        Generate speech with edge-tts and play it using playsound.
        This function is async, but playback itself is blocking.
        """
        communicate = edge_tts.Communicate(
            text,
            self.voice,
            rate=self.rate,
            volume=self.volume,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_file = Path(tmpdir) / "response.mp3"

            await communicate.save(str(temp_file))

            print(f"Playing response...")
            playsound(str(temp_file), block=True)

    def speak(self, text):
        print("Synthesizing speech (EdgeTTS)...")
        
        try:
            html_text = markdown.markdown(text)
            soup = BeautifulSoup(html_text, "html.parser")
            clean_text = soup.get_text()
            clean_text = " ".join(clean_text.split())
        except Exception as e:
            print(f"Warning: Text cleaning failed ({e}), using raw text.")
            clean_text = text
        
        if not clean_text:
            return

        try:
            # Run the async function
            asyncio.run(self._stream_audio(clean_text))
        except Exception as e:
            print(f"TTS Error: {e}")
            traceback.print_exc()

def main():
    print("Initializing Jarvis...")
    
    wake_word = WakeWordListener()
    stt = SpeechTranscriber()
    agent = GeminiAssistant()
    tts = EdgeTTS()
    
    print("\n--- Jarvis Voice Assistant Ready ---")
    print("Say 'Jarvis' or 'Hey Jarvis' to start.")
    
    try:
        while True:
            if wake_word.listen_for_wake_word():
                
                text = stt.listen_and_transcribe()
                
                if text:
                    response = agent.generate_response(text)
                    
                    if response:
                        tts.speak(response)
                
                print("\nResuming wake word listening...\n")
                
    except KeyboardInterrupt:
        print("\nStopping...")
        wake_word.stop_stream()
        sys.exit(0)

if __name__ == "__main__":
    main()
