import speech_recognition as sr
from geopy import Nominatim
from gtts import gTTS
import os
import playsound
import sounddevice as sd
from scipy.io.wavfile import write
import tempfile
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from datetime import datetime
import pytz
import subprocess
import geopy
# 获取当前天气
def get_weather(city="Singapore"):
    api_key = 'your_openweathermap_api_key'
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    weather_data = response.json()
    return weather_data['weather'][0]['description'], weather_data['main']['temp']
# 获取新加坡当前时间
def get_current_time():
    tz = pytz.timezone('Asia/Singapore')
    singapore_time = datetime.now(tz)
    return singapore_time.strftime('%H:%M')
# 发送邮件
def recognize_speech_from_mic(device=3, channels=2):
    recognizer = sr.Recognizer()
    fs = 30000
    seconds = 5
    print("Recording...")
    audio_data = sd.rec(int(seconds * fs), samplerate=fs, channels=channels, dtype='int16', device=device)
    sd.wait()  # 等待录音结束
    print("Recording done.")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
        write(temp_audio_file.name, fs, audio_data)  # 保存为WAV文件
        temp_audio_file_name = temp_audio_file.name
    with sr.AudioFile(temp_audio_file_name) as source:
        audio = recognizer.record(source)
        try:
            print("Recognizing...")
            text = recognizer.recognize_google(audio)
            print(f"User said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return ""
        finally:
            os.remove(temp_audio_file_name)  # 删除临时文件
def ask_for_more_help():
    speak_text("Do you need any other help? If not, you can say exit.")
    print("Listening for more help or exit command...")
    return recognize_speech_from_mic()
def speak_text(text):
    try:
        tts = gTTS(text=text, lang='en')
        filename = "response.mp3"
        tts.save(filename)
        playsound.playsound(filename)
        os.remove(filename)
    except Exception as e:
        print(f"Error in speaking text: {e}")
def car():
    speak_text("Where would you like to go?")
    print("Listening for destination...")
    destination = recognize_speech_from_mic()
    print(f"Destination: {destination}")

    if destination:
        # Send the destination to the server
        url = "http://192.168.92.51:8008/send_alert"  # Replace with your actual server endpoint
        data = {"message": destination , "status": 1}
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                speak_text("Your ride request has been sent successfully.")
                print("Ride request sent successfully.")
            else:
                speak_text("Failed to send your ride request. Please try again.")
                print(f"Failed to send ride request. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            speak_text("Failed to send your ride request. Please try again.")
            print(f"RequestException: {e}")


        try:
            subprocess.run(["python", "/home/pi/license/mainget.py"]) 
            exit(0) # Ensure 'python3' and '1.py' are correct for your environment
            print("mainget.py script started.")
        except Exception as e:
            print(f"Failed to start mainget.py script: {e}")
    else:
        speak_text("No destination provided.")
def get_weather(city_name, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        weather_data = response.json()
        description = weather_data['weather'][0]['description']
        temp = weather_data['main']['temp']
        return description, temp
    else:
        return "Error", f"Unable to get weather data: {response.json().get('message', 'Unknown error')}"
class Direction:
    def __init__(self, api_mapbox):
        self.api_key = api_mapbox

    def get_lat_lon(self, location):
        try:
            url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{location}.json?access_token={self.api_key}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data['features']:
                    lon, lat = data['features'][0]['geometry']['coordinates']
                    return lat, lon
                else:
                    return None, None
            else:
                print(f"Error in geocoding: {response.status_code}")
                return None, None
        except Exception as e:
            print(f"Error in geocoding: {e}")
            return None, None

    def ask_for_direction(self):
        speak_text("Where do you want directions to?")
        print("Listening for destination...")
        destination = recognize_speech_from_mic()
        print(f"Destination: {destination}")

        if destination:
            lat, lon = self.get_lat_lon(destination)
            if lat and lon:
                print(f"Converted Latitude: {lat}, Longitude: {lon}")
                try:
                    subprocess.Popen(["python", "testgps.py", str(lat), str(lon)])
                    print("gps.py script started with latitude and longitude.")
                    speak_text("Thought autopilot was launched for you")
                    exit(0)
                except Exception as e:
                    print(f"Failed to start gps.py script: {e}")
            else:
                speak_text("I couldn't find that location. Please try again.")
        else:
            speak_text("No destination provided.")
def main():
    speak_text("HI！ let me help you！")

    while True:
        text = recognize_speech_from_mic()
        while not text:
            speak_text("I didn't understand that. Please try again.")
            text = recognize_speech_from_mic()

        while text:
            if "weather" in text.lower():
                api_key = 'Your_openweathermap_api_key'
                while True:
                    speak_text("Which city's weather would you like to know? ")
                    print("Listening for city name...")
                    city_name = recognize_speech_from_mic()
                    while not city_name:
                        speak_text("I didn't catch the city name. Please try again.")
                        city_name = recognize_speech_from_mic()

                    if "exit" in city_name.lower():
                        break

                    description, temp = get_weather(city_name, api_key)
                    if description != "Error":
                        response = f"The current weather in {city_name} is {description} with a temperature of {temp} degrees Celsius."
                        print(response)
                        speak_text(response)
                        break
                    else:
                        response = f"Unable to get weather data for {city_name}. Please try again."
                        print(response)
                        speak_text(response)

            elif "car" in text.lower():
                car()
            elif "navigation" in text.lower() or "navigate" in text.lower():
                api_mapbox = 'your_mapbox_api_key'
                direction = Direction(api_mapbox)
                direction.ask_for_direction()
            elif "time" in text.lower():
                current_time = get_current_time()
                response = f"The current time in your location is {current_time}."
                print(response)
                speak_text(response)

            elif "email" in text.lower():
                to_email = "Your_email_address"
                if to_email:
                    speak_text("What is the subject of the email?")
                    print("Listening for email subject...")
                    subject = recognize_speech_from_mic()
                    while not subject:
                        speak_text("I didn't catch the subject. Please try again.")
                        subject = recognize_speech_from_mic()

                from_email = 'Sender_email_address'
                password = 'Sender_email_password'

                speak_text("What do you want to say in the email?")
                print("Listening for email body...")
                body = recognize_speech_from_mic()
                while not body:
                    speak_text("I didn't catch the email body. Please try again.")
                    body = recognize_speech_from_mic()

                if body:
                    msg = MIMEMultipart()
                    msg['From'] = from_email
                    msg['To'] = to_email
                    msg['Subject'] = subject

                    msg.attach(MIMEText(body, 'plain'))

                    try:
                        server = smtplib.SMTP('smtp.qq.com', 587)
                        server.starttls()
                        server.login(from_email, password)
                        server.sendmail(from_email, to_email, msg.as_string())
                        server.quit()
                        print("Email sent successfully!")
                        speak_text("Email sent successfully!")
                    except Exception as e:
                        print(f"Failed to send email: {e}")
                        speak_text("Failed to send email.")
                else:
                    print("No email body provided.")
                    speak_text("No email body provided.")
            elif "exit" in text.lower():
                response = "Exiting the voice assistant."
                print(response)
                speak_text(response)
                return

            else:
                response = "I didn't understand that. Please try again."
                print(response)
                speak_text(response)

            # Ask if the user needs more help
            more_help = ask_for_more_help()
            if "exit" in more_help.lower() or "stop" in more_help.lower():
                response = "Goodbye!"
                print(response)
                speak_text(response)
                return
            elif more_help:
                text = more_help
            else:
                speak_text("I didn't understand that. Please try again.")
                text = ""

if __name__ == "__main__":
    main()
