#!/usr/bin/env python3

"""
Shell Tools MCP Server

Provides tools for shell navigation and interaction.

Author: Martin Legrand - HolobiomicsLab, CNRS
"""


import os
import sys
from fastmcp import FastMCP
from typing import Optional
import shlex
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent 
sys.path.append(str(project_root))  # Add 'a/' to Python's search path
from shared.shared import CommandResult, run_bash_subprocess, return_as_dict


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
def get_mcp_name() -> str:
    return "Bash command MCP"

@mcp.tool
@return_as_dict
def execute_command(command: str, timeout: int = 30) -> dict:
    f"""
    Execute a shell command and return the output with better error handling and security.
    You should NEVER use this tool to execute Rscript, use the dedicated Rscript tool instead.
    execute_command does not support multiple positional arguments or combined positional and keyword arguments
    
    Args:
        command (str): The shell command to execute
        timeout (int): Command timeout in seconds (default: 30)
        working_directory (str): Optional directory to execute the command in

    Returns:
        dict : {CommandResult.__doc__}
    """
    
    print(f"Executing command: {command}")

    working_directory = None
    
    dangerous_patterns = [
        ['rm', '-r'], ['rm', '-rf'], ['rm', '-f'],
        ['kill', '-9'], ['chmod', '777'],
        ['mv', '/etc'], ['cp', '/etc'], ['rm', '/etc'], 
        ['rm', '/usr'], ['rm', '/var'], ['rm', '/'],
        [':()', '{', ':|:&', '};:']  # Fork bomb pattern
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
                exit_code=-1
            )
    
    return run_bash_subprocess(command, timeout=timeout)

if len(sys.argv) > 1 and sys.argv[1].isdigit():
    port = int(sys.argv[1])
else:
    port = int(input("Enter port number: "))
print(f"Running Shell MCP server on port {port}")
mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path="/mcp")