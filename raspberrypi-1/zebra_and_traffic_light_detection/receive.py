import serial
import time
import os
try:
    print("Listening on /dev/ttyACM0... Press CTRL+C to exit")
    ser = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=1)

    while True:
        msg = ser.readline()
        smsg = msg.decode('utf-8').strip()

        if len(smsg) > 0:
            print('RX:{}'.format(smsg))

            if smsg == "Voice assistant" or smsg == "Fall Down":
                response = "response" + '\r\n'
                ser.write(str.encode(response))
                if smsg == "Voice assistant":
                    os.system("python3 ./main.py")
                print('Response sent...')

                time.sleep(1)

except KeyboardInterrupt:
    if ser.is_open:
        ser.close()

    print("Program terminated!")

