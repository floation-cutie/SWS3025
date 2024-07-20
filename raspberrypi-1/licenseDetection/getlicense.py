import socket

def receive_file(filename, host='192.168.252.45', port=12345):
    # 创建socket对象
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # 连接到服务器
        s.connect((host, port))
        print(f"Connected to {host}:{port}")

        # 接收数据并写入文件
        with open(filename, 'wb') as f:
            while True:
                data = s.recv(1024)
                if not data:
                    break
                f.write(data)
        print("File has been received successfully.")

# 调用函数，接收文件
receive_file('license.txt')

