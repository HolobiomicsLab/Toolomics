# Adding a New MCP Server to Toolomics

This guide explains how to create and integrate a new MCP server into the Toolomics project running on ToolHive.

## Overview

After the ToolHive migration, all MCP servers:
- Run in isolated Docker containers
- Use `stdio` transport (proxied to SSE by ToolHive)
- Are automatically discovered by Mimosa-AI
- Have dynamic port allocation

## Step-by-Step Process

### 1. Create the Server Directory

Choose the appropriate location based on your server type:

**For host-based servers (most common):**
```bash
mkdir -p mcp_host/your-server-name
cd mcp_host/your-server-name
```

**For Docker-based servers (special cases):**
```bash
mkdir -p mcp_docker/your-server-name
cd mcp_docker/your-server-name
```

### 2. Create the Server File

Create `server.py` with the required structure:

```python
#!/usr/bin/env python3

"""
Your Server Name MCP Server

Provides tools for [describe functionality].
"""

from fastmcp import FastMCP
from typing import Any, Dict, List
import sys
from pathlib import Path

# Add project root to path for shared imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from shared import return_as_dict, run_bash_subprocess, CommandResult

description = """
Your server description here.
Explain what this server does and what tools it provides.
"""

mcp = FastMCP(
    name="Your Server Name MCP",
    instructions=description,
)

@mcp.tool
def get_mcp_name() -> str:
    """Required: Get the name of this MCP server"""
    return "Your Server Name MCP"

@mcp.tool
def your_tool_function(parameter: str) -> Dict[str, Any]:
    """
    Description of what this tool does.
    
    Args:
        parameter: Description of the parameter
        
    Returns:
        Dict containing the result
    """
    try:
        # Your tool implementation here
        result = {"status": "success", "data": f"Processed: {parameter}"}
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Add more @mcp.tool functions as needed

# Required: Use stdio transport for ToolHive compatibility
print("Starting Your Server Name MCP server with stdio transport...")
mcp.run(transport="stdio")
```

### 3. Add Dependencies

If your server needs additional Python packages:

1. **Add to requirements.txt:**
```bash
echo "your-package-name>=1.0.0" >> requirements.txt
```

2. **Import in your server:**
```python
try:
    import your_package
    YOUR_PACKAGE_AVAILABLE = True
except ImportError:
    YOUR_PACKAGE_AVAILABLE = False
    print("Warning: your-package not available. Some features may not work.")
```

### 4. Update the ToolHive Registry

Add your server to `registry.json`:

```json
{
  "servers": {
    "toolomics-your-server": {
      "description": "Brief description of your server",
      "image": "holobiomicslab/toolomics:latest",
      "args": ["python", "/app/mcp_host/your-server-name/server.py"],
      "env_vars": [
        {
          "name": "MCP_SERVER_TYPE",
          "value": "your-server-type"
        }
      ]
    },
    // ... existing servers
  }
}
```

### 5. Update Start Script (Optional)

If you want your server to start automatically, add it to `start-toolhive.sh`:

```bash
SERVERS=(
    "toolomics-rscript"
    "toolomics-browser"
    "toolomics-csv"
    "toolomics-search"  
    "toolomics-pdf"
    "toolomics-shell-docker"
    "toolomics-your-server"  # Add your server here
)
```

### 6. Test Your Server

1. **Build and start with your server:**
```bash
./start-toolhive.sh --rebuild
```

2. **Verify it's running:**
```bash
thv list
```

3. **Test discovery with Mimosa-AI:**
```bash
cd /path/to/Mimosa-AI
uv run python -c "
import asyncio
from sources.core.tools_manager import ToolManager
from config import Config

async def test():
    config = Config()
    tool_manager = ToolManager(config)
    mcps = await tool_manager.discover_mcp_servers()
    for mcp in mcps:
        if 'your-server' in mcp.toolhive_name:
            print(f'✅ Found: {mcp.name}')
            print(f'   Tools: {mcp.tools}')

asyncio.run(test())
"
```

4. **Check server logs:**
```bash
thv logs toolomics-your-server
```

### 7. Testing Individual Tools

You can test individual tools using the ToolHive CLI:

```bash
# Test basic connectivity
curl -X POST http://127.0.0.1:PORT/messages \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

## File Structure Example

After following this guide, your structure should look like:

```
toolomics/
├── mcp_host/
│   ├── your-server-name/
│   │   └── server.py          # Your new server
│   ├── browser/
│   ├── csv/
│   └── ...
├── registry.json              # Updated with your server
├── start-toolhive.sh          # Optionally updated
├── requirements.txt           # Updated if needed
└── ...
```

## Best Practices

### Tool Design
- **Always include `get_mcp_name()` tool** - required for identification
- **Use descriptive tool names** - avoid generic names like `process()` or `run()`
- **Provide clear documentation** - include docstrings with Args and Returns
- **Handle errors gracefully** - return error status rather than throwing exceptions
- **Use type hints** - helps with MCP protocol schema generation

### Server Configuration
- **Use `stdio` transport only** - required for ToolHive compatibility
- **Don't hardcode ports** - ToolHive handles port management
- **Include server description** - helps users understand functionality
- **Use environment variables** for configuration when needed

### Testing
- **Test in isolation first** - make sure your server.py runs standalone
- **Test via ToolHive** - ensure it works in the containerized environment
- **Test discovery** - verify Mimosa-AI can find and connect to your server
- **Test all tools** - ensure every @mcp.tool function works correctly

### Integration
- **Follow naming conventions** - use `toolomics-` prefix in registry
- **Update documentation** - add your server to relevant docs
- **Consider dependencies** - minimize external package requirements when possible
- **Test with existing servers** - ensure no conflicts with other servers

## Troubleshooting

### Server Won't Start
1. Check server logs: `thv logs toolomics-your-server`
2. Verify Python syntax: `python mcp_host/your-server-name/server.py`
3. Check imports: ensure all required packages are available
4. Verify registry.json syntax: use `jq . registry.json` to validate

### Server Not Discovered
1. Ensure server is running: `thv list`
2. Check registry entry syntax
3. Verify the server is accessible: test the `/sse` endpoint
4. Check Mimosa-AI discovery: run the test script above

### Tool Errors
1. Check tool function signatures match MCP requirements
2. Verify return types are JSON-serializable
3. Test error handling with invalid inputs
4. Check server logs for Python exceptions

## Example: Simple Echo Server

Here's a complete example of a minimal MCP server:

```python
#!/usr/bin/env python3
"""
Echo MCP Server - Simple example server
"""

from fastmcp import FastMCP
from typing import Any, Dict

description = """
Echo MCP Server provides a simple echo tool for testing.
"""

mcp = FastMCP(
    name="Echo MCP",
    instructions=description,
)

@mcp.tool
def get_mcp_name() -> str:
    return "Echo MCP"

@mcp.tool  
def echo(message: str) -> Dict[str, Any]:
    """Echo back the input message.
    
    Args:
        message: The message to echo back
        
    Returns:
        Dict containing the echoed message
    """
    return {
        "status": "success",
        "echo": message,
        "length": len(message)
    }

print("Starting Echo MCP server with stdio transport...")
mcp.run(transport="stdio")
```

Registry entry for echo server:
```json
"toolomics-echo": {
  "description": "Simple echo server for testing",
  "image": "holobiomicslab/toolomics:latest",
  "args": ["python", "/app/mcp_host/echo/server.py"],
  "env_vars": [
    {
      "name": "MCP_SERVER_TYPE",
      "value": "echo"
    }
  ]
}
```

This creates a fully functional MCP server that will be automatically discovered by Mimosa-AI and accessible via ToolHive.