#!/usr/bin/env python3

"""
Test client for DECIMER Classifier MCP Server
Tests the classify_chemical_structure MCP tool specifically
"""

import asyncio
import json
import sys
from fastmcp import Client

async def test_decimer_classifier(port: int = 5150):
    """Test DECIMER Classifier MCP tool comprehensively."""
    
    async with Client(f"http://localhost:{port}/mcp") as client:
        print("🚀 Connected to DECIMER MCP Server")
        
        # List available tools
        tools = await client.list_tools()
        print(f"📋 Available tools: {[tool.name for tool in tools]}")
        print()
        
        # Check if classify_chemical_structure tool exists
        classifier_tool = None
        for tool in tools:
            if tool.name == "classify_chemical_structure":
                classifier_tool = tool
                break
        
        if not classifier_tool:
            print("❌ classify_chemical_structure tool not found!")
            return False
        
        print("✅ Found classify_chemical_structure tool")
        print(f"   Description: {classifier_tool.description}")
        
        # Test 1: Classify chemical structure (caffeine.png)
        print("\n" + "=" * 60)
        print("TEST 1: Classify chemical structure (caffeine.png)")
        print("=" * 60)
        
        result = await client.call_tool("classify_chemical_structure", {
            "image_path": "workspace/caffeine.png"
        })
        
        tool_output = json.loads(result.content[0].text)
        test1_pass = False
        if tool_output.get('status') == 'success':
            stdout_data = json.loads(tool_output['stdout'])
            print("✅ Classification successful!")
            print(f"   Image: workspace/caffeine.png")
            print(f"   Is Chemical: {stdout_data.get('is_chemical', 'N/A')}")
            print(f"   Confidence Score: {stdout_data.get('confidence_score', 'N/A')}")
            print(f"   Message: {stdout_data.get('message', 'N/A')}")
            
            # Check if result is as expected (should be True for caffeine)
            expected_chemical = True
            actual_chemical = stdout_data.get('is_chemical', False)
            print(f"\n   Expected (True): {expected_chemical}")
            print(f"   Actual: {actual_chemical}")
            test1_pass = actual_chemical == expected_chemical
            print(f"   ✅ Test Result: {'PASS' if test1_pass else 'FAIL'}")
        else:
            print(f"❌ Error: {tool_output.get('stderr', 'Unknown error')}")
        
        # Test 2: Classify non-chemical structure (chinese_character.jpg)
        print("\n" + "=" * 60)
        print("TEST 2: Classify non-chemical structure (chinese_character.jpg)")
        print("=" * 60)
        
        result = await client.call_tool("classify_chemical_structure", {
            "image_path": "workspace/chinese_character.jpg"
        })
        
        tool_output = json.loads(result.content[0].text)
        test2_pass = False
        if tool_output.get('status') == 'success':
            stdout_data = json.loads(tool_output['stdout'])
            print("✅ Classification successful!")
            print(f"   Image: workspace/chinese_character.jpg")
            print(f"   Is Chemical: {stdout_data.get('is_chemical', 'N/A')}")
            print(f"   Confidence Score: {stdout_data.get('confidence_score', 'N/A')}")
            print(f"   Message: {stdout_data.get('message', 'N/A')}")
            
            # Check if result is as expected (should be False for chinese character)
            expected_chemical = False
            actual_chemical = stdout_data.get('is_chemical', True)
            print(f"\n   Expected (False): {expected_chemical}")
            print(f"   Actual: {actual_chemical}")
            test2_pass = actual_chemical == expected_chemical
            print(f"   ✅ Test Result: {'PASS' if test2_pass else 'FAIL'}")
        else:
            print(f"❌ Error: {tool_output.get('stderr', 'Unknown error')}")
        
        # Test 3: Test with non-existent file
        print("\n" + "=" * 60)
        print("TEST 3: Error handling (non-existent file)")
        print("=" * 60)
        
        result = await client.call_tool("classify_chemical_structure", {
            "image_path": "/app/workspace/nonexistent.png"
        })
        
        tool_output = json.loads(result.content[0].text)
        test3_pass = False
        if tool_output.get('status') == 'error':
            print("✅ Error handling works correctly!")
            print(f"   Error message: {tool_output.get('stderr', 'N/A')}")
            test3_pass = True
        else:
            print("⚠️ Expected error but got success - this might be unexpected")
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Test 1 (Chemical structure): {'✅ PASS' if test1_pass else '❌ FAIL'}")
        print(f"Test 2 (Non-chemical structure): {'✅ PASS' if test2_pass else '❌ FAIL'}")
        print(f"Test 3 (Error handling): {'✅ PASS' if test3_pass else '❌ FAIL'}")
        
        all_pass = test1_pass and test2_pass and test3_pass
        print(f"\n{'🎉 ALL TESTS PASSED!' if all_pass else '⚠️ SOME TESTS FAILED!'}")
        print("=" * 60)
        
        return all_pass


def help():
    print("USAGE")
    print(f"\t{__file__} [port]")
    print(f"\nDefault port: 5150")
    print(f"To run with specific port:")
    print(f"  python {__file__} 5151")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help"]:
            help()
            sys.exit(0)
        elif sys.argv[1].isdigit():
            port = int(sys.argv[1])
        else:
            print("❌ Invalid port number. Use -h for help.")
            sys.exit(1)
    else:
        port = 5150
    
    print(f"🧪 Testing DECIMER Classifier MCP Server on port {port}")
    print("📌 Make sure the server is running first:")
    print("   ./mcp_host/decimer/run.sh")
    print()
    
    success = asyncio.run(test_decimer_classifier(port))
    sys.exit(0 if success else 1)
