import serial
import time
import requests
import smtplib
import psutil
import os
from email.mime.text import MIMEText
from email.header import Header

def is_script_running(script_name):
    # 检查系统上的所有进程
    for proc in psutil.process_iter(['pid', 'cmdline']):
        # 检查进程的命令行参数中是否包含 script_name
        if proc.info['cmdline'] and any(script_name in arg for arg in proc.info['cmdline']):
            return True
    return False

# 邮箱配置
smtp_server = 'smtp.qq.com'
from_addr = 'Sender_email_address'
password = 'Sender_email_password'
to_addr = 'Receiver_email_address'

# 初始化邮件发送函数
def send_email(subject, body):
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['From'] = Header(from_addr)
    msg['To'] = Header(to_addr)
    msg['Subject'] = Header(subject)
    try:
        server = smtplib.SMTP_SSL(smtp_server, 465)
        server.login(from_addr, password)
        server.sendmail(from_addr, [to_addr], msg.as_string())
        print("邮件发送成功")
    except Exception as e:
        print("邮件发送失败", e)
    finally:
        server.quit()

# 发送POST请求
def send_post(message, longitude, latitude):
    url = "http://192.168.92.51:8008/send_alert"
    data = {
        "message": message + f" at longitude: {longitude}, latitude: {latitude}",
        "status": 2
    }
    response = requests.post(url, json=data)
    print(f"POST request sent, response status code: {response.status_code}")

# 主程序
try:
    ser = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=1)
    print("Listening on /dev/ttyACM0... Press CTRL+C to exit")
    previous_count_fall_down_time = -5

    while True:
        msg = ser.readline().decode('utf-8').strip()

        if msg:
            print(f'RX: {msg}')

            if msg in ["Voice assistant", "Fall Down", "Emergency"]:
                response = "response\r\n"
                ser.write(response.encode())
                print("receive msg")
                if msg == "Voice assistant":
                    if not is_script_running("/home/pi/assistant.py"):
                        os.system("python3 /home/pi/assistant.py")
                        print('Response sent...')

                elif msg == "Fall Down" or msg == "Emergency":
                    current_time = time.time()
                    if (current_time - previous_count_fall_down_time > 5):
                        print("debug")
                        response = requests.get("http://192.168.92.51:8008/location")
                        if response.status_code == 200:
                            location = response.json()
                            lng, lat = None, None

                            if location.get('status') == 'success':
                                lng, lat = location['longitude'], location['latitude']

                            subject = f"{msg} Alert!"
                            body = f"{msg} detected! Please check the user's condition. Location is longitude: {lng}, latitude: {lat}."
                            send_email(subject, body)
                            send_post(msg, lng, lat)

                            previous_count_fall_down_time = current_time
                            print('Response sent...')
                        else: 
                            print(f"Failed to fetch location data, status code: {response.status_code}")

        time.sleep(1)

except KeyboardInterrupt:
    if ser.is_open:
        ser.close()
    print("Program terminated!")
