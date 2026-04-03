#!/usr/bin/env python3

"""
Shell Tools MCP Server

Provides tools for shell navigation and interaction with parallel command execution.

Author: Martin Legrand - HolobiomicsLab, CNRS
"""

import os
import sys
import asyncio
import uuid
from dataclasses import dataclass, field
from typing import Dict, Optional
from fastmcp import FastMCP
import shlex
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import threading
import time

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


@dataclass
class CommandTask:
    """Represents a command task in the queue."""
    command_id: str
    command: str
    timeout: int
    future: asyncio.Future
    created_at: float = field(default_factory=time.time)


class CommandQueueExecutor:
    """
    Manages parallel command execution with a queue system.

    This executor allows multiple commands to be processed concurrently,
    preventing blocking when multiple agents use the tool simultaneously.
    """

    def __init__(self, max_concurrent: int = 10):
        """
        Initialize the command queue executor.

        Args:
            max_concurrent: Maximum number of commands that can run in parallel
        """
        self.max_concurrent = max_concurrent
        self._semaphore: Optional[asyncio.Semaphore] = None
        self._queue: asyncio.Queue = None
        self._active_tasks: Dict[str, CommandTask] = {}
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=max_concurrent)
        self._initialized = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def _ensure_initialized(self):
        """Ensure the executor is initialized with proper asyncio primitives."""
        if not self._initialized:
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)

            self._semaphore = asyncio.Semaphore(self.max_concurrent)
            self._queue = asyncio.Queue()
            self._initialized = True

    async def submit_command(self, command: str, timeout: int = 300) -> CommandResult:
        """
        Submit a command for execution and wait for the result.

        This method allows multiple commands to be processed concurrently
        using a semaphore to limit the number of parallel executions.

        Args:
            command: The shell command to execute
            timeout: Command timeout in seconds

        Returns:
            CommandResult with the execution outcome
        """
        self._ensure_initialized()

        command_id = str(uuid.uuid4())[:8]
        print(f"[Queue] Received command {command_id}: {command[:50]}...")

        # Use semaphore to limit concurrent executions
        async with self._semaphore:
            print(f"[Queue] Executing command {command_id} (active: {self.max_concurrent - self._semaphore._value}/{self.max_concurrent})")

            with self._lock:
                task = CommandTask(
                    command_id=command_id,
                    command=command,
                    timeout=timeout,
                    future=asyncio.get_event_loop().create_future()
                )
                self._active_tasks[command_id] = task

            try:
                # Run the blocking subprocess in a thread pool to avoid blocking the event loop
                result = await asyncio.get_event_loop().run_in_executor(
                    self._executor,
                    self._run_command_sync,
                    command,
                    timeout,
                    command_id
                )
                return result
            finally:
                with self._lock:
                    self._active_tasks.pop(command_id, None)
                print(f"[Queue] Completed command {command_id}")

    def _run_command_sync(self, command: str, timeout: int, command_id: str) -> CommandResult:
        """
        Synchronously run a command (called from thread pool).

        Args:
            command: The shell command to execute
            timeout: Command timeout in seconds
            command_id: Unique identifier for this command

        Returns:
            CommandResult with the execution outcome
        """
        return run_bash_subprocess(command, timeout=timeout, command_id=command_id)

    def get_queue_status(self) -> dict:
        """Get the current status of the command queue."""
        with self._lock:
            return {
                "max_concurrent": self.max_concurrent,
                "active_commands": len(self._active_tasks),
                "available_slots": self._semaphore._value if self._semaphore else self.max_concurrent,
                "active_command_ids": list(self._active_tasks.keys())
            }

    def shutdown(self):
        """Shutdown the executor and clean up resources."""
        self._executor.shutdown(wait=True)


# Global command queue executor
command_executor = CommandQueueExecutor(max_concurrent=10)


def run_bash_subprocess(
    command: str,
    timeout: int = 300,
    max_output_size: int = 32000,
    command_id: str = None
) -> CommandResult:
    """
    Run command with streaming output to prevent buffer deadlock.

    Args:
        command: The shell command to execute
        timeout: Command timeout in seconds
        max_output_size: Maximum output size in bytes
        command_id: Optional identifier for logging
    """
    import subprocess
    import select
    import fcntl

    cwd = "/app/workspace"
    log_prefix = f"[{command_id}] " if command_id else ""

    # Force directory cache refresh for Docker bind mounts
    # The dentry cache can hold stale directory listings - we need aggressive invalidation
    try:
        # Method 1: Open directory with O_DIRECTORY to force inode refresh
        dir_fd = os.open(cwd, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fstat(dir_fd)  # Force stat refresh
            os.fsync(dir_fd)  # Sync any pending operations
        except OSError:
            pass  # fsync may fail on read-only directory fd, that's OK
        finally:
            os.close(dir_fd)

        # Method 2: Touch the directory to invalidate caches
        os.utime(cwd, None)
    except (OSError, PermissionError):
        pass

    # Method 3: Use scandir which opens a fresh directory stream
    try:
        with os.scandir(cwd) as entries:
            # Force iteration to actually read the directory
            _ = [e.name for e in entries]
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

    print(f"{log_prefix}Running command: {command} with timeout: {timeout} seconds in {cwd}")
    start_time = time.time()

    try:
        proc = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            # Use bytes mode for proper non-blocking I/O with select()
            text=False
        )

        stdout_chunks = []
        stderr_chunks = []
        stdout_size = 0
        stderr_size = 0

        # Get file descriptors for direct os.read() calls
        stdout_fd = proc.stdout.fileno() if proc.stdout else None
        stderr_fd = proc.stderr.fileno() if proc.stderr else None

        # Set non-blocking mode on file descriptors
        if stdout_fd is not None:
            flags = fcntl.fcntl(stdout_fd, fcntl.F_GETFL)
            fcntl.fcntl(stdout_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        if stderr_fd is not None:
            flags = fcntl.fcntl(stderr_fd, fcntl.F_GETFL)
            fcntl.fcntl(stderr_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

        # Track if streams are still open
        stdout_open = stdout_fd is not None
        stderr_open = stderr_fd is not None

        while stdout_open or stderr_open:
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > timeout:
                print(f"{log_prefix}Command timeout after {elapsed:.2f}s: {command}")
                proc.kill()
                proc.wait(timeout=5)
                return CommandResult(
                    status="error",
                    stderr=f"Command timed out after {timeout} seconds",
                    exit_code=-1
                )

            # Build list of open streams for select
            readable = []
            if stdout_open:
                readable.append(proc.stdout)
            if stderr_open:
                readable.append(proc.stderr)

            if not readable:
                break

            try:
                ready_to_read, _, _ = select.select(readable, [], [], 0.1)
            except (ValueError, OSError):
                # Pipes closed
                break

            # Read from ready streams using os.read() for truly non-blocking I/O
            for stream in ready_to_read:
                try:
                    fd = stream.fileno()
                    chunk = os.read(fd, 4096)
                    if chunk:
                        if stream == proc.stdout and stdout_size < max_output_size:
                            stdout_chunks.append(chunk)
                            stdout_size += len(chunk)
                        elif stream == proc.stderr and stderr_size < max_output_size:
                            stderr_chunks.append(chunk)
                            stderr_size += len(chunk)
                    else:
                        # Empty read means EOF
                        if stream == proc.stdout:
                            stdout_open = False
                        elif stream == proc.stderr:
                            stderr_open = False
                except BlockingIOError:
                    # No data available right now, continue
                    pass
                except (IOError, OSError) as e:
                    # Stream closed or error
                    if stream == proc.stdout:
                        stdout_open = False
                    elif stream == proc.stderr:
                        stderr_open = False

            # Also check if process finished (helps detect EOF sooner)
            if proc.poll() is not None:
                # Process done, do one more iteration to drain any remaining data
                # After that, the next iteration will find empty reads and exit
                pass

        # Wait for process to complete if not already
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

        duration = time.time() - start_time
        exit_code = proc.returncode

        # Decode bytes to text
        stdout_text = b''.join(stdout_chunks)[:max_output_size].decode('utf-8', errors='replace')
        stderr_text = b''.join(stderr_chunks)[:max_output_size].decode('utf-8', errors='replace')

        print(f"{log_prefix}Command completed in {duration:.2f}s with exit code {exit_code}")
        print(f"{log_prefix}Stdout length: {len(stdout_text)}, Stderr length: {len(stderr_text)}")

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
        import traceback
        print(f"{log_prefix}Exception in run_bash_subprocess: {e}")
        traceback.print_exc()
        return CommandResult(
            status="error",
            stderr=str(e),
            exit_code=-1,
        )


@mcp.tool
@return_as_dict
async def execute_command(command: str, timeout: int = 300) -> dict:
    """
    Execute a shell command and return the output with better error handling and security.

    This tool uses a command queue system that allows multiple commands to run in parallel,
    preventing blocking when multiple agents use the tool simultaneously.

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

    # Submit command to the queue for parallel execution
    return await command_executor.submit_command(command, timeout=timeout)


@mcp.tool
def get_command_queue_status() -> dict:
    """
    Get the current status of the command execution queue.

    Returns information about active commands and available execution slots.
    Useful for monitoring parallel command execution.

    Returns:
        dict: Queue status including:
            - max_concurrent: Maximum parallel commands allowed
            - active_commands: Number of currently running commands
            - available_slots: Number of available execution slots
            - active_command_ids: List of active command identifiers
    """
    return command_executor.get_queue_status()


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
    print(f"Command queue initialized with max {command_executor.max_concurrent} concurrent executions")
    mcp.run(transport="streamable-http", port=port, host="0.0.0.0")
