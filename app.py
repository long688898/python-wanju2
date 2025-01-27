import os
import subprocess
import sys
from multiprocessing import Process
import socket
import pkg_resources

def install_requirements():
    """安装所需的依赖包"""
    try:
        # 首先更新pip
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # 安装wheel（这有助于安装预编译包）
        subprocess.check_call([sys.executable, "-m", "pip", "install", "wheel"])
        
        # 尝试使用预编译的wheel安装PyYAML
        try:
            subprocess.check_call([
                sys.executable, 
                "-m", 
                "pip", 
                "install", 
                "PyYAML==6.0.1", 
                "--only-binary", 
                ":all:"
            ])
        except subprocess.CalledProcessError:
            # 如果预编译安装失败，尝试安装开发工具并从源码构建
            if os.name != 'nt':  # 如果不是Windows系统
                subprocess.check_call(["apt-get", "update"])
                subprocess.check_call([
                    "apt-get", 
                    "install", 
                    "-y", 
                    "python3-dev",
                    "build-essential",
                    "libyaml-dev"
                ])
            subprocess.check_call([
                sys.executable, 
                "-m", 
                "pip", 
                "install", 
                "PyYAML==6.0.1"
            ])
        
        # 安装Flask
        subprocess.check_call([
            sys.executable, 
            "-m", 
            "pip", 
            "install", 
            "Flask==2.3.2"
        ])
        
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def check_dependencies():
    """检查必要的依赖是否已安装"""
    required = {'Flask', 'PyYAML'}
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed
    
    if missing:
        print(f"Missing dependencies: {missing}")
        return False
    return True

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port):
    port = start_port
    while is_port_in_use(port):
        port += 1
    return port

def start_server(port):
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
    if not check_dependencies():
        print("Installing missing dependencies...")
        install_requirements()
    
    # 设置默认端口
    initial_port = int(os.environ.get('SERVER_PORT', os.environ.get('PORT', 3001)))
    port = find_available_port(initial_port)
    
    if port != initial_port:
        print(f"Port {initial_port} is in use. Using port {port} instead.")
    
    # 启动web服务器进程
    server_process = Process(target=start_server, args=(port,))
    server_process.start()
    
    try:
        # 执行命令
        cmd = "curl --version && (chmod +x ./start.sh && ./start.sh)"
        execute_command(cmd)
        
        # 等待服务器进程
        server_process.join()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        server_process.terminate()
        server_process.join()
    except Exception as e:
        print(f"Error: {e}")
        server_process.terminate()
        server_process.join()
        sys.exit(1)
