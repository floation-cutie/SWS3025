import smbus2
import bme280
import time
import csv
import os
import pandas as pd
import requests
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# 读取训练数据
file_path = 'export.csv'
weather_data = pd.read_csv(file_path)

# 天气编号与天气文本的对应关系
weather_mapping = {
    1: 'Clear', 2: 'Fair', 3: 'Cloudy', 4: 'Overcast', 5: 'Fog',
    6: 'Freezing Fog', 7: 'Light Rain', 8: 'Rain', 9: 'Heavy Rain',
    10: 'Freezing Rain', 11: 'Heavy Freezing Rain', 12: 'Sleet',
    13: 'Heavy Sleet', 14: 'Light Snowfall', 15: 'Snowfall',
    16: 'Heavy Snowfall', 17: 'Rain Shower', 18: 'Heavy Rain Shower',
    19: 'Sleet Shower', 20: 'Heavy Sleet Shower', 21: 'Snow Shower',
    22: 'Heavy Snow Shower', 23: 'Lightning', 24: 'Hail', 25: 'Thunderstorm',
    26: 'Heavy Thunderstorm', 27: 'Storm'
}

# 选择特征和目标变量
features = ['temp', 'rhum', 'pres']
target = 'coco'

X = weather_data[features]
y = weather_data[target]

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

# 初始化随机森林分类器模型
clf = RandomForestClassifier(random_state=42)

# 训练模型
clf.fit(X_train, y_train)

def predict_weather(temp, rhum, pres):
    # 使用训练好的模型进行预测
    input_data = pd.DataFrame([[temp, rhum, pres]], columns=['temp', 'rhum', 'pres'])
    prediction_code = clf.predict(input_data)[0]
    predicted_weather = weather_mapping.get(prediction_code, 'none')
    return predicted_weather

# 写入日志到CSV文件
def write_log(data, head=False):
    with open("log.csv", "a+", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if head:
            writer.writerow(["Time", "Temperature", "Pressure", "Humidity"])
        else:
            writer.writerow(data)

# 加载传感器参数并采集数据
def collect_sensor_data(bus, address, calibration_params):
    data = bme280.sample(bus, address, calibration_params)
    time_string = data.timestamp.strftime("%H:%M:%S")
    temperature = data.temperature
    pressure = data.pressure
    humidity = data.humidity
    print("Time:", time_string)
    print("Temperature:", temperature, "C")
    print("Pressure:", pressure, "hPa")
    print("Humidity:", humidity, "% rH")
    string_data = [time_string, "{:.2f}".format(temperature), "{:.2f}".format(pressure), "{:.2f}".format(humidity)]
    write_log(string_data)
    print("-" * 20)
    return temperature, pressure, humidity

# 预测温度、湿度和压力
def predict_next_data():
    # 读取数据
    data = pd.read_csv('log.csv')

    # 将时间列转换为日期时间格式并设置为索引
    today = pd.to_datetime('today').strftime('%Y-%m-%d')
    data['Time'] = pd.to_datetime(today + ' ' + data['Time'], format='%Y-%m-%d %H:%M:%S')
    data.set_index('Time', inplace=True)

    # 创建滞后特征
    data['temp_lag1'] = data['Temperature'].shift(1)
    data['rhum_lag1'] = data['Humidity'].shift(1)
    data['pres_lag1'] = data['Pressure'].shift(1)

    # 删除包含缺失值的行
    data.dropna(inplace=True)

    if len(data) < 2:
        raise ValueError("数据集不足以进行滞后特征分析。")

    features = ['temp_lag1', 'rhum_lag1', 'pres_lag1']
    target_temp = 'Temperature'
    target_rhum = 'Humidity'
    target_pres = 'Pressure'

    X = data[features]
    y_temp = data[target_temp]
    y_rhum = data[target_rhum]
    y_pres = data[target_pres]

    # 训练模型
    model_temp = LinearRegression()
    model_rhum = LinearRegression()
    model_pres = LinearRegression()

    model_temp.fit(X, y_temp)
    model_rhum.fit(X, y_rhum)
    model_pres.fit(X, y_pres)

    # 准备用于预测的最后一条数据
    last_row = data.iloc[-1]

    # 创建用于预测的输入
    new_data = pd.DataFrame({
        'temp_lag1': [last_row['temp_lag1']],
        'rhum_lag1': [last_row['rhum_lag1']],
        'pres_lag1': [last_row['pres_lag1']]
    })

    # 多步预测，假设预测 60 个时间段
    num_steps = 600
    predictions = []

    for step in range(num_steps):
        # 预测当前步的值
        temp_pred = model_temp.predict(new_data)
        rhum_pred = model_rhum.predict(new_data)
        pres_pred = model_pres.predict(new_data)

        # 将当前步的预测结果添加到列表中
        predictions.append((temp_pred[0], rhum_pred[0], pres_pred[0]))

        # 更新新数据，用于下一步预测
        new_data = pd.DataFrame({
            'temp_lag1': [temp_pred[0]],
            'rhum_lag1': [rhum_pred[0]],
            'pres_lag1': [pres_pred[0]]
        })

    # 输出所有预测结果
    for i, (temp_pred, rhum_pred, pres_pred) in enumerate(predictions, start=1):
        continue

    return temp_pred, rhum_pred, pres_pred

# 将预测结果发送到另一台树莓派
def send_data_to_server(current_weather, predicted_weather):
    url = "http://192.168.92.106:5000/receive_data"
    data = {
        "current_weather": current_weather,
        "predicted_weather": predicted_weather
    }
    response = requests.post(url, json=data)
    print(f"Sent data to server: {response.status_code}")

# 主程序
if __name__ == "__main__":
    # 清空日志文件并写入头部
    if os.path.exists("log.csv"):
        open("log.csv", 'w').close()
    write_log("", head=True)

    # 设置传感器和总线参数
    port = 1
    address = 0x77
    bus = smbus2.SMBus(port)
    calibration_params = bme280.load_calibration_params(bus, address)

    # 循环采集数据和预测
    interval_seconds = 2  # 记录间隔为10秒
    num = 0

    while True:
        # 每10秒记录一次数据
        sensor_data = collect_sensor_data(bus, address, calibration_params)
        time.sleep(interval_seconds)
        temp_cur, pres_cur, rhum_cur = sensor_data
        current_weather = predict_weather(temp_cur, rhum_cur, pres_cur)
        num += 1

        if num == 10:  # 每分钟预测一次
            num = 0
            temp_pred, rhum_pred, pres_pred = predict_next_data()
            print(f'Predicted Temperature for the next 10 minutes: {temp_pred}')
            print(f'Predicted Humidity for the next 10 minutes: {rhum_pred}')
            print(f'Predicted Pressure for the next 10 minutes: {pres_pred}')
            predicted_weather = predict_weather(temp_pred, rhum_pred, pres_pred)

            print(f"{temp_cur}")
            print(f"{rhum_cur}")
            print(f"{pres_cur}")
            
            print(f"现在的天气是：{current_weather}")
            print(f"预测的天气是：{predicted_weather}")


            send_data_to_server(current_weather, predicted_weather)

