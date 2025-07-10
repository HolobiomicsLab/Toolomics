#!/usr/bin/env python3

"""
Test client for Shell MCP Server
Demonstrates all functionality with realistic test scenarios.
"""

import asyncio
import json
from fastmcp import Client

async def test_shell():
    """Test all Shell operations comprehensively."""
    
    shell_port = 5102
    # Connect to the MCP server
    async with Client(f"http://localhost:{shell_port}/mcp") as client:
        print("🚀 Connected to Shell MCP Server")
        
        # List available tools
        tools = await client.list_tools()
        print(f"📋 Available tools: {[tool.name for tool in tools]}")
        print()
        
        # Test 1
        print("=" * 50)
        print("TEST 1: calling ls commands")
        print("=" * 50)
        
        result = await client.call_tool("execute_command", {
            "command": "ls",
        })

        dict_result = json.loads(result[0].text) if result else {}
        print(f"📋 Command output: {dict_result['stdout']}")

        # Test 2
        print("=" * 50)
        print("TEST 2: check file exists")
        print("=" * 50)
        
        result = await client.call_tool("execute_command", {
            "command": "test -e storage/QC_0.mzML",
        })

        dict_result = json.loads(result[0].text) if result else {}
        print(f"📋 Command output: {dict_result['stdout']}")
        


if __name__ == "__main__":
    print("🧪 Starting Shell MCP server.py Tests")
    asyncio.run(test_shell())