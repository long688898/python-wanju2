import os
import subprocess
from flask import Flask
from multiprocessing import Process
import socket

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

def execute_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Command execution failed: {e}")
        print(f"Error output: {e.stderr}")

if __name__ == "__main__":
    # Set default port to 8080 or use SERVER_PORT or PORT environment variable
    initial_port = int(os.environ.get('SERVER_PORT', os.environ.get('PORT', 3001)))
    port = find_available_port(initial_port)
    
    if port != initial_port:
        print(f"Port {initial_port} is in use. Using port {port} instead.")
    
    # Start the web server in a separate process
    server_process = Process(target=start_server, args=(port,))
    server_process.start()
    
    # Define and execute the command
    cmd = "curl --version && (chmod +x ./start.sh && ./start.sh)"
    execute_command(cmd)
    
    # Wait for the server process to finish
    server_process.join()
