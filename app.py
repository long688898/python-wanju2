import os
import subprocess
import sys
from multiprocessing import Process
import socket
import time

def upgrade_pip():
    """升级pip到最新版本"""
    try:
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip"
        ])
        print("Successfully upgraded pip")
    except subprocess.CalledProcessError as e:
        print(f"Failed to upgrade pip: {e}")

def install_build_dependencies():
    """安装构建依赖"""
    dependencies = [
        "wheel",
        "setuptools>=45.0.0",
        "cython"
    ]
    for dep in dependencies:
        try:
            subprocess.check_call([
                sys.executable,
                "-m",
                "pip",
                "install",
                "--upgrade",
                dep
            ])
            print(f"Successfully installed {dep}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {dep}: {e}")

def install_package(package_name, version=None, retries=3):
    """安装指定依赖，带重试机制"""
    package = f"{package_name}=={version}" if version else package_name
    
    for attempt in range(retries):
        try:
            print(f"Attempting to install {package} (attempt {attempt + 1}/{retries})")
            subprocess.check_call([
                sys.executable,
                "-m",
                "pip",
                "install",
                "--no-cache-dir",
                "--no-deps" if attempt == 0 else "",  # 首次尝试不安装依赖
                package
            ])
            print(f"Successfully installed {package}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {e}")
            if attempt < retries - 1:
                print("Retrying with dependencies...")
                time.sleep(1)  # 等待一秒后重试
            else:
                print(f"Failed to install {package} after {retries} attempts")
                return False

def is_package_installed(package_name):
    """检查指定包是否已安装"""
    try:
        __import__(package_name.lower())
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
    # 升级pip
    upgrade_pip()
    
    # 安装构建依赖
    install_build_dependencies()
    
    # 安装必要的包
    packages_to_install = [
        ('Flask', '2.3.2'),
        ('streamlit', None)  # None表示安装最新版本
    ]
    
    for package, version in packages_to_install:
        if not is_package_installed(package):
            print(f"Installing {package}...")
            if not install_package(package, version):
                print(f"Failed to install {package}. Exiting...")
                sys.exit(1)
        else:
            print(f"{package} is already installed")
    
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
