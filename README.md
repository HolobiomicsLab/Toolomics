<h1 align="center">Toolomics</h1>

<p align="center">
    <em>Companion platform for MCP server management and workspace-isolated scientific tool execution for Mimosa and other MCP-compatible agents.</em>
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

> ***Toolomics*** exposes computational tools as discoverable MCP services, manages isolated multi-instance workspaces, and lets agents share files across scientific workflows.

Toolomics is the companion MCP server management project described alongside Mimosa in [`main_arxiv.tex`](main_arxiv.tex). In this repository, that means:
- discovering MCP services from `server.py` and `docker-compose.yml` definitions under `mcp_host/`
- assigning ports and recording them in instance-specific `config_<instance_id>.json` files
- isolating workspaces, Docker projects, volumes, and auxiliary services per deployment instance
- making files created by one MCP server immediately available to other MCP servers through a shared workspace

## Quick Start

Run Toolomics against a workspace and a port range:

```bash
./start.sh <min port> <max port> <workspace name>
```

Example:

```bash
./start.sh 5000 5099 workspace_mimosa
```

On first run, Toolomics will:
1. check Python and `pip`
2. optionally install `requirements.txt`
3. create or reuse the requested workspace
4. derive an instance ID from the workspace path
5. create or update `config_<instance_id>.json` with discovered services and assigned ports

Newly discovered services are added with `"enabled": false` by default. Enable the MCP servers you want in the generated config file, then rerun `./start.sh`.

### Manual Deployment

If you prefer to run the deployment script directly:

**1. Install dependencies**
```bash
python3.10 -m pip install -r requirements.txt
# or
uv pip install -r requirements.txt
```

**2. Run the deployment manager**
```bash
python3.10 deploy.py --config config.json --mcp-dir mcp_host --workspace <workspace name> --host_port_min <min port> --host_port_max <max port>
```

Passing `--config config.json` is supported, but `deploy.py` will automatically expand it to an instance-specific file such as `config_86517947.json` based on the workspace path.

## Centralized Workspace

All MCP servers execute against a centralized workspace directory (default: `workspace/`). This means:

- Browser MCP downloads files to the workspace
- PDF MCP processes files already present in the workspace
- Other MCP servers can consume the same files without copying them between tool-specific directories

Example paths:
- `workspace/downloaded_file.pdf`
- `workspace/extracted_text.txt`
- `workspace/output_file.json`

This centralized approach ensures that AI agents can easily find and work with files across different MCP tools without needing to track file locations.

## Multi-Instance Deployment

Toolomics supports running multiple independent instances simultaneously, each with its own workspace and Docker service isolation.

### How It Works

Each instance is automatically assigned a unique **instance ID** (8-character hash) derived from the workspace path. This ID is used to:
- **Isolate Docker containers, volumes, and auxiliary ports** per instance
- **Create instance-specific config files** (`config_${INSTANCE_ID}.json`) to prevent configuration conflicts

This means each instance has its own configuration and doesn't interfere with others.

**Example: deploy two instances concurrently**

```bash
# Terminal 1: Instance for user Martin
./start.sh 5000 5099 workspace_martin

# Terminal 2: Instance for user John (simultaneous)
./start.sh 5100 5199 workspace_john
```

### Automatic Resource Isolation

Each instance automatically gets isolated resources:

| Resource | Isolation Method |
|----------|------------------|
| **Workspace** | Separate directory (`workspace_martin/`, `workspace_john/`) |
| **Docker Containers** | Suffixed with instance ID (`xcmsrocker_a3f2b1c9`, `xcmsrocker_f7e2d4a1`) |
| **Data Volumes** | Instance-specific names (`rstudio_data_a3f2b1c9`, `redis-data_f7e2d4a1`) |
| **MCP Server Ports** | Different port ranges (5000-5099 vs 5100-5199) |
| **Auxiliary Ports** | Dynamic allocation (8787→9537, 8080→9037, etc.) |

This multi-tenant, workspace-isolated design is the same property referenced in the manuscript when Toolomics is described as the companion discovery and execution layer for Mimosa.

## Discovering And Using MCP Services

To interact with the tools using a client such as Mimosa or another MCP-compatible agent, you can use the generated config file directly or scan a predefined local port range.

### Finding the MCP Port

Each MCP server is assigned a port, which is recorded in the instance-specific config file. For example:

```json
[
  {
    "path": "mcp_host/pdf/server.py",
    "port": 5002,
    "enabled": true
  },
  {
    "path": "mcp_host/image_analysis/server.py",
    "port": 5006,
    "enabled": true
  },
  {
    "path": "mcp_host/shell/docker-compose.yml",
    "port": 5012,
    "enabled": true
  }
]
```

### Scanning A Predefined Port Range

Toolomics includes a helper script that scans `localhost:5000-5200` and enumerates active MCP tools:

```bash
python3 discover_mcp.py
```

This mirrors the local port-range discovery pattern described in the manuscript for Mimosa's tool discovery layer.

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

## Adding A New MCP

You can easily add a new tool as an MCP server.

### Steps to Add a New MCP

1. Create a `server.py` file with your MCP implementation. It should accept the assigned port as either an environment variable or the first command-line argument.
2. Place the file in a subfolder of `mcp_host/`, for example `mcp_host/your_tool_name/server.py`.
3. Run `./start.sh` or `deploy.py` to let Toolomics discover the service and assign it a port.
4. Set `"enabled": true` for the new service in the generated `config_<instance_id>.json`, then rerun deployment.

### Example MCP Implementation

The `fastmcp` library simplifies the creation of MCP servers. Here's a basic example:

```python
#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from fastmcp import FastMCP

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from shared import CommandResult, run_bash_subprocess, return_as_dict

description = "A calculator MCP."

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

## Dockerizing an MCP Server

For MCP servers that require isolated dependencies or need to run in a containerized environment, you can deploy them with Docker. This is one of the main ways Toolomics keeps tool dependencies isolated across concurrent scientific workflows.

### How It Works

If a `docker-compose.yml` file exists in the same directory as your `server.py`, the deployment script will:
- **Automatically deploy the server in Docker** instead of running it directly on the host
- **Skip the standalone Python execution** to avoid duplicate deployments
- **Pass the assigned port** to the Docker container via the `MCP_PORT` environment variable
- **Pass instance isolation metadata** such as `INSTANCE_ID` and `WORKSPACE_PATH` to the container

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
      - INSTANCE_ID=${INSTANCE_ID}
    volumes:
      - ../../${WORKSPACE_PATH}:/app/workspace:rw
```

**Important**: The build context must be set to the project root (`../..`) to allow the Dockerfile to access `shared.py` and other project files.

4. Place the folder in `mcp_host/` (e.g., `mcp_host/my_tool/`)

The deployment script will automatically:
- Detect the `docker-compose.yml`
- Assign a port in the selected host range
- Set the `MCP_PORT` environment variable
- Set `INSTANCE_ID` and `WORKSPACE_PATH`
- Build and start the Docker container
- Skip running `server.py` directly on the host

### Learn More

For detailed documentation on `fastmcp`, visit the [fastmcp GitHub repository](https://github.com/jlowin/fastmcp).

## License

Toolomics is distributed under the Apache License 2.0. See [LICENSE](LICENSE), [NOTICE.txt](NOTICE.txt), [`docs/licensing-notes.md`](docs/licensing-notes.md), and [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) for the repository licensing and contribution terms.
