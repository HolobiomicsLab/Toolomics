<h1 align="center">Toolomics</h1>

<p align="center">
    <em>A suite of MCP-based Tools from the HolobiomicsLab. Used by AI-Agents such as <i>Mimosa-AI</i></em>
</p>

<p align="center">
    <img src="https://img.shields.io/github/license/HolobiomicsLab/Toolomics?style=flat-square&logo=opensourceinitiative&logoColor=white&color=4caf82" alt="license">
    <img src="https://img.shields.io/github/last-commit/HolobiomicsLab/Toolomics?style=flat-square&logo=git&logoColor=white&color=4caf82" alt="last-commit">
    <img src="https://img.shields.io/github/languages/count/HolobiomicsLab/Toolomics?style=flat-square&color=4caf82" alt="repo-language-count">
</p>

<p align="center">
    <a href="https://github.com/HolobiomicsLab/Toolomics/stargazers">
        <img src="https://img.shields.io/github/stars/HolobiomicsLab/Toolomics?style=social" alt="GitHub Stars">
    </a>
    <a href="https://opensource.org/licenses/Apache-2.0">
        <img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=flat-square" alt="License: Apache 2.0">
    </a>
</p>

---

> ***Toolomics*** — deploys containerized tools, manages isolated instances, and enables file sharing across AI agents for bioinformatics, metabolomics, molecular docking, and beyond.

**Use cases:**
- Deploy MCP servers for browser automation, PDF processing, and data extraction
- Run isolated, multi-instance agent workspaces with automatic resource management
- Orchestrate containerized bioinformatics pipelines (XCMS, RStudio, Redis) with zero config

## Install & deploy tools

### Deploy all tools automatically

```bash
./start.sh <min port> <max port> <workspace name>
```

### Deploy using python script

***Not recommanded, start.sh will handle python, requirements and workpsace installation automatically.***

First, install the required dependencies, you can use either pip or the faster UV package manager:

**1. Install dependencies:**
```bash
python3.10 -m pip install -r requirements.txt
# or using UV
uv pip install -r requirements.txt
```

**2. Run script:**
```bash
python3.10 deploy.py --config config.json --workspace <workspace name> --host_port_min <min port> --host_port_max <max port>
```

## Centralized File Management

All MCP servers execute in a centralized **workspace directory** (default: `workspace/`). This means:

- **Browser MCP** downloads files → `workspace/downloaded_file.pdf`
- **PDF MCP** processes files → `workspace/extracted_text.txt`
- **Any MCP** creates files → `workspace/output_file.json`

This centralized approach ensures that AI agents can easily find and work with files across different MCP tools without needing to track file locations.

## Multi-Instance Deployment

Toolomics supports running **multiple independent instances simultaneously**, each with its own workspace and Docker service isolation.

### How It Works

Each instance is automatically assigned a unique **instance ID** (8-character hash) derived from the workspace path. This ID is used to:
- **Isolate Docker containers, volumes, and auxiliary ports** per instance
- **Create instance-specific config files** (`config_${INSTANCE_ID}.json`) to prevent configuration conflicts

This means each instance has its own configuration and doesn't interfere with others.

**Example: Deploy two instances concurrently**

```bash
# Terminal 1: Instance for user Martin
start.sh 5000 5100 workspace_martin

# Terminal 2: Instance for user John (simultaneous)
start.sh 5100 5200 workspace_john
```

### Automatic Resource Isolation

Each instance automatically gets isolated resources:

| Resource | Isolation Method |
|----------|------------------|
| **Workspace** | Separate directory (`workspace_martin/`, `workspace_john/`) |
| **Docker Containers** | Suffixed with instance ID (`xcmsrocker_a3f2b1c9`, `xcmsrocker_f7e2d4a1`) |
| **Data Volumes** | Instance-specific names (`rstudio_data_a3f2b1c9`, `redis-data_f7e2d4a1`) |
| **MCP Server Ports** | Different port ranges (5000-5100 vs 5100-5200) |
| **Auxiliary Ports** | Dynamic allocation (8787→9537, 8080→9037, etc.) |

## Using MCP with Your Client

To interact with the tools using a client (e.g., for your AI agent), you can use the `fastmcp` library.

### Finding the MCP Port

Each MCP server is assigned a port, which is recorded in the `config.json` file. For example:

```json
[
    {
        "mcp_host/browser/server.py": 5002
    },
    {
        "mcp_host/Rscript/server.py": 5001
    },
    {
        "mcp_host/files/csv/server.py": 5101
    }
]
```

### Example Client Code

Here is an example of how to use a client to interact with an MCP server running on port `5002`:

```python
from fastmcp import Client

async def main():
    # Connect to the MCP server
    port = 5002
    async with Client(f"http://localhost:{port}/mcp") as client:
        tools = await client.list_tools()
        print(f"Available tools: {tools}")
        
        # Example: Use browser tool to download a file
        # File will be saved to workspace/ directory
        result = await client.call_tool("download_file", {
            "url": "https://example.com/document.pdf",
            "filename": "document.pdf"
        })
        print(f"Result: {result.text}")
        
        # The file is now available at workspace/document.pdf
        # Other MCP tools can access it from the same location
```

## Adding a New MCP

You can easily add a new tool as an MCP server.

### Steps to Add a New MCP

1. Create a `server.py` file with your MCP implementation, it should take the port number as first argument (eg: `server.py 5003`).
2. Place the file in a subfolder of the `mcp_host` directory. For example, to add a metabolomics-related tool, create a subfolder like `mcp_host/your_tool_name`.

The `deploy.py` script will look for new `server.py` file, attribute a port for your script and add it to `config.json` (unless you manually did by modifying the config.json), finally it will run your script with the assigned port as first argument.


### Example MCP Implementation

The `fastmcp` library simplifies the creation of MCP servers. Here's a basic example:

```python
#!/usr/bin/env python3

from fastmcp import FastMCP
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))  # Add 'a/' to Python's search path

from shared import CommandResult, run_bash_subprocess, return_as_dict

description = """
a calculator that ...
"""

mcp = FastMCP(
    name="calculator",
    instructions=description,
)

@mcp.tool
@return_as_dict
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers."""
    return a * b

if __name__ == "__main__":
    port = None
    if "MCP_PORT" in os.environ:
        port = int(os.environ["MCP_PORT"])
    elif "FASTMCP_PORT" in os.environ:
        port = int(os.environ["FASTMCP_PORT"])
    elif len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        sys.exit(1)
    mcp.run(transport="streamable-http", port=port, host="0.0.0.0")
```

### Automatic Port Assignment

When you run the `start.sh` or `deploy.py` script for the first time, it will automatically assign a port to your new MCP server and save the mapping in the `config.json` file.

## Dockerizing an MCP Server

For MCP servers that require isolated dependencies or need to run in a containerized environment (e.g., for ML models, system tools, or heavy dependencies), you can deploy them using Docker.

### How It Works

If a `docker-compose.yml` file exists in the same directory as your `server.py`, the deployment script will:
- **Automatically deploy the server in Docker** instead of running it directly on the host
- **Skip the standalone Python execution** to avoid duplicate deployments
- **Pass the assigned port** to the Docker container via the `MCP_PORT` environment variable

### Steps to Dockerize an MCP

1. Create your `server.py` file that reads the port from environment variables:

```python
import os
import sys
from fastmcp import FastMCP

mcp = FastMCP(name="MyDockerizedTool")

@mcp.tool
def my_tool():
    """Your tool implementation"""
    pass

if __name__ == "__main__":
    # Read port from environment variable (set by deploy.py) or command line
    port = None
    if "MCP_PORT" in os.environ:
        port = int(os.environ["MCP_PORT"])
    elif len(sys.argv) > 1:
        port = int(sys.argv[1])
    
    assert port is not None, "Port must be provided"
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path="/mcp")
```

2. Create a `Dockerfile` in the same directory:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy shared.py from project root (context is set to project root in docker-compose.yml)
COPY shared.py /app/shared.py

# Copy the MCP server code from the subdirectory
COPY mcp_host/my_tool /app

# Install Python dependencies
RUN pip install -r /app/requirements.txt

CMD ["python", "server.py"]
```

**Note**: Since the build context is the project root, all COPY paths are relative to the project root.

3. Create a `docker-compose.yml` in the same directory:

```yaml
services:
  app:
    build:
      context: ../..
      dockerfile: mcp_host/my_tool/Dockerfile
    ports:
      - "${MCP_PORT}:${MCP_PORT}"
    environment:
      - MCP_PORT=${MCP_PORT}
    volumes:
      - ../../workspace:/workspace
```

**Important**: The build context must be set to the project root (`../..`) to allow the Dockerfile to access `shared.py` and other project files.

4. Place the folder in `mcp_host/` (e.g., `mcp_host/my_tool/`)

The deployment script will automatically:
- Detect the `docker-compose.yml`
- Assign a port (5000-5099 range for mcp_host)
- Set the `MCP_PORT` environment variable
- Build and start the Docker container
- Skip running `server.py` directly on the host

### Learn More

For detailed documentation on `fastmcp`, visit the [fastmcp GitHub repository](https://github.com/jlowin/fastmcp).
