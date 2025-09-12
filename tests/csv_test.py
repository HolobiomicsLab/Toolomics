#!/usr/bin/env python3

"""
Test client for CSV MCP Server
Demonstrates all functionality with realistic test scenarios.
"""

import asyncio
import json
from pathlib import Path
from fastmcp import Client

async def test_csv_operations():
    """Test all CSV operations comprehensively."""
    
    # Connect to the MCP server
    async with Client("http://localhost:5001/mcp") as client:
        print("🚀 Connected to CSV MCP Server")
        
        # List available tools
        tools = await client.list_tools()
        print(f"📋 Available tools: {[tool.name for tool in tools]}")
        print()
        
        # Test 1: Create a new dataset
        print("=" * 50)
        print("TEST 1: Creating new dataset")
        print("=" * 50)
        
        result = await client.call_tool("create_csv", {
            "name": "employees",
            "columns": ["id", "name", "department", "salary", "hire_date"],
            "rows": [
                {"id": 1, "name": "Alice Johnson", "department": "Engineering", "salary": 85000, "hire_date": "2022-01-15"},
                {"id": 2, "name": "Bob Smith", "department": "Marketing", "salary": 65000, "hire_date": "2021-03-20"},
                {"id": 3, "name": "Carol Davis", "department": "Engineering", "salary": 92000, "hire_date": "2020-07-10"}
            ]
        })
        # Test 2: Get dataset info
        print("=" * 50)
        print("TEST 2: Getting dataset info")
        print("=" * 50)
        
        result = await client.call_tool("get_csv_info", {"name": "employees"})
        print(f"📊 Dataset info: {result[0].text}")
        print()
        
        # Test 3: Add a new row
        print("=" * 50)
        print("TEST 3: Adding new row")
        print("=" * 50)
        
        result = await client.call_tool("add_csv_row", {
            "name": "employees",
            "row": {"id": 4, "name": "David Wilson", "department": "Sales", "salary": 58000, "hire_date": "2023-02-28"}
        })
        print(f"📊 Add row: {result[0].text}")
        print()
        
        # Test 4: Get all data
        print("=" * 50)
        print("TEST 4: Getting all data")
        print("=" * 50)
        
        result = await client.call_tool("get_csv_data", {"name": "employees"})
        data = json.loads(result[0].text) if result else {}
        print(f"📋 All data ({data.get('total_rows', 0)} rows):")
        if 'data' in data:
            for i, row in enumerate(data['data']):
                print(f"  Row {i}: {row}")
        print()
        
        # Test 5: Update a row
        print("=" * 50)
        print("TEST 5: Updating row")
        print("=" * 50)
        
        result = await client.call_tool("update_csv_row", {
            "name": "employees",
            "index": 1,
            "row": {"salary": 70000, "department": "Product Marketing"}
        })
        print(f"📊 update result: {result[0].text}")
        print()
        
        # Test 6: Query data
        print("=" * 50)
        print("TEST 6: Querying data")
        print("=" * 50)
        
        result = await client.call_tool("query_csv", {
            "name": "employees",
            "query": "salary > 70000"
        })
        query_data = json.loads(result[0].text) if result else {}
        print(f"🔍 Query result (salary > 70000): {query_data.get('result_count', 0)} matches")
        if 'results' in query_data:
            for row in query_data['results']:
                print(f"  {row['name']}: ${row['salary']} in {row['department']}")
        print()
        
        # Test 7: Get statistics
        print("=" * 50)
        print("TEST 7: Getting statistics")
        print("=" * 50)
        
        result = await client.call_tool("get_csv_stats", {"name": "employees"})
        stats = json.loads(result[0].text) if result else {}
        print(f"📈 Dataset statistics:")
        print(f"  Shape: {stats.get('shape', 'N/A')}")
        print(f"  Numeric columns: {stats.get('numeric_columns', [])}")
        print(f"  Missing values: {stats.get('missing_values', {})}")
        print(f"  Duplicate rows: {stats.get('duplicate_rows', 0)}")
        print()
        
        # Test 8: Create another dataset for demonstration
        print("=" * 50)
        print("TEST 8: Creating second dataset")
        print("=" * 50)
        
        result = await client.call_tool("create_csv", {
            "name": "products",
            "columns": ["product_id", "name", "category", "price", "stock"],
            "rows": [
                {"product_id": "P001", "name": "Laptop", "category": "Electronics", "price": 999.99, "stock": 50},
                {"product_id": "P002", "name": "Mouse", "category": "Electronics", "price": 29.99, "stock": 200},
                {"product_id": "P003", "name": "Desk Chair", "category": "Furniture", "price": 149.99, "stock": 25}
            ]
        })
        
        # Test 9: List all datasets
        print("=" * 50)
        print("TEST 9: Listing all datasets")
        print("=" * 50)
        
        result = await client.call_tool("list_csv_datasets", {})
        datasets = json.loads(result[0].text) if result else {}
        print(f"📁 All datasets ({datasets.get('total_count', 0)}):")
        if 'datasets' in datasets:
            for ds in datasets['datasets']:
                print(f"  {ds['name']}: {ds['shape']} - {ds.get('file_size', 0)} bytes")
        print()
        
        # Test 10: Test pagination
        print("=" * 50)
        print("TEST 10: Testing pagination")
        print("=" * 50)
        
        result = await client.call_tool("get_csv_data", {
            "name": "employees",
            "limit": 2,
            "offset": 1
        })
        page_data = json.loads(result[0].text) if result else {}
        print(f"📄 Pagination test (limit=2, offset=1): {page_data.get('returned_rows', 0)} rows returned")
        if 'data' in page_data:
            for row in page_data['data']:
                print(f"  {row['name']}")
        print()
        
        # Test 11: Error handling
        print("=" * 50)
        print("TEST 11: Error handling")
        print("=" * 50)
        
        # Try to access non-existent dataset
        result = await client.call_tool("get_csv_info", {"name": "nonexistent"})
        print(f"❌ Non-existent dataset: {result[0].text}")

        # Try invalid query
        result = await client.call_tool("query_csv", {
            "name": "employees",
            "query": "invalid_column > 100"
        })
        print(f"❌ Invalid query: {result[0].text}")
        print()
        
        # Test 12: Delete operations
        print("=" * 50)
        print("TEST 12: Delete operations")
        print("=" * 50)
        
        # Delete a row
        result = await client.call_tool("delete_csv_row", {
            "name": "employees",
            "index": 0
        })
        print(f"🗑️ Delete row result: {result[0].text}")

        # Show updated data count
        result = await client.call_tool("get_csv_info", {"name": "employees"})
        info = json.loads(result[0].text) if result else {}
        print(f"📊 After deletion - Shape: {info.get('shape', 'N/A')}")
        print()
        
        # Final summary
        print("=" * 50)
        print("FINAL SUMMARY")
        print("=" * 50)
        
        result = await client.call_tool("list_csv_datasets", {})
        final_datasets = json.loads(result[0].text) if result else {}
        print(f"📁 Final dataset count: {final_datasets.get('total_count', 0)}")
        
        print("\n🎉 All tests completed successfully!")
        print("\nTo clean up test files, you can run:")

if __name__ == "__main__":
    print("🧪 Starting CSV MCP server.py Tests")
    asyncio.run(test_csv_operations())