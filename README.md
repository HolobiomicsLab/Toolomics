
# Toolomics

*A suite of tools from the Holobiomics Lab for Agents, organized as a set of MCP servers.*

## Installation

To install the required dependencies, run:

```bash
python3.10 -m pip install -r requirements.txt
```

## Deploying Tools

### Deploy All Tools

To deploy all tools, use the following command:

```bash
python3.10 deploy.py <config path>
```

For example : 

```bash
python3.10 deploy.py config_host.json 
```

### Deploy Specific Tools

To deploy tools within a specific subfolder of the `mcp_servers` directory, pass the subfolder name as an argument:

```bash
python3.10 deploy.py metabolomics
```

For example, the above command will start all MCP servers within the `metabolomics` subfolder.

## Using MCP with Your Client

To interact with the tools using a client (e.g., for your AI agent), you can use the `fastmcp` library.

### Finding the MCP Port

Each MCP server is assigned a port, which is recorded in the `ports_config.json` file. For example:

```json
[
    {
        "mcp_servers/instruments/server.py": 5000
    },
    {
        "mcp_servers/files/csv/server.py": 5001
    },
    {
        "mcp_servers/computer_use/browser/server.py": 5002
    }
]
```

### Example Client Code

Here is an example of how to use a client to interact with an MCP server running on port `5006`:

```python
from fastmcp import Client

async def main():
    # Connect to the MCP server
    port = 5006
    async with Client(f"http://localhost:{port}/mcp") as client:
        tools = await client.list_tools()
        print(f"Available tools: {tools}")
        result = await client.call_tool("add", {"a": 5, "b": 3})
        print(f"Result: {result.text}")
```

## Adding a New MCP

You can easily add a new tool as an MCP server.

### Steps to Add a New MCP

1. Create a `server.py` file with your MCP implementation.
2. Place the file in a subfolder of the `mcp_servers` directory. For example, to add a metabolomics-related tool, create a subfolder like `mcp_servers/metabolomics/your_tool_name_folder`.

### Example MCP Implementation

The `fastmcp` library simplifies the creation of MCP servers. Here's a basic example:

```python
from fastmcp import FastMCP

# Create a server instance
mcp = FastMCP(name="MyAssistantServer")

@mcp.tool
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers."""
    return a * b
```

### Automatic Port Assignment

When you run the `deploy.py` script for the first time, it will automatically assign a port to your new MCP server and save the mapping in the `ports_config.json` file.

### Learn More

For detailed documentation on `fastmcp`, visit the [fastmcp GitHub repository](https://github.com/jlowin/fastmcp).

