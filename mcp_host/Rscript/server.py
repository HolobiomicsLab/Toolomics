#!/usr/bin/env python3

"""
CSV Management MCP Server

Provides tools for creating, reading, and manipulating CSV files.

Author: Martin Legrand - HolobiomicsLab, CNRS
"""

import os
import subprocess
import tempfile
import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP
import shutil
from datetime import datetime

mcp = FastMCP("Rscript manager")

# Ensure storage directory exists
STORAGE_DIR = Path("./storage")
STORAGE_DIR.mkdir(exist_ok=True)

SCRIPT_DIR = "mcp_host/Rscript" / Path("./script")
SCRIPT_DIR.mkdir(exist_ok=True)

print(f"Using storage directory: {STORAGE_DIR}")
print(f"Using script directory: {SCRIPT_DIR}")
def create_return_dict(
    status: str,
    stdout: str = "",
    stderr: str = "",
    exit_code: int = 0,
    working_directory: Optional[str] = None,
) -> Dict[str, Any]:
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
    }

def run_r_docker(script_name:str,timeout:int=120) -> Dict[str, Any]:
    try:
        # Run the R script inside the xcmsrocker container
        docker_cmd = [
            "docker",
            "exec",
            "xcmsrocker",
            "Rscript",
            f"/home/script/{script_name}",
        ]
        result = subprocess.run(
            docker_cmd, capture_output=True, text=True, timeout=timeout
        )

        return create_return_dict(
            status="success" if result.returncode == 0 else "error",
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.returncode,
        )
    except subprocess.TimeoutExpired:
        return create_return_dict(
            status="error",
            stderr=f"Command timed out after {timeout} seconds",
            exit_code=-1,
        )
    except Exception as e:
        return create_return_dict(
            status="error",
            stderr=str(e),
            exit_code=-1,
        )

    

@mcp.tool
def execute_r_code(r_code: str) -> str:
    """
    Execute R code inside the xcmsrocker Docker container and return the output or error.
    Also saves the executed R script in the storage directory.

    Args:
        r_code: The R code to execute as a string.

    Returns:
        The standard output or error message from the containerized Rscript.
    """
    try:
        # Copy the temp file to rstudio_data (host), which is /home/rstudio in the container
        script_name = f"rscript_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.R"
        script_path = SCRIPT_DIR / script_name
        with open(script_path, "w") as f:
            f.write(r_code)

        return run_r_docker(script_name)

    except Exception as e:
        return create_return_dict(
            status="error",
            stderr=str(e),
            exit_code=-1,
        )


@mcp.tool
def list_storage_files() -> List[str]:
    """
    List all files in the storage directory.

    Returns:
        A list of filenames in the storage directory.
    """
    return [f.name for f in STORAGE_DIR.iterdir() if f.is_file()]


@mcp.tool
def execute_r_script_file(filename: str) -> str:
    """
    Execute an existing R script file from the storage directory using Rscript.

    Args:
        filename: The name of the R script file in the storage directory.

    Returns:
        The standard output or error message from Rscript.
    """
    script_path = SCRIPT_DIR / filename
    if not script_path.exists() or not script_path.is_file():
        return f"File '{filename}' does not exist in storage."
    
    return run_r_docker()


import sys

if len(sys.argv) > 1 and sys.argv[1].isdigit():
    port = int(sys.argv[1])
else:
    port = int(input("Enter port number: "))
print(f"Starting CSV MCP server on port {port}...")
mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path="/mcp")
