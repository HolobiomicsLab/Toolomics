#!/usr/bin/env python3

"""
Test DECIMER Transformer MCP Tools

Tests the SMILES generation functionality using FastMCP client.
This test requires the DECIMER MCP server to be running on port 5150.

Author: Generated for HolobiomicsLab, CNRS
"""

import asyncio
import json
import os
import sys
import subprocess
from pathlib import Path

# Add FastMCP to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

try:
    from fastmcp import Client
except ImportError:
    print("❌ FastMCP not available. Please install it first.")
    print("   pip install fastmcp")
    sys.exit(1)


async def test_decimer_transformer(port: int = 5150):
    """Test DECIMER Transformer MCP tool comprehensively."""
    
    async with Client(f"http://localhost:{port}/mcp") as client:
        print("🚀 Connected to DECIMER MCP Server")
        
        # List available tools
        tools = await client.list_tools()
        print(f"📋 Available tools: {[tool.name for tool in tools]}")
        print()
        
        # Check if predict_smiles tool exists
        transformer_tool = None
        for tool in tools:
            if tool.name == "predict_smiles":
                transformer_tool = tool
                break
        
        if not transformer_tool:
            print("❌ predict_smiles tool not found!")
            return
        
        print("✅ Found predict_smiles tool")
        print(f"   Description: {transformer_tool.description}")
        
        # Test 1: SMILES generation from caffeine image
        print("\n" + "=" * 60)
        print("TEST 1: SMILES Generation from Caffeine Image")
        print("=" * 60)
        
        # Copy caffeine image to container first
        caffeine_container_path = "/app/workspace/caffeine.png"
        
        # Check if file exists locally
        caffeine_local_file = "/home/tjiang/repos/Mimosa_project/toolomics/DECIMER-Image-Classifier/tests/caffeine.png"
        if os.path.exists(caffeine_local_file):
            print(f"📁 Copying {caffeine_local_file} to container...")
            copy_cmd = f"docker cp {caffeine_local_file} decimer-mcp:/app/workspace/"
            if os.system(copy_cmd) == 0:
                print("✅ File copied successfully")
            else:
                print("❌ Failed to copy file")
                return
        else:
            print(f"❌ Local file not found: {caffeine_local_file}")
            return
        
        result = await client.call_tool("predict_smiles", {
            "image_path": caffeine_container_path
        })
        
        tool_output = json.loads(result.content[0].text)
        if tool_output.get('status') == 'success':
            stdout_data = json.loads(tool_output['stdout'])
            smiles = stdout_data.get('smiles', '')
            print("✅ SMILES generation successful!")
            print(f"   SMILES: {smiles}")
            print(f"   Length: {len(smiles)} characters")
            print(f"   Message: {stdout_data.get('message', 'N/A')}")
            
            # Validate SMILES format (basic checks)
            print("\n🔍 SMILES Validation:")
            if smiles:
                print(f"   - Contains parentheses: {'(' in smiles or ')' in smiles}")
                print(f"   - Contains brackets: {'[' in smiles or ']' in smiles}")
                print(f"   - Contains common atoms: {'C' in smiles}")
                print(f"   - Looks like caffeine: {'C' in smiles and len(smiles) > 20}")
            else:
                print("   - Empty SMILES generated")
        else:
            print(f"❌ SMILES generation failed: {tool_output.get('stderr', 'Unknown error')}")
        
        # Test 2: SMILES generation from non-chemical image
        print("\n" + "=" * 60)
        print("TEST 2: SMILES Generation from Non-Chemical Image")
        print("=" * 60)
        
        # Copy chinese character image to container
        chinese_local_file = "/home/tjiang/repos/Mimosa_project/toolomics/DECIMER-Image-Classifier/tests/chinese_character.jpg"
        chinese_container_path = "/app/workspace/chinese_character.jpg"
        
        if os.path.exists(chinese_local_file):
            print(f"📁 Copying {chinese_local_file} to container...")
            copy_cmd = f"docker cp {chinese_local_file} decimer-mcp:/app/workspace/"
            if os.system(copy_cmd) == 0:
                print("✅ File copied successfully")
            else:
                print("❌ Failed to copy file")
                return
        else:
            print(f"❌ Local file not found: {chinese_local_file}")
            
            # Create a simple test image as fallback
            print("🔧 Creating a simple test image instead...")
            create_cmd = """
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# Create a simple black rectangle
img_array = np.zeros((100, 100, 3), dtype=np.uint8)
img = Image.fromarray(img_array)
img.save('/app/workspace/test_image.png')
print('Created test image')
"""
            result_cmd = subprocess.run(["docker", "exec", "decimer-mcp", "python", "-c", create_cmd], 
                                      capture_output=True, text=True)
            if result_cmd.returncode == 0:
                print("✅ Created test image")
                chinese_container_path = "/app/workspace/test_image.png"
            else:
                print("❌ Failed to create test image")
                return
        
        result2 = await client.call_tool("predict_smiles", {
            "image_path": chinese_container_path
        })
        
        tool_output2 = json.loads(result2.content[0].text)
        if tool_output2.get('status') == 'success':
            stdout_data2 = json.loads(tool_output2['stdout'])
            smiles2 = stdout_data2.get('smiles', '')
            print("🔍 Non-chemical image processed:")
            print(f"   SMILES: {smiles2}")
            print(f"   Length: {len(smiles2)} characters")
            print(f"   Message: {stdout_data2.get('message', 'N/A')}")
            
            print("\n📝 Note: DECIMER may try to interpret any image as chemical structure")
        else:
            print(f"❌ Processing failed: {tool_output2.get('stderr', 'Unknown error')}")
        
        # Test 3: Error handling for non-existent file
        print("\n" + "=" * 60)
        print("TEST 3: Error Handling (Non-existent File)")
        print("=" * 60)
        
        result3 = await client.call_tool("predict_smiles", {
            "image_path": "/app/workspace/nonexistent.png"
        })
        
        tool_output3 = json.loads(result3.content[0].text)
        if tool_output3.get('status') == 'error':
            print("✅ Error correctly detected:")
            print(f"   Message: {tool_output3.get('stderr', 'Unknown error')}")
        else:
            print(f"❌ Expected error, but got: {tool_output3}")
        
        print("\n" + "=" * 60)
        print("📊 TRANSFORMER TEST SUMMARY")
        print("=" * 60)
        
        # Count results
        tests_passed = 0
        tests_total = 3
        
        if tool_output.get('status') == 'success':
            print("✅ Test 1 (Caffeine SMILES): PASSED")
            tests_passed += 1
        else:
            print("❌ Test 1 (Caffeine SMILES): FAILED")
        
        if tool_output2.get('status') == 'success':
            print("✅ Test 2 (Non-chemical image): PASSED")
            tests_passed += 1
        else:
            print("❌ Test 2 (Non-chemical image): FAILED")
        
        if tool_output3.get('status') == 'error':
            print("✅ Test 3 (Error handling): PASSED")
            tests_passed += 1
        else:
            print("❌ Test 3 (Error handling): FAILED")
        
        print(f"\n🎯 Results: {tests_passed}/{tests_total} tests passed")
        
        if tests_passed == tests_total:
            print("🎉 All transformer tests passed!")
        else:
            print("⚠️ Some transformer tests failed!")
        
        return tests_passed == tests_total


async def main():
    """Main test function."""
    print("🚀 DECIMER Transformer MCP Test Suite")
    print("=" * 50)
    print("Make sure the DECIMER MCP server is running on port 5150")
    print("Run: ./mcp_docker/decimer/run.sh")
    print()
    
    # Check if container is running
    try:
        result = subprocess.run(["docker", "ps", "--filter", "name=decimer-mcp", "--format", "{{.Names}}"], 
                               capture_output=True, text=True)
        if "decimer-mcp" not in result.stdout:
            print("❌ DECIMER MCP container is not running!")
            print("   Please start it first: ./mcp_docker/decimer/run.sh")
            return False
        else:
            print("✅ DECIMER MCP container is running")
    except Exception as e:
        print(f"❌ Error checking container status: {e}")
        return False
    
    # Run transformer tests
    success = await test_decimer_transformer()
    
    if success:
        print("\n🎉 All transformer tests completed successfully!")
        return True
    else:
        print("\n⚠️ Some transformer tests failed!")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)