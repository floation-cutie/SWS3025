from flask import Flask, jsonify, request, Response
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import cv2
import random
import time
import serial
import pynmea2
import time

app = Flask(__name__)
CORS(app, supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*")

latest_response = None
response_valid = False

destinationLng = None
destinationLat = None
locationData = None

@app.route('/send_destination', methods=['POST'])
def send_destination():
    global destinationLng, destinationLat
    data = request.get_json()
    # data = request.get_headers()
    # print(data)
    destinationLng = data.get('longitude', None)
    destinationLat = data.get('latitude', None)
    print(destinationLng, destinationLat)
    global locationData
    locationData = jsonify({'longitude': destinationLng, 'latitude': destinationLat})
    return jsonify({'status': 'success', 'message': 'Destination received'}), 200

@app.route('/get_destination', methods=['GET'])
def get_destination():
    global destinationLng, destinationLat
    if destinationLng is not None and destinationLat is not None:
        return jsonify({'status': 'success', 'longitude': destinationLng, 'latitude': destinationLat}), 200
    else:
        return jsonify({'status': 'error', 'message': 'No destination available'}), 404

@app.route('/arrived', methods=['POST'])
def arrived():
    global destinationLng, destinationLat
    destinationLng = None
    destinationLat = None
    return jsonify({'status': 'success', 'message': 'Arrived'}), 200

@app.route('/get_latest_response', methods=['GET'])
def get_latest_response():
    global latest_response, response_valid
    if latest_response is not None and response_valid == True:
        response_valid = False
        return jsonify({'status': 'success', 'latest_response': latest_response}), 200
    else:
        return jsonify({'status': 'error', 'message': 'No response available'}), 404
 
def gen_frames():
    # pass
    cap = cv2.VideoCapture(0)  # 使用第一个摄像头
    while True:
        success, frame = cap.read()  # 读取每一帧
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/send_alert', methods=['POST'])
def send_alert():
    data = request.get_json()
    message = data.get('message', '')
    status = data.get('status', 0)
    
    if status == 1:
        socketio.emit('alert', {'message': message, 'type': 'input'})
    elif status == 2:
        socketio.emit('alert', {'message': message, 'type': 'message'})
    else:
        return jsonify({'status': 'ignored', 'message': 'Stat is not 1'}), 200
    return jsonify({'status': 'success', 'message': 'Alert processed'}), 200

def init_gps():
    try:
        return serial.Serial("/dev/ttyAMA0", 9600, timeout=1)
    except serial.SerialException:
        print("无法打开串口或GPS设备未连接")
        return None

gps_serial = init_gps()

# 获取实时GPS数据
def get_gps_data():
    if gps_serial is not None:
        gps_serial.flushInput()
        line = gps_serial.readline().decode('utf-8', errors='ignore')
        # print('###', line)
        while (line.startswith('$GPRMC') == False):
            line = gps_serial.readline().decode('utf-8', errors='ignore')
        if line.startswith('$GPRMC'):
            print(line)
            try:
                rmc = pynmea2.parse(line)
                if rmc.status == 'A':  # 确保数据有效
                    return {'latitude': rmc.latitude, 'longitude': rmc.longitude}
            except pynmea2.ParseError:
                print("GPS解析错误")
    return None

# GPS sent from the GPS module
@app.route('/location', methods=['GET'])
def location():
    gps_data = get_gps_data()
    if gps_data is not None:
        return jsonify({'status': 'success', 'longitude': gps_data['longitude'], 'latitude': gps_data['latitude']}), 200
    else:
        return jsonify({'status': 'error', 'message': 'GPS data is not valid'}), 200

# GPS sent from the phone
# @app.route('/location', methods=['GET'])
# def location():
#     global locationData
#     global destinationLng, destinationLat
#     if locationData is not None:
#         return jsonify({'status': 'success', 'longitude': destinationLng, 'latitude': destinationLat}), 200
#     else:
#         return jsonify({'status': 'error', 'message': 'GPS data is not valid'}), 200

# Random GPS
# @app.route('/location', methods=['GET'])
# def location():
#     base_latitude = 1.306911
#     base_longitude = 103.769356
#     max_offset = 0.01
#     latitude = base_latitude + random.uniform(-max_offset, max_offset)
#     longitude = base_longitude + random.uniform(-max_offset, max_offset)
#     return jsonify({'latitude': latitude, 'longitude': longitude})

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('response_from_client')
def handle_client_response(data):
    global latest_response
    latest_response = data['response']
    global response_valid
    response_valid = True
    print("Received response from client:", latest_response)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8008, allow_unsafe_werkzeug=True)
