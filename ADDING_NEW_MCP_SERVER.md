# Adding a New MCP Server to Toolomics

This comprehensive guide walks you through creating and integrating a new MCP server into the Toolomics suite.

## Prerequisites

Before starting, ensure you have:
- **ToolHive** installed: `curl -sSL https://get.toolhive.dev | sh`
- **Docker** running on your system
- **Python 3.10** environment
- Basic understanding of the **FastMCP** framework

## Overview

Toolomics uses a standardized architecture where all MCP servers:
1. Are located in `mcp_host/your_tool_name/` directory
2. Run in Docker containers managed by ToolHive
3. Share a centralized workspace (mounted as `/projects` in containers)
4. Use standardized response patterns via `shared.py` utilities
5. Are registered in `registry.json` for ToolHive management

## Step 1: Create the Server Directory Structure

Create your new MCP server directory:

```bash
mkdir -p mcp_host/your_tool_name
cd mcp_host/your_tool_name
```

## Step 2: Implement Your MCP Server

Create `server.py` with the following template:

```python
#!/usr/bin/env python3

"""
Your Tool Name MCP Server

Brief description of what your tool does and its main capabilities.

Author: Your Name - HolobiomicsLab, CNRS
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from fastmcp import FastMCP

# Add project root to path for shared imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from shared import CommandResult, run_bash_subprocess, return_as_dict

# Server description for documentation
description = """
Your Tool Name MCP Server provides tools for [describe main functionality].
It allows [list main capabilities and use cases].
"""

# Initialize FastMCP server
mcp = FastMCP(
    name="Your Tool Name MCP",
    instructions=description,
)

@mcp.tool
def get_mcp_name() -> str:
    """Get the name of this MCP server
    
    Returns:
        str: The name of this MCP server
        
    Example:
        >>> get_mcp_name()
        "Your Tool Name MCP"
    """
    return "Your Tool Name MCP"

@mcp.tool
@return_as_dict
def your_main_tool(input_param: str, optional_param: Optional[str] = None) -> Dict[str, Any]:
    """
    Main tool function - describe what it does here.
    
    Args:
        input_param (str): Description of the main parameter
        optional_param (Optional[str]): Description of optional parameter
    
    Returns:
        dict: CommandResult dictionary with status, stdout, stderr, exit_code
        
    Example:
        your_main_tool(input_param="example", optional_param="value")
    """
    try:
        # Your tool logic here
        # Use /projects for file operations (mounted from host workspace/):
        workspace_path = Path("/projects")
        
        # Example: Create a file in workspace
        output_file = workspace_path / "your_tool_output.txt"
        
        # Your processing logic
        result_data = f"Processed: {input_param}"
        
        # Write to workspace if needed
        output_file.write_text(result_data)
        
        return CommandResult(
            status="success",
            stdout=f"Successfully processed {input_param}. Output saved to {output_file}",
            stderr="",
            exit_code=0
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stdout="",
            stderr=str(e),
            exit_code=1
        )

@mcp.tool
@return_as_dict
def list_workspace_files() -> Dict[str, Any]:
    """
    List files in the shared workspace directory.
    
    Returns:
        dict: CommandResult with list of files in workspace
    """
    try:
        workspace_path = Path("/projects")
        if not workspace_path.exists():
            return CommandResult(
                status="error",
                stdout="",
                stderr="Workspace directory not found",
                exit_code=1
            )
        
        files = [f.name for f in workspace_path.iterdir() if f.is_file()]
        
        return CommandResult(
            status="success",
            stdout=f"Files in workspace: {', '.join(files) if files else 'No files found'}",
            stderr="",
            exit_code=0
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stdout="",
            stderr=str(e),
            exit_code=1
        )

# Server startup logic
if __name__ == "__main__":
    print("Starting Your Tool Name MCP server with streamable-http transport...")
    
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
```

## Step 3: Register Your Server in ToolHive

Add your server to `registry.json`:

```json
{
  "servers": {
    // ... existing servers ...
    "toolomics-your-tool": {
      "description": "Your tool description - what it does and main capabilities",
      "image": "holobiomicslab/toolomics:latest",
      "transport": "streamable-http",
      "args": ["python", "/app/mcp_host/your_tool_name/server.py"],
      "env_vars": [
        {
          "name": "MCP_SERVER_TYPE",
          "value": "your-tool"
        }
      ]
    }
  }
}
```

**Important naming conventions:**
- Server name: `toolomics-your-tool` (kebab-case)
- Directory name: `your_tool_name` (snake_case)
- Environment variable value: `your-tool` (kebab-case)

## Step 4: Update start.sh Script

Add your server to the `SERVERS` array in `start.sh`:

```bash
# List of servers to start (Toolomics + Essential MCP servers)
# Note: The registry contains many more MCP servers available.
# Use 'thv run <server-name>' to start additional servers as needed.
SERVERS=(
    "toolomics-rscript"
    "toolomics-browser" 
    "toolomics-csv"
    "toolomics-search"
    "toolomics-pdf"
    "toolomics-shell"
    "toolomics-your-tool"    # Add your server here
    "fetch"
    "git"
    "filesystem"
    "time"
    "arxiv-mcp-server"
)
```

## Step 5: Create a Test Script

Create `tests/toolomics_your_tool_test.py` following the comprehensive test pattern:

```python
#!/usr/bin/env python3

"""
Test client for Your Tool Name MCP Server
Demonstrates functionality with realistic test scenarios.
"""

import asyncio
import json
from pathlib import Path
from fastmcp import Client

async def test_your_tool_operations():
    """Test all your tool operations comprehensively."""
    
    # Connect to the MCP server (you'll need to find the actual port)
    # Run `thv list` to see the assigned port
    async with Client("http://localhost:PORT/mcp") as client:
        print("🚀 Connected to Your Tool Name MCP Server")
        
        # List available tools
        tools = await client.list_tools()
        print(f"📋 Available tools: {[tool.name for tool in tools]}")
        print()
        
        # Test 1: Get server name
        print("=" * 50)
        print("TEST 1: Getting server name")
        print("=" * 50)
        
        result = await client.call_tool("get_mcp_name", {})
        print(f"🏷️ Server name: {result[0].text}")
        print()
        
        # Test 2: Test main functionality
        print("=" * 50)
        print("TEST 2: Testing main tool")
        print("=" * 50)
        
        result = await client.call_tool("your_main_tool", {
            "input_param": "test_value",
            "optional_param": "optional_value"
        })
        print(f"✅ Main tool result: {result[0].text}")
        print()
        
        # Test 3: List workspace files
        print("=" * 50)
        print("TEST 3: Listing workspace files")
        print("=" * 50)
        
        result = await client.call_tool("list_workspace_files", {})
        print(f"📁 Workspace files: {result[0].text}")
        print()
        
        print("🎉 All tests completed successfully!")

if __name__ == "__main__":
    print("🧪 Starting Your Tool Name MCP Server Tests")
    asyncio.run(test_your_tool_operations())
```

## Step 6: Build and Deploy

1. **Rebuild the Docker image** (includes your new server):
```bash
./start.sh --rebuild
```

2. **Or build manually if needed**:
```bash
./build-toolhive.sh
```

3. **Start all services**:
```bash
./start.sh
```

## Step 7: Test Your Server

1. **Check if your server is running**:
```bash
thv list
```
Look for `toolomics-your-tool` in the output.

2. **Check server logs**:
```bash
thv logs toolomics-your-tool
```

3. **Run your test script using the test runner**:
```bash
# Run with the comprehensive test runner
python tests/run_all_mcp_tests.py --server your-tool

# Or run your test file directly
python tests/toolomics_your_tool_test.py

# Or use the convenience script
./test_all_mcps.sh your-tool
```

## Common Patterns and Best Practices

### File Operations
Always use the `/projects` directory for file operations to ensure compatibility with other MCP servers (this is mounted from the host `workspace/` directory):

```python
from pathlib import Path

# Correct way to handle files
workspace = Path("/projects")
input_file = workspace / "input.txt"
output_file = workspace / "output.json"

# Read from workspace
if input_file.exists():
    content = input_file.read_text()

# Write to workspace
output_file.write_text(json.dumps(result_data))
```

### Error Handling
Use the `CommandResult` class for consistent error handling:

```python
try:
    # Your logic here
    return CommandResult(
        status="success",
        stdout="Operation completed successfully",
        stderr="",
        exit_code=0
    )
except FileNotFoundError as e:
    return CommandResult(
        status="error",
        stdout="",
        stderr=f"File not found: {e}",
        exit_code=2
    )
except Exception as e:
    return CommandResult(
        status="error",
        stdout="",
        stderr=f"Unexpected error: {e}",
        exit_code=1
    )
```

### Tool Documentation
Follow FastMCP documentation patterns:

```python
@mcp.tool
@return_as_dict
def process_data(input_data: str, format_type: str = "json") -> Dict[str, Any]:
    """
    Process input data and return formatted results.
    
    Args:
        input_data (str): The data to process
        format_type (str): Output format - "json", "csv", or "txt" (default: "json")
    
    Returns:
        dict: CommandResult with processed data
        
    Example:
        process_data(input_data="sample data", format_type="json")
    """
```

### Environment Variables
Access server-specific environment variables:

```python
server_type = os.environ.get("MCP_SERVER_TYPE", "unknown")
port = os.environ.get("MCP_PORT") or os.environ.get("FASTMCP_PORT")
```

## Troubleshooting

### Server Not Starting
1. **Check ToolHive status**:
```bash
thv list
```

2. **Check server logs**:
```bash
thv logs toolomics-your-tool
```

3. **Verify registry.json syntax**:
```bash
python -m json.tool registry.json
```

### Import Errors
If you get import errors for `shared`:
```python
# Make sure this is at the top of your server.py
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
```

### Port Issues
ToolHive assigns ports dynamically. Always check current ports with:
```bash
thv list --format table
```

### Container Issues
If the container doesn't build:
1. **Check Dockerfile** - ensure your dependencies are in `requirements.txt`
2. **Rebuild image**: `./start.sh --rebuild`
3. **Check Docker**: `docker images holobiomicslab/toolomics:latest`

### Testing Connection Issues
If your test client can't connect:
1. **Verify server is running**: `thv list`
2. **Check the correct port**: Use port from `thv list` output
3. **Verify endpoint**: Use `http://localhost:PORT/mcp`

## Example: Simple Text Processing Server

Here's a complete working example of a text processing MCP server:

### File: `mcp_host/text_processor/server.py`

```python
#!/usr/bin/env python3

"""
Text Processing MCP Server
Provides tools for text analysis and manipulation in the workspace.
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, Any, Optional
from fastmcp import FastMCP

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from shared import CommandResult, run_bash_subprocess, return_as_dict

mcp = FastMCP(
    name="Text Processing MCP",
    instructions="Provides text processing and analysis tools for workspace files"
)

@mcp.tool
def get_mcp_name() -> str:
    return "Text Processing MCP"

@mcp.tool
@return_as_dict
def count_words(filename: str) -> Dict[str, Any]:
    """Count words, lines, and characters in a text file."""
    try:
        filepath = Path("/projects") / filename
        if not filepath.exists():
            return CommandResult(
                status="error",
                stderr=f"File '{filename}' not found in workspace",
                exit_code=1
            )
        
        content = filepath.read_text(encoding='utf-8')
        words = len(content.split())
        lines = len(content.splitlines())
        chars = len(content)
        
        stats = {
            "filename": filename,
            "words": words,
            "lines": lines, 
            "characters": chars
        }
        
        return CommandResult(
            status="success",
            stdout=f"Text statistics: {stats}",
            exit_code=0
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=str(e),
            exit_code=1
        )

@mcp.tool
@return_as_dict
def find_pattern(filename: str, pattern: str) -> Dict[str, Any]:
    """Find regex pattern matches in a text file."""
    try:
        filepath = Path("/projects") / filename
        if not filepath.exists():
            return CommandResult(
                status="error",
                stderr=f"File '{filename}' not found",
                exit_code=1
            )
        
        content = filepath.read_text(encoding='utf-8')
        matches = re.findall(pattern, content, re.MULTILINE)
        
        return CommandResult(
            status="success",
            stdout=f"Found {len(matches)} matches: {matches[:10]}",  # Show first 10
            exit_code=0
        )
        
    except re.error as e:
        return CommandResult(
            status="error",
            stderr=f"Invalid regex pattern: {e}",
            exit_code=2
        )
    except Exception as e:
        return CommandResult(
            status="error", 
            stderr=str(e),
            exit_code=1
        )

if __name__ == "__main__":
    port = int(os.environ.get("MCP_PORT") or sys.argv[1])
    mcp.run(transport="streamable-http", port=port, host="0.0.0.0")
```

### Registry Entry:
```json
"toolomics-text-processor": {
  "description": "Text processing and analysis MCP server",
  "image": "holobiomicslab/toolomics:latest", 
  "transport": "streamable-http",
  "args": ["python", "/app/mcp_host/text_processor/server.py"],
  "env_vars": [
    {
      "name": "MCP_SERVER_TYPE",
      "value": "text-processor"
    }
  ]
}
```

## Step 8: Add to Test Suite

Integrate your server with the comprehensive test runner by adding it to `tests/run_all_mcp_tests.py`:

```python
# Add your server to the SERVER_CONFIGS dictionary
"your-tool": {
    "test_file": "toolomics_your_tool_test.py", 
    "name_variants": ["your-tool", "yourtool"],
    "expected_tools": ["get_mcp_name", "your_main_tool", "list_workspace_files"]
}
```

## Next Steps

After successfully creating and testing your MCP server:

1. **Document your tools** - Add descriptions to your tool functions
2. **Add comprehensive tests** - Follow the 4-phase test pattern (Discovery, Tools, Use Cases, Health)
3. **Update documentation** - Add your server to README.md if it's a major addition
4. **Consider dependencies** - Add any new Python packages to `requirements.txt`
5. **Test integration** - Verify your server works well with other MCP servers in the workspace
6. **Run full test suite** - Ensure all tests pass with your new server: `./test_all_mcps.sh`

Your new MCP server is now ready to be used by AI agents through ToolHive! 🎉