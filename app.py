import os
import subprocess
import sys
from multiprocessing import Process
import socket

def setup_environment():
    """设置环境并安装必要的系统依赖"""
    try:
        # 检查是否为 Debian/Ubuntu 系统
        if os.path.exists('/etc/debian_version'):
            subprocess.check_call([
                'sudo', 
                'apt-get', 
                'update'
            ])
            subprocess.check_call([
                'sudo',
                'apt-get',
                'install',
                '-y',
                'python3-dev',
                'build-essential'
            ])
    except subprocess.CalledProcessError as e:
        print(f"Warning: Unable to install system dependencies: {e}")
        # 继续执行，因为可能已经安装了必要的依赖

def install_dependencies():
    """安装 Python 依赖"""
    try:
        # 升级 pip
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip"
        ])
        
        # 安装必要的构建工具
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "setuptools",
            "wheel"
        ])
        
        # 安装项目依赖
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            "requirements.txt"
        ])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
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
            env=os.environ.copy()
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
    print("Setting up environment...")
    setup_environment()
    
    print("Installing dependencies...")
    if not install_dependencies():
        print("Failed to install dependencies")
        sys.exit(1)
    
    # 设置默认端口
    initial_port = int(os.environ.get('SERVER_PORT', os.environ.get('PORT', 3001)))
    port = find_available_port(initial_port)
    
    if port != initial_port:
        print(f"Port {initial_port} is in use. Using port {port} instead.")
    
    # 启动web服务器进程
    server_process = Process(target=start_server, args=(port,))
    server_process.daemon = True
    server_process.start()
    
    try:
        if os.path.exists('./start.sh'):
            cmd = "chmod +x ./start.sh && ./start.sh"
            execute_command(cmd)
        else:
            print("Warning: start.sh not found")
        
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
