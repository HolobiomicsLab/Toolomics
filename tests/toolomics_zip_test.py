#!/usr/bin/env python3

"""
Test script for the Zip File Operations MCP Server

This script tests the basic functionality of the zip MCP server.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

try:
    from fastmcp import Client
except ImportError:
    print("❌ FastMCP not installed. Install with: pip install fastmcp")
    sys.exit(1)

async def test_zip_server():
    """Test the zip MCP server functionality."""
    
    print("🧪 Testing Zip File Operations MCP Server")
    print("=" * 50)
    
    # You'll need to get the actual port from: thv list
    # This is just a placeholder - update with the actual port
    port = input("Enter the port number for toolomics-zip server (from 'thv list'): ").strip()
    
    if not port.isdigit():
        print("❌ Invalid port number")
        return
    
    server_url = f"http://localhost:{port}/mcp"
    
    try:
        async with Client(server_url) as client:
            print(f"✅ Connected to zip server at {server_url}")
            
            # Test 1: List available tools
            print("\n📋 Available tools:")
            tools = await client.list_tools()
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Test 2: List ZIP files (should be empty initially)
            print("\n📁 Testing list_zip_files...")
            result = await client.call_tool("list_zip_files", {})
            print(f"Result: {result[0].text}")
            
            # Test 3: Create a ZIP from files (this will fail if no files exist, which is expected)
            print("\n📦 Testing create_zip_from_files...")
            try:
                result = await client.call_tool("create_zip_from_files", {
                    "file_paths": ["test.txt", "example.md"],
                    "zip_name": "test_archive"
                })
                print(f"Result: {result[0].text}")
            except Exception as e:
                print(f"Expected error (no files exist): {e}")
            
            # Test 4: Try to list contents of non-existent ZIP
            print("\n📋 Testing list_zip_contents on non-existent file...")
            try:
                result = await client.call_tool("list_zip_contents", {
                    "zip_name": "nonexistent.zip"
                })
                print(f"Result: {result[0].text}")
            except Exception as e:
                print(f"Expected error: {e}")
            
            print("\n✅ Basic zip server tests completed!")
            print("💡 To test file operations, create some files in the workspace directory first.")
            
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        print("💡 Make sure the toolomics-zip server is running with 'thv list'")

if __name__ == "__main__":
    asyncio.run(test_zip_server())
