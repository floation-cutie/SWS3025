import time
import os
import serial


ser = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=1)
response = "distance message" + '\n'
#print("DEBUG" + response)
ser.write(str.encode(response))
ser.close()

