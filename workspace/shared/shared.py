from dataclasses import dataclass, asdict
from functools import wraps
import os
from typing import Optional
import subprocess

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
        elif hasattr(result, '__dataclass_fields__'):
            return asdict(result)
        return result
    return wrapper

def run_bash_subprocess(command: str, timeout: int = 30,) -> CommandResult:
    #cwd = working_directory if working_directory and os.path.exists(working_directory) else None
    print(f"Running command: {command} with timeout: {timeout} seconds")
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=True
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

