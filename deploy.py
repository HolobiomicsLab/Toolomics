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
from pathlib import Path
import select
from dataclasses import dataclass
from typing import Dict, List, Optional
import threading
import logging

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
    
    def __post_init__(self):
        if self.process_type not in ['python', 'docker']:
            raise ValueError(f"Invalid process type: {self.process_type}")

class ProcessManager:
    """Manages MCP server processes with proper lifecycle"""
    
    def __init__(self, workspace_dir: Path):
        self.processes: List[ProcessInfo] = []
        self.shutdown_event = threading.Event()
        self.workspace_dir = workspace_dir
        # Ensure workspace directory exists
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
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
        cmd = [sys.executable, str(absolute_server_path), str(port)]
        proc = subprocess.Popen(
            cmd,
            cwd=self.workspace_dir,  # Execute in workspace directory
            env=env,                 # Preserve import paths
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
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
            process_type='docker'
        )
        
        self.processes.append(process_info)
        logger.info(f"Started Docker compose: {compose_file}")
        return process_info
    
    def monitor_processes(self, check_interval: float = 0.1):
        """Monitor all processes with non-blocking I/O"""
        while self.processes and not self.shutdown_event.is_set():
            # Check process outputs
            for process_info in self.processes[:]:
                self._check_process_output(process_info)
                
                # Remove completed/failed processes
                if process_info.proc.poll() is not None:
                    self._handle_process_completion(process_info)
                    self.processes.remove(process_info)
            
            time.sleep(check_interval)
    
    def _check_process_output(self, process_info: ProcessInfo):
        """Check and log process output"""
        proc = process_info.proc
        
        if proc.stdout and proc.stdout.readable():
            try:
                if hasattr(select, 'select'):
                    ready, _, _ = select.select([proc.stdout], [], [], 0)
                    if ready:
                        line = proc.stdout.readline()
                        if line:
                            logger.info(f"[{process_info.file_path}:{process_info.port}] {line.strip()}")
                else:
                    # Fallback for Windows
                    line = proc.stdout.readline()
                    if line:
                        logger.info(f"[{process_info.file_path}:{process_info.port}] {line.strip()}")
            except Exception as e:
                logger.error(f"Error reading output from {process_info.file_path}: {e}")
    
    def _handle_process_completion(self, process_info: ProcessInfo):
        """Handle process completion"""
        return_code = process_info.proc.poll()
        
        # Read remaining output
        try:
            remaining_output, _ = process_info.proc.communicate(timeout=1)
            if remaining_output:
                for line in remaining_output.split('\n'):
                    if line.strip():
                        logger.info(f"[{process_info.file_path}] {line.strip()}")
        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout reading final output from {process_info.file_path}")
        
        if return_code != 0:
            logger.error(f"Process {process_info.file_path} exited with code {return_code}")
        else:
            logger.info(f"Process {process_info.file_path} completed successfully")
    
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
        """Assign ports to server files"""
        config = self.load_config()
        
        # Find next available port
        used_ports = set(config.values())
        next_port = max(used_ports) + 1 if used_ports else starting_port
        
        # Assign ports to new servers
        for server_file in server_files:
            server_str = str(server_file)
            if server_str not in config:
                while next_port in used_ports:
                    next_port += 1
                config[server_str] = next_port
                used_ports.add(next_port)
                next_port += 1
        
        self.save_config(config)
        return config

class MCPDeploymentManager:
    """Main deployment manager that orchestrates all components"""
    
    def __init__(self, mcp_dir: str, workspace_dir: str, config_path: str):
        self.mcp_dir = Path(mcp_dir)
        self.workspace_dir = Path(workspace_dir)
        self.process_manager = ProcessManager(self.workspace_dir)
        self.config_manager = ConfigManager(config_path)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.process_manager.shutdown()
        sys.exit(0)
    
    def deploy(self, skip_docker: bool = False, starting_port: int = STARTING_PORT):
        """Deploy all MCP servers and Docker services"""
        if not self.mcp_dir.exists():
            raise FileNotFoundError(f"MCP directory {self.mcp_dir} does not exist")
        
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
    main()
