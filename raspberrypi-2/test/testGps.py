import serial
import pynmea2
import time
 
def gps_get():
    print("开始测试：")
        
    # 创建 GPS 串口的句柄
    ser = serial.Serial("/dev/ttyAMA0", 9600)
 
    print("获取句柄成功，进入循环：")
    while True:
        # 读取一行 GPS 信息
        line = str(ser.readline())[2:-5]  # 直接在转换时去除前两位及末尾的转义字符
        # print(line)
            
        # 寻找包含地理坐标的那一行数据
        if line.startswith('$GPRMC'):
            try:
                rmc = pynmea2.parse(line)
                if rmc.status == 'V':
                    print("数据无效")
                else:
                    print("当前坐标：")
                    print("北纬(度分秒)：", float(rmc.lat)/100, "度")
                    print("东经(度分秒)：", float(rmc.lon)/100, "度")
                    print("************")
                    print("北纬(十进制)：", rmc.latitude, "度")
                    print("东经(十进制)：", rmc.longitude, "度")
            except pynmea2.ParseError as e:
                print("解析错误：", e)
        
if __name__ == "__main__":
    gps_get()

