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
        Path: ./workspace if it exists (container environment), otherwise current working directory
    """
    workspace_path = Path("./")
    #if not workspace_path.exists():
    #    workspace_path = Path.cwd()
    return workspace_path


def run_bash_subprocess(
    command: str,
    timeout: int = 30,
) -> CommandResult:
    import os
    # Set working directory to ./workspace for consistency
    cwd = "./workspace" if os.path.exists("./workspace") else None
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