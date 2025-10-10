#!/usr/bin/env python3

"""
Test client for Shell MCP Server
Demonstrates all functionality with realistic test scenarios.
"""

import asyncio
import sys
import json
from fastmcp import Client

async def test_shell(shell_port: int = 5002):
    """Test all Shell operations comprehensively."""
    
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

        dict_result = json.loads(result.content[0].text) if result else {}
        print(f"📋 Command output: {dict_result}")

        # Test 2
        print("=" * 50)
        print("TEST 2: check file exists")
        print("=" * 50)
        
        result = await client.call_tool("execute_command", {
            "command": "test -e , workspace/QC_0.mzML",
        })

        dict_result = json.loads(result.content[0].text) if result else {}
        print(f"📋 Command output: {dict_result}")

        # Test 3
        print("=" * 50)
        print("TEST 3: try remove file")
        print("=" * 50)
        
        result = await client.call_tool("execute_command", {
            "command": "rm -f workspace/QC_0_adducts.csv",
        })

        dict_result = json.loads(result.content[0].text) if result else {}
        print(f"📋 Command output: {dict_result}")
        

def help():
    print("USAGE")
    print(f"\t{sys.argv[0]} <port>")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        help()
        exit()
    print("🧪 Starting Shell MCP server.py Tests")
    port = sys.argv[1]
    asyncio.run(test_shell(port))