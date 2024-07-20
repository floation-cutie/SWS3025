import smbus2
import bme280
import time
import csv
import os
import pandas as pd
from sklearn.linear_model import LinearRegression

# 函数：写入日志到CSV文件
def write_log(data, head=False):
    with open("log.csv", "a+", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if head:
            writer.writerow(["Time", "Temperature", "Pressure", "Humidity"])
        else:
            writer.writerow(data)

# 函数：加载传感器参数并采集数据
def collect_sensor_data(bus, address, calibration_params):
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
    return data

# 函数：预测下一个小时的温度、湿度和压力
def predict_next_hour_data(data):
    # 加载日志数据
    data_log = pd.read_csv('log.csv')

    # 转换时间并设置索引
    today = pd.to_datetime('today').strftime('%Y-%m-%d')
    data_log['Time'] = pd.to_datetime(today + ' ' + data_log['Time'], format='%Y-%m-%d %H:%M:%S')
    data_log.set_index('Time', inplace=True)

    # 创建滞后特征
    data_log['temp_lag1'] = data_log['Temperature'].shift(1)
    data_log['rhum_lag1'] = data_log['Humidity'].shift(1)
    data_log['pres_lag1'] = data_log['Pressure'].shift(1)

    # 删除缺失值
    data_log.dropna(inplace=True)

    # 检查数据量是否足够
    if len(data_log) < 2:
        raise ValueError("数据不足以进行预测。")

    # 特征和目标值
    features = ['temp_lag1', 'rhum_lag1', 'pres_lag1']
    target_temp = 'Temperature'
    target_rhum = 'Humidity'
    target_pres = 'Pressure'

    X = data_log[features]
    y_temp = data_log[target_temp]
    y_rhum = data_log[target_rhum]
    y_pres = data_log[target_pres]

    # 训练模型
    model_temp = LinearRegression()
    model_rhum = LinearRegression()
    model_pres = LinearRegression()

    model_temp.fit(X, y_temp)
    model_rhum.fit(X, y_rhum)
    model_pres.fit(X, y_pres)

    # 准备用于预测的最后一条数据
    last_row = data_log.iloc[-1]

    # 创建用于预测的输入数据
    new_data = pd.DataFrame({
        'temp_lag1': [last_row['temp_lag1']],
        'rhum_lag1': [last_row['rhum_lag1']],
        'pres_lag1': [last_row['pres_lag1']]
    })

    # 预测下一个数据
    temp_pred = model_temp.predict(new_data)
    rhum_pred = model_rhum.predict(new_data)
    pres_pred = model_pres.predict(new_data)

    return temp_pred[0], rhum_pred[0], pres_pred[0]

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
    num_steps = 30  # 30个预测步骤
    interval_seconds = 20  # 记录间隔为20秒
    predictions = []

    for step in range(num_steps):
        # 每20秒记录一次数据
        sensor_data = collect_sensor_data(bus, address, calibration_params)
        time.sleep(interval_seconds)

        # 每分钟预测一次
        current_minute = int(sensor_data.timestamp.strftime("%M"))
        if current_minute % 1 == 0:  # 每分钟预测一次，可以根据需要调整间隔
            temp_pred, rhum_pred, pres_pred = predict_next_hour_data(sensor_data)
            print(f'Predicted Temperature for the next hour: {temp_pred}')
            print(f'Predicted Humidity for the next hour: {rhum_pred}')
            print(f'Predicted Pressure for the next hour: {pres_pred}')
            predictions.append((temp_pred, rhum_pred, pres_pred))

    # 输出最后一个预测结果
    last_temp_pred, last_rhum_pred, last_pres_pred = predictions[-1]
    print(f'Final Predicted Temperature for the next hour: {last_temp_pred}')
    print(f'Final Predicted Humidity for the next hour: {last_rhum_pred}')
    print(f'Final Predicted Pressure for the next hour: {last_pres_pred}')
