
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

## Requirements

### ToolHive
Toolomics uses ToolHive for container orchestration and MCP server management. Install ToolHive:

```bash
curl -sSL https://get.toolhive.dev | sh
```

### UV Package Manager (Optional but Recommended)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Deploying Tools

### Start All Services

```bash
./start.sh
```

This will:
- Build the Docker image if needed
- Start SearxNG services for web search
- Deploy all MCP servers via ToolHive
- Create the centralized workspace directory

### Rebuild and Start

```bash
./start.sh --rebuild
```

Forces a rebuild of the Docker image before starting services.

### Managing Services

```bash
# List running servers
thv list

# Check server logs
thv logs <server-name>

# Stop specific server
thv stop <server-name>

# Stop all servers
thv stop --all
```

## Centralized File Management

All MCP servers execute in a centralized **workspace directory** (default: `workspace/`). This means:

- **Browser MCP** downloads files → `workspace/downloaded_file.pdf`
- **PDF MCP** processes files → `workspace/extracted_text.txt`
- **Any MCP** creates files → `workspace/output_file.json`

This centralized approach ensures that AI agents can easily find and work with files across different MCP tools without needing to track file locations.

## Available MCP Servers

All servers are located in `mcp_host/` and run in Docker containers managed by ToolHive:

- **browser**: Web automation with Selenium and SearxNG search integration
- **csv**: CSV data processing, manipulation, and analysis
- **pdf**: PDF text extraction and document processing
- **Rscript**: R script execution environment for statistical computing
- **mcp_search**: MCP server registry search and discovery
- **shell**: Secure shell command execution with safety filters

All servers share the same containerized environment with the centralized workspace mounted for seamless file sharing.

### ToolHive Service Management

All MCP servers are managed through ToolHive, which handles:

- **Automatic port assignment**: ToolHive dynamically assigns available ports
- **Service discovery**: AI agents connect through ToolHive's registry system
- **Container orchestration**: Docker containers are managed automatically
- **Network integration**: All services are connected to the SearxNG network
- **Workspace mounting**: The centralized workspace is automatically mounted in all containers

Server configurations are defined in `registry.json` and managed by ToolHive.

## Adding a New MCP

You can easily add a new tool as an MCP server.

### Steps to Add a New MCP

#### 1. Create Your MCP Server

Create your MCP server in the `mcp_host/` directory:

```
mcp_host/
└── your_tool_name/
    └── server.py
```

#### 2. Implement Your Server

Create a `server.py` file in your chosen directory following the required pattern:

- Use the centralized `workspace/` directory for file operations
- Import shared utilities from `shared.py`
- Use `@return_as_dict` decorator for standardized responses
- Follow FastMCP patterns with proper error handling

#### 3. Register with ToolHive

Add your new server to `registry.json` following the existing pattern:

```json
{
  "servers": {
    "toolomics-your-tool": {
      "description": "Your tool description",
      "image": "holobiomicslab/toolomics:latest",
      "transport": "streamable-http",
      "args": ["python", "/app/mcp_host/your_tool/server.py"],
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

#### 4. Deploy

Run `./start.sh` to deploy your new server with all others.

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

# Add project root to path for shared imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from shared import CommandResult, run_bash_subprocess, return_as_dict

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
        stdout=word_count,
        exit_code=0
    )

# ToolHive will provide the port via environment or arguments
if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    port = 8000  # Default fallback

print(f"Starting Text Processing MCP server on port {port}...")
mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path="/mcp")
```

### Testing Your MCP Server

You can test individual MCP servers using the test scripts in the `tests/` directory:

```bash
python tests/csv_test.py
python tests/R_test.py
python tests/shell_test.py
```

### Learn More

For detailed documentation on `fastmcp`, visit the [fastmcp GitHub repository](https://github.com/jlowin/fastmcp).
