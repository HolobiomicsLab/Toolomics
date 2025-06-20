#!/usr/bin/env python3

"""
Deployement script for MCP servers
This script finds all server.py files in subdirectories of mcp_servers and starts them as server servers.
"""

import os
import sys
import time
import json
import subprocess
import sys
import signal
from pathlib import Path
import select

# TODO use https://slurm.schedmd.com/overview.html ????

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
    processes.append({'proc': proc, 'server_path': server_path, 'port': port, 'type': 'python'})
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
            return_code = proc.poll()
            if return_code is not None:
                stdout, stderr = proc.communicate()
                if p['type'] == 'python':
                    print(f"Process {p['server_path']}:", stdout or stderr)
                    if return_code != 0:
                        print(f"ERROR: Python server {p['server_path']} exited with code {return_code}")
                elif p['type'] == 'docker':
                    if return_code != 0:
                        error_msg = stderr or stdout or f"Exit code: {return_code}"
                        raise RuntimeError(f"Docker compose process for {p['compose_file']} failed: {error_msg}")
                    else:
                        print(f"Docker {p['compose_file']} completed successfully")
            else:
                raise RuntimeError(f"Process {p['server_path']} not responding, on hang or deadlock.")

def find_docker_compose_files(root_dir):
    """Find all docker-compose.yml files in subdirectories"""
    compose_files = []
    for root, _, files in os.walk(root_dir):
        if 'docker-compose.yml' in files:
            compose_files.append(str(Path(root) / 'docker-compose.yml'))
    return compose_files

def run_docker_compose(compose_file):
    """Run docker-compose in background"""
    cmd = ['docker-compose', '-f', compose_file, 'up', '-d']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    processes.append({'proc': proc, 'compose_file': compose_file, 'type': 'docker'})

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
        folder = os.path.join(DEFAULT_FOLDER, sys.argv[1])
    if not os.path.exists(folder):
        raise FileNotFoundError(f"Directory {folder} does not exist.")
    return folder

def main():
    root_dir = get_mcp_folder()
    config_path = "./ports_config.json"
    ports_config = get_ports_config(config_path)
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    # First run any docker-compose files
    print("Looking for docker-compose.yml files in subdirectories of:", root_dir)
    compose_files = find_docker_compose_files(root_dir)
    if compose_files:
        print(f"Found {len(compose_files)} docker-compose.yml files to start:")
        for compose_file in compose_files:
            print(f"Starting {compose_file}")
            proc = run_docker_compose(compose_file)
        print("Waiting 5 seconds for docker containers to start...")
        time.sleep(5)

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
