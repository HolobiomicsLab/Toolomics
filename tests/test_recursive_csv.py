#!/usr/bin/env python3

"""
Test recursive listing functionality for CSV MCP Server
"""

import asyncio
import json
import sys
from pathlib import Path
from fastmcp import Client

async def test_recursive_listing(port: int = 5007):
    """Test that list_csv_datasets finds files recursively."""
    
    async with Client(f"http://localhost:{port}/mcp") as client:
        print("🚀 Connected to CSV MCP Server")
        print()
        
        # Test 1: Set working path to main test directory
        print("=" * 50)
        print("TEST 1: Setting up test directory structure")
        print("=" * 50)
        
        result = await client.call_tool("set_working_path", {
            "subfolder": "recursive_test"
        })
        print(f"📂 Set working path: {result.content[0].text}")
        print()
        
        # Test 2: Create CSV in root of test directory
        print("Creating CSV in root directory...")
        result = await client.call_tool("create_csv", {
            "name": "root_data",
            "columns": ["id", "value"],
            "rows": [{"id": 1, "value": "root"}]
        })
        print(f"✅ Created: {result.content[0].text}")
        print()
        
        # Test 3: Create CSV in subdirectory
        print("Creating CSV in 'data' subdirectory...")
        result = await client.call_tool("set_working_path", {
            "subfolder": "recursive_test/data"
        })
        print(f"📂 Changed path: {result.content[0].text}")
        
        result = await client.call_tool("create_csv", {
            "name": "subdir_data",
            "columns": ["id", "value"],
            "rows": [{"id": 2, "value": "subdir"}]
        })
        print(f"✅ Created: {result.content[0].text}")
        print()
        
        # Test 4: Create CSV in nested subdirectory
        print("Creating CSV in 'data/nested' subdirectory...")
        result = await client.call_tool("set_working_path", {
            "subfolder": "recursive_test/data/nested"
        })
        print(f"📂 Changed path: {result.content[0].text}")
        
        result = await client.call_tool("create_csv", {
            "name": "nested_data",
            "columns": ["id", "value"],
            "rows": [{"id": 3, "value": "nested"}]
        })
        print(f"✅ Created: {result.content[0].text}")
        print()
        
        # Test 5: Go back to root test directory and list all
        print("=" * 50)
        print("TEST 2: Listing all CSV files recursively")
        print("=" * 50)
        
        result = await client.call_tool("set_working_path", {
            "subfolder": "recursive_test"
        })
        print(f"📂 Changed back to root test path: {result.content[0].text}")
        print()
        
        result = await client.call_tool("list_csv_datasets", {})
        datasets = json.loads(result.content[0].text) if result else {}
        
        print(f"📁 Found {datasets.get('total_count', 0)} datasets:")
        if 'datasets' in datasets:
            for ds in datasets['datasets']:
                print(f"  ✓ {ds.get('path', ds['name'])}: {ds['shape']} - {ds.get('file_size', 0)} bytes")
        print()
        
        # Verify we found all 3 files
        expected_files = ['root_data', 'subdir_data', 'nested_data']
        found_files = [ds['name'] for ds in datasets.get('datasets', [])]
        
        print("=" * 50)
        print("VERIFICATION")
        print("=" * 50)
        
        all_found = True
        for expected in expected_files:
            if expected in found_files:
                print(f"✅ Found {expected}")
            else:
                print(f"❌ Missing {expected}")
                all_found = False
        
        print()
        if all_found and datasets.get('total_count', 0) == 3:
            print("🎉 SUCCESS: All CSV files found recursively!")
        else:
            print(f"❌ FAILED: Expected 3 files, found {datasets.get('total_count', 0)}")
        
        print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("USAGE")
        print(f"\t{sys.argv[0]} <port>")
        sys.exit(1)
    
    print("🧪 Testing Recursive CSV Listing")
    port = int(sys.argv[1])
    asyncio.run(test_recursive_listing(port))
