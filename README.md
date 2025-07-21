
# Toolomics

*A suite of tools from the Holobiomics Lab for Agents, organized as a set of MCP servers.*

## Installation

To install the required dependencies, you can use either pip or the faster UV package manager:

### Using pip (traditional)
```bash
python3.10 -m pip install -r requirements.txt
```

### Using UV (recommended, faster)
```bash
uv pip install -r requirements.txt
```

## Deploying Tools

### Deploy all tools automatically (docker+host)

```bash
./start.sh
```

### Deploy docker Tools only

To deploy all docker-tools:

```bash
docker build -t toolomics .
docker run -it -p 5100-5200:5100-5200 toolomics
```

By default we use port 5100 to 5200 for MCPs running **in docker**.

### Deploy host Tools only

To deploy all the on-host tools, use the following command:

```bash
python3.10 deploy.py --config <config path>
```

By default we use port 5000 to 5100 for MCPs running **on host**.

For example : 

```bash
python3.10 deploy.py --config config.json 
```

## Centralized File Management

All MCP servers execute in a centralized **workspace directory** (default: `workspace/`). This means:

- **Browser MCP** downloads files → `workspace/downloaded_file.pdf`
- **PDF MCP** processes files → `workspace/extracted_text.txt`
- **Any MCP** creates files → `workspace/output_file.json`

This centralized approach ensures that AI agents can easily find and work with files across different MCP tools without needing to track file locations.

### Intelligent Port Management

Each MCP server is automatically assigned an available port, which is recorded in the `config.json` file. The system uses intelligent port detection to avoid conflicts:

- **Host servers** use ports 5000-5099
- **Docker servers** use ports 5100-5199
- **Automatic conflict resolution**: If a port is already in use, the system finds the next available port
- **Persistent configuration**: Port assignments are saved and reused across deployments
- **No process killing**: Unlike previous versions, the system works around existing processes instead of terminating them

Example configuration:
```json
[
    {
        "mcp_host/browser/server.py": 5002
    },
    {
        "mcp_host/Rscript/server.py": 5001
    },
    {
        "mcp_docker/shell/server.py": 5101
    }
]
```

The deployment system will automatically:
- Check which ports are currently available
- Reassign ports if previously assigned ones are no longer available
- Log all port assignments and conflicts for transparency
- Update the configuration file only when changes are made

## Adding a New MCP

You can easily add a new tool as an MCP server.

### Steps to Add a New MCP

#### 1. Choose the Right Location

- **`mcp_host/your_tool_name/`**: For safe tools that run directly on the host (ports 5000-5099)
  - Use for data processing, file manipulation, API calls
  
- **`mcp_docker/your_tool_name/`**: For potentially unsafe tools that need containerization (ports 5100-5199)
  - Use for shell commands, system operations, or untrusted code execution

#### 2. Create Your MCP Server

Create a `server.py` file in your chosen directory following the required pattern:

- Must accept port number as first command line argument
- Use the centralized `workspace/` directory for file operations
- Return structured responses with proper error handling

#### 3. Deploy Automatically

Run the deployment script to discover and start your new MCP server:

```bash
python3.10 deploy.py --config config.json
```

The script will automatically:
- Find your new `server.py` file
- Assign an appropriate port
- Update `config.json` with the port mapping
- Start your server

### Example MCP Implementation

Here's a complete example showing the required structure:

```python
#!/usr/bin/env python3

"""
Text Processing MCP Server
Provides tools for basic text operations in the workspace.
"""

import sys
from pathlib import Path
from typing import Dict, Any
from fastmcp import FastMCP

# mandatory
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))  # Add 'a/' to Python's search path
from workspace.shared.shared import CommandResult, run_bash_subprocess, return_as_dict

mcp = FastMCP(
    name="Text Processing MCP",
    instructions="Provides text processing tools for the workspace"
)

@mcp.tool
@return_as_dict
def count_words_in_file(file_path: str) -> Dict[str, Any]:
    """
    Count the number of words in a text file from the workspace.
    Args:
        filename: Name of the file to analyze
    Returns:
        Dictionary with word count and file information
    """
    if not file_path.exists():
        return CommandResult(
            status="error",
            stderr=f"File '{file_path}' not found in workspace",
            exit_code=-1
        )
    content = file_path.read_text(encoding='utf-8')
    word_count = len(content.split())
    return CommandResult(
        status="success",
        stdout=word_count
        exit_code=0
    )

# Required: Port handling for deployment
if len(sys.argv) > 1 and sys.argv[1].isdigit():
    port = int(sys.argv[1])
else:
    port = int(input("Enter port number: "))

print(f"Starting Text Processing MCP server on port {port}...")
mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path="/mcp")
```

### Automatic Port Assignment

When you run the `deploy.py` script for the first time, it will automatically assign a port to your new MCP server and save the mapping in the `config.json` file.

### Learn More

For detailed documentation on `fastmcp`, visit the [fastmcp GitHub repository](https://github.com/jlowin/fastmcp).
