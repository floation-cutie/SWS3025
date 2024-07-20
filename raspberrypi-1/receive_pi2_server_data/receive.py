from flask import Flask, request, jsonify
import serial
import os

import time

app = Flask(__name__)
weather_data = {}
distance_data = {}

@app.route('/receive_data', methods=['POST'])
def receive_data():
    global weather_data
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400

    weather_data['current_weather'] = data.get('current_weather', 'unknown')
    weather_data['predicted_weather'] = data.get('predicted_weather', 'unknown')
    print("Received data:", weather_data)
    return jsonify({"message": "Data received successfully"}), 200

@app.route('/receive_distance_data', methods=['POST'])
def receive_distance_data():
    global distance_data
    data = request.json
    if not data:
        return jsonify({"error": "No distance data received"}), 400

    distance_data['dist'] = data.get('dist', 'unknown')
    print("Received data:", distance_data)
    print("Communicating with micro:bit on /dev/ttyACM0...")
    ser = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=1)
    response = "D" + '\n'
    ser.write(str.encode(response))
    if ser.is_open:
        ser.close()
    print('message sent...')
    return jsonify({"message": "Distance data received successfully"}), 200


@app.route('/get_weather_data', methods=['GET'])
def get_weather_data():
    global weather_data
    return jsonify(weather_data)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
