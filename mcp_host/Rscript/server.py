#!/usr/bin/env python3

"""
CSV Management MCP Server

Provides tools for creating, reading, and manipulating R script.
"""

from pathlib import Path
from typing import Any, Dict, List
from fastmcp import FastMCP
from datetime import datetime
import sys
import os

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from shared import return_as_dict, run_bash_subprocess, CommandResult

description = """
R script MCP Server provides tools for executing R scripts and managing R environments.
The tools allow for executing R code / scripts, save R scripts, and listing files in specific directories.
This tool should not be used for installing software or packages, as it is not designed for that purpose.
"""

mcp = FastMCP(
    name="R script MCP",
    instructions=description,
)





# Ensure workspace directory exists
# STORAGE_DIR = Path("./workspace")
# STORAGE_DIR.mkdir(exist_ok=True)

SCRIPT_DIR = Path("/projects")
SCRIPT_DIR.mkdir(exist_ok=True)


# print(f"Using workspace directory: {STORAGE_DIR}")
print(f"Using script directory: {SCRIPT_DIR}")


def run_rscript(script_path: str) -> CommandResult:
    """
    Run an R script using the xcmsrocker Docker container.

    Args:
        script_name: The name of the R script file to execute.

    Returns:
        CommandResult containing the status, stdout, stderr, and exit code.
    """
    cmd = f"Rscript {script_path}"
    result = run_bash_subprocess(cmd, timeout=60)
    
    # Limit stdout and stderr to 4000 characters
    if len(result.stdout) > 4000:
        result.stdout = result.stdout[:4000] + "\n... (output truncated to 4000 characters)"
    
    if len(result.stderr) > 4000:
        result.stderr = result.stderr[:4000] + "\n... (error output truncated to 4000 characters)"
    
    return result   


@mcp.tool
@return_as_dict
def execute_r_code(r_code: str) -> Dict[str, Any]:
    """
    Execute R code.
    Also saves the executed R script in the script directory.

    Args:
        r_code: The R code to execute as a string.

    Returns:
        dict: {CommandResult.__doc__}

    Example:
        >>> execute_r_code(r_code="print('Hello World')")
        {{
            "status": "success",
            "stdout": "[1] \"Hello World\"\\n",
            "stderr": "",
            "exit_code": 0
        }}
    """
    try:
        # Copy the temp file to rstudio_data (host), which is /home/rstudio in the container
        script_name = f"rscript_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.R"
        script_path = script_name
        with open(script_path, "w") as f:
            f.write(r_code)
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Error saving R script: {str(e)}",
            exit_code=-1,
        )

    # print(run_bash_subprocess("ls"))

    res = run_rscript(script_path)
    print(f"Executed R script: {script_name} with result: {res}")
    return res


@mcp.tool
def write_r_script(r_code: str, filename: str) -> str:
    """
    Write the R script in the script directory.

    Args:
        r_code: The R code to write as a string.
        filename: The name of the file to save the script as.

    Returns:
        str: A message indicating success or failure.

    Example:
        >>> write_r_script(r_code="x <- 1:10\\nprint(x)", filename="example.r")
        "Script written successfully: /path/to/script/example.r"
    """
    try:
        # Copy the temp file to rstudio_data (host), which is /home/rstudio in the container
        # script_name = f"rscript_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.R"
        script_path = filename
        with open(script_path, "w") as f:
            f.write(r_code)
        return "Script written successfully: " + str(script_path)
    except Exception as e:
        return "Script writing failed: " + str(e)


@mcp.tool
def list_workspace_files() -> List[str]:
    """
    List all files in the workspace directory.

    Returns:
        A list of filenames in the workspace directory.

    Example:
        >>> list_workspace_files()
        ["analysis1.r", "data.csv", "results.txt"]
    """
    return [f.name for f in Path(".").iterdir() if f.is_file()]


@mcp.tool
def list_script_files() -> List[str]:
    """
    List all files in the script directory.

    Returns:
        A list of filenames in the script directory.

    Example:
        >>> list_script_files()
        ["analysis.r", "preprocessing.r", "visualization.r"]
    """
    return [f.name for f in Path(".").iterdir() if f.is_file()]


@mcp.tool
@return_as_dict
def execute_r_script_file(filename: str) -> Dict[str, Any]:
    """
    Execute an existing R script file from the script directory using Rscript.

    Args:
        filename: The name of the R script file in the script directory.

    Returns:
        dict: {CommandResult.__doc__}

    Example:
        >>> execute_r_script_file(filename="analysis.r")
        {{
            "status": "success",
            "stdout": "Analysis completed\\n",
            "stderr": "",
            "exit_code": 0
        }}
    """
    script_path =  Path(".") / filename
    if not script_path.exists() or not script_path.is_file():
        return f"File '{filename}' does not exist in script dir."

    return run_rscript(script_path)


print("Starting R script MCP server with streamable-http transport...")
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
