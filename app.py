import os
import subprocess
import sys
from multiprocessing import Process
import socket

def check_and_install_dependencies():
    try:
        import flask
    except ImportError:
        print("Flask not installed. Installing Flask...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Flask==2.3.2"])

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port):
    port = start_port
    while is_port_in_use(port):
        port += 1
    return port

def start_server(port):
    from flask import Flask  # Import Flask here after ensuring it's installed
    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        return 'Hello, World!'

    try:
        app.run(host='0.0.0.0', port=port)
    except OSError as e:
        print(f"Could not start the server on port {port}: {e}")

def execute_command(cmd):
    try:
        # 添加环境变量检查
        if os.name == 'nt':  # Windows
            shell = True
        else:  # Unix-like
            shell = False
            cmd = cmd.split()

        result = subprocess.run(
            cmd,
            shell=shell,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Command execution failed: {e}")
        print(f"Error output: {e.stderr}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # 检查并安装依赖
    check_and_install_dependencies()

    # 设置默认端口
    initial_port = int(os.environ.get('SERVER_PORT', os.environ.get('PORT', 3001)))
    port = find_available_port(initial_port)
    
    if port != initial_port:
        print(f"Port {initial_port} is in use. Using port {port} instead.")
    
    # 启动web服务器进程
    server_process = Process(target=start_server, args=(port,))
    server_process.start()
    
    # 定义并执行命令
    cmd = "curl --version && (chmod +x ./start.sh && ./start.sh)"
    execute_command(cmd)
    
    try:
        # 等待服务器进程结束
        server_process.join()
    except KeyboardInterrupt:
        print("\nShutting down the server...")
        server_process.terminate()
        server_process.join()
