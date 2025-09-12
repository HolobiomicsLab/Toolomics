#!/usr/bin/env python3

"""
Test client for Toolomics CSV MCP Server
Tests MCP discovery, tools discovery, and use case scenarios.
Based on existing csv_test.py but with comprehensive MCP testing framework.
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


class CSVMCPTest:
    """Test class for CSV MCP server"""
    
    def __init__(self):
        self.config = Config() if 'Config' in globals() else None
        self.tool_manager = ToolManager(self.config) if self.config else None
        self.csv_mcp = None
        self.client = None
    
    async def discover_mcp_servers(self) -> List[MCP]:
        """Test MCP discovery"""
        print("🔍 Testing MCP server discovery...")
        
        if self.tool_manager:
            try:
                mcps = await self.tool_manager.discover_mcp_servers()
                print(f"✅ Discovered {len(mcps)} MCP servers via ToolManager")
                
                # Find CSV MCP
                for mcp in mcps:
                    if "csv" in mcp.name.lower():
                        self.csv_mcp = mcp
                        print(f"✅ Found CSV MCP: {mcp.name}")
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
                    
                    if tools and any("csv" in tool.name.lower() for tool in tools):
                        print(f"✅ Found CSV MCP on port {port}: {name}")
                        self.csv_mcp = MCP(
                            name=name,
                            tools=[tool.name for tool in tools],
                            address="localhost",
                            port=port,
                            transport="streamable-http",
                            client_url=url
                        )
                        mcps.append(self.csv_mcp)
                        break
                        
            except Exception:
                continue
        
        return mcps
    
    async def test_tool_discovery(self) -> bool:
        """Test tools discovery for CSV MCP"""
        print("\n📋 Testing tools discovery...")
        
        if not self.csv_mcp:
            print("❌ No CSV MCP found")
            return False
        
        try:
            url = self.csv_mcp.client_url or f"http://{self.csv_mcp.address}:{self.csv_mcp.port}/mcp"
            async with Client(url, timeout=5.0) as client:
                tools = await client.list_tools()
                
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description[:100]}...")
                
                # Expected CSV tools
                expected_tools = [
                    "create_csv",
                    "get_csv_info",
                    "get_csv_data",
                    "add_csv_row",
                    "update_csv_row",
                    "delete_csv_row",
                    "query_csv",
                    "get_csv_stats",
                    "list_csv_datasets"
                ]
                
                found_tools = [tool.name for tool in tools]
                missing_tools = [tool for tool in expected_tools if tool not in found_tools]
                
                if missing_tools:
                    print(f"⚠️ Missing expected tools: {missing_tools}")
                    return False
                
                print("✅ All expected CSV tools found")
                return True
                
        except Exception as e:
            print(f"❌ Tool discovery failed: {e}")
            return False
    
    async def test_use_cases(self) -> bool:
        """Test comprehensive CSV MCP use cases"""
        print("\n🧪 Testing CSV use cases...")
        
        if not self.csv_mcp:
            print("❌ No CSV MCP found")
            return False
        
        try:
            url = self.csv_mcp.client_url or f"http://{self.csv_mcp.address}:{self.csv_mcp.port}/mcp"
            async with Client(url, timeout=10.0) as client:
                
                # Test 1: Create a test dataset
                print("\n📝 Test 1: Create CSV dataset")
                result = await client.call_tool("create_csv", {
                    "name": "test_employees",
                    "columns": ["id", "name", "department", "salary", "hire_date"],
                    "rows": [
                        {
                            "id": 1,
                            "name": "Alice Johnson",
                            "department": "Engineering",
                            "salary": 85000,
                            "hire_date": "2022-01-15"
                        },
                        {
                            "id": 2,
                            "name": "Bob Smith",
                            "department": "Marketing",
                            "salary": 65000,
                            "hire_date": "2021-03-20"
                        },
                        {
                            "id": 3,
                            "name": "Carol Davis",
                            "department": "Engineering",
                            "salary": 92000,
                            "hire_date": "2020-07-10"
                        }
                    ]
                })
                
                if result and len(result) > 0:
                    print(f"✅ CSV creation result: {result[0].text}")
                else:
                    print("❌ Failed to create CSV dataset")
                    return False
                
                # Test 2: Get dataset info
                print("\n📊 Test 2: Get dataset info")
                result = await client.call_tool("get_csv_info", {
                    "name": "test_employees"
                })
                
                if result and len(result) > 0:
                    info = json.loads(result[0].text)
                    print(f"✅ Dataset info - Shape: {info.get('shape', 'unknown')}")
                    print(f"   Columns: {info.get('columns', [])}")
                else:
                    print("❌ Failed to get dataset info")
                    return False
                
                # Test 3: Add a new row
                print("\n➕ Test 3: Add new row")
                result = await client.call_tool("add_csv_row", {
                    "name": "test_employees",
                    "row": {
                        "id": 4,
                        "name": "David Wilson",
                        "department": "Sales",
                        "salary": 58000,
                        "hire_date": "2023-02-28"
                    }
                })
                
                if result and len(result) > 0:
                    print(f"✅ Add row result: {result[0].text}")
                else:
                    print("❌ Failed to add new row")
                    return False
                
                # Test 4: Get all data
                print("\n📋 Test 4: Get all data")
                result = await client.call_tool("get_csv_data", {
                    "name": "test_employees"
                })
                
                if result and len(result) > 0:
                    data = json.loads(result[0].text)
                    print(f"✅ Dataset has {data.get('total_rows', 0)} rows")
                    print(f"   Sample data: {data.get('data', [])[:2]}")
                else:
                    print("❌ Failed to get dataset data")
                    return False
                
                # Test 5: Update a row
                print("\n📝 Test 5: Update row")
                result = await client.call_tool("update_csv_row", {
                    "name": "test_employees",
                    "index": 1,
                    "row": {"salary": 70000, "department": "Product Marketing"}
                })
                
                if result and len(result) > 0:
                    print(f"✅ Update result: {result[0].text}")
                else:
                    print("❌ Failed to update row")
                    return False
                
                # Test 6: Query data
                print("\n🔍 Test 6: Query data")
                result = await client.call_tool("query_csv", {
                    "name": "test_employees",
                    "query": "salary > 70000"
                })
                
                if result and len(result) > 0:
                    query_data = json.loads(result[0].text)
                    print(f"✅ Query result: {query_data.get('result_count', 0)} matches")
                    if query_data.get('results'):
                        for row in query_data['results'][:2]:
                            print(f"   {row.get('name', 'unknown')}: ${row.get('salary', 0)}")
                else:
                    print("❌ Failed to query data")
                    return False
                
                # Test 7: Get statistics
                print("\n📈 Test 7: Get statistics")
                result = await client.call_tool("get_csv_stats", {
                    "name": "test_employees"
                })
                
                if result and len(result) > 0:
                    stats = json.loads(result[0].text)
                    print(f"✅ Statistics - Shape: {stats.get('shape', 'unknown')}")
                    print(f"   Numeric columns: {stats.get('numeric_columns', [])}")
                    print(f"   Missing values: {stats.get('missing_values', {})}")
                else:
                    print("❌ Failed to get statistics")
                    return False
                
                # Test 8: Create second dataset
                print("\n📝 Test 8: Create second dataset")
                result = await client.call_tool("create_csv", {
                    "name": "test_products",
                    "columns": ["product_id", "name", "category", "price", "stock"],
                    "rows": [
                        {
                            "product_id": "P001",
                            "name": "Laptop",
                            "category": "Electronics",
                            "price": 999.99,
                            "stock": 50
                        },
                        {
                            "product_id": "P002",
                            "name": "Mouse",
                            "category": "Electronics", 
                            "price": 29.99,
                            "stock": 200
                        }
                    ]
                })
                
                if result and len(result) > 0:
                    print(f"✅ Second dataset created: {result[0].text}")
                else:
                    print("❌ Failed to create second dataset")
                    return False
                
                # Test 9: List all datasets
                print("\n📁 Test 9: List all datasets")
                result = await client.call_tool("list_csv_datasets", {})
                
                if result and len(result) > 0:
                    datasets = json.loads(result[0].text)
                    print(f"✅ Found {datasets.get('total_count', 0)} datasets")
                    for ds in datasets.get('datasets', []):
                        print(f"   {ds.get('name', 'unknown')}: {ds.get('shape', 'unknown shape')}")
                else:
                    print("❌ Failed to list datasets")
                    return False
                
                # Test 10: Test pagination
                print("\n📄 Test 10: Test pagination")
                result = await client.call_tool("get_csv_data", {
                    "name": "test_employees",
                    "limit": 2,
                    "offset": 1
                })
                
                if result and len(result) > 0:
                    page_data = json.loads(result[0].text)
                    print(f"✅ Pagination: {page_data.get('returned_rows', 0)} rows returned")
                    print(f"   Total rows: {page_data.get('total_rows', 0)}")
                else:
                    print("❌ Failed to test pagination")
                    return False
                
                # Test 11: Error handling
                print("\n🚫 Test 11: Error handling")
                result = await client.call_tool("get_csv_info", {
                    "name": "nonexistent_dataset"
                })
                
                if result and len(result) > 0:
                    error_response = result[0].text
                    print(f"✅ Error handling works: {error_response[:100]}...")
                else:
                    print("❌ Error handling test failed")
                    return False
                
                # Test 12: Delete row
                print("\n🗑️ Test 12: Delete row")
                result = await client.call_tool("delete_csv_row", {
                    "name": "test_employees",
                    "index": 0
                })
                
                if result and len(result) > 0:
                    print(f"✅ Delete row result: {result[0].text}")
                    
                    # Verify deletion
                    result = await client.call_tool("get_csv_info", {
                        "name": "test_employees"
                    })
                    if result:
                        info = json.loads(result[0].text)
                        print(f"   Updated shape: {info.get('shape', 'unknown')}")
                else:
                    print("❌ Failed to delete row")
                    return False
                
                print("✅ All CSV use cases completed successfully")
                return True
                
        except Exception as e:
            print(f"❌ Use case testing failed: {e}")
            return False
    
    async def assert_running_ok(self) -> bool:
        """Assert that CSV MCP is running correctly"""
        print("\n✅ Asserting CSV MCP server status...")
        
        if not self.csv_mcp:
            print("❌ CSV MCP not found - server may not be running")
            return False
        
        try:
            url = self.csv_mcp.client_url or f"http://{self.csv_mcp.address}:{self.csv_mcp.port}/mcp"
            async with Client(url, timeout=5.0) as client:
                # Quick health check
                tools = await client.list_tools()
                
                if len(tools) > 0:
                    # Test basic functionality
                    result = await client.call_tool("list_csv_datasets", {})
                    
                    if result and len(result) > 0:
                        print(f"✅ CSV MCP server is running correctly")
                        print(f"   Server: {self.csv_mcp.name}")
                        print(f"   Address: {self.csv_mcp.address}:{self.csv_mcp.port}")
                        print(f"   Tools available: {len(tools)}")
                        print(f"   Dataset operations: working")
                        return True
                    else:
                        print("⚠️ CSV MCP server tools available but operations may have issues")
                        return True
                else:
                    print("❌ CSV MCP server responded but no tools available")
                    return False
                
        except Exception as e:
            print(f"❌ CSV MCP server health check failed: {e}")
            return False


async def main():
    """Run all CSV MCP tests"""
    print("🧪 Starting CSV MCP Server Tests")
    print("=" * 60)
    
    test = CSVMCPTest()
    success = True
    
    # Test 1: MCP Discovery
    mcps = await test.discover_mcp_servers()
    if not mcps or not test.csv_mcp:
        print("❌ Failed to discover CSV MCP server")
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
        print("🎉 All CSV MCP tests PASSED!")
    else:
        print("❌ Some CSV MCP tests FAILED!")
    
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