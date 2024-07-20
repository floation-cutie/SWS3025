import cv2
import numpy as np
import speech_recognition as sr
from gtts import gTTS
import os
import playsound
import sounddevice as sd
from scipy.io.wavfile import write
import tempfile
import threading
import time
import traffic_light_recognition

def process_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # 增强对比度
    enhanced = cv2.equalizeHist(blurred)
    edges = cv2.Canny(enhanced, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=50, maxLineGap=50)
    detected = False
    if lines is not None:
        grouped_lines = group_lines(lines)
        if len(grouped_lines) >= 5:
            detected = True
    return detected

def group_lines(lines):
    def calculate_slope(line):
        x1, y1, x2, y2 = line[0]
        if x2 - x1 == 0:
            return None
        return (y2 - y1) / (x2 - x1)

    def is_parallel(slope1, slope2, threshold=0.1):
        if slope1 is None or slope2 is None:
            return False
        return abs(slope1 - slope2) < threshold

    def is_spacing_consistent(grouped_lines, new_line, threshold=20):
        if not grouped_lines:
            return True
        x1, y1, x2, y2 = new_line
        for line in grouped_lines:
            x1_group, y1_group, x2_group, y2_group = line
            if abs(y1 - y1_group) > threshold or abs(y2 - y2_group) > threshold:
                return False
        return True

    slopes = [calculate_slope(line) for line in lines]
    grouped_lines = []
    for i in range(len(lines)):
        line = lines[i][0]
        slope = slopes[i]
        if slope is None:
            continue
        if not grouped_lines:
            grouped_lines.append(line)
        else:
            if is_parallel(calculate_slope([grouped_lines[-1]]), slope) and is_spacing_consistent(grouped_lines, line):
                grouped_lines.append(line)
    return grouped_lines

def recognize_speech_from_mic(device=2, channels=1):
    recognizer = sr.Recognizer()
    fs = 8000  # 设置为蓝牙耳机的采样率
    seconds = 5  # 录音时间
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

def speak_text(text):
    try:
        tts = gTTS(text=text, lang='en')
        filename = "response.mp3"
        tts.save(filename)
        playsound.playsound(filename)
        os.remove(filename)
    except Exception as e:
        print(f"Error in speaking text: {e}")

def monitor_voice_commands(recognition_thread):
    while True:
        user_input = recognize_speech_from_mic()
        if user_input:
            if "turn off" in user_input.lower() and (recognition_thread is not None and recognition_thread.is_alive()):
                traffic_light_recognition.stop_recognition()
                recognition_thread.join()
                speak_text("Traffic light recognition system stopped.")
                time.sleep(5)
                return "stop"
            elif "quit" in user_input.lower() or "exit" in user_input.lower():
                speak_text("Shutting down the system.")
                if recognition_thread is not None and recognition_thread.is_alive():
                    traffic_light_recognition.stop_recognition()
                    recognition_thread.join()
                return "quit"

def main():
    while True:
        # 尝试打开多个摄像头设备
        camera_indices = [0,1]
        cap = None
        for index in camera_indices:
            cap = cv2.VideoCapture(index)
            if cap.isOpened():
                print(f"Successfully opened camera with index {index}")
                break
        if cap is None or not cap.isOpened():
            print("Cannot open any camera")
            exit()

        recognition_thread = None

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Cannot receive frame (stream end?). Exiting ...")
                break

            detected = process_frame(frame)

            if detected:
                print("检测到斑马线")
                speak_text("Zebra crossing detected. Do you need to cross the road?")
                cap.release()  # 释放摄像头

                while True:
                    user_input = recognize_speech_from_mic()

                    if "yes" in user_input.lower():
                        if recognition_thread is None or not recognition_thread.is_alive():
                            recognition_thread = threading.Thread(target=traffic_light_recognition.start_recognition)
                            recognition_thread.start()
                            speak_text("Traffic light recognition system started.")
                            voice_command_thread = threading.Thread(target=monitor_voice_commands, args=(recognition_thread,))
                            voice_command_thread.start()
                            while voice_command_thread.is_alive():
                                time.sleep(1)  # 等待语音命令线程结束
                            result = voice_command_thread.join()
                            if result == "quit":
                                break
                            elif result == "stop":
                                continue  # 返回斑马线检测
                        else:
                            speak_text("Traffic light recognition system is already running.")
                        break
                    elif "no" in user_input.lower() or "not" in user_input.lower():
                        speak_text("Okay, no need to cross the road.")
                        time.sleep(5)  # 等待5秒后继续斑马线检测
                        break
                    else:
                        speak_text("Sorry, I did not understand that. Please say yes or no.")

            if cv2.waitKey(1) == ord('q'):
                break

        if cap is not None:
            cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
