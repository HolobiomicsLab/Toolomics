# Adding a New MCP Server to Toolomics

A simple guide to create and integrate a new MCP server.

## Prerequisites

- **ToolHive** installed: `curl -sSL https://get.toolhive.dev | sh`
- **Docker** running
- **Python 3.10**
- Basic understanding of **FastMCP**

## Key Architecture Points

All MCP servers in Toolomics:
- Live in `mcp_host/your_tool_name/` 
- Run in Docker containers via ToolHive
- Share files through `/projects` directory (mounted from host `workspace/`)
- Use `shared.py` utilities for consistent responses
- Are registered in `registry.json`

## Step 1: Create Directory and Server File

```bash
mkdir -p mcp_host/your_tool_name
```

Create `mcp_host/your_tool_name/server.py` with this template:

```python
#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from typing import Dict, Any
from fastmcp import FastMCP

# Import shared utilities
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from shared import CommandResult, return_as_dict, get_workspace_path

# Initialize server
mcp = FastMCP(name="Your Tool Name MCP", instructions="Brief description of what your tool does")

@mcp.tool
@return_as_dict
def your_main_tool(input_param: str) -> Dict[str, Any]:
    """Main tool function - describe what it does here."""
    try:
        # IMPORTANT: Always use get_workspace_path() for file operations
        workspace_path = get_workspace_path()
        output_file = workspace_path / "output.txt"
        
        # Create directories if needed
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Your processing logic
        result = f"Processed: {input_param}"
        output_file.write_text(result)
        
        return CommandResult(
            status="success",
            stdout=f"Successfully processed {input_param}",
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
def list_files() -> Dict[str, Any]:
    """List files in workspace."""
    try:
        files = [f.name for f in get_workspace_path().iterdir() if f.is_file()]
        return CommandResult(
            status="success",
            stdout=f"Files: {', '.join(files) if files else 'No files'}",
            exit_code=0
        )
    except Exception as e:
        return CommandResult(status="error", stderr=str(e), exit_code=1)

if __name__ == "__main__":
    port = int(os.environ.get("MCP_PORT", sys.argv[1]))
    mcp.run(transport="streamable-http", port=port, host="0.0.0.0")
```

## Step 2: Add to Registry Update Script

**NEW AUTOMATED PROCESS:** Add your server to the `TOOLOMICS_SERVERS` configuration in `registry/update_registry.py`:

```python
"toolomics-your-tool": {
    "path": "your_tool_name/server.py",
    "description": "Brief description of what your tool does",
    "image": "holobiomicslab/toolomics:local",
    "args": ["python", "/app/mcp_host/your_tool_name/server.py"],
    "tags": ["toolomics", "your-domain", "your-keywords"]
}
```

**Naming Convention:**
- Registry name: `toolomics-your-tool` (kebab-case)
- Directory: `your_tool_name` (snake_case)
- Path: `your_tool_name/server.py` (matches directory structure)

## Step 3: Run Registry Update

**AUTOMATIC REGISTRY & START.SH UPDATE:**
```bash
python registry/update_registry.py
```

This script automatically:
- ✅ **Creates backup** of current registry.json (keeps latest 5)
- ✅ **Extracts actual tool names** from your server.py using advanced regex
- ✅ **Updates registry.json** with your server and detected tools
- ✅ **Updates start.sh SERVERS array** with your new server
- ✅ **Syncs official MCP servers** list as commented options
- ✅ **Preserves active servers** like playwright, plotting, filesystem, git

**No more manual editing of registry.json or start.sh!**

## Step 4: Deploy and Test

1. **Deploy:**
```bash
./start.sh --rebuild
```

2. **Check if running:**
```bash
thv list | grep your-tool
```

3. **Test with the test runner:**
```bash
python tests/run_all_mcp_tests.py --server your-tool
```

Or create a simple test in `tests/toolomics_your_tool_test.py`:

```python
import asyncio
from fastmcp import Client

async def test_your_tool():
    # Get port from: thv list 
    async with Client("http://localhost:PORT/mcp") as client:
        result = await client.call_tool("your_main_tool", {"input_param": "test"})
        print(f"Result: {result[0].text}")

asyncio.run(test_your_tool())
```

## Important File Operations Rule

**⚠️ CRITICAL:** Always use `get_workspace_path()` for file operations

```python
# ✅ Correct - files appear in host workspace/ folder
workspace = get_workspace_path()  # Uses /projects in container, falls back to cwd
output_file = workspace / "data" / "output.csv"
output_file.parent.mkdir(parents=True, exist_ok=True)  # Create dirs if needed
output_file.write_text("your data")

# ❌ Wrong - files get lost in container or inconsistent behavior
output_file = Path("./output.csv")     # Don't use relative paths
workspace = Path("/workspace")         # Wrong mount path
workspace = Path("/projects")          # Hardcoded without fallback
workspace = Path.cwd()                 # No container awareness
```

This ensures:
- Files appear in your host `workspace/` folder
- Other MCP servers can access the files  
- Proper cross-tool compatibility
- Development environment compatibility (falls back to current directory)

## Troubleshooting

**Server not starting?**
```bash
thv logs toolomics-your-tool  # Check logs
python -m json.tool registry.json  # Validate JSON syntax
```

**Import errors?**
Make sure the project root path is added correctly in your server.py.

**Files not appearing in workspace/?**
Double-check you're using `get_workspace_path()` not hardcoded paths, relative paths, or `/workspace`.

---

**That's it!** Your MCP server should now be working and files should appear in your `workspace/` folder. 🎉