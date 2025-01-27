import os
import subprocess
import sys
from multiprocessing import Process
import socket

def install_flask():
    """只安装Flask依赖"""
    try:
        subprocess.check_call([
            sys.executable, 
            "-m", 
            "pip", 
            "install", 
            "--no-cache-dir",  # 不使用缓存
            "Flask==2.3.2"
        ])
    except subprocess.CalledProcessError as e:
        print(f"Error installing Flask: {e}")
        sys.exit(1)

def is_flask_installed():
    """检查Flask是否已安装"""
    try:
        import flask
        return True
    except ImportError:
        return False

def is_port_in_use(port):
    """检查端口是否在使用中"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port):
    """找到可用端口"""
    port = start_port
    while is_port_in_use(port):
        port += 1
    return port

def start_server(port):
    """启动Flask服务器"""
    try:
        from flask import Flask
        app = Flask(__name__)

        @app.route('/')
        def hello_world():
            return 'Hello, World!'

        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)

def execute_command(cmd):
    """执行shell命令"""
    try:
        # 区分操作系统
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
            text=True,
            env=os.environ.copy()  # 使用当前环境变量
        )
        if result.stdout:
            print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Command execution failed: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # 检查并安装Flask
    if not is_flask_installed():
        print("Installing Flask...")
        install_flask()
    
    # 设置默认端口
    initial_port = int(os.environ.get('SERVER_PORT', os.environ.get('PORT', 3001)))
    port = find_available_port(initial_port)
    
    if port != initial_port:
        print(f"Port {initial_port} is in use. Using port {port} instead.")
    
    # 启动web服务器进程
    server_process = Process(target=start_server, args=(port,))
    server_process.daemon = True  # 设置为守护进程
    server_process.start()
    
    try:
        # 执行命令
        if os.path.exists('./start.sh'):
            cmd = "chmod +x ./start.sh && ./start.sh"
            execute_command(cmd)
        else:
            print("Warning: start.sh not found")
        
        # 等待服务器进程
        server_process.join()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if server_process.is_alive():
            server_process.terminate()
            server_process.join(timeout=5)
            if server_process.is_alive():
                server_process.kill()
