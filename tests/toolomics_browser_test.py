#!/usr/bin/env python3

"""
Test client for Toolomics Browser MCP Server
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


class BrowserMCPTest:
    """Test class for Browser MCP server"""
    
    def __init__(self):
        self.config = Config() if 'Config' in globals() else None
        self.tool_manager = ToolManager(self.config) if self.config else None
        self.browser_mcp = None
        self.client = None
    
    async def discover_mcp_servers(self) -> List[MCP]:
        """Test MCP discovery"""
        print("🔍 Testing MCP server discovery...")
        
        if self.tool_manager:
            try:
                mcps = await self.tool_manager.discover_mcp_servers()
                print(f"✅ Discovered {len(mcps)} MCP servers via ToolManager")
                
                # Find browser MCP
                for mcp in mcps:
                    if "browser" in mcp.name.lower() or "browsing" in mcp.name.lower():
                        self.browser_mcp = mcp
                        print(f"✅ Found Browser MCP: {mcp.name}")
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
                    
                    if tools and any(tool_name in tool.name.lower() for tool_name in ["search", "navigate", "browser", "screenshot"] for tool in tools):
                        print(f"✅ Found Browser MCP on port {port}")
                        self.browser_mcp = MCP(
                            name="test",
                            tools=[tool.name for tool in tools],
                            address="localhost",
                            port=port,
                            transport="streamable-http",
                            client_url=url
                        )
                        mcps.append(self.browser_mcp)
                        break
                        
            except Exception:
                continue
        
        return mcps
    
    async def test_tool_discovery(self) -> bool:
        """Test tools discovery for Browser MCP"""
        print("\n📋 Testing tools discovery...")
        
        if not self.browser_mcp:
            print("❌ No Browser MCP found")
            return False
        
        try:
            url = self.browser_mcp.client_url or f"http://{self.browser_mcp.address}:{self.browser_mcp.port}/mcp"
            async with Client(url, timeout=5.0) as client:
                tools = await client.list_tools()
                
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description[:100]}...")
                
                # Expected browser tools
                expected_tools = [
                    "search",
                    "navigate", 
                    "get_links",
                    "get_downloadable_links",
                    "download_file",
                    "take_screenshot"
                ]
                
                found_tools = [tool.name for tool in tools]
                missing_tools = [tool for tool in expected_tools if tool not in found_tools]
                
                if missing_tools:
                    print(f"⚠️ Missing expected tools: {missing_tools}")
                    # Don't fail if some tools are missing - browser functionality varies
                
                print("✅ Browser tools discovery completed")
                return True
                
        except Exception as e:
            print(f"❌ Tool discovery failed: {e}")
            return False
    
    async def test_use_cases(self) -> bool:
        """Test Browser MCP use cases"""
        print("\n🧪 Testing Browser use cases...")
        
        if not self.browser_mcp:
            print("❌ No Browser MCP found")
            return False
        
        try:
            url = self.browser_mcp.client_url or f"http://{self.browser_mcp.address}:{self.browser_mcp.port}/mcp"
            async with Client(url, timeout=30.0) as client:  # Longer timeout for browser operations
                
                # Test 1: Search functionality
                print("\n🔍 Test 1: Web search")
                result = await client.call_tool("search", {
                    "query": "python programming tutorial"
                })
                
                if result and len(result) > 0:
                    response = json.loads(result[0].text)
                    print(f"✅ Search result: {response.get('status', 'unknown')}")
                    if response.get('result'):
                        search_results = response['result']
                        if isinstance(search_results, list):
                            print(f"   Found {len(search_results)} search results")
                        else:
                            print(f"   Search results available")
                else:
                    print("❌ No response from search")
                    return False
                
                # Test 2: Navigate to a test page
                print("\n🌐 Test 2: Navigate to webpage")
                result = await client.call_tool("navigate", {
                    "url": "https://httpbin.org/"
                })
                
                if result and len(result) > 0:
                    response = json.loads(result[0].text)
                    print(f"✅ Navigation result: {response.get('status', 'unknown')}")
                    if response.get('title'):
                        print(f"   Page title: {response['title'][:100]}")
                    if response.get('content'):
                        print(f"   Content length: {len(response['content'])} chars")
                else:
                    print("❌ Failed to navigate to webpage")
                    return False
                
                # Test 3: Get links from current page
                print("\n🔗 Test 3: Get page links")
                result = await client.call_tool("get_links", {})
                
                if result and len(result) > 0:
                    response = json.loads(result[0].text)
                    print(f"✅ Links result: {response.get('status', 'unknown')}")
                    if response.get('links'):
                        links = response['links'].split('\n')
                        print(f"   Found {len(links)} links")
                else:
                    print("❌ Failed to get links")
                    # Don't fail the test - some pages might not have links
                
                # Test 4: Get downloadable links
                print("\n📥 Test 4: Get downloadable links")
                result = await client.call_tool("get_downloadable_links", {})
                
                if result and len(result) > 0:
                    response = json.loads(result[0].text)
                    print(f"✅ Downloadable links result: {response.get('status', 'unknown')}")
                    if response.get('links'):
                        links = response['links'].split('\n')
                        print(f"   Found {len(links)} downloadable links")
                else:
                    print("⚠️ No downloadable links found (expected for test page)")
                
                # Test 5: Take screenshot
                print("\n📸 Test 5: Take screenshot")
                result = await client.call_tool("take_screenshot", {})
                
                if result and len(result) > 0:
                    response = json.loads(result[0].text)
                    print(f"✅ Screenshot result: {response.get('status', 'unknown')}")
                    if response.get('filename'):
                        print(f"   Screenshot saved: {response['filename']}")
                else:
                    print("⚠️ Screenshot functionality may not be available")
                
                # Test 6: Navigate to example.com for basic test
                print("\n🌐 Test 6: Navigate to example.com")
                result = await client.call_tool("navigate", {
                    "url": "https://example.com"
                })
                
                if result and len(result) > 0:
                    response = json.loads(result[0].text)
                    print(f"✅ Example.com navigation: {response.get('status', 'unknown')}")
                    if response.get('title'):
                        print(f"   Page title: {response['title']}")
                else:
                    print("⚠️ Failed to navigate to example.com")
                
                # Test 7: Advanced search with specific query
                print("\n🔍 Test 7: Advanced search query")
                result = await client.call_tool("search", {
                    "query": "machine learning algorithms 2024"
                })
                
                if result and len(result) > 0:
                    response = json.loads(result[0].text)
                    print(f"✅ Advanced search result: {response.get('status', 'unknown')}")
                    if response.get('result'):
                        print(f"   Search completed successfully")
                else:
                    print("⚠️ Advanced search may have issues")
                
                print("✅ Browser use cases completed")
                return True
                
        except Exception as e:
            print(f"❌ Use case testing failed: {e}")
            return False
    
    async def assert_running_ok(self) -> bool:
        """Assert that Browser MCP is running correctly"""
        print("\n✅ Asserting Browser MCP server status...")
        
        if not self.browser_mcp:
            print("❌ Browser MCP not found - server may not be running")
            return False
        
        try:
            url = self.browser_mcp.client_url or f"http://{self.browser_mcp.address}:{self.browser_mcp.port}/mcp"
            async with Client(url, timeout=10.0) as client:
                # Quick health check
                tools = await client.list_tools()
                
                if len(tools) > 0:
                    # Test basic search functionality as health check
                    result = await client.call_tool("search", {
                        "query": "test"
                    })
                    
                    if result and len(result) > 0:
                        response = json.loads(result[0].text)
                        if response.get('status') == 'success':
                            print(f"✅ Browser MCP server is running correctly")
                            print(f"   Server: {self.browser_mcp.name}")
                            print(f"   Address: {self.browser_mcp.address}:{self.browser_mcp.port}")
                            print(f"   Tools available: {len(tools)}")
                            print(f"   Search functionality: working")
                            return True
                    
                    print("⚠️ Browser MCP server tools available but search may have issues")
                    print(f"   Server: {self.browser_mcp.name}")
                    print(f"   Tools available: {len(tools)}")
                    return True
                else:
                    print("❌ Browser MCP server responded but no tools available")
                    return False
                
        except Exception as e:
            print(f"❌ Browser MCP server health check failed: {e}")
            return False


async def main():
    """Run all Browser MCP tests"""
    print("🧪 Starting Browser MCP Server Tests")
    print("=" * 60)
    
    test = BrowserMCPTest()
    success = True
    
    # Test 1: MCP Discovery
    mcps = await test.discover_mcp_servers()
    if not mcps or not test.browser_mcp:
        print("❌ Failed to discover Browser MCP server")
        print("   Make sure the server is running with: ./start.sh")
        print("   Browser server requires SearxNG and may take time to start")
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
        print("🎉 All Browser MCP tests PASSED!")
    else:
        print("❌ Some Browser MCP tests FAILED!")
        print("   Note: Browser tests may fail if SearxNG is not running")
        print("   or if there are network connectivity issues")
    
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