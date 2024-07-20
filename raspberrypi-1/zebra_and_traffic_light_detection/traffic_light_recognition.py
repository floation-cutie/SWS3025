import torch
import cv2
import yaml
from gtts import gTTS
import os
import playsound

recognition_active = False

# 加载配置文件
with open('/home/pi/zegreen/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# 加载模型
model = torch.hub.load('ultralytics/yolov5', config['model'], pretrained=True)
model.conf = 0.2  # 设置较低的置信度阈值，以提高检测灵敏度
model.iou = config['iou_thres']  # 设置 IoU 阈值
device = config['device']  # 选择设备
model.to(device)

def speak_text(text):
    try:
        tts = gTTS(text=text, lang='en')
        filename = "response.mp3"
        tts.save(filename)
        playsound.playsound(filename)
        os.remove(filename)
    except Exception as e:
        print(f"Error in speaking text: {e}")

def start_recognition():
    global recognition_active
    recognition_active = True

    # 尝试打开指定的摄像头设备路径
    camera_paths = ["/dev/video0", "/dev/video1"]
    # camera_paths = ["http://192.168.252.106:8085"]
    cap = None

    for path in camera_paths:
        cap = cv2.VideoCapture(path)
        if cap.isOpened():
            print(f"Successfully opened camera with path {path}")
            break
        else:
            cap = None

    if cap is None:
        print("Cannot open any camera")
        return

    print("摄像头已打开，开始读取视频流...")

    while recognition_active:
        ret, frame = cap.read()
        if not ret:
            print("未能读取视频帧，尝试重新读取...")
            continue

        # 推理
        results = model(frame)

        # 处理结果
        labels, cord = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]

        red_count = 0
        green_count = 0
        largest_area = 0
        closest_light_color = None

        for i in range(n):
            row = cord[i]
            if row[4] >= 0.25:  # 使用较低的置信度阈值
                x1, y1, x2, y2 = int(row[0] * x_shape), int(row[1] * y_shape), int(row[2] * x_shape), int(row[3] * y_shape)
                bgr = (0, 255, 0)

                if "light" in model.names[int(labels[i])]:
                    # 裁剪红绿灯区域
                    light = frame[y1:y2, x1:x2]
                    hsv = cv2.cvtColor(light, cv2.COLOR_BGR2HSV)

                    # 红色检测范围（包括不同亮度的红色）
                    mask_red1 = cv2.inRange(hsv, (0, 50, 50), (10, 255, 255))
                    mask_red2 = cv2.inRange(hsv, (160, 50, 50), (180, 255, 255))
                    mask_red = cv2.bitwise_or(mask_red1, mask_red2)

                    # 绿色检测范围
                    mask_green = cv2.inRange(hsv, (35, 50, 50), (85, 255, 255))

                    if cv2.countNonZero(mask_red) > cv2.countNonZero(mask_green):
                        color_label = "Red"
                        red_count += 1
                        bgr = (0, 0, 255)
                    else:
                        color_label = "Green"
                        green_count += 1
                        bgr = (0, 255, 0)

                    # 计算红绿灯区域的面积
                    area = (x2 - x1) * (y2 - y1)

                    # 更新面积最大的红绿灯
                    if area > largest_area:
                        largest_area = area
                        closest_light_color = color_label

        # 返回最近红绿灯颜色和数量，并进行语音输出
        if closest_light_color:
            print(f"最近的红绿灯颜色: {closest_light_color}")
            print(f"红灯数量: {red_count}, 绿灯数量: {green_count}")
            if closest_light_color == "Red":
                speak_text("Please wait.")
            elif closest_light_color == "Green":
                speak_text("You can cross the street.")

    # 释放资源
    cap.release()
    print("摄像头已关闭")

def stop_recognition():
    global recognition_active
    recognition_active = False

if __name__ == "__main__":
    start_recognition()
