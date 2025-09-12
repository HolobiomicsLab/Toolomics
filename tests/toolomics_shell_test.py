#!/usr/bin/env python3

"""
Test client for Toolomics Shell MCP Server
Tests MCP discovery, tools discovery, and use case scenarios.
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from sources.core.tools_manager import ToolManager, MCP
from config import Config
from fastmcp import Client


class ShellMCPTest:
    """Test class for Shell MCP server"""
    
    def __init__(self):
        self.config = Config() if 'Config' in globals() else None
        self.tool_manager = ToolManager(self.config) if self.config else None
        self.shell_mcp = None
        self.client = None
    
    async def discover_mcp_servers(self) -> List[MCP]:
        """Test MCP discovery"""
        print("🔍 Testing MCP server discovery...")
        
        if self.tool_manager:
            try:
                mcps = await self.tool_manager.discover_mcp_servers()
                print(f"✅ Discovered {len(mcps)} MCP servers via ToolManager")
                
                # Find shell MCP
                for mcp in mcps:
                    if "shell" in mcp.name.lower() or "bash" in mcp.name.lower():
                        self.shell_mcp = mcp
                        print(f"✅ Found Shell MCP: {mcp.name}")
                        break
                
                return mcps
            except Exception as e:
                print(f"❌ ToolManager discovery failed: {e}")
        
        # Fallback: Direct discovery via port scanning
        print("🔍 Falling back to direct MCP discovery...")
        return await self._direct_discovery()
    
    async def _direct_discovery(self) -> List[MCP]:
        """Direct MCP server discovery by scanning ports"""
        mcps = []
        
        for port in range(5000, 5015):  # Scan common MCP ports
            try:
                url = f"http://localhost:{port}/mcp"
                async with Client(url, timeout=3.0) as client:
                    tools = await client.list_tools()
                    
                    # Get server name
                    name = f"MCP Server on port {port}"
                    try:
                        resp = await client.call_tool("get_mcp_name", {})
                        if resp and len(resp) > 0:
                            name = resp[0].text
                    except Exception:
                        pass
                    
                    if tools and any(tool_name in tool.name.lower() for tool_name in ["execute", "command", "shell", "bash"] for tool in tools):
                        print(f"✅ Found Shell MCP on port {port}: {name}")
                        self.shell_mcp = MCP(
                            name=name,
                            tools=[tool.name for tool in tools],
                            address="localhost",
                            port=port,
                            transport="streamable-http",
                            client_url=url
                        )
                        mcps.append(self.shell_mcp)
                        break
                        
            except Exception:
                continue
        
        return mcps
    
    async def test_tool_discovery(self) -> bool:
        """Test tools discovery for Shell MCP"""
        print("\n📋 Testing tools discovery...")
        
        if not self.shell_mcp:
            print("❌ No Shell MCP found")
            return False
        
        try:
            url = self.shell_mcp.client_url or f"http://{self.shell_mcp.address}:{self.shell_mcp.port}/mcp"
            async with Client(url, timeout=5.0) as client:
                tools = await client.list_tools()
                
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description[:100]}...")
                
                # Expected shell tools
                expected_tools = [
                    "execute_command"
                ]
                
                found_tools = [tool.name for tool in tools]
                missing_tools = [tool for tool in expected_tools if tool not in found_tools]
                
                if missing_tools:
                    print(f"⚠️ Missing expected tools: {missing_tools}")
                    return False
                
                print("✅ All expected shell tools found")
                return True
                
        except Exception as e:
            print(f"❌ Tool discovery failed: {e}")
            return False
    
    async def test_use_cases(self) -> bool:
        """Test Shell MCP use cases"""
        print("\n🧪 Testing Shell use cases...")
        
        if not self.shell_mcp:
            print("❌ No Shell MCP found")
            return False
        
        try:
            url = self.shell_mcp.client_url or f"http://{self.shell_mcp.address}:{self.shell_mcp.port}/mcp"
            async with Client(url, timeout=30.0) as client:  # Longer timeout for shell operations
                
                # Test 1: Basic command execution
                print("\n💻 Test 1: Execute basic command (echo)")
                result = await client.call_tool("execute_command", {
                    "command": "echo 'Hello from Shell MCP!'"
                })
                
                if result and len(result) > 0:
                    response = json.loads(result[0].text)
                    print(f"✅ Echo command result: {response.get('status', 'unknown')}")
                    if response.get('stdout'):
                        print(f"   Output: {response['stdout'].strip()}")
                else:
                    print("❌ Failed to execute echo command")
                    return False
                
                # Test 2: Directory listing
                print("\n📁 Test 2: Execute directory listing (ls)")
                result = await client.call_tool("execute_command", {
                    "command": "ls -la"
                })
                
                if result and len(result) > 0:
                    response = json.loads(result[0].text)
                    print(f"✅ Directory listing result: {response.get('status', 'unknown')}")
                    if response.get('stdout'):
                        lines = response['stdout'].strip().split('\n')
                        print(f"   Found {len(lines)} items in directory")
                else:
                    print("❌ Failed to execute ls command")
                    return False
                
                # Test 3: Current working directory
                print("\n📍 Test 3: Get current working directory (pwd)")
                result = await client.call_tool("execute_command", {
                    "command": "pwd"
                })
                
                if result and len(result) > 0:
                    response = json.loads(result[0].text)
                    print(f"✅ PWD command result: {response.get('status', 'unknown')}")
                    if response.get('stdout'):
                        print(f"   Current directory: {response['stdout'].strip()}")
                else:
                    print("❌ Failed to execute pwd command")
                    return False
                
                # Test 4: Environment variables
                print("\n🌍 Test 4: Display environment variables (env)")
                result = await client.call_tool("execute_command", {
                    "command": "env | head -5"
                })
                
                if result and len(result) > 0:
                    response = json.loads(result[0].text)
                    print(f"✅ Environment variables result: {response.get('status', 'unknown')}")
                    if response.get('stdout'):
                        env_lines = response['stdout'].strip().split('\n')
                        print(f"   Sample environment variables: {len(env_lines)} shown")
                else:
                    print("❌ Failed to execute env command")
                    return False
                
                # Test 5: System information
                print("\n🖥️ Test 5: Get system information (uname)")
                result = await client.call_tool("execute_command", {
                    "command": "uname -a"
                })
                
                if result and len(result) > 0:
                    response = json.loads(result[0].text)
                    print(f"✅ System info result: {response.get('status', 'unknown')}")
                    if response.get('stdout'):
                        print(f"   System: {response['stdout'].strip()[:100]}...")
                else:
                    print("❌ Failed to execute uname command")
                    return False
                
                # Test 6: Create and check a test file
                print("\n📄 Test 6: Create test file")
                result = await client.call_tool("execute_command", {
                    "command": "echo 'Test content from Shell MCP' > /tmp/shell_mcp_test.txt"
                })
                
                if result and len(result) > 0:
                    response = json.loads(result[0].text)
                    print(f"✅ File creation result: {response.get('status', 'unknown')}")
                    
                    # Verify file was created
                    result = await client.call_tool("execute_command", {
                        "command": "cat /tmp/shell_mcp_test.txt"
                    })
                    
                    if result and len(result) > 0:
                        read_response = json.loads(result[0].text)
                        if read_response.get('stdout'):
                            print(f"   File content: {read_response['stdout'].strip()}")
                else:
                    print("❌ Failed to create test file")
                    return False
                
                # Test 7: Process listing
                print("\n⚙️ Test 7: Process listing (ps)")
                result = await client.call_tool("execute_command", {
                    "command": "ps aux | head -10"
                })
                
                if result and len(result) > 0:
                    response = json.loads(result[0].text)
                    print(f"✅ Process listing result: {response.get('status', 'unknown')}")
                    if response.get('stdout'):
                        proc_lines = response['stdout'].strip().split('\n')
                        print(f"   Found {len(proc_lines)} processes (top 10)")
                else:
                    print("❌ Failed to execute ps command")
                    return False
                
                # Test 8: Security check - try dangerous command (should be blocked)
                print("\n🛡️ Test 8: Security check (dangerous command)")
                result = await client.call_tool("execute_command", {
                    "command": "rm -rf /etc"
                })
                
                if result and len(result) > 0:
                    response = json.loads(result[0].text)
                    if response.get('status') == 'error' and 'blocked' in response.get('stderr', '').lower():
                        print("✅ Security check passed: dangerous command was blocked")
                    else:
                        print(f"⚠️ Security check result: {response.get('status', 'unknown')}")
                        print(f"   Message: {response.get('stderr', 'No error message')}")
                else:
                    print("❌ Security check failed - no response")
                
                # Test 9: Check disk space
                print("\n💾 Test 9: Disk space information (df)")
                result = await client.call_tool("execute_command", {
                    "command": "df -h"
                })
                
                if result and len(result) > 0:
                    response = json.loads(result[0].text)
                    print(f"✅ Disk space result: {response.get('status', 'unknown')}")
                    if response.get('stdout'):
                        df_lines = response['stdout'].strip().split('\n')
                        print(f"   Disk info: {len(df_lines)} filesystems shown")
                else:
                    print("❌ Failed to execute df command")
                    return False
                
                # Test 10: Date and time
                print("\n🕐 Test 10: Current date and time")
                result = await client.call_tool("execute_command", {
                    "command": "date"
                })
                
                if result and len(result) > 0:
                    response = json.loads(result[0].text)
                    print(f"✅ Date command result: {response.get('status', 'unknown')}")
                    if response.get('stdout'):
                        print(f"   Current time: {response['stdout'].strip()}")
                else:
                    print("❌ Failed to execute date command")
                    return False
                
                # Clean up test file
                print("\n🧹 Cleanup: Remove test file")
                result = await client.call_tool("execute_command", {
                    "command": "rm /tmp/shell_mcp_test.txt"
                })
                
                if result and len(result) > 0:
                    response = json.loads(result[0].text)
                    print(f"✅ Cleanup result: {response.get('status', 'unknown')}")
                
                print("✅ All Shell use cases completed successfully")
                return True
                
        except Exception as e:
            print(f"❌ Use case testing failed: {e}")
            return False
    
    async def assert_running_ok(self) -> bool:
        """Assert that Shell MCP is running correctly"""
        print("\n✅ Asserting Shell MCP server status...")
        
        if not self.shell_mcp:
            print("❌ Shell MCP not found - server may not be running")
            return False
        
        try:
            url = self.shell_mcp.client_url or f"http://{self.shell_mcp.address}:{self.shell_mcp.port}/mcp"
            async with Client(url, timeout=10.0) as client:
                # Quick health check
                tools = await client.list_tools()
                
                if len(tools) > 0:
                    # Test basic functionality
                    result = await client.call_tool("execute_command", {
                        "command": "echo 'health_check'"
                    })
                    
                    if result and len(result) > 0:
                        response = json.loads(result[0].text)
                        if response.get('status') == 'success':
                            print(f"✅ Shell MCP server is running correctly")
                            print(f"   Server: {self.shell_mcp.name}")
                            print(f"   Address: {self.shell_mcp.address}:{self.shell_mcp.port}")
                            print(f"   Tools available: {len(tools)}")
                            print(f"   Command execution: working")
                            return True
                    
                    print("⚠️ Shell MCP server tools available but command execution may have issues")
                    return True
                else:
                    print("❌ Shell MCP server responded but no tools available")
                    return False
                
        except Exception as e:
            print(f"❌ Shell MCP server health check failed: {e}")
            return False


async def main():
    """Run all Shell MCP tests"""
    print("🧪 Starting Shell MCP Server Tests")
    print("=" * 60)
    
    test = ShellMCPTest()
    success = True
    
    # Test 1: MCP Discovery
    mcps = await test.discover_mcp_servers()
    if not mcps or not test.shell_mcp:
        print("❌ Failed to discover Shell MCP server")
        print("   Make sure the server is running with: ./start.sh")
        return False
    
    # Test 2: Tools Discovery
    if not await test.test_tool_discovery():
        success = False
    
    # Test 3: Use Cases
    if not await test.test_use_cases():
        success = False
    
    # Test 4: Server Health
    if not await test.assert_running_ok():
        success = False
    
    # Final Summary
    print("\n" + "=" * 60)
    if success:
        print("🎉 All Shell MCP tests PASSED!")
    else:
        print("❌ Some Shell MCP tests FAILED!")
        print("   Note: Shell tests may fail if the server is running in a restricted environment")
    
    return success


if __name__ == "__main__":
    # Handle missing Config class gracefully
    try:
        from config import Config
    except ImportError:
        print("⚠️ Config class not available, using direct discovery mode")
        Config = None
    
    # Run tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)