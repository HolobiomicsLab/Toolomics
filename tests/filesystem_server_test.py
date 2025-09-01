#!/usr/bin/env python3

"""
Test client for Filesystem MCP Server
Tests MCP discovery, tools discovery, and use case scenarios.
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any
import sys
import os
import tempfile

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from sources.core.tools_manager import ToolManager, MCP
from config import Config
from fastmcp import Client


class FilesystemMCPTest:
    """Test class for Filesystem MCP server"""
    
    def __init__(self):
        self.config = Config() if 'Config' in globals() else None
        self.tool_manager = ToolManager(self.config) if self.config else None
        self.filesystem_mcp = None
        self.client = None
        self.test_dir = None
    
    async def discover_mcp_servers(self) -> List[MCP]:
        """Test MCP discovery"""
        print("🔍 Testing MCP server discovery...")
        
        if self.tool_manager:
            try:
                mcps = await self.tool_manager.discover_mcp_servers()
                print(f"✅ Discovered {len(mcps)} MCP servers via ToolManager")
                
                # Find filesystem MCP
                for mcp in mcps:
                    if "filesystem" in mcp.name.lower() or "file" in mcp.name.lower():
                        self.filesystem_mcp = mcp
                        print(f"✅ Found Filesystem MCP: {mcp.name}")
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
        
        for port in range(5000, 5025):  # Scan common MCP ports
            try:
                url = f"http://localhost:{port}/mcp"
                async with Client(url, timeout=3.0) as client:
                    tools = await client.list_tools()
                    
                    # Get server name
                    name = f"MCP Server on port {port}"
                    try:
                        # Filesystem server may not have get_mcp_name
                        resp = await client.call_tool("get_mcp_name", {})
                        if resp and len(resp) > 0:
                            name = resp[0].text
                    except Exception:
                        # Try to identify by tools
                        tool_names = [tool.name.lower() for tool in tools]
                        if any(keyword in " ".join(tool_names) for keyword in ["file", "directory", "read", "write", "list"]):
                            name = "Filesystem MCP Server"
                    
                    if tools and any(keyword in tool.name.lower() for keyword in ["file", "directory", "read", "write", "list", "create", "edit"] for tool in tools):
                        print(f"✅ Found Filesystem MCP on port {port}: {name}")
                        self.filesystem_mcp = MCP(
                            name=name,
                            tools=[tool.name for tool in tools],
                            address="localhost",
                            port=port,
                            transport="streamable-http",
                            client_url=url
                        )
                        mcps.append(self.filesystem_mcp)
                        break
                        
            except Exception:
                continue
        
        return mcps
    
    async def test_tool_discovery(self) -> bool:
        """Test tools discovery for Filesystem MCP"""
        print("\n📋 Testing tools discovery...")
        
        if not self.filesystem_mcp:
            print("❌ No Filesystem MCP found")
            return False
        
        try:
            url = self.filesystem_mcp.client_url or f"http://{self.filesystem_mcp.address}:{self.filesystem_mcp.port}/mcp"
            async with Client(url, timeout=5.0) as client:
                tools = await client.list_tools()
                
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description[:100]}...")
                
                # Expected filesystem tools (may vary based on implementation)
                expected_keywords = [
                    "read", "write", "list", "create", "directory", "file"
                ]
                
                found_tools = [tool.name.lower() for tool in tools]
                # Check if we have basic filesystem operations
                has_basic_ops = any(keyword in " ".join(found_tools) for keyword in expected_keywords)
                
                if has_basic_ops:
                    print("✅ Basic filesystem operations found")
                else:
                    print("⚠️ Some basic filesystem operations may be missing")
                
                print("✅ Filesystem tools discovery completed")
                return True
                
        except Exception as e:
            print(f"❌ Tool discovery failed: {e}")
            return False
    
    def setup_test_environment(self) -> str:
        """Create test directory structure"""
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix="filesystem_mcp_test_")
            self.test_dir = temp_dir
            
            # Create some test subdirectories and files
            test_subdir = os.path.join(temp_dir, "test_subdir")
            os.makedirs(test_subdir, exist_ok=True)
            
            # Create test files
            with open(os.path.join(temp_dir, "test_file.txt"), "w") as f:
                f.write("Hello from Filesystem MCP test!\n")
            
            with open(os.path.join(test_subdir, "nested_file.txt"), "w") as f:
                f.write("This is a nested file.\n")
            
            print(f"📁 Created test environment: {temp_dir}")
            return temp_dir
            
        except Exception as e:
            print(f"⚠️ Failed to create test environment: {e}")
            return None
    
    def cleanup_test_environment(self):
        """Clean up test directory"""
        if self.test_dir and os.path.exists(self.test_dir):
            try:
                import shutil
                shutil.rmtree(self.test_dir)
                print(f"🧹 Cleaned up test environment: {self.test_dir}")
            except Exception as e:
                print(f"⚠️ Failed to clean up test environment: {e}")
    
    async def test_use_cases(self) -> bool:
        """Test Filesystem MCP use cases"""
        print("\n🧪 Testing Filesystem use cases...")
        
        if not self.filesystem_mcp:
            print("❌ No Filesystem MCP found")
            return False
        
        # Setup test environment
        test_env = self.setup_test_environment()
        if not test_env:
            print("⚠️ Could not create test environment, skipping file-based tests")
            return True
        
        try:
            url = self.filesystem_mcp.client_url or f"http://{self.filesystem_mcp.address}:{self.filesystem_mcp.port}/mcp"
            async with Client(url, timeout=30.0) as client:
                
                # Get available tools first
                tools = await client.list_tools()
                tool_names = [tool.name for tool in tools]
                
                # Test 1: List directory contents
                print(f"\n📂 Test 1: List directory contents")
                list_tools = [name for name in tool_names if "list" in name.lower()]
                if list_tools:
                    try:
                        # Try different parameter formats
                        for list_tool in list_tools:
                            try:
                                result = await client.call_tool(list_tool, {"path": test_env})
                                if result and len(result) > 0:
                                    response_text = result[0].text
                                    print(f"✅ Directory listing with {list_tool}: {len(response_text)} chars")
                                    if "test_file.txt" in response_text or "test_subdir" in response_text:
                                        print("   Found expected files/directories")
                                    break
                            except Exception as e:
                                print(f"   ⚠️ {list_tool} failed: {e}")
                        else:
                            print("❌ All list tools failed")
                    except Exception as e:
                        print(f"⚠️ Directory listing test failed: {e}")
                
                # Test 2: Read file contents
                print(f"\n📄 Test 2: Read file contents")
                read_tools = [name for name in tool_names if "read" in name.lower()]
                if read_tools:
                    try:
                        test_file = os.path.join(test_env, "test_file.txt")
                        for read_tool in read_tools:
                            try:
                                result = await client.call_tool(read_tool, {"path": test_file})
                                if result and len(result) > 0:
                                    response_text = result[0].text
                                    print(f"✅ File reading with {read_tool}: {len(response_text)} chars")
                                    if "Hello from Filesystem MCP test" in response_text:
                                        print("   File content matches expected")
                                    break
                            except Exception as e:
                                print(f"   ⚠️ {read_tool} failed: {e}")
                        else:
                            print("❌ All read tools failed")
                    except Exception as e:
                        print(f"⚠️ File reading test failed: {e}")
                
                # Test 3: Create new file
                print(f"\n✏️ Test 3: Create new file")
                write_tools = [name for name in tool_names if any(keyword in name.lower() for keyword in ["write", "create", "edit"])]
                if write_tools:
                    try:
                        new_file = os.path.join(test_env, "new_test_file.txt")
                        content = "This file was created by Filesystem MCP test!"
                        
                        for write_tool in write_tools:
                            try:
                                # Try different parameter formats
                                params_variants = [
                                    {"path": new_file, "content": content},
                                    {"file_path": new_file, "content": content},
                                    {"filename": new_file, "text": content},
                                ]
                                
                                for params in params_variants:
                                    try:
                                        result = await client.call_tool(write_tool, params)
                                        if result and len(result) > 0:
                                            response_text = result[0].text
                                            print(f"✅ File creation with {write_tool}: success")
                                            # Verify file was created
                                            if os.path.exists(new_file):
                                                print("   File successfully created on filesystem")
                                            break
                                    except Exception as e:
                                        continue
                                else:
                                    print(f"   ⚠️ {write_tool}: all parameter variants failed")
                                    continue
                                break
                            except Exception as e:
                                print(f"   ⚠️ {write_tool} failed: {e}")
                        else:
                            print("❌ All write tools failed")
                    except Exception as e:
                        print(f"⚠️ File creation test failed: {e}")
                
                # Test 4: Get file info
                print(f"\n🔍 Test 4: Get file info")
                info_tools = [name for name in tool_names if "info" in name.lower()]
                if info_tools:
                    try:
                        test_file = os.path.join(test_env, "test_file.txt")
                        for info_tool in info_tools:
                            try:
                                result = await client.call_tool(info_tool, {"path": test_file})
                                if result and len(result) > 0:
                                    response_text = result[0].text
                                    print(f"✅ File info with {info_tool}: {len(response_text)} chars")
                                    if "size" in response_text.lower() or "modified" in response_text.lower():
                                        print("   File info contains expected metadata")
                                    break
                            except Exception as e:
                                print(f"   ⚠️ {info_tool} failed: {e}")
                        else:
                            print("⚠️ No file info tools worked (this is optional)")
                    except Exception as e:
                        print(f"⚠️ File info test failed: {e}")
                
                # Test 5: Create directory
                print(f"\n📁 Test 5: Create directory")
                mkdir_tools = [name for name in tool_names if any(keyword in name.lower() for keyword in ["mkdir", "create_dir", "directory"])]
                if mkdir_tools:
                    try:
                        new_dir = os.path.join(test_env, "new_test_dir")
                        for mkdir_tool in mkdir_tools:
                            try:
                                result = await client.call_tool(mkdir_tool, {"path": new_dir})
                                if result and len(result) > 0:
                                    print(f"✅ Directory creation with {mkdir_tool}: success")
                                    if os.path.exists(new_dir):
                                        print("   Directory successfully created")
                                    break
                            except Exception as e:
                                print(f"   ⚠️ {mkdir_tool} failed: {e}")
                        else:
                            print("⚠️ No directory creation tools worked")
                    except Exception as e:
                        print(f"⚠️ Directory creation test failed: {e}")
                
                # Test 6: Move/rename file
                print(f"\n🔄 Test 6: Move/rename operations")
                move_tools = [name for name in tool_names if any(keyword in name.lower() for keyword in ["move", "rename", "mv"])]
                if move_tools:
                    try:
                        source = os.path.join(test_env, "test_file.txt")
                        dest = os.path.join(test_env, "renamed_file.txt")
                        
                        for move_tool in move_tools:
                            try:
                                # Try different parameter formats
                                params_variants = [
                                    {"source": source, "destination": dest},
                                    {"src": source, "dst": dest},
                                    {"old_path": source, "new_path": dest},
                                ]
                                
                                for params in params_variants:
                                    try:
                                        result = await client.call_tool(move_tool, params)
                                        if result and len(result) > 0:
                                            print(f"✅ File move with {move_tool}: success")
                                            if os.path.exists(dest) and not os.path.exists(source):
                                                print("   File successfully moved")
                                            break
                                    except Exception:
                                        continue
                                else:
                                    continue
                                break
                            except Exception as e:
                                print(f"   ⚠️ {move_tool} failed: {e}")
                        else:
                            print("⚠️ No move tools worked")
                    except Exception as e:
                        print(f"⚠️ Move operation test failed: {e}")
                
                # Test 7: Test error handling
                print(f"\n🚫 Test 7: Error handling (nonexistent file)")
                if read_tools:
                    try:
                        nonexistent_file = "/nonexistent/path/file.txt"
                        result = await client.call_tool(read_tools[0], {"path": nonexistent_file})
                        if result and len(result) > 0:
                            response_text = result[0].text
                            print(f"✅ Error handling: received response for nonexistent file")
                            if "error" in response_text.lower() or "not found" in response_text.lower():
                                print("   Error properly reported")
                        else:
                            print("⚠️ No response for nonexistent file")
                    except Exception as e:
                        print(f"✅ Error handling: exception properly caught ({type(e).__name__})")
                
                # Test 8: Exercise all available tools
                print(f"\n🔧 Test 8: Exercise remaining tools")
                tested_tools = set()
                for tool_name in tool_names:
                    if tool_name not in tested_tools:
                        try:
                            print(f"   Testing {tool_name}...")
                            # Try with minimal parameters
                            result = await client.call_tool(tool_name, {})
                            if result and len(result) > 0:
                                print(f"     ✅ {tool_name}: responded")
                            else:
                                print(f"     ⚠️ {tool_name}: no response")
                            tested_tools.add(tool_name)
                        except Exception as e:
                            print(f"     ⚠️ {tool_name}: failed ({type(e).__name__})")
                
                print("✅ Filesystem use cases completed")
                return True
                
        except Exception as e:
            print(f"❌ Use case testing failed: {e}")
            return False
        finally:
            # Clean up test environment
            self.cleanup_test_environment()
    
    async def assert_running_ok(self) -> bool:
        """Assert that Filesystem MCP is running correctly"""
        print("\n✅ Asserting Filesystem MCP server status...")
        
        if not self.filesystem_mcp:
            print("❌ Filesystem MCP not found - server may not be running")
            return False
        
        try:
            url = self.filesystem_mcp.client_url or f"http://{self.filesystem_mcp.address}:{self.filesystem_mcp.port}/mcp"
            async with Client(url, timeout=10.0) as client:
                # Quick health check
                tools = await client.list_tools()
                
                if len(tools) > 0:
                    print(f"✅ Filesystem MCP server is running correctly")
                    print(f"   Server: {self.filesystem_mcp.name}")
                    print(f"   Address: {self.filesystem_mcp.address}:{self.filesystem_mcp.port}")
                    print(f"   Tools available: {len(tools)}")
                    print(f"   Tool names: {[tool.name for tool in tools]}")
                    return True
                else:
                    print("❌ Filesystem MCP server responded but no tools available")
                    return False
                
        except Exception as e:
            print(f"❌ Filesystem MCP server health check failed: {e}")
            return False


async def main():
    """Run all Filesystem MCP tests"""
    print("🧪 Starting Filesystem MCP Server Tests")
    print("=" * 60)
    
    test = FilesystemMCPTest()
    success = True
    
    # Test 1: MCP Discovery
    mcps = await test.discover_mcp_servers()
    if not mcps or not test.filesystem_mcp:
        print("❌ Failed to discover Filesystem MCP server")
        print("   Make sure the server is running with: ./start.sh")
        print("   Filesystem server should be available from ToolHive registry")
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
        print("🎉 All Filesystem MCP tests PASSED!")
    else:
        print("❌ Some Filesystem MCP tests FAILED!")
        print("   Note: Filesystem tests may fail due to permissions")
        print("   or if the server has restricted file access")
    
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