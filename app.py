import os
import subprocess
from flask import Flask
from multiprocessing import Process
import socket

def check_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def start_server(port):
    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        return 'Hello, World!'

    app.run(host='0.0.0.0', port=port)

# 设置默认端口
default_port = 3000
port = int(os.environ.get('SERVER_PORT', os.environ.get('PORT', default_port)))

# 检查端口是否被占用
if check_port_in_use(port):
    print(f"Port {port} is in use. Trying a different port.")
    port = default_port + 1  # 使用备用端口

# 定义要执行的命令
cmd = "chmod +x ./start.sh && ./start.sh"

# 启动 Web 服务器进程
server_process = Process(target=start_server, args=(port,))
server_process.start()

# 执行 shell 命令
subprocess.run(cmd, shell=True)

# 等待服务器进程结束（可选）
server_process.join()
