from flask import Flask, Response
from picamera2 import Picamera2
from threading import Lock
import time

app = Flask(__name__)
camera = None
camera_lock = Lock()

def get_camera():
    global camera
    if camera is None:
        camera = Picamera2()
        camera.start()
    return camera

def gen_frames():
    with camera_lock:
        cam = get_camera()
        for _ in range(30):  # Generate frames for some time or until a stop condition
            frame = cam.capture_array('main')  # Adjust as per your configuration
            ret, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(0.1)  # Adjust frame rate as needed

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8088, threaded=True)
