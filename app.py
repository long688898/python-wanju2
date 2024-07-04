import os
import subprocess
from flask import Flask
from multiprocessing import Process
import socket
import time

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port):
    port = start_port
    while is_port_in_use(port):
        port += 1
    return port

def start_server(port):
    app = Flask(__name__)
    @app.route('/')
    def hello_world():
        return 'Hello, World!'
    try:
        app.run(host='0.0.0.0', port=port)
    except OSError as e:
        print(f"Could not start the server on port {port}: {e}")

def download_file(url, filename, max_attempts=3):
    for attempt in range(1, max_attempts + 1):
        try:
            result = subprocess.run(['curl', '-o', filename, url], check=True, capture_output=True, text=True)
            print(f"Download {filename} successful")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Download {filename} failed (Attempt {attempt} of {max_attempts})")
            print(f"Error: {e.stderr}")
            if attempt == max_attempts:
                print(f"Download {filename} failed after {max_attempts} attempts")
    return False

def execute_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Command execution failed: {e}")
        print(f"Error output: {e.stderr}")

if __name__ == "__main__":
    initial_port = int(os.environ.get('SERVER_PORT', os.environ.get('PORT', 3001)))
    port = find_available_port(initial_port)
    
    if port != initial_port:
        print(f"Port {initial_port} is in use. Using port {port} instead.")
    
    server_process = Process(target=start_server, args=(port,))
    server_process.start()
    
    print("Using curl for downloads.")
    
    # Check if ps command exists
    ps_exists = subprocess.run(['which', 'ps'], capture_output=True).returncode == 0
    if not ps_exists:
        print("ps command does not exist. Process checking will be limited.")
    
    # Download files
    files_to_download = {
        'web.js': 'https://example.com/web.js',
        'nezha.js': 'https://example.com/nezha.js',
        'cff.js': 'https://example.com/cff.js'
    }
    
    download_success = True
    for filename, url in files_to_download.items():
        if not download_file(url, filename):
            download_success = False
    
    if not download_success:
        print("Some files failed to download after multiple attempts")
    
    # Start the downloaded scripts
    for filename in files_to_download.keys():
        if os.path.exists(filename):
            execute_command(f"node {filename} &")
