#!/usr/bin/env python3

"""
Test script to verify that MCP servers execute in the workspace directory
and create files in the centralized location.
"""

import asyncio
import json
import os
import tempfile
import shutil
from pathlib import Path
from fastmcp import Client

async def test_workspace_functionality():
    """Test that MCP servers create files in the workspace directory."""
    
    shell_port = 5102
        
    print("🚀 Testing Shell MCP Server workspace functionality")
    async with Client(f"http://localhost:{shell_port}/mcp") as client:
        
        # Test 1: Create a test file in the workspace
        print("\n" + "=" * 50)
        print("TEST 1: Create a test file")
        print("=" * 50)
        
        test_filename = "workspace_test_file.txt"
        test_content = "This is a test file created by MCP server"
        
        result = await client.call_tool("execute_command", {
            "command": f"echo '{test_content}' > {test_filename}",
        })

        print(f"📋 Command output: {result[0].text}")
        
        # Test 2: Verify the file was created in workspace
        print("\n" + "=" * 50)
        print("TEST 2: Verify file exists in workspace")
        print("=" * 50)
        
        result = await client.call_tool("execute_command", {
            "command": f"ls -la {test_filename}",
        })

        print(f"📋 Command output: {result[0].text}")
        
        # Test 3: Check current working directory
        print("\n" + "=" * 50)
        print("TEST 3: Check current working directory")
        print("=" * 50)
        
        result = await client.call_tool("execute_command", {
            "command": "pwd",
        })

        print(f"📋 Command output: {result[0].text}")


if __name__ == "__main__":
    print("Starting Workspace Functionality Tests")
    print()
    
    asyncio.run(test_workspace_functionality())
