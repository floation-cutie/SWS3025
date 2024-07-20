import cv2
import time
from aip import AipOcr
import requests

APP_ID = '96287581'
API_KEY = 'jqbUntYJ1pkMadlrcWxsaM2L'
SECRET_KEY = '7CKNhDxTaZ5uuaSsGfnvDz6jNt7vwQiF'

client = AipOcr(APP_ID, API_KEY, SECRET_KEY)


def get_file_content(file_path):
    """读取图片文件"""
    with open(file_path, 'rb') as fp:
        return fp.read()


def recognize_license_plate(image_path):
    """识别车牌"""
    image = get_file_content(image_path)
    result = client.licensePlate(image)

    if 'words_result' in result:
        return result['words_result']['number']
    else:
        return None


def get_latest_plate(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                latest_response = data.get('latest_response')
                return latest_response
        return None
    except requests.RequestException as e:
        print(f"Error fetching data from URL: {e}")
        return None


def post_recognition_result(url):
    try:
        response = requests.post(url, json={"message": "CAR ARRIVED!", "status": 2})
        if response.status_code == 200:
            print("结果已发送到服务器")
        else:
            print(f"发送结果失败，状态码: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error posting data to URL: {e}")


def main():
    # 示例URL
    get_url = "http://192.168.92.51:8008/get_latest_response"
    post_url = "http://192.168.92.51:8008/send_alert"

    # 初始化已知车牌列表
    known_plates = []

    # 打开视频流（0表示默认摄像头）
    cap = cv2.VideoCapture(0)

    frame_rate = 1 / 5  # 每5秒截取一帧
    prev = time.time()  # 初始化prev变量

    get_required = True

    while True:
        if get_required:
            # 每次 get 请求之前等待 10 秒
            #time.sleep(10)

            # 获取最新车牌号
            latest_plate = get_latest_plate(get_url)
            if latest_plate and latest_plate not in known_plates:
                known_plates.append(latest_plate)
                print(f"Updated known plates: {known_plates}")
            get_required = False  # 停止后续的GET请求

        time_elapsed = time.time() - prev
        ret, frame = cap.read()
        if not ret:
            break

        if time_elapsed > frame_rate:
            prev = time.time()
            # 保存帧为JPEG图像
            image_path = 'frame.jpg'
            cv2.imwrite(image_path, frame)

            # 识别车牌
            plate_number = recognize_license_plate(image_path)
            if plate_number:
                # 输出识别到的车牌号
                print(f"识别出的车牌号: {plate_number}")
                if plate_number in known_plates:
                    print("车牌号匹配: True")
                    post_recognition_result(post_url)
                    get_required = True
                else:
                    print("车牌号不匹配: False")

        # 按q键退出循环
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
