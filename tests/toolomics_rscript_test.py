#!/usr/bin/env python3

"""
Test client for Toolomics R Script MCP Server
Tests MCP discovery, tools discovery, and use case scenarios.
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any
import sys
import os

# Import shared utilities
from test_utils import get_tool_manager, create_mcp_object
from fastmcp import Client


class RScriptMCPTest:
    """Test class for R Script MCP server"""
    
    def __init__(self):
        self.tool_manager = get_tool_manager()
        self.rscript_mcp = None
        self.client = None
    
    async def discover_mcp_servers(self) -> list:
        """Test MCP discovery"""
        print("🔍 Testing MCP server discovery...")
        
        if self.tool_manager:
            try:
                mcps = await self.tool_manager.discover_mcp_servers()
                print(f"✅ Discovered {len(mcps)} MCP servers via ToolManager")
                
                # Find R script MCP
                for mcp in mcps:
                    if "rscript" in mcp.name.lower() or "r script" in mcp.name.lower():
                        self.rscript_mcp = mcp
                        print(f"✅ Found R Script MCP: {mcp.name}")
                        break
                
                return mcps
            except Exception as e:
                print(f"❌ ToolManager discovery failed: {e}")
        
        # Fallback: Direct discovery via port scanning
        print("🔍 Falling back to direct MCP discovery...")
        return await self._direct_discovery()
    
    async def _direct_discovery(self) -> list:
        """Direct MCP server discovery by scanning ports"""
        mcps = []
        
        for port in range(5000, 5010):  # Scan common MCP ports
            try:
                url = f"http://localhost:{port}/mcp"
                async with Client(url, timeout=3.0) as client:
                    tools = await client.list_tools()
                    
                    if tools and any("r" in tool.name.lower() for tool in tools):
                        print(f"✅ Found R Script MCP on port {port}")
                        self.rscript_mcp = create_mcp_object(
                            name="test",
                            tools=[tool.name for tool in tools],
                            address="localhost",
                            port=port,
                            transport="streamable-http",
                            client_url=url
                        )
                        mcps.append(self.rscript_mcp)
                        break
                        
            except Exception:
                continue
        
        return mcps
    
    async def test_tool_discovery(self) -> bool:
        """Test tools discovery for R Script MCP"""
        print("\n📋 Testing tools discovery...")
        
        if not self.rscript_mcp:
            print("❌ No R Script MCP found")
            return False
        
        try:
            url = self.rscript_mcp.client_url or f"http://{self.rscript_mcp.address}:{self.rscript_mcp.port}/mcp"
            async with Client(url, timeout=5.0) as client:
                tools = await client.list_tools()
                
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description[:100]}...")
                
                # Expected R script tools
                expected_tools = [
                    "execute_r_code",
                    "write_r_script", 
                    "list_workspace_files",
                    "list_script_files",
                    "execute_r_script_file"
                ]
                
                found_tools = [tool.name for tool in tools]
                missing_tools = [tool for tool in expected_tools if tool not in found_tools]
                
                if missing_tools:
                    print(f"⚠️ Missing expected tools: {missing_tools}")
                    return False
                
                print("✅ All expected R script tools found")
                return True
                
        except Exception as e:
            print(f"❌ Tool discovery failed: {e}")
            return False
    
    async def test_use_cases(self) -> bool:
        """Test R Script MCP use cases"""
        print("\n🧪 Testing R Script use cases...")
        
        if not self.rscript_mcp:
            print("❌ No R Script MCP found")
            return False
        
        try:
            url = self.rscript_mcp.client_url or f"http://{self.rscript_mcp.address}:{self.rscript_mcp.port}/mcp"
            async with Client(url, timeout=10.0) as client:
                
                # Test 1: Execute simple R code
                print("\n📝 Test 1: Execute simple R code")
                result = await client.call_tool("execute_r_code", {
                    "r_code": "cat('Hello from R!\\n'); 2 + 2"
                })
                
                if result and len(result) > 0:
                    response = json.loads(result[0].text)
                    print(f"✅ R code execution result: {response.get('status', 'unknown')}")
                    if response.get('stdout'):
                        print(f"   Output: {response['stdout'].strip()}")
                else:
                    print("❌ No response from execute_r_code")
                    return False
                
                # Test 2: Write R script file
                print("\n📝 Test 2: Write R script to file")
                r_code = """
# Test R script
x <- 1:10
y <- x^2
plot(x, y, main="Test Plot", xlab="X", ylab="Y")
cat("Script completed successfully\\n")
"""
                result = await client.call_tool("write_r_script", {
                    "r_code": r_code,
                    "filename": "test_script.R"
                })
                
                if result and len(result) > 0:
                    print(f"✅ Script write result: {result[0].text}")
                else:
                    print("❌ Failed to write R script")
                    return False
                
                # Test 3: List script files
                print("\n📝 Test 3: List script files")
                result = await client.call_tool("list_script_files", {})
                
                if result and len(result) > 0:
                    files = json.loads(result[0].text)
                    print(f"✅ Found {len(files)} script files: {files}")
                else:
                    print("❌ Failed to list script files")
                    return False
                
                # Test 4: Execute R script file
                print("\n📝 Test 4: Execute R script file")
                if "test_script.R" in files:
                    result = await client.call_tool("execute_r_script_file", {
                        "filename": "test_script.R"
                    })
                    
                    if result and len(result) > 0:
                        response = json.loads(result[0].text)
                        print(f"✅ Script execution result: {response.get('status', 'unknown')}")
                        if response.get('stdout'):
                            print(f"   Output: {response['stdout'].strip()}")
                    else:
                        print("❌ Failed to execute R script file")
                        return False
                
                # Test 5: List workspace files
                print("\n📝 Test 5: List workspace files")
                result = await client.call_tool("list_workspace_files", {})
                
                if result and len(result) > 0:
                    workspace_files = json.loads(result[0].text)
                    print(f"✅ Found {len(workspace_files)} workspace files: {workspace_files}")
                else:
                    print("❌ Failed to list workspace files")
                    return False
                
                # Test 6: Statistical analysis example
                print("\n📝 Test 6: Statistical analysis example")
                stats_code = """
# Generate sample data
set.seed(123)
data <- data.frame(
    x = rnorm(100, mean=10, sd=2),
    y = rnorm(100, mean=20, sd=3)
)

# Calculate statistics
cat("Summary statistics:\\n")
cat("X mean:", mean(data$x), "\\n")
cat("Y mean:", mean(data$y), "\\n")
cat("Correlation:", cor(data$x, data$y), "\\n")

# Simple regression
model <- lm(y ~ x, data=data)
cat("R-squared:", summary(model)$r.squared, "\\n")
"""
                result = await client.call_tool("execute_r_code", {
                    "r_code": stats_code
                })
                
                if result and len(result) > 0:
                    response = json.loads(result[0].text)
                    print(f"✅ Statistical analysis result: {response.get('status', 'unknown')}")
                    if response.get('stdout'):
                        print(f"   Output: {response['stdout'].strip()}")
                else:
                    print("❌ Failed to execute statistical analysis")
                    return False
                
                print("✅ All R Script use cases completed successfully")
                return True
                
        except Exception as e:
            print(f"❌ Use case testing failed: {e}")
            return False
    
    async def assert_running_ok(self) -> bool:
        """Assert that R Script MCP is running correctly"""
        print("\n✅ Asserting R Script MCP server status...")
        
        if not self.rscript_mcp:
            print("❌ R Script MCP not found - server may not be running")
            return False
        
        try:
            url = self.rscript_mcp.client_url or f"http://{self.rscript_mcp.address}:{self.rscript_mcp.port}/mcp"
            async with Client(url, timeout=5.0) as client:
                # Quick health check
                tools = await client.list_tools()
                
                if len(tools) > 0:
                    print(f"✅ R Script MCP server is running correctly")
                    print(f"   Server: {self.rscript_mcp.name}")
                    print(f"   Address: {self.rscript_mcp.address}:{self.rscript_mcp.port}")
                    print(f"   Tools available: {len(tools)}")
                    return True
                else:
                    print("❌ R Script MCP server responded but no tools available")
                    return False
                
        except Exception as e:
            print(f"❌ R Script MCP server health check failed: {e}")
            return False


async def main():
    """Run all R Script MCP tests"""
    print("🧪 Starting R Script MCP Server Tests")
    print("=" * 60)
    
    test = RScriptMCPTest()
    success = True
    
    # Test 1: MCP Discovery
    mcps = await test.discover_mcp_servers()
    if not mcps or not test.rscript_mcp:
        print("❌ Failed to discover R Script MCP server")
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
        print("🎉 All R Script MCP tests PASSED!")
    else:
        print("❌ Some R Script MCP tests FAILED!")
    
    return success


if __name__ == "__main__":
    # Run tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)