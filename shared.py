from dataclasses import dataclass, asdict
from functools import wraps
import subprocess
from pathlib import Path


@dataclass
class CommandResult:
    """A standardized result container for shell command execution.

    Attributes:
        status (str): Status of the operation ("success"/"error"). Defaults to "success".
        stdout (str): Standard output from the command. Defaults to "".
        stderr (str): Standard error from the command. Defaults to "".
        exit_code (int): Exit code of the command. Defaults to 0.
    """

    status: str = "success"
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0


def return_as_dict(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, CommandResult):
            return asdict(result)
        elif hasattr(result, "__dataclass_fields__"):
            return asdict(result)
        return result

    return wrapper


def get_workspace_path() -> Path:
    """Get standardized workspace path with fallback.
    
    Returns:
        Path: Absolute path of the current working directory (which should be the workspace when MCP servers run)
    """
    # When MCP servers are deployed, they run with cwd=workspace_dir
    # So the current working directory IS the workspace
    # Return absolute path to ensure proper resolution in recursive operations
    return Path(".").resolve()


def run_bash_subprocess(
    command: str,
    timeout: int = 30,
) -> CommandResult:
    import os
    # Use get_workspace_path() to get the correct workspace directory
    # This works for both Dockerized (returns mounted path) and non-Dockerized MCPs
    cwd = str(get_workspace_path())
    
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
