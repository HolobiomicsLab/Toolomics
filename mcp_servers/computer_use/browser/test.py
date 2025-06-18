
#!/usr/bin/env python3

"""
Test client for Browser MCP Server
"""

import asyncio
import json
from pathlib import Path
from fastmcp import Client

async def test_browser_operations():
    """Test browser comprehensively."""
    # Connect to the MCP server
    async with Client("http://localhost:5003/mcp") as client:
        print("🚀 Connected to Browser MCP Server")
        # List available tools
        tools = await client.list_tools()
        print(f"📋 Available tools: {[tool.name for tool in tools]}")
        print()
    
        print("Test initializing browser")
        result = await client.call_tool("browser_init")
        print(f"🔧 Browser initialized: {result[0]}")

        print("Test opening a URL")
        result = await client.call_tool("navigate", {"url": "www.google.com"})
        print(f"🌐 Navigated to URL: {result[0]}")

if __name__ == "__main__":
    print("🧪 Starting Browser MCP server.py Tests")
    asyncio.run(test_browser_operations())