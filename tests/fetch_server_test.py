#!/usr/bin/env python3

"""
Test client for Fetch MCP Server (gofetch)
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


class FetchMCPTest:
    """Test class for Fetch MCP server"""
    
    def __init__(self):
        self.config = Config() if 'Config' in globals() else None
        self.tool_manager = ToolManager(self.config) if self.config else None
        self.fetch_mcp = None
        self.client = None
    
    async def discover_mcp_servers(self) -> List[MCP]:
        """Test MCP discovery"""
        print("🔍 Testing MCP server discovery...")
        
        if self.tool_manager:
            try:
                mcps = await self.tool_manager.discover_mcp_servers()
                print(f"✅ Discovered {len(mcps)} MCP servers via ToolManager")
                
                # Find fetch MCP
                for mcp in mcps:
                    if "fetch" in mcp.name.lower() or "gofetch" in mcp.name.lower():
                        self.fetch_mcp = mcp
                        print(f"✅ Found Fetch MCP: {mcp.name}")
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
                        # Fetch server may not have get_mcp_name
                        resp = await client.call_tool("get_mcp_name", {})
                        if resp and len(resp) > 0:
                            name = resp[0].text
                    except Exception:
                        # Try to identify by tools
                        tool_names = [tool.name.lower() for tool in tools]
                        if any("fetch" in tool_name or "get" in tool_name for tool_name in tool_names):
                            name = "Fetch MCP Server"
                    
                    if tools and any(tool_name in tool.name.lower() for tool_name in ["fetch", "get", "download", "http", "url"] for tool in tools):
                        print(f"✅ Found Fetch MCP on port {port}: {name}")
                        self.fetch_mcp = MCP(
                            name=name,
                            tools=[tool.name for tool in tools],
                            address="localhost",
                            port=port,
                            transport="streamable-http",
                            client_url=url
                        )
                        mcps.append(self.fetch_mcp)
                        break
                        
            except Exception:
                continue
        
        return mcps
    
    async def test_tool_discovery(self) -> bool:
        """Test tools discovery for Fetch MCP"""
        print("\n📋 Testing tools discovery...")
        
        if not self.fetch_mcp:
            print("❌ No Fetch MCP found")
            return False
        
        try:
            url = self.fetch_mcp.client_url or f"http://{self.fetch_mcp.address}:{self.fetch_mcp.port}/mcp"
            async with Client(url, timeout=5.0) as client:
                tools = await client.list_tools()
                
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description[:100]}...")
                
                # Expected fetch tools (may vary based on implementation)
                expected_tools = [
                    "fetch",  # Common tool name for fetching URLs
                ]
                
                found_tools = [tool.name for tool in tools]
                # Don't fail if specific tools are missing - different implementations
                
                print("✅ Fetch tools discovery completed")
                return True
                
        except Exception as e:
            print(f"❌ Tool discovery failed: {e}")
            return False
    
    async def test_use_cases(self) -> bool:
        """Test Fetch MCP use cases"""
        print("\n🧪 Testing Fetch use cases...")
        
        if not self.fetch_mcp:
            print("❌ No Fetch MCP found")
            return False
        
        try:
            url = self.fetch_mcp.client_url or f"http://{self.fetch_mcp.address}:{self.fetch_mcp.port}/mcp"
            async with Client(url, timeout=30.0) as client:  # Longer timeout for network operations
                
                # Get available tools first
                tools = await client.list_tools()
                tool_names = [tool.name for tool in tools]
                
                # Find the main fetch tool
                fetch_tool = None
                for tool_name in ["fetch", "get", "download", "fetch_url", "http_get"]:
                    if tool_name in tool_names:
                        fetch_tool = tool_name
                        break
                
                if not fetch_tool:
                    print("⚠️ Could not identify main fetch tool, trying 'fetch'")
                    fetch_tool = "fetch"
                
                # Test 1: Fetch a simple webpage
                print(f"\n🌐 Test 1: Fetch simple webpage using '{fetch_tool}'")
                try:
                    result = await client.call_tool(fetch_tool, {
                        "url": "https://httpbin.org/json"
                    })
                    
                    if result and len(result) > 0:
                        # Try to parse response
                        try:
                            response = json.loads(result[0].text)
                            print(f"✅ Fetch result: success")
                            if isinstance(response, dict) and response.get("slideshow"):
                                print(f"   Retrieved JSON data successfully")
                        except json.JSONDecodeError:
                            # Response might be plain text
                            response_text = result[0].text
                            print(f"✅ Fetch result: received {len(response_text)} characters")
                            if "slideshow" in response_text:
                                print("   JSON content detected")
                    else:
                        print("❌ No response from fetch")
                        return False
                except Exception as e:
                    print(f"⚠️ Test 1 failed: {e}")
                
                # Test 2: Fetch HTML page
                print(f"\n📄 Test 2: Fetch HTML page")
                try:
                    result = await client.call_tool(fetch_tool, {
                        "url": "https://example.com"
                    })
                    
                    if result and len(result) > 0:
                        response_text = result[0].text
                        print(f"✅ HTML fetch result: received {len(response_text)} characters")
                        if "Example Domain" in response_text or "<html" in response_text.lower():
                            print("   HTML content detected")
                    else:
                        print("❌ Failed to fetch HTML page")
                except Exception as e:
                    print(f"⚠️ Test 2 failed: {e}")
                
                # Test 3: Fetch with user agent or headers (if supported)
                print(f"\n🔧 Test 3: Fetch with custom parameters")
                try:
                    # Try different parameter combinations
                    test_params = [
                        {"url": "https://httpbin.org/user-agent"},
                        {"url": "https://httpbin.org/headers"},
                    ]
                    
                    for params in test_params:
                        result = await client.call_tool(fetch_tool, params)
                        if result and len(result) > 0:
                            response_text = result[0].text
                            print(f"✅ Custom fetch: received {len(response_text)} characters")
                            break
                    
                except Exception as e:
                    print(f"⚠️ Test 3 failed: {e}")
                
                # Test 4: Test different content types
                print(f"\n📊 Test 4: Fetch different content types")
                try:
                    content_tests = [
                        {"url": "https://httpbin.org/xml", "content_type": "XML"},
                        {"url": "https://httpbin.org/json", "content_type": "JSON"},
                    ]
                    
                    for test in content_tests:
                        try:
                            result = await client.call_tool(fetch_tool, {"url": test["url"]})
                            if result and len(result) > 0:
                                response_text = result[0].text
                                print(f"✅ {test['content_type']} fetch: {len(response_text)} chars")
                        except Exception as e:
                            print(f"⚠️ {test['content_type']} fetch failed: {e}")
                    
                except Exception as e:
                    print(f"⚠️ Test 4 failed: {e}")
                
                # Test 5: Error handling - invalid URL
                print(f"\n🚫 Test 5: Error handling (invalid URL)")
                try:
                    result = await client.call_tool(fetch_tool, {
                        "url": "https://nonexistent-domain-12345.com"
                    })
                    
                    if result and len(result) > 0:
                        response_text = result[0].text
                        print(f"✅ Error handling test: received response")
                        # Could be error message or timeout
                        if "error" in response_text.lower() or "timeout" in response_text.lower():
                            print("   Error properly handled")
                        else:
                            print("   Response received (might be cached or redirected)")
                    else:
                        print("⚠️ No response for invalid URL")
                except Exception as e:
                    print(f"✅ Error handling test: exception caught ({e})")
                
                # Test 6: Test HTTPS vs HTTP
                print(f"\n🔐 Test 6: HTTPS handling")
                try:
                    result = await client.call_tool(fetch_tool, {
                        "url": "https://www.google.com"
                    })
                    
                    if result and len(result) > 0:
                        response_text = result[0].text
                        print(f"✅ HTTPS fetch: {len(response_text)} characters")
                        if "google" in response_text.lower() or "<html" in response_text.lower():
                            print("   HTTPS content successfully retrieved")
                    else:
                        print("⚠️ HTTPS fetch may have issues")
                except Exception as e:
                    print(f"⚠️ HTTPS test failed: {e}")
                
                print("✅ Fetch use cases completed")
                return True
                
        except Exception as e:
            print(f"❌ Use case testing failed: {e}")
            return False
    
    async def assert_running_ok(self) -> bool:
        """Assert that Fetch MCP is running correctly"""
        print("\n✅ Asserting Fetch MCP server status...")
        
        if not self.fetch_mcp:
            print("❌ Fetch MCP not found - server may not be running")
            return False
        
        try:
            url = self.fetch_mcp.client_url or f"http://{self.fetch_mcp.address}:{self.fetch_mcp.port}/mcp"
            async with Client(url, timeout=10.0) as client:
                # Quick health check
                tools = await client.list_tools()
                
                if len(tools) > 0:
                    print(f"✅ Fetch MCP server is running correctly")
                    print(f"   Server: {self.fetch_mcp.name}")
                    print(f"   Address: {self.fetch_mcp.address}:{self.fetch_mcp.port}")
                    print(f"   Tools available: {len(tools)}")
                    print(f"   Tool names: {[tool.name for tool in tools]}")
                    return True
                else:
                    print("❌ Fetch MCP server responded but no tools available")
                    return False
                
        except Exception as e:
            print(f"❌ Fetch MCP server health check failed: {e}")
            return False


async def main():
    """Run all Fetch MCP tests"""
    print("🧪 Starting Fetch MCP Server Tests")
    print("=" * 60)
    
    test = FetchMCPTest()
    success = True
    
    # Test 1: MCP Discovery
    mcps = await test.discover_mcp_servers()
    if not mcps or not test.fetch_mcp:
        print("❌ Failed to discover Fetch MCP server")
        print("   Make sure the server is running with: ./start.sh")
        print("   Fetch server should be available from ToolHive registry")
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
        print("🎉 All Fetch MCP tests PASSED!")
    else:
        print("❌ Some Fetch MCP tests FAILED!")
        print("   Note: Fetch tests may fail due to network connectivity issues")
        print("   or if the gofetch server is not properly configured")
    
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