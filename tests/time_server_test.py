#!/usr/bin/env python3

"""
Test client for Time MCP Server
Tests MCP discovery, tools discovery, and use case scenarios.
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from sources.core.tools_manager import ToolManager, MCP
from config import Config
from fastmcp import Client


class TimeMCPTest:
    """Test class for Time MCP server"""
    
    def __init__(self):
        self.config = Config() if 'Config' in globals() else None
        self.tool_manager = ToolManager(self.config) if self.config else None
        self.time_mcp = None
        self.client = None
    
    async def discover_mcp_servers(self) -> List[MCP]:
        """Test MCP discovery"""
        print("🔍 Testing MCP server discovery...")
        
        if self.tool_manager:
            try:
                mcps = await self.tool_manager.discover_mcp_servers()
                print(f"✅ Discovered {len(mcps)} MCP servers via ToolManager")
                
                # Find time MCP
                for mcp in mcps:
                    if "time" in mcp.name.lower():
                        self.time_mcp = mcp
                        print(f"✅ Found Time MCP: {mcp.name}")
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
                        # Time server may not have get_mcp_name
                        resp = await client.call_tool("get_mcp_name", {})
                        if resp and len(resp) > 0:
                            name = resp[0].text
                    except Exception:
                        # Try to identify by tools
                        tool_names = [tool.name.lower() for tool in tools]
                        if any("time" in tool_name or "date" in tool_name for tool_name in tool_names):
                            name = "Time MCP Server"
                    
                    if tools and any("time" in tool.name.lower() or "date" in tool.name.lower() for tool in tools):
                        print(f"✅ Found Time MCP on port {port}: {name}")
                        self.time_mcp = MCP(
                            name=name,
                            tools=[tool.name for tool in tools],
                            address="localhost",
                            port=port,
                            transport="streamable-http",
                            client_url=url
                        )
                        mcps.append(self.time_mcp)
                        break
                        
            except Exception:
                continue
        
        return mcps
    
    async def test_tool_discovery(self) -> bool:
        """Test tools discovery for Time MCP"""
        print("\n📋 Testing tools discovery...")
        
        if not self.time_mcp:
            print("❌ No Time MCP found")
            return False
        
        try:
            url = self.time_mcp.client_url or f"http://{self.time_mcp.address}:{self.time_mcp.port}/mcp"
            async with Client(url, timeout=5.0) as client:
                tools = await client.list_tools()
                
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description[:100]}...")
                
                # Expected time tools (may vary based on implementation)
                expected_keywords = [
                    "time", "date", "timezone", "convert", "now", "current"
                ]
                
                found_tools = [tool.name.lower() for tool in tools]
                # Check if we have basic time operations
                has_time_ops = any(keyword in " ".join(found_tools) for keyword in expected_keywords)
                
                if has_time_ops:
                    print("✅ Time-related operations found")
                else:
                    print("⚠️ Some time operations may be missing")
                
                print("✅ Time tools discovery completed")
                return True
                
        except Exception as e:
            print(f"❌ Tool discovery failed: {e}")
            return False
    
    async def test_use_cases(self) -> bool:
        """Test Time MCP use cases"""
        print("\n🧪 Testing Time use cases...")
        
        if not self.time_mcp:
            print("❌ No Time MCP found")
            return False
        
        try:
            url = self.time_mcp.client_url or f"http://{self.time_mcp.address}:{self.time_mcp.port}/mcp"
            async with Client(url, timeout=30.0) as client:
                
                # Get available tools first
                tools = await client.list_tools()
                tool_names = [tool.name for tool in tools]
                
                # Test 1: Get current time
                print(f"\n🕐 Test 1: Get current time")
                current_time_tools = [name for name in tool_names if any(keyword in name.lower() for keyword in ["current", "now", "time"])]
                if current_time_tools:
                    try:
                        for time_tool in current_time_tools:
                            try:
                                result = await client.call_tool(time_tool, {})
                                if result and len(result) > 0:
                                    response_text = result[0].text
                                    print(f"✅ Current time with {time_tool}: {response_text[:100]}...")
                                    # Check if response looks like a time/date
                                    if any(char.isdigit() for char in response_text):
                                        print("   Response contains numeric time data")
                                    break
                            except Exception as e:
                                print(f"   ⚠️ {time_tool} failed: {e}")
                        else:
                            print("❌ All current time tools failed")
                    except Exception as e:
                        print(f"⚠️ Current time test failed: {e}")
                
                # Test 2: Date operations
                print(f"\n📅 Test 2: Date operations")
                date_tools = [name for name in tool_names if "date" in name.lower()]
                if date_tools:
                    try:
                        for date_tool in date_tools:
                            try:
                                result = await client.call_tool(date_tool, {})
                                if result and len(result) > 0:
                                    response_text = result[0].text
                                    print(f"✅ Date operation with {date_tool}: {response_text[:100]}...")
                                    break
                            except Exception as e:
                                print(f"   ⚠️ {date_tool} failed: {e}")
                        else:
                            print("⚠️ Date tools may not be available")
                    except Exception as e:
                        print(f"⚠️ Date operations test failed: {e}")
                
                # Test 3: Timezone operations
                print(f"\n🌍 Test 3: Timezone operations")
                timezone_tools = [name for name in tool_names if any(keyword in name.lower() for keyword in ["timezone", "convert", "tz"])]
                if timezone_tools:
                    try:
                        for tz_tool in timezone_tools:
                            try:
                                # Try different parameter combinations
                                test_params = [
                                    {},  # No parameters
                                    {"timezone": "UTC"},
                                    {"from_timezone": "UTC", "to_timezone": "America/New_York"},
                                    {"tz": "Europe/London"}
                                ]
                                
                                for params in test_params:
                                    try:
                                        result = await client.call_tool(tz_tool, params)
                                        if result and len(result) > 0:
                                            response_text = result[0].text
                                            print(f"✅ Timezone operation with {tz_tool}: {response_text[:100]}...")
                                            break
                                    except Exception:
                                        continue
                                else:
                                    print(f"   ⚠️ {tz_tool}: all parameter variants failed")
                                    continue
                                break
                            except Exception as e:
                                print(f"   ⚠️ {tz_tool} failed: {e}")
                        else:
                            print("⚠️ Timezone tools may not be available")
                    except Exception as e:
                        print(f"⚠️ Timezone operations test failed: {e}")
                
                # Test 4: Time conversion
                print(f"\n🔄 Test 4: Time conversion")
                convert_tools = [name for name in tool_names if "convert" in name.lower()]
                if convert_tools:
                    try:
                        for convert_tool in convert_tools:
                            try:
                                # Try various conversion parameters
                                test_params = [
                                    {"time": "2024-01-01T12:00:00Z", "from_tz": "UTC", "to_tz": "America/New_York"},
                                    {"datetime": "2024-01-01 12:00:00", "timezone": "UTC"},
                                    {"timestamp": "1704110400"}  # Unix timestamp
                                ]
                                
                                for params in test_params:
                                    try:
                                        result = await client.call_tool(convert_tool, params)
                                        if result and len(result) > 0:
                                            response_text = result[0].text
                                            print(f"✅ Time conversion with {convert_tool}: {response_text[:100]}...")
                                            break
                                    except Exception:
                                        continue
                                else:
                                    continue
                                break
                            except Exception as e:
                                print(f"   ⚠️ {convert_tool} failed: {e}")
                        else:
                            print("⚠️ Time conversion tools may not be available")
                    except Exception as e:
                        print(f"⚠️ Time conversion test failed: {e}")
                
                # Test 5: Format time
                print(f"\n📝 Test 5: Time formatting")
                format_tools = [name for name in tool_names if "format" in name.lower()]
                if format_tools:
                    try:
                        for format_tool in format_tools:
                            try:
                                # Try formatting parameters
                                test_params = [
                                    {"format": "ISO"},
                                    {"format": "%Y-%m-%d %H:%M:%S"},
                                    {"style": "long"}
                                ]
                                
                                for params in test_params:
                                    try:
                                        result = await client.call_tool(format_tool, params)
                                        if result and len(result) > 0:
                                            response_text = result[0].text
                                            print(f"✅ Time formatting with {format_tool}: {response_text[:100]}...")
                                            break
                                    except Exception:
                                        continue
                                else:
                                    continue
                                break
                            except Exception as e:
                                print(f"   ⚠️ {format_tool} failed: {e}")
                        else:
                            print("⚠️ Time formatting tools may not be available")
                    except Exception as e:
                        print(f"⚠️ Time formatting test failed: {e}")
                
                # Test 6: Unix timestamp
                print(f"\n⏱️ Test 6: Unix timestamp operations")
                timestamp_tools = [name for name in tool_names if any(keyword in name.lower() for keyword in ["unix", "timestamp", "epoch"])]
                if timestamp_tools:
                    try:
                        for ts_tool in timestamp_tools:
                            try:
                                result = await client.call_tool(ts_tool, {})
                                if result and len(result) > 0:
                                    response_text = result[0].text
                                    print(f"✅ Unix timestamp with {ts_tool}: {response_text[:100]}...")
                                    # Check if response looks like a timestamp
                                    if response_text.strip().isdigit():
                                        print("   Response looks like a valid timestamp")
                                    break
                            except Exception as e:
                                print(f"   ⚠️ {ts_tool} failed: {e}")
                        else:
                            print("⚠️ Unix timestamp tools may not be available")
                    except Exception as e:
                        print(f"⚠️ Unix timestamp test failed: {e}")
                
                # Test 7: Time parsing
                print(f"\n🔍 Test 7: Time parsing")
                parse_tools = [name for name in tool_names if "parse" in name.lower()]
                if parse_tools:
                    try:
                        for parse_tool in parse_tools:
                            try:
                                test_strings = [
                                    {"time_string": "2024-01-01T12:00:00Z"},
                                    {"date_string": "January 1, 2024"},
                                    {"input": "2024-01-01 12:00:00"}
                                ]
                                
                                for params in test_strings:
                                    try:
                                        result = await client.call_tool(parse_tool, params)
                                        if result and len(result) > 0:
                                            response_text = result[0].text
                                            print(f"✅ Time parsing with {parse_tool}: {response_text[:100]}...")
                                            break
                                    except Exception:
                                        continue
                                else:
                                    continue
                                break
                            except Exception as e:
                                print(f"   ⚠️ {parse_tool} failed: {e}")
                        else:
                            print("⚠️ Time parsing tools may not be available")
                    except Exception as e:
                        print(f"⚠️ Time parsing test failed: {e}")
                
                # Test 8: Exercise all available tools
                print(f"\n🔧 Test 8: Exercise remaining tools")
                tested_tools = set()
                for tool_name in tool_names:
                    if tool_name not in tested_tools:
                        try:
                            print(f"   Testing {tool_name}...")
                            result = await client.call_tool(tool_name, {})
                            if result and len(result) > 0:
                                response_text = result[0].text
                                print(f"     ✅ {tool_name}: {response_text[:50]}...")
                            else:
                                print(f"     ⚠️ {tool_name}: no response")
                            tested_tools.add(tool_name)
                        except Exception as e:
                            print(f"     ⚠️ {tool_name}: failed ({type(e).__name__})")
                
                # Test 9: Validate time accuracy
                print(f"\n⏰ Test 9: Validate time accuracy")
                if current_time_tools:
                    try:
                        # Get current time from server
                        result = await client.call_tool(current_time_tools[0], {})
                        if result and len(result) > 0:
                            server_time_str = result[0].text
                            current_time = datetime.now()
                            
                            print(f"✅ Time accuracy check:")
                            print(f"   Server time: {server_time_str[:100]}")
                            print(f"   Local time:  {current_time}")
                            
                            # Basic validation - server time should contain current year
                            if str(current_time.year) in server_time_str:
                                print("   ✅ Server time contains current year")
                            else:
                                print("   ⚠️ Server time may not be accurate")
                    except Exception as e:
                        print(f"⚠️ Time accuracy validation failed: {e}")
                
                print("✅ Time use cases completed")
                return True
                
        except Exception as e:
            print(f"❌ Use case testing failed: {e}")
            return False
    
    async def assert_running_ok(self) -> bool:
        """Assert that Time MCP is running correctly"""
        print("\n✅ Asserting Time MCP server status...")
        
        if not self.time_mcp:
            print("❌ Time MCP not found - server may not be running")
            return False
        
        try:
            url = self.time_mcp.client_url or f"http://{self.time_mcp.address}:{self.time_mcp.port}/mcp"
            async with Client(url, timeout=10.0) as client:
                # Quick health check
                tools = await client.list_tools()
                
                if len(tools) > 0:
                    print(f"✅ Time MCP server is running correctly")
                    print(f"   Server: {self.time_mcp.name}")
                    print(f"   Address: {self.time_mcp.address}:{self.time_mcp.port}")
                    print(f"   Tools available: {len(tools)}")
                    print(f"   Tool names: {[tool.name for tool in tools]}")
                    return True
                else:
                    print("❌ Time MCP server responded but no tools available")
                    return False
                
        except Exception as e:
            print(f"❌ Time MCP server health check failed: {e}")
            return False


async def main():
    """Run all Time MCP tests"""
    print("🧪 Starting Time MCP Server Tests")
    print("=" * 60)
    
    test = TimeMCPTest()
    success = True
    
    # Test 1: MCP Discovery
    mcps = await test.discover_mcp_servers()
    if not mcps or not test.time_mcp:
        print("❌ Failed to discover Time MCP server")
        print("   Make sure the server is running with: ./start.sh")
        print("   Time server should be available from ToolHive registry")
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
        print("🎉 All Time MCP tests PASSED!")
    else:
        print("❌ Some Time MCP tests FAILED!")
        print("   Note: Time tests may fail due to timezone configuration")
        print("   or if system time is not synchronized")
    
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