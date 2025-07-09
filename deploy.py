#!/usr/bin/env python3

"""
Deployement script for MCP servers
This script finds all server.py files in subdirectories of mcp_servers and starts them as server servers.
"""

import os
import argparse
import sys
import time
import json
import subprocess
import sys
import signal
from pathlib import Path
import select

# TODO use https://slurm.schedmd.com/overview.html ????

DEFAULT_FOLDER = "mcp_host"
STARTING_PORT = 5000

class process:
    """Class to represent a running process"""
    def __init__(self, proc, file=None, port=None, compose_file=None, type='python', status='running'):
        self.proc = proc
        self.file = file
        self.port = port
        self.type = type
        self.status = status

    def __repr__(self):
        return f"Process(file={self.file}, port={self.port}, type={self.type}, status={self.status})"

# Global list to keep track of running processes and their info
processes = []

def start_servers(server_path, port):
    """Start an server server on specified port"""
    if not os.path.exists(server_path):
        raise FileNotFoundError(f"Server file not found: {server_path}")
    cmd = [sys.executable, str(server_path), str(port)]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    processes.append(process(proc, file=server_path, port=port, type='python'))
    return proc

def cleanup(_signum, _frame):
    """Cleanup all running processes on exit"""
    print(f"\nCleaning up before exit (Signal: {_signum})")
    for p in processes:
        p.proc.kill()
        #p.proc.terminate()
    sys.exit(0)

def monitor_processes():
    """Monitor all running processes using non-blocking I/O"""
    import time
    
    while processes:
        time.sleep(0.1)
        for p in processes[:]:
            proc = p.proc
            
            if proc.stdout and proc.stdout.readable():
                try:
                    if hasattr(select, 'select'):
                        ready, _, _ = select.select([proc.stdout], [], [], 0)
                        if ready:
                            line = proc.stdout.readline()
                            if line:
                                print(f"[{p.file}:{p.port}] {line.strip()}")
                    else:
                        line = proc.stdout.readline()
                        if line:
                            print(f"[{p.file}:{p.port}] {line.strip()}")
                except:
                    pass
            
            return_code = proc.poll()
            if return_code is not None:
                remaining_output, _ = proc.communicate()
                if remaining_output:
                    for line in remaining_output.split('\n'):
                        if line.strip():
                            print(f"[{p.file}:{p.port}] {line.strip()}")
                
                if p.type == 'python':
                    if return_code != 0:
                        print(f"ERROR: Python server {p.file} exited with code {return_code}")
                        p.status = 'failed'
                    else:
                        print(f"Python server {p.file} completed successfully")
                        p.status = 'completed'
                elif p.type == 'docker':
                    if return_code != 0:
                        p.status = 'failed'
                        raise RuntimeError(f"Docker compose process for {p.file} failed with exit code: {return_code}")
                    elif p.status == 'running':
                        print(f"Docker {p.file} successfully run.")
                        p.status = 'completed'
                
                processes.remove(p)

def find_docker_compose_files(mcp_dir):
    """Find all docker-compose.yml files in subdirectories"""
    compose_files = []
    for root, _, files in os.walk(mcp_dir):
        if 'docker-compose.yml' in files:
            compose_files.append(str(Path(root) / 'docker-compose.yml'))
    return compose_files

def run_docker_compose(compose_file):
    """Run docker-compose in background"""
    print(f"Running docker-compose for {compose_file}")
    platform = sys.platform
    if platform == "linux":
        cmd = ['docker', 'compose','-f', compose_file, 'up', '-d']
    else: # for macOS or Windows
        cmd = ['docker-compose', '-f', compose_file, 'up', '-d']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    processes.append(process(proc, file=compose_file, type='docker'))

def find_server_files(mcp_dir):
    """Find all server.py files in subdirectories"""
    server_files = []
    for root, _, files in os.walk(mcp_dir):
        if 'server.py' in files:
            server_files.append(str(Path(root) / 'server.py'))
    return server_files

def create_server_config_file(file_path, config=[]):
    """Create or update configuration file"""
    with open(file_path, 'w') as f:
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
    if not os.path.exists(folder):
        raise FileNotFoundError(f"Directory {folder} does not exist.")
    return folder

def run_dockers(compose_files):
    if compose_files:
        print(f"Found {len(compose_files)} docker-compose.yml files to start:")
        for cmpf in compose_files:
            print(f"Starting {cmpf}")
            run_docker_compose(cmpf)
        print("Waiting 3 seconds for docker containers to start...")
        time.sleep(3)

def run_mcp_servers(server_files, config_path, config_json):
    if not server_files:
        print("No server.py files found in subdirectories")
        return
    print(f"Found {len(server_files)} MCP servers to start.")
    ports_config = port_attribution(config_json, server_files)
    create_server_config_file(config_path, ports_config)
    print("Using ports configuration at:", config_path)
    for server in ports_config:
        server_file = list(server.keys())[0]
        port = server[server_file]
        if server_file in server_files:
            print(f"Starting {server_file} on port {port}")
            if os.path.exists(server_file):
                start_servers(server_file, port)

def get_argument_config():
    """Get command line arguments"""
    parser = argparse.ArgumentParser(description="Deploy MCP servers")
    parser.add_argument("--config", help="Path to the ports configuration file", default="config.json")
    parser.add_argument("--mcp-dir", default=DEFAULT_FOLDER, help=f"Directory containing MCP servers (default: {DEFAULT_FOLDER})")
    parser.add_argument("--starting-port", type=int, default=STARTING_PORT, help=f"Starting port number (default: {STARTING_PORT})")
    parser.add_argument("--no-docker", action="store_true", help="Skip docker-compose files")
    args = parser.parse_args()
    return args

def main():
    args = get_argument_config()
    mcp_dir = args.mcp_dir
    config_path = args.config
    
    if not os.path.exists(mcp_dir):
        raise FileNotFoundError(f"Directory {mcp_dir} does not exist.")
    
    config_json = get_ports_config(config_path)
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    if not args.no_docker:
        print("Looking for docker-compose.yml files in subdirectories of:", mcp_dir)
        compose_files = find_docker_compose_files(mcp_dir)
        run_dockers(compose_files)

    print("Looking for server.py files in subdirectories of:", mcp_dir)
    server_files = find_server_files(mcp_dir)
    run_mcp_servers(server_files, config_path, config_json)

    print("\nAll servers running. Press Ctrl+C to stop.\n")
    monitor_processes()

if __name__ == "__main__":
    main()
