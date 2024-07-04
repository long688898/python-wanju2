import os
import subprocess
from flask import Flask
from multiprocessing import Process
import socket

# Function to find an available port
def find_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

# Function to start the web server
def start_server(port):
    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        return 'Hello, World!'

    app.run(host='0.0.0.0', port=port)

# Set default port to an available port or use SERVER_PORT or PORT environment variable
port = int(os.environ.get('SERVER_PORT', os.environ.get('PORT', find_free_port())))

# Define the command to be executed
cmd = "chmod +x ./start.sh && ./start.sh"

# Start the web server in a separate process
server_process = Process(target=start_server, args=(port,))
server_process.start()

# Execute the shell command with shell=True
subprocess.run(cmd, shell=True)

# Optionally, join the server process if you want the script to wait for the server to finish
server_process.join()
