import smbus2
import bme280
import time
import csv
import os

def write_log(data, head=False):
    with open("log.csv", "a+", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if head:
            writer.writerow(["Time", "Temperature", "Pressure", "Humidity"])
        else:
            writer.writerow(data)


if os.path.exists("log.csv"):
    open("log.csv", 'w').close()  

write_log("", head=True)  

port = 1
address = 0x77
bus = smbus2.SMBus(port)
calibration_params = bme280.load_calibration_params(bus, address)

while True:
    data = bme280.sample(bus, address, calibration_params)
    time_string = data.timestamp.strftime("%H:%M:%S")
    temperature = "{:.2f}".format(data.temperature)
    pressure = "{:.2f}".format(data.pressure)
    humidity = "{:.2f}".format(data.humidity)
    print("Time:", time_string)
    print("Temperature:", temperature, "C")
    print("Pressure:", pressure, "hPa")
    print("Humidity:", humidity, "% rH")
    string_data = [time_string, temperature, pressure, humidity]
    
    write_log(string_data)
    print("-" * 20)
    time.sleep(20)
