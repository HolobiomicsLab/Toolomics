#!/usr/bin/env python3

"""
MCP Server Deployment Script
"""

import argparse
import sys
import time
import json
import subprocess 
import signal
import os
import socket
import hashlib
from pathlib import Path
import select
from dataclasses import dataclass
from typing import Dict, List, Optional
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def is_port_in_use(port: int, host: str = "0.0.0.0") -> bool:
    """
    Check if a port is currently in use.
    
    Args:
        port: The port number to check
        host: The host address (default: 0.0.0.0)
    
    Returns:
        True if port is in use, False if available
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except OSError:
            return True


def find_available_port(start_port: int, end_port: int, used_ports: set = None) -> Optional[int]:
    """
    Find the next available port in a range.
    
    Args:
        start_port: Starting port number
        end_port: Ending port number (inclusive)
        used_ports: Set of ports already assigned in config (optional)
    
    Returns:
        Available port number or None if no ports available
    """
    if used_ports is None:
        used_ports = set()
    
    for port in range(start_port, end_port + 1):
        if port not in used_ports and not is_port_in_use(port):
            return port
    
    return None

DEFAULT_FOLDER = "mcp_host"
WORKSPACE_FOLDER = "workspace"
        
# Define default port ranges, overwritten by arguments
HOST_PORT_MIN = 5000
HOST_PORT_MAX = 5099


def generate_instance_id(workspace_path: str) -> str:
    """
    Generate a unique instance ID from workspace path.
    Uses first 8 characters of MD5 hash of workspace path.
    
    Args:
        workspace_path: Path to the workspace directory
    
    Returns:
        Unique instance ID (8 characters)
    
    Example:
        "workspace_martin" -> "a3f2b1c9"
        "workspace_john" -> "f7e2d4a1"
    """
    workspace_abs = Path(workspace_path).resolve()
    hash_obj = hashlib.md5(str(workspace_abs).encode())
    instance_id = hash_obj.hexdigest()[:8]
    logger.info(f"Generated instance_id '{instance_id}' for workspace '{workspace_abs}'")
    return instance_id

@dataclass
class ProcessInfo:
    """Immutable process information"""
    proc: subprocess.Popen
    file_path: str
    port: Optional[int] = None
    process_type: str = 'python'
    status: str = 'running'
    is_critical: bool = False  # If True, failure will cause deployment to exit
    
    def __post_init__(self):
        if self.process_type not in ['python', 'docker']:
            raise ValueError(f"Invalid process type: {self.process_type}")

class ProcessManager:
    """Manages MCP server processes with proper lifecycle"""
    
    def __init__(self, workspace_dir: Path, instance_id: str = "default"):
        self.processes: List[ProcessInfo] = []
        self.shutdown_event = threading.Event()
        self.failure_event = threading.Event()  # Set when a critical process fails
        self.workspace_dir = workspace_dir
        self.failed_processes: List[ProcessInfo] = []  # Track failed processes
        self.instance_id = instance_id  # Unique instance identifier for Docker services
    
    def start_python_server(self, server_path: Path, port: int) -> ProcessInfo:
        """Start a Python MCP server in the workspace directory"""
        if not server_path.exists():
            raise FileNotFoundError(f"Server file not found: {server_path}")

        # Set up environment with server directory in PYTHONPATH
        server_dir = server_path.parent
        env = os.environ.copy()
        current_pythonpath = env.get('PYTHONPATH', '')
        if current_pythonpath:
            env['PYTHONPATH'] = f"{server_dir}:{current_pythonpath}"
        else:
            env['PYTHONPATH'] = str(server_dir)
        
        # Use absolute path for the server file since we're changing working directory
        absolute_server_path = server_path.resolve()
        
        # Use the same Python interpreter that's running this script
        py_cmd = sys.executable
        
        cmd = [py_cmd, str(absolute_server_path), str(port)]
        proc = subprocess.Popen(
            cmd,
            cwd=self.workspace_dir,  # Execute in workspace directory
            env=env,                 # Preserve import paths
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,  # Capture stderr separately
            text=True, 
            bufsize=1
        )
        
        process_info = ProcessInfo(
            proc=proc,
            file_path=str(server_path),
            port=port,
            process_type='python'
        )
        
        self.processes.append(process_info)
        logger.info(f"Started Python server: {absolute_server_path} on port {port} (workspace: {self.workspace_dir})")
        return process_info
    
    def start_docker_compose(self, compose_file: Path, port: Optional[int] = None) -> ProcessInfo:
        """Start docker-compose service with optional port configuration"""
        platform = sys.platform
        # Use instance ID as docker-compose project name for isolation
        project_name = f"toolomics_{self.instance_id}"
        if platform == "linux":
            cmd = ['docker', 'compose', '-p', project_name, '-f', str(compose_file), 'up', '-d']
        else:
            cmd = ['docker-compose', '-p', project_name, '-f', str(compose_file), 'up', '-d']
        
        logger.info(f"Using Docker project name: {project_name}")
        
        # Set up environment with port if provided
        env = os.environ.copy()
        if port is not None:
            env['MCP_PORT'] = str(port)
            env['FASTMCP_PORT'] = str(port)
            logger.info(f"Setting MCP_PORT={port} for docker-compose: {compose_file}")
        
        # Set instance-specific environment variables for Docker services
        env['INSTANCE_ID'] = self.instance_id
        logger.info(f"Setting INSTANCE_ID={self.instance_id} for docker-compose: {compose_file}")
        
        # Set auxiliary ports for services that need them
        # RStudio Server port (default 8787, offset by 1000+ instance hash to avoid conflicts)
        rstudio_port = 9000 + (int(self.instance_id, 16) % 1000)
        env['RSTUDIO_PORT'] = str(rstudio_port)
        
        # SearxNG port (default 8080, offset by 1000+ instance hash to avoid conflicts)
        searxng_port = 9500 + (int(self.instance_id, 16) % 1000)
        env['SEARXNG_PORT'] = str(searxng_port)
        
        logger.info(f"Setting auxiliary ports - RSTUDIO_PORT={rstudio_port}, SEARXNG_PORT={searxng_port}")
            
        proc = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        process_info = ProcessInfo(
            proc=proc,
            file_path=str(compose_file),
            port=port,
            process_type='docker',
            is_critical=False
        )
        
        self.processes.append(process_info)
        logger.info(f"Started Docker compose: {compose_file}" + (f" on port {port}" if port else ""))
        return process_info
    
    def monitor_processes(self, check_interval: float = 0.1):
        """Monitor all processes with non-blocking I/O"""
        while self.processes and not self.shutdown_event.is_set() and not self.failure_event.is_set():
            # Check process outputs
            for process_info in self.processes[:]:
                self._check_process_output(process_info)
                
                # Remove completed/failed processes
                if process_info.proc.poll() is not None:
                    failed = self._handle_process_completion(process_info)
                    self.processes.remove(process_info)
                    
                    # If a critical process failed, trigger shutdown
                    if failed and process_info.is_critical:
                        logger.error(f"Critical process {process_info.file_path} failed, initiating shutdown...")
                        self.failure_event.set()
                        break
            
            time.sleep(check_interval)
        
        # If we exited due to failure, shutdown remaining processes
        if self.failure_event.is_set():
            self.shutdown()
            self._display_failure_summary()
            sys.exit(1)
    
    def _check_process_output(self, process_info: ProcessInfo):
        """Check and log process output"""
        proc = process_info.proc
        
        # Check stdout
        if proc.stdout and proc.stdout.readable():
            try:
                if hasattr(select, 'select'):
                    # Use select to check if data is available
                    ready, _, _ = select.select([proc.stdout], [], [], 0)
                    while ready:
                        line = proc.stdout.readline()
                        if not line:
                            break
                        logger.info(f"[{process_info.file_path}:{process_info.port}] STDOUT: {line.strip()}")
                        # Check if more data is available
                        ready, _, _ = select.select([proc.stdout], [], [], 0)
                else:
                    # Fallback for Windows - try to read one line
                    try:
                        line = proc.stdout.readline()
                        if line:
                            logger.info(f"[{process_info.file_path}:{process_info.port}] STDOUT: {line.strip()}")
                    except:
                        pass
            except Exception as e:
                logger.error(f"Error reading stdout from {process_info.file_path}: {e}")
        
        # Check stderr
        if proc.stderr and proc.stderr.readable():
            try:
                if hasattr(select, 'select'):
                    # Use select to check if data is available
                    ready, _, _ = select.select([proc.stderr], [], [], 0)
                    while ready:
                        line = proc.stderr.readline()
                        if not line:
                            break
                        logger.error(f"[{process_info.file_path}:{process_info.port}] STDERR: {line.strip()}")
                        # Check if more data is available
                        ready, _, _ = select.select([proc.stderr], [], [], 0)
                else:
                    # Fallback for Windows - try to read one line
                    try:
                        line = proc.stderr.readline()
                        if line:
                            logger.error(f"[{process_info.file_path}:{process_info.port}] STDERR: {line.strip()}")
                    except:
                        pass
            except Exception as e:
                logger.error(f"Error reading stderr from {process_info.file_path}: {e}")
    
    def _handle_process_completion(self, process_info: ProcessInfo) -> bool:
        """Handle process completion and return True if process failed"""
        return_code = process_info.proc.poll()
        
        # Read remaining output from both stdout and stderr
        try:
            stdout_output, stderr_output = process_info.proc.communicate(timeout=1)
            
            # Display remaining stdout
            if stdout_output:
                logger.info(f"[{process_info.file_path}] Final STDOUT:")
                for line in stdout_output.split('\n'):
                    if line.strip():
                        logger.info(f"[{process_info.file_path}] STDOUT: {line.strip()}")
            
            # Display remaining stderr
            if stderr_output:
                logger.error(f"[{process_info.file_path}] Final STDERR:")
                for line in stderr_output.split('\n'):
                    if line.strip():
                        logger.error(f"[{process_info.file_path}] STDERR: {line.strip()}")
                        
        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout reading final output from {process_info.file_path}")
            # Force kill and try to get output
            try:
                process_info.proc.kill()
                stdout_output, stderr_output = process_info.proc.communicate(timeout=1)
                if stderr_output:
                    logger.error(f"[{process_info.file_path}] STDERR (after kill): {stderr_output}")
            except Exception as e:
                print(str(e))
                pass
        
        # Track failed processes
        failed = return_code != 0
        if failed:
            logger.error(f"Process {process_info.file_path} exited with code {return_code}")
            self.failed_processes.append(process_info)
        else:
            logger.info(f"Process {process_info.file_path} completed successfully")
        
        return failed
    
    def _display_failure_summary(self):
        """Display a summary of failed processes"""
        if not self.failed_processes:
            return
        
        logger.error("=" * 80)
        logger.error("ONE OR MORE PROCESSES FAILED")
        logger.error("=" * 80)
        logger.error(f"Number of failed processes: {len(self.failed_processes)}")
        
        for process_info in self.failed_processes:
            logger.error(f"FAILED: {process_info.file_path}")
            logger.error(f"  Port: {process_info.port}")
            logger.error(f"  Type: {process_info.process_type}")
            logger.error(f"  Exit Code: {process_info.proc.returncode}")
            logger.error(f"  Critical: {process_info.is_critical}")
        
    def shutdown(self):
        """Gracefully shutdown all processes"""
        logger.info("Shutting down all processes...")
        self.shutdown_event.set()
        
        for process_info in self.processes:
            try:
                process_info.proc.terminate()
                process_info.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning(f"Force killing process {process_info.file_path}")
                process_info.proc.kill()
            except Exception as e:
                logger.error(f"Error shutting down {process_info.file_path}: {e}")

class ServerDiscovery:
    """Handles discovery of MCP servers and Docker services"""
    
    @staticmethod
    def has_gpu() -> bool:
        """Detect if GPU (NVIDIA) is available on the system"""
        try:
            # Check if nvidia-smi command exists and can detect GPU
            result = subprocess.run(
                ['nvidia-smi'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
            has_nvidia = result.returncode == 0
            if has_nvidia:
                logger.info("GPU detected: NVIDIA GPU available")
            else:
                logger.info("No GPU detected: Running in CPU-only mode")
            return has_nvidia
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
            logger.info(f"No GPU detected: {e}")
            return False
    
    @staticmethod
    def find_server_files(mcp_dir: Path) -> List[Path]:
        """Find all server.py files in subdirectories, excluding those with docker-compose.yml in the same folder"""
        server_files = []
        for server_file in mcp_dir.rglob('server.py'):
            if server_file.parent != mcp_dir:  # Must be in subdirectory
                # Check if there's a docker-compose.yml in the same directory
                docker_compose_in_same_dir = (server_file.parent / 'docker-compose.yml').exists()
                
                if not docker_compose_in_same_dir:
                    server_files.append(server_file)
                else:
                    logger.info(f"Skipping {server_file} - docker-compose.yml found in same directory")
        return server_files
    
    @staticmethod
    def find_docker_compose_files(mcp_dir: Path) -> List[Path]:
        """
        Find all docker-compose files in subdirectories.
        Prefers .gpu.yml files when GPU is available, otherwise uses standard .yml files.
        """
        has_gpu = ServerDiscovery.has_gpu()
        compose_files = []
        processed_dirs = set()
        
        # First pass: collect all docker-compose files by directory
        compose_by_dir = {}
        for compose_file in mcp_dir.rglob('docker-compose*.yml'):
            if compose_file.parent != mcp_dir:  # Must be in subdirectory
                parent = compose_file.parent
                if parent not in compose_by_dir:
                    compose_by_dir[parent] = []
                compose_by_dir[parent].append(compose_file)
        
        # Second pass: select appropriate file based on GPU availability
        for parent, files in compose_by_dir.items():
            gpu_file = None
            standard_file = None
            
            for f in files:
                if f.name == 'docker-compose.gpu.yml':
                    gpu_file = f
                elif f.name == 'docker-compose.yml':
                    standard_file = f
            
            # Select the appropriate file
            if has_gpu and gpu_file:
                logger.info(f"Using GPU-enabled compose file: {gpu_file}")
                compose_files.append(gpu_file)
            elif standard_file:
                if has_gpu and not gpu_file:
                    logger.info(f"GPU detected but no .gpu.yml found, using standard: {standard_file}")
                else:
                    logger.info(f"Using standard compose file: {standard_file}")
                compose_files.append(standard_file)
            else:
                logger.warning(f"No suitable docker-compose file found in {parent}")
        
        return compose_files

class ConfigManager:
    """Manages port configuration with persistence"""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        
    def load_config(self) -> Dict[str, dict]:
        """
        Load port configuration with enabled flag.
        Returns dict mapping path to {"port": int, "enabled": bool}
        """
        if not self.config_path.exists():
            return {}
            
        try:
            with open(self.config_path, 'r') as f:
                config_list = json.load(f)
                config_dict = {}
                
                for item in config_list:
                    if 'path' in item and 'port' in item:
                        # New format
                        path = item['path']
                        config_dict[path] = {
                            'port': item['port'],
                            'enabled': item.get('enabled', True)  # Default to enabled
                        }
                    else:
                        raise ValueError("Can't parse config.json file")
                
                return config_dict
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def save_config(self, config: Dict[str, dict]) -> None:
        """
        Save port configuration with enabled flag.
        Config dict maps path to {"port": int, "enabled": bool}
        """
        # Convert dict to list format with new structure
        config_list = [
            {
                "path": path,
                "port": info['port'],
                "enabled": info['enabled']
            }
            for path, info in config.items()
        ]
        
        with open(self.config_path, 'w') as f:
            json.dump(config_list, f, indent=4)
    
    def assign_ports(self, server_files: List[Path], compose_files: List[Path] = None,
                     starting_port: int = HOST_PORT_MIN,
                     host_port_min: int = HOST_PORT_MIN,
                     host_port_max: int = HOST_PORT_MAX) -> Dict[str, dict]:
        """
        Assign ports to server files and docker-compose files with proper range management.
        Preserves enabled status for existing servers, new servers are enabled by default.
        Returns dict mapping path to {"port": int, "enabled": bool}
        """
        config = self.load_config()
        
        # Separate servers by type
        host_servers = []
        
        for server_file in server_files:
            host_servers.append(server_file)
        
        # Get currently used ports
        used_ports = set(info['port'] for info in config.values())
        
        # Assign ports to host servers (5000-5099)
        next_host_port = starting_port
        for server_file in host_servers:
            server_str = str(server_file)
            if server_str not in config:
                # Find next available port in host range
                while (next_host_port in used_ports or 
                       next_host_port < host_port_min or 
                       next_host_port > host_port_max):
                    next_host_port += 1
                    if next_host_port > host_port_max:
                        raise RuntimeError(f"No available ports in host range ({host_port_min}-{host_port_max}) for server {server_str}")
                
                config[server_str] = {'port': next_host_port, 'enabled': False}
                used_ports.add(next_host_port)
                logger.info(f"Assigned host port {next_host_port} to {server_str} (enabled by default)")
                next_host_port += 1
        
        # Assign ports to docker-compose files
        if compose_files:
            for compose_file in compose_files:
                compose_str = str(compose_file)
                if compose_str not in config:
                    # Check if there's a server.py in the same directory
                    # Docker-compose with server.py in mcp_host - use host range
                    while (next_host_port in used_ports or 
                           next_host_port < host_port_min or 
                           next_host_port > host_port_max):
                        next_host_port += 1
                        if next_host_port > host_port_max:
                            raise RuntimeError(f"No available ports in host range ({host_port_min}-{host_port_max}) for compose {compose_str}")
                        
                    config[compose_str] = {'port': next_host_port, 'enabled': False}
                    used_ports.add(next_host_port)
                    logger.info(f"Assigned host port {next_host_port} to {compose_str} (enabled by default)")
                    next_host_port += 1
        
        self.save_config(config)
        return config

class MCPDeploymentManager:
    """Main deployment manager that orchestrates all components"""
    
    def __init__(self, mcp_dir: str, workspace_dir: str, config_path: str):
        self.mcp_dir = Path(mcp_dir)
        self.workspace_dir = Path(workspace_dir)
        
        # Generate unique instance ID from workspace path for Docker service isolation
        self.instance_id = generate_instance_id(workspace_dir)
        
        self.process_manager = ProcessManager(self.workspace_dir, self.instance_id)
        self.config_manager = ConfigManager(config_path)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.process_manager.shutdown()
        sys.exit(0)
    
    def deploy(self, skip_docker: bool = False, starting_port: int = HOST_PORT_MIN,
                                                host_port_min: int = HOST_PORT_MIN,
                                                host_port_max: int = HOST_PORT_MAX):
        """Deploy all MCP servers and Docker services"""
        if not self.mcp_dir.exists():
            raise FileNotFoundError(f"MCP directory {self.mcp_dir} does not exist")
        
        # Discover all services first
        compose_files = ServerDiscovery.find_docker_compose_files(self.mcp_dir)
        server_files = ServerDiscovery.find_server_files(self.mcp_dir)
        
        # Assign ports to all services
        logger.info("Assigning ports to all services...")
        port_config = self.config_manager.assign_ports(server_files, compose_files, starting_port, host_port_min, host_port_max)
        
        # Start Docker services
        if not skip_docker:
            self._deploy_docker_services(compose_files, port_config, host_port_min, host_port_max)
        
        # Start MCP servers
        self._deploy_mcp_servers(server_files, port_config, host_port_min, host_port_max)
        
        # Monitor processes
        logger.info("All services started. Monitoring processes...")
        logger.info(f"Workspace directory: {self.workspace_dir}")
        logger.info("All MCP servers will create files directly in the workspace directory")
        self.process_manager.monitor_processes()
    
    def _deploy_docker_services(self, compose_files: List[Path], port_config: Dict[str, dict], 
                               host_port_min: int = HOST_PORT_MIN, host_port_max: int = HOST_PORT_MAX):
        """Deploy Docker Compose services with assigned ports (only if enabled)"""
        if not compose_files:
            logger.info("No Docker Compose files found")
            return
        
        logger.info(f"Found {len(compose_files)} Docker Compose files")
        started_count = 0
        disabled_count = 0
        config_updated = False
        
        for compose_file in compose_files:
            try:
                compose_str = str(compose_file)
                config_entry = port_config.get(compose_str, {})
                
                if not config_entry.get('enabled', True):
                    logger.info(f"Skipping disabled Docker service: {compose_str}")
                    disabled_count += 1
                    continue
                
                port = config_entry.get('port')
                
                # Check if port is in use
                if is_port_in_use(port):
                    logger.warning(f"Port {port} is already in use for {compose_str}")
                    
                    # Get all currently used ports in config
                    used_ports = set(info['port'] for info in port_config.values())
                    
                    # Find an available port
                    new_port = find_available_port(host_port_min, host_port_max, used_ports)
                    
                    if new_port is None:
                        logger.error(f"No available ports in range {host_port_min}-{host_port_max}")
                        continue
                    
                    logger.info(f"Reassigning {compose_str} from port {port} to {new_port}")
                    port_config[compose_str]['port'] = new_port
                    port = new_port
                    config_updated = True
                
                self.process_manager.start_docker_compose(compose_file, port)
                started_count += 1
            except Exception as e:
                logger.error(f"⚠️ Failed to start Docker service {compose_file}: {e}")
        
        # Save config if any ports were reassigned
        if config_updated:
            logger.info("Updating config.json with new port assignments")
            self.config_manager.save_config(port_config)
        
        if started_count > 0:
            logger.info(f"Started {started_count} Docker services ({disabled_count} disabled)")
            logger.info("Waiting for Docker services to start...")
            time.sleep(3)
        elif disabled_count > 0:
            logger.info(f"⚠️ All {disabled_count} Docker services are disabled. Change config.json to enable.")
    
    def _deploy_mcp_servers(self, server_files: List[Path], port_config: Dict[str, dict],
                          host_port_min: int = HOST_PORT_MIN, host_port_max: int = HOST_PORT_MAX):
        """Deploy MCP Python servers with assigned ports (only if enabled)"""
        if not server_files:
            logger.info("⚠️ No MCP server files found")
            return
        
        logger.info(f"Found {len(server_files)} MCP servers")
        started_count = 0
        disabled_count = 0
        config_updated = False
        
        for server_file in server_files:
            server_str = str(server_file)
            config_entry = port_config.get(server_str, {})
            
            if not config_entry.get('enabled', True):
                logger.info(f"Skipping disabled MCP server: {server_str}")
                disabled_count += 1
                continue
            
            port = config_entry.get('port')
            
            # Check if port is in use
            if is_port_in_use(port):
                logger.warning(f"Port {port} is already in use for {server_str}")
                
                # Get all currently used ports in config
                used_ports = set(info['port'] for info in port_config.values())
                
                # Find an available port
                new_port = find_available_port(host_port_min, host_port_max, used_ports)
                
                if new_port is None:
                    logger.error(f"No available ports in range {host_port_min}-{host_port_max}")
                    continue
                
                logger.info(f"Reassigning {server_str} from port {port} to {new_port}")
                port_config[server_str]['port'] = new_port
                port = new_port
                config_updated = True
            
            try:
                self.process_manager.start_python_server(server_file, port)
                started_count += 1
            except Exception as e:
                logger.error(f"Failed to start server {server_file}: {e}")
        
        # Save config if any ports were reassigned
        if config_updated:
            logger.info("Updating config.json with new port assignments")
            self.config_manager.save_config(port_config)
        
        logger.info(f"Started {started_count} MCP servers ({disabled_count} disabled)")
        if started_count == 0:
            raise Exception("⚠️ No MCP server enabled, change config.json and select MCP servers to enable.")

def main():
    parser = argparse.ArgumentParser(description="Deploy MCP servers with centralized workspace file management")
    parser.add_argument("--mcp-dir", default=DEFAULT_FOLDER, help=f"MCP servers directory (default: {DEFAULT_FOLDER})")
    parser.add_argument("--workspace", default=WORKSPACE_FOLDER, help=f"Workspace directory where all MCP servers will create files (default: {WORKSPACE_FOLDER})")
    parser.add_argument("--config", default="config.json", help="Port configuration file")
    parser.add_argument("--starting-port", type=int, default=HOST_PORT_MIN, help=f"Starting port (default: {HOST_PORT_MIN})")
    parser.add_argument("--host_port_min", type=int, default=HOST_PORT_MIN, help="Minimum port for port assignment range.")
    parser.add_argument("--host_port_max", type=int, default=HOST_PORT_MAX, help="Maximum port for port assignment range.")
    parser.add_argument("--no-docker", action="store_true", help="Skip Docker services")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        deployment_manager = MCPDeploymentManager(
            mcp_dir=args.mcp_dir,
            workspace_dir=args.workspace,
            config_path=args.config
        )
        deployment_manager.deploy(
            skip_docker=args.no_docker,
            starting_port=args.starting_port,
            host_port_min=args.host_port_min,
            host_port_max=args.host_port_max
        )
        
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
