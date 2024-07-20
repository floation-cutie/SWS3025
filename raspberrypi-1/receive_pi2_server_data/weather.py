import requests
import time
from gtts import gTTS
import playsound
import os
import threading
import sounddevice as sd
from scipy.io.wavfile import write
import tempfile

def get_weather_data():
    try:
        response = requests.get("http://localhost:5000/get_weather_data")
        if response.status_code == 200:
            return response.json()
        else:
            return {}
    except Exception as e:
        print(f"Error getting weather data: {e}")
        return {}

def speak_text(text, device=None):
    try:
        tts = gTTS(text=text, lang='en')
        filename = "response.mp3"
        tts.save(filename)
        playsound.playsound(filename, block=True)
        os.remove(filename)
    except Exception as e:
        print(f"Error in speaking text: {e}")

def monitor_weather_changes():
    last_weather_data = get_weather_data()
    while True:
        weather_data = get_weather_data()
        if weather_data:
            current_weather = weather_data.get('current_weather', 'unknown')
            predicted_weather = weather_data.get('predicted_weather', 'unknown')
            if current_weather != predicted_weather:
                speak_text(f"The weather will change. It is currently {current_weather} but it will become {predicted_weather}. Please be prepared.")
            last_weather_data = weather_data
        time.sleep(1)  # 每10秒检查一次天气变化

def main():
    weather_thread = threading.Thread(target=monitor_weather_changes, daemon=True)
    weather_thread.start()
    while True:
        time.sleep(1)  # 主线程可以执行其他任务，这里只是保持程序运行

if __name__ == "__main__":
    main()
