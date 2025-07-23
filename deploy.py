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
from pathlib import Path
import select
from dataclasses import dataclass
from typing import Dict, List, Optional
import threading
import logging
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DEFAULT_FOLDER = "mcp_host"
STARTING_PORT = 5000
WORKSPACE_FOLDER = "workspace"

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
    
    def __init__(self, workspace_dir: Path, python_executable: str = None):
        self.processes: List[ProcessInfo] = []
        self.shutdown_event = threading.Event()
        self.failure_event = threading.Event()  # Set when a critical process fails
        self.workspace_dir = workspace_dir
        self.failed_processes: List[ProcessInfo] = []  # Track failed processes
        self.python_executable = python_executable or sys.executable
        
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
        cmd = [self.python_executable, str(absolute_server_path), str(port)]
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
    
    def start_docker_compose(self, compose_file: Path) -> ProcessInfo:
        """Start docker-compose service"""
        platform = sys.platform
        if platform == "linux":
            cmd = ['docker', 'compose', '-f', str(compose_file), 'up', '-d']
        else:
            cmd = ['docker-compose', '-f', str(compose_file), 'up', '-d']
            
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        process_info = ProcessInfo(
            proc=proc,
            file_path=str(compose_file),
            process_type='docker',
            is_critical=True
        )
        
        self.processes.append(process_info)
        logger.info(f"Started Docker compose: {compose_file}")
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
                        logger.info(f"[{process_info.file_path}:{process_info.port}] STDERR: {line.strip()}")
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
                logger.info(f"[{process_info.file_path}] Final STDERR:")
                for line in stderr_output.split('\n'):
                    if line.strip():
                        logger.info(f"[{process_info.file_path}] STDERR: {line.strip()}")
                        
        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout reading final output from {process_info.file_path}")
            # Force kill and try to get output
            try:
                process_info.proc.kill()
                stdout_output, stderr_output = process_info.proc.communicate(timeout=1)
                if stderr_output:
                    logger.error(f"[{process_info.file_path}] STDERR (after kill): {stderr_output}")
            except:
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

class PortUtils:
    """Utilities for port management and availability checking"""
    
    @staticmethod
    def is_port_available(port: int, host: str = 'localhost') -> bool:
        """Check if a port is available for binding"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                return result != 0  # Port is available if connection fails
        except Exception:
            return False
    
    @staticmethod
    def find_free_port(start_port: int, end_port: int, host: str = 'localhost') -> Optional[int]:
        """Find the first available port in the given range"""
        for port in range(start_port, end_port + 1):
            if PortUtils.is_port_available(port, host):
                return port
        return None
    
    @staticmethod
    def get_used_ports_in_range(start_port: int, end_port: int, host: str = 'localhost') -> List[int]:
        """Get list of ports that are currently in use in the given range"""
        used_ports = []
        for port in range(start_port, end_port + 1):
            if not PortUtils.is_port_available(port, host):
                used_ports.append(port)
        return used_ports

class ServerDiscovery:
    """Handles discovery of MCP servers and Docker services"""
    
    @staticmethod
    def find_server_files(mcp_dir: Path) -> List[Path]:
        """Find all server.py files in subdirectories"""
        server_files = []
        for server_file in mcp_dir.rglob('server.py'):
            if server_file.parent != mcp_dir:  # Must be in subdirectory
                server_files.append(server_file)
        return server_files
    
    @staticmethod
    def find_docker_compose_files(mcp_dir: Path) -> List[Path]:
        """Find all docker-compose.yml files in subdirectories"""
        compose_files = []
        for compose_file in mcp_dir.rglob('docker-compose.yml'):
            if compose_file.parent != mcp_dir:  # Must be in subdirectory
                compose_files.append(compose_file)
        return compose_files

class ConfigManager:
    """Manages port configuration with persistence"""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        
    def load_config(self) -> Dict[str, int]:
        """Load port configuration"""
        if not self.config_path.exists():
            return {}
            
        try:
            with open(self.config_path, 'r') as f:
                config_list = json.load(f)
                # Convert list format to dict
                return {list(item.keys())[0]: list(item.values())[0] for item in config_list}
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def save_config(self, config: Dict[str, int]) -> None:
        """Save port configuration"""
        # Convert dict to list format for compatibility
        config_list = [{path: port} for path, port in config.items()]
        
        with open(self.config_path, 'w') as f:
            json.dump(config_list, f, indent=4)
    
    def assign_ports(self, server_files: List[Path], starting_port: int = STARTING_PORT) -> Dict[str, int]:
        """Assign ports to server files with intelligent port availability checking"""
        config = self.load_config()
        
        # Define port ranges
        HOST_PORT_MIN = 5000
        HOST_PORT_MAX = 5099
        DOCKER_PORT_MIN = 5100
        DOCKER_PORT_MAX = 5199
        
        # Separate servers by type
        host_servers = []
        docker_servers = []
        
        for server_file in server_files:
            if "mcp_docker" in str(server_file):
                docker_servers.append(server_file)
            else:
                host_servers.append(server_file)
        
        # Check which ports from existing config are still available
        config_changed = False
        for server_str, port in list(config.items()):
            if not PortUtils.is_port_available(port):
                logger.warning(f"Port {port} for {server_str} is no longer available, will reassign")
                del config[server_str]
                config_changed = True
        
        # Get currently used ports from config
        used_ports = set(config.values())
        
        # Check for port conflicts in the ranges and log them
        host_used_ports = PortUtils.get_used_ports_in_range(HOST_PORT_MIN, HOST_PORT_MAX)
        docker_used_ports = PortUtils.get_used_ports_in_range(DOCKER_PORT_MIN, DOCKER_PORT_MAX)
        
        if host_used_ports:
            logger.info(f"Found {len(host_used_ports)} ports in use in host range ({HOST_PORT_MIN}-{HOST_PORT_MAX}): {host_used_ports}")
        if docker_used_ports:
            logger.info(f"Found {len(docker_used_ports)} ports in use in docker range ({DOCKER_PORT_MIN}-{DOCKER_PORT_MAX}): {docker_used_ports}")
        
        # Assign ports to host servers (5000-5099)
        for server_file in host_servers:
            server_str = str(server_file)
            if server_str not in config:
                # Find next available port in host range, starting from preferred port
                preferred_start = max(starting_port, HOST_PORT_MIN)
                available_port = PortUtils.find_free_port(preferred_start, HOST_PORT_MAX)
                
                if available_port is None:
                    raise RuntimeError(f"No available ports in host range ({HOST_PORT_MIN}-{HOST_PORT_MAX}) for server {server_str}")
                
                # Make sure we don't assign the same port to multiple servers
                while available_port in used_ports:
                    available_port = PortUtils.find_free_port(available_port + 1, HOST_PORT_MAX)
                    if available_port is None:
                        raise RuntimeError(f"No available ports in host range ({HOST_PORT_MIN}-{HOST_PORT_MAX}) for server {server_str}")
                
                config[server_str] = available_port
                used_ports.add(available_port)
                logger.info(f"Assigned host port {available_port} to {server_str}")
                config_changed = True
        
        # Assign ports to docker servers (5100-5199)
        for server_file in docker_servers:
            server_str = str(server_file)
            if server_str not in config:
                # Find next available port in docker range
                available_port = PortUtils.find_free_port(DOCKER_PORT_MIN, DOCKER_PORT_MAX)
                
                if available_port is None:
                    raise RuntimeError(f"No available ports in docker range ({DOCKER_PORT_MIN}-{DOCKER_PORT_MAX}) for server {server_str}")
                
                # Make sure we don't assign the same port to multiple servers
                while available_port in used_ports:
                    available_port = PortUtils.find_free_port(available_port + 1, DOCKER_PORT_MAX)
                    if available_port is None:
                        raise RuntimeError(f"No available ports in docker range ({DOCKER_PORT_MIN}-{DOCKER_PORT_MAX}) for server {server_str}")
                
                config[server_str] = available_port
                used_ports.add(available_port)
                logger.info(f"Assigned docker port {available_port} to {server_str}")
                config_changed = True
        
        # Only save config if it changed
        if config_changed:
            self.save_config(config)
            logger.info("Port configuration updated and saved")
        else:
            logger.info("Port configuration unchanged")
        
        return config

class MCPDeploymentManager:
    """Main deployment manager that orchestrates all components"""
    
    def __init__(self, mcp_dir: str, workspace_dir: str, config_path: str):
        self.mcp_dir = Path(mcp_dir)
        self.workspace_dir = Path(workspace_dir)
        self.python_executable = self._get_python310_executable()
        self.process_manager = ProcessManager(self.workspace_dir, self.python_executable)
        self.config_manager = ConfigManager(config_path)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _get_python310_executable(self) -> str:
        """Find and return the python3.10 executable path"""
        # Try common python3.10 executable names
        python_candidates = ['python3.10', 'python3.10.exe']
        
        for candidate in python_candidates:
            python_path = shutil.which(candidate)
            if python_path:
                logger.info(f"Found python3.10 at: {python_path}")
                return python_path
        
        # If python3.10 not found, check if current python is 3.10
        try:
            result = subprocess.run([sys.executable, '--version'], 
                                  capture_output=True, text=True, check=True)
            version_output = result.stdout.strip()
            if '3.10' in version_output:
                logger.info(f"Current Python interpreter is 3.10: {sys.executable}")
                return sys.executable
        except subprocess.CalledProcessError:
            pass
        
        # Fallback: raise error if python3.10 not found
        raise RuntimeError("Python 3.10 not found. Please install Python 3.10 or ensure it's in your PATH")
    
    def _install_requirements(self):
        """Install requirements from requirements.txt using python3.10"""
        requirements_file = Path("requirements.txt")
        
        if not requirements_file.exists():
            logger.warning("requirements.txt not found, skipping requirements installation")
            return
        
        logger.info("Installing requirements from requirements.txt...")
        try:
            cmd = [self.python_executable, '-m', 'pip', 'install', '-r', str(requirements_file)]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info("Requirements installation completed successfully")
            if result.stdout:
                logger.debug(f"pip install stdout: {result.stdout}")
            if result.stderr:
                logger.debug(f"pip install stderr: {result.stderr}")
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install requirements: {e}")
            logger.error(f"Command: {' '.join(cmd)}")
            if e.stdout:
                logger.error(f"stdout: {e.stdout}")
            if e.stderr:
                logger.error(f"stderr: {e.stderr}")
            raise RuntimeError(f"Requirements installation failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during requirements installation: {e}")
            raise
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.process_manager.shutdown()
        sys.exit(0)
    
    def deploy(self, skip_docker: bool = False, starting_port: int = STARTING_PORT):
        """Deploy all MCP servers and Docker services"""
        if not self.mcp_dir.exists():
            raise FileNotFoundError(f"MCP directory {self.mcp_dir} does not exist")
        
        # Install requirements first
        logger.info("=" * 60)
        logger.info("PRELIMINARY STEP: Installing requirements")
        logger.info("=" * 60)
        self._install_requirements()
        
        # Start Docker services
        if not skip_docker:
            self._deploy_docker_services()
        
        # Start MCP servers
        self._deploy_mcp_servers(starting_port)
        
        # Monitor processes
        logger.info("All services started. Monitoring processes...")
        logger.info(f"Workspace directory: {self.workspace_dir}")
        logger.info("All MCP servers will create files directly in the workspace directory")
        self.process_manager.monitor_processes()
    
    def _deploy_docker_services(self):
        """Deploy Docker Compose services"""
        compose_files = ServerDiscovery.find_docker_compose_files(self.mcp_dir)
        
        if not compose_files:
            logger.info("No Docker Compose files found")
            return
        
        logger.info(f"Found {len(compose_files)} Docker Compose files")
        for compose_file in compose_files:
            try:
                self.process_manager.start_docker_compose(compose_file)
            except Exception as e:
                logger.error(f"Failed to start Docker service {compose_file}: {e}")
        
        if compose_files:
            logger.info("Waiting for Docker services to start...")
            time.sleep(3)
    
    def _deploy_mcp_servers(self, starting_port: int):
        """Deploy MCP Python servers"""
        server_files = ServerDiscovery.find_server_files(self.mcp_dir)
        
        if not server_files:
            logger.info("No MCP server files found")
            return
        
        logger.info(f"Found {len(server_files)} MCP servers")
        port_config = self.config_manager.assign_ports(server_files, starting_port)
        
        for server_file in server_files:
            server_str = str(server_file)
            port = port_config[server_str]
            
            try:
                self.process_manager.start_python_server(server_file, port)
            except Exception as e:
                logger.error(f"Failed to start server {server_file}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Deploy MCP servers with centralized workspace file management")
    parser.add_argument("--mcp-dir", default=DEFAULT_FOLDER, help=f"MCP servers directory (default: {DEFAULT_FOLDER})")
    parser.add_argument("--workspace", default=WORKSPACE_FOLDER, help=f"Workspace directory where all MCP servers will create files (default: {WORKSPACE_FOLDER})")
    parser.add_argument("--config", default="config.json", help="Port configuration file")
    parser.add_argument("--starting-port", type=int, default=STARTING_PORT, help=f"Starting port (default: {STARTING_PORT})")
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
            starting_port=args.starting_port
        )
        
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    os.makedirs('workspace', exist_ok=True)  # Ensure workspace directory exists
    main()
