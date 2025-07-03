#!/usr/bin/env python3

"""
Shell Tools MCP Server

Provides tools for shell navigation and interaction.

Author: Martin Legrand - HolobiomicsLab, CNRS
"""


import time
import os
import sys
import threading
from fastmcp import FastMCP
from typing import List, Dict, Any, Optional
import subprocess
import shlex

mcp = FastMCP("Shell Tools Server")

def run_bash_subprocess(command: str, timeout: int = 30, cwd: Optional[str] = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
        shell=True
    )

def create_return_dict(status: str,
                       stdout: str = "",
                       stderr: str = "",
                       exit_code: int = 0,
                       working_directory: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a standardized return dictionary for MCP shell tools.
    Args:
        status: Status of the operation (success/error)
        stdout: Standard output from the command
        stderr: Standard error from the command
        exit_code: Exit code of the command
        working_directory: Directory where the command was executed
    """
    return {
        "status": status or "success",
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
        "working_directory": working_directory or os.getcwd()
    }

@mcp.tool
def execute_command(command: str, timeout: int = 30, working_directory: Optional[str] = "workspace") -> Dict[str, Any]:
    """
    Execute a shell command and return the output with better error handling and security.
    
    Args:
        command: The shell command to execute
        timeout: Command timeout in seconds (default: 30)
        working_directory: Optional directory to execute the command in
    """
    
    print(f"Executing command: {command}")
    
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
            return create_return_dict(
                status="error",
                stdout="Command blocked for security reasons",
                stderr="Command blocked for security reasons",
                exit_code=-1,
                working_directory=working_directory or os.getcwd()
            )
    
    try:
        cwd = working_directory if working_directory and os.path.exists(working_directory) else None
        result = run_bash_subprocess(command, timeout=timeout, cwd=cwd)

        return create_return_dict(
            status="success" if result.returncode == 0 else "error",
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.returncode
        )
        
    except subprocess.TimeoutExpired:
        return create_return_dict(
            status="error",
            stderr=f"Command timed out after {timeout} seconds",
            exit_code=-1,
            working_directory=cwd or os.getcwd()
        )
    except Exception as e:
        return create_return_dict(
            status="error",
            stderr=str(e),
            exit_code=-1,
            working_directory=cwd or os.getcwd()
        )

if len(sys.argv) > 1 and sys.argv[1].isdigit():
    port = int(sys.argv[1])
else:
    port = int(input("Enter port number: "))
print(f"Running Shell MCP server on port {port}")
mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path="/mcp")