#!/usr/bin/env python3

"""
Deployement script for MCP servers
This script finds all server.py files in subdirectories of mcp_servers and starts them as server servers.
"""

import os
import sys
import json
import subprocess
import sys
import signal
from pathlib import Path
import select

DEFAULT_FOLDER = "mcp_servers"
STARTING_PORT = 5000

# Global list to keep track of running processes and their info
processes = []

def start_server_server(server_path, port):
    """Start an server server on specified port"""
    if not os.path.exists(server_path):
        raise FileNotFoundError(f"Server file not found: {server_path}")
    cmd = [sys.executable, str(server_path), str(port)]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    processes.append({'proc': proc, 'server_path': server_path, 'port': port})
    return proc

def cleanup(_signum, _frame):
    """Cleanup all running processes on exit"""
    for p in processes:
        p['proc'].terminate()
    sys.exit(0)

def monitor_processes():
    """Monitor all running processes using non-blocking I/O"""
    import time
    
    while processes:
        time.sleep(0.1)
        for p in processes[:]:
            proc = p['proc']
            if proc.poll() is not None:
                stdout, stderr = proc.communicate()
                if stdout:
                    print(f"[{p['server_path']}:{p['port']}] {stdout}")
                if stderr:
                    print(f"[{p['server_path']}:{p['port']}] ERROR: {stderr}")
                print(f"Process {p['server_path']} on port {p['port']} exited with code {proc.returncode}")
                processes.remove(p)

def find_server_files(root_dir):
    """Find all server.py files in subdirectories"""
    server_files = []
    for root, _, files in os.walk(root_dir):
        if 'server.py' in files:
            server_files.append(str(Path(root) / 'server.py'))
    return server_files

def create_server_config_file(file_path, config=[]):
    """Create or update configuration file"""
    with open(file_path, 'w') as f:
        print(f"Creating configuration file at {file_path}")
        json.dump(config, f, indent=4)

def get_ports_config(file_path):
    """Read ports configuration from json file"""
    import json
    if not os.path.exists(file_path):
        print(f"Configuration file {file_path} does not exist. Returning empty config.")
        return []
    with open(file_path, 'r') as f:
        return json.load(f)

def find_largest_port(ports_config):
    """Find the largest port number in the configuration"""
    if not ports_config:
        return STARTING_PORT
    
    ports = []
    for config_dict in ports_config:
        port = list(config_dict.values())[0]
        ports.append(int(port))
    return max(ports) if ports else STARTING_PORT

def port_attribution(config, server_files):
    """Find and assign ports to server files"""
    if config == []:
        print(f"No ports configuration found, using default ports starting from {STARTING_PORT} ")
        return [{file_path: STARTING_PORT + i} for i, file_path in enumerate(server_files)]
    elif len(config) < len(server_files):
        start_port = find_largest_port(config)+1
        config_files = [list(d.keys())[0] for d in config]
        new_files = [f for f in server_files if f not in config_files]
        print(f"Not enough ports configured, starting from port {start_port}")
        new_files_config = [{server: start_port + i} for i, server in enumerate(new_files)]
        config.extend(new_files_config)
    return config

def get_mcp_folder():
    folder = DEFAULT_FOLDER 
    if len(sys.argv) > 1:
        folder = sys.argv[1]
    if not os.path.exists(folder):
        raise FileNotFoundError(f"Directory {folder} does not exist.")
    return folder

def main():
    root_dir = get_mcp_folder()
    config_path = "./ports_config.json"
    ports_config = get_ports_config(config_path)
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    print("Looking for server.py files in subdirectories of:", root_dir)
    server_files = find_server_files(root_dir)

    if not server_files:
        print("No server.py files found in subdirectories")
        return

    print(f"Found {len(server_files)} server.py files to start:")
    ports_config = port_attribution(ports_config, server_files)
    create_server_config_file(config_path, ports_config)
    print("Using ports configuration:", ports_config)
    for server in ports_config:
        server_file = list(server.keys())[0]
        port = server[server_file]
        print(f"Starting {server_file} on port {port}")
        start_server_server(server_file, port)

    print("\nAll servers running. Press Ctrl+C to stop.\n")
    monitor_processes()

if __name__ == "__main__":
    main()
