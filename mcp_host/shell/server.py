#!/usr/bin/env python3

"""
Shell Tools MCP Server

Provides tools for shell navigation and interaction.

Author: Martin Legrand - HolobiomicsLab, CNRS
"""

import os
import sys
from fastmcp import FastMCP
import shlex
import subprocess
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))  # Add 'a/' to Python's search path

from shared import CommandResult, return_as_dict, get_workspace_path

description = """
Shell Tools MCP Server provides tools for shell navigation and interaction.
It execute command in bash in a docker container, allowing users to run shell commands securely.
It should not be used to execute Rscript commands; use the dedicated Rscript tool instead.
"""

mcp = FastMCP(
    name="Bash command MCP",
    instructions=description,
)

def run_bash_subprocess(
    command: str,
    timeout: int = 300,
    max_output_size: int = 32000
) -> CommandResult:
    """
    Run command with streaming output to prevent buffer deadlock.
    """
    import os
    import time
    
    cwd = "/app/workspace"
    
    # Force directory refresh by listing it (triggers inode cache invalidation)
    try:
        os.listdir(cwd)
    except Exception:
        pass
    
    # Verify the directory exists and is accessible
    if not os.path.exists(cwd):
        return CommandResult(
            status="error",
            stderr=f"Workspace directory does not exist: {cwd}",
            exit_code=-1,
        )
    
    if not os.access(cwd, os.R_OK | os.W_OK | os.X_OK):
        return CommandResult(
            status="error",
            stderr=f"Workspace directory is not accessible: {cwd}",
            exit_code=-1,
        )
    
    print(f"Running command: {command} with timeout: {timeout} seconds in {cwd}")
    start_time = time.time()
    
    try:
        # ✅ FIX: Use Popen for streaming instead of run() to prevent buffer deadlock
        proc = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,  # ✅ FIX: Prevent interactive hangs
            text=True,
            bufsize=1  # Line buffered
        )
        
        # Collect output with streaming to prevent deadlock
        stdout_lines = []
        stderr_lines = []
        stdout_size = 0
        stderr_size = 0
        
        # Non-blocking read with timeout
        while proc.poll() is None:
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > timeout:
                print(f"Command timeout after {elapsed:.2f}s: {command}")
                proc.kill()
                proc.wait(timeout=5)
                return CommandResult(
                    status="error",
                    stderr=f"Command timed out after {timeout} seconds",
                    exit_code=-1
                )
            
            # Read available output (non-blocking)
            try:
                if proc.stdout:
                    line = proc.stdout.readline()
                    if line and stdout_size < max_output_size:
                        stdout_lines.append(line)
                        stdout_size += len(line)
            except:
                pass
            
            try:
                if proc.stderr:
                    line = proc.stderr.readline()
                    if line and stderr_size < max_output_size:
                        stderr_lines.append(line)
                        stderr_size += len(line)
            except:
                pass
            
            time.sleep(0.01)  # Small delay to prevent busy-wait
        
        # Get remaining output
        try:
            stdout_remaining, stderr_remaining = proc.communicate(timeout=1)
            if stdout_remaining and stdout_size < max_output_size:
                remaining_space = max_output_size - stdout_size
                stdout_lines.append(stdout_remaining[:remaining_space])
            if stderr_remaining and stderr_size < max_output_size:
                remaining_space = max_output_size - stderr_size
                stderr_lines.append(stderr_remaining[:remaining_space])
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        
        duration = time.time() - start_time
        exit_code = proc.returncode
        
        stdout_text = ''.join(stdout_lines)[:max_output_size]
        stderr_text = ''.join(stderr_lines)[:max_output_size]
        
        print(f"Command completed in {duration:.2f}s with exit code {exit_code}")
        
        return CommandResult(
            status="success" if exit_code == 0 else "error",
            stdout=stdout_text,
            stderr=stderr_text,
            exit_code=exit_code,
        )
        
    except subprocess.TimeoutExpired:
        return CommandResult(
            status="error",
            stderr=f"Command timed out after {timeout} seconds",
            exit_code=-1,
        )
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=str(e),
            exit_code=-1,
        )



@mcp.tool
@return_as_dict
def execute_command(command: str, timeout: int = 300) -> dict:
    """
    Execute a shell command and return the output with better error handling and security.

    Args:
        command (str): The shell command to execute
        timeout (int): Command timeout in seconds (default: 300 = 5 minutes, max: 7200 = 2 hours)

    Returns:
        dict : {CommandResult.__doc__}

    Examples:
        execute_command(command="ls -la /tmp") # command= is very important
        execute_command(command="long_process.sh", timeout=3600)  # 1 hour timeout for long tasks
    """

    # ✅ FIX: Enforce maximum timeout of 2 hours (7200 seconds)
    if timeout > 7200:
        print(f"Warning: Timeout {timeout}s exceeds maximum 7200s (2 hours), capping to 7200s")
        timeout = 7200
    
    print(f"Executing command: {command} (timeout: {timeout}s)")

    dangerous_patterns = [
        "sudo"
        "htop"
        "top"
        "vim"
        "nano"
        "gedit"
        "emacs"
        "nvim"
    ]
    try:
        command_words = shlex.split(command.lower())
    except ValueError:
        command_words = command.lower().split()

    # Check for dangerous command patterns
    for pattern in dangerous_patterns:
        if all(word in command_words for word in pattern):
            return CommandResult(
                status="error",
                stdout="Command blocked for security reasons",
                stderr="Command blocked for security reasons",
                exit_code=-1,
            )

    return run_bash_subprocess(command, timeout=timeout)


print("Starting Shell MCP server with streamable-http transport...")
if __name__ == "__main__":
    # Get port from environment variable (set by ToolHive) or command line argument as fallback
    port = None
    if "MCP_PORT" in os.environ:
        port = int(os.environ["MCP_PORT"])
        print(f"Using port from MCP_PORT environment variable: {port}")
    elif "FASTMCP_PORT" in os.environ:
        port = int(os.environ["FASTMCP_PORT"])
        print(f"Using port from FASTMCP_PORT environment variable: {port}")
    elif len(sys.argv) == 2:
        port = int(sys.argv[1])
        print(f"Using port from command line argument: {port}")
    else:
        print("Usage: python server.py <port>")
        print("Or set MCP_PORT/FASTMCP_PORT environment variable")
        sys.exit(1)

    print(f"Starting server on port {port}")
    mcp.run(transport="streamable-http", port=port, host="0.0.0.0")
