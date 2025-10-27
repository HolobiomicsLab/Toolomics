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
    timeout: int = 30,
) -> CommandResult:
    # Use the fixed workspace path from the volume mount
    # This is more reliable than os.getcwd() which can change during runtime
    import os
    cwd = "/app/workspace"
    
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
    
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=timeout, shell=True, cwd=cwd
        )
        return CommandResult(
            status="success" if result.returncode == 0 else "error",
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.returncode,
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
def execute_command(command: str) -> dict:
    """
    Execute a shell command and return the output with better error handling and security.
    You should NEVER use this tool to execute Rscript, use the dedicated Rscript tool instead.
    execute_command does not support multiple positional arguments or combined positional and keyword arguments

    Args:
        command (str): The shell command to execute

    Returns:
        dict : {CommandResult.__doc__}

    Example:
        execute_command(command="ls -la /tmp")
    """

    print(f"Executing command: {command}")

    dangerous_patterns = [
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

    return run_bash_subprocess(command, timeout=36000)


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
