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
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))  # Add 'a/' to Python's search path

from shared import CommandResult, run_bash_subprocess, return_as_dict

description = """
Shell Tools MCP Server provides tools for shell navigation and interaction.
It execute command in bash in a docker container, allowing users to run shell commands securely.
It should not be used to execute Rscript commands; use the dedicated Rscript tool instead.
"""

mcp = FastMCP(
    name="Bash command MCP",
    instructions=description,
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
        ["rm", "-r"],
        ["rm", "-rf"],
        ["rm", "-f"],
        ["kill", "-9"],
        ["chmod", "777"],
        ["mv", "/etc"],
        ["cp", "/etc"],
        ["rm", "/etc"],
        ["rm", "/usr"],
        ["rm", "/var"],
        ["rm", "/"],
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

    return run_bash_subprocess(command, timeout=1800)


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
