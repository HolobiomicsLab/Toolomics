
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

### Deploy all tools automatically

```bash
./start.sh
```

### Deploy Tools on Docker

```bash
docker build -t toolomics .
docker run -it -p 5100-5200:5100-5200 toolomics
```

By default we use port 5100 to 5200 for MCPs running **in docker**.

### Deploy Tools on Host

To deploy all tools, use the following command:

```bash
python3.10 deploy.py --config <config path>
```

By default we use port 5000 to 5100 for MCPs running **on host**.

For example : 

```bash
python3.10 deploy.py --config config.json 
```

## Using MCP with Your Client

To interact with the tools using a client (e.g., for your AI agent), you can use the `fastmcp` library.

### Finding the MCP Port

Each MCP server is assigned a port, which is recorded in the `config.json` file. For example:

```json
[
    {
        "mcp_host/instruments/server.py": 5000
    },
    {
        "mcp_host/files/csv/server.py": 5001
    },
    {
        "mcp_host/computer_use/browser/server.py": 5002
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

1. Create a `server.py` file with your MCP implementation, it should take the port number as first argument (eg: `server.py 5003`).
2. Place the file in a subfolder of the `mcp_servers` directory. For example, to add a metabolomics-related tool, create a subfolder like `mcp_servers/metabolomics/your_tool_name_folder`.

The `deploy.py` script will look for new `server.py` file, attribute a port for your script and add it to `config.json` (unless you manually did by modifying the config.json), finally it will run your script with the assigned port as first argument.

### Example MCP Implementation

The `fastmcp` library simplifies the creation of MCP servers. Here's a basic example:

```python
from fastmcp import FastMCP

mcp = FastMCP(name="Calculator")

@mcp.tool
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers."""
    return a * b

port = -1
if len(sys.argv) > 1 and sys.argv[1].isdigit():
    port = int(sys.argv[1])
assert port > 0, "You must pass the port as an argument to the script."
mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path="/mcp")
```

### Automatic Port Assignment

When you run the `deploy.py` script for the first time, it will automatically assign a port to your new MCP server and save the mapping in the `config.json` file.

### Learn More

For detailed documentation on `fastmcp`, visit the [fastmcp GitHub repository](https://github.com/jlowin/fastmcp).
