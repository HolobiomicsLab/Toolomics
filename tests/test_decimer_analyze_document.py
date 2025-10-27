#!/usr/bin/env python3

"""
Test DECIMER analyze_chemical_document MCP Tool

Tests the complete chemical document analysis workflow:
- Segmentation of chemical structures
- Classification of each segment
- SMILES generation for chemical structures
- Comprehensive results and statistics

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


async def test_analyze_chemical_document(port: int = 5150):
    """Test DECIMER analyze_chemical_document MCP tool comprehensively."""
    
    async with Client(f"http://localhost:{port}/mcp") as client:
        print("🚀 Connected to DECIMER MCP Server")
        
        # List available tools
        tools = await client.list_tools()
        print(f"📋 Available tools: {[tool.name for tool in tools]}")
        print()
        
        # Check if analyze_chemical_document tool exists
        analyze_tool = None
        for tool in tools:
            if tool.name == "analyze_chemical_document":
                analyze_tool = tool
                break
        
        if not analyze_tool:
            print("❌ analyze_chemical_document tool not found!")
            return
        
        print("✅ Found analyze_chemical_document tool")
        print(f"   Description: {analyze_tool.description}")
        
        # Test 1: Analyze PDF document with chemical structures
        print("\n" + "=" * 70)
        print("TEST 1: Complete Analysis of PDF Document (1.pdf)")
        print("=" * 70)
        
        # Use the existing PDF file
        pdf_path = "workspace/1.pdf"
        
        # Check if PDF exists in container
        check_cmd = ["docker", "exec", "decimer-mcp", "test", "-f", pdf_path]
        if subprocess.run(check_cmd, capture_output=True).returncode != 0:
            print(f"❌ PDF file not found in container: {pdf_path}")
            print("   Please ensure 1.pdf is in the workspace directory")
            return
        
        print(f"📄 Analyzing PDF: {pdf_path}")
        
        result = await client.call_tool("analyze_chemical_document", {
            "document_path": pdf_path,
            "output_dir": "workspace/analysis_output"
        })
        
        tool_output = json.loads(result.content[0].text)
        if tool_output.get('status') == 'success':
            stdout_data = json.loads(tool_output['stdout'])
            
            print("✅ Document analysis successful!")
            print(f"📊 Analysis Summary:")
            
            summary = stdout_data.get('summary', {})
            print(f"   - Total segments found: {summary.get('total_segments', 'N/A')}")
            print(f"   - Chemical structures: {summary.get('chemical_structures', 'N/A')}")
            print(f"   - Non-chemical segments: {summary.get('non_chemical', 'N/A')}")
            
            results = stdout_data.get('results', [])
            print(f"\n🔍 Detailed Results ({len(results)} segments):")
            
            chemical_count = 0
            for i, result_item in enumerate(results):
                image_path = result_item.get('image_path', 'N/A')
                classification = result_item.get('classification', {})
                smiles_prediction = result_item.get('smiles_prediction', {})
                
                is_chemical = classification.get('is_chemical', False)
                confidence = classification.get('confidence_score', 'N/A')
                smiles = smiles_prediction.get('smiles', '')
                
                print(f"\n   Segment {i+1}:")
                print(f"     📁 File: {os.path.basename(image_path)}")
                print(f"     🧪 Is Chemical: {is_chemical}")
                print(f"     📊 Confidence: {confidence}")
                
                if is_chemical:
                    chemical_count += 1
                    if smiles:
                        print(f"     🧬 SMILES: {smiles}")
                    else:
                        print(f"     ⚠️ No SMILES generated")
                else:
                    print(f"     📝 Non-chemical segment")
            
            print(f"\n🎯 Summary:")
            print(f"   - Successfully analyzed {len(results)} segments")
            print(f"   - Found {chemical_count} chemical structures")
            print(f"   - Generated SMILES for chemical structures")
            
        else:
            print(f"❌ Document analysis failed: {tool_output.get('stderr', 'Unknown error')}")
            return False
        
        # Test 2: Analyze single chemical structure image
        print("\n" + "=" * 70)
        print("TEST 2: Analysis of Single Chemical Structure Image")
        print("=" * 70)
        
        # Copy caffeine image to container
        caffeine_local_file = "/home/tjiang/repos/Mimosa_project/toolomics/DECIMER-Image-Classifier/tests/caffeine.png"
        caffeine_container_path = "workspace/caffeine.png"
        
        #if os.path.exists(caffeine_local_file):
        #    print(f"📁 Copying {caffeine_local_file} to container...")
        #    copy_cmd = f"docker cp {caffeine_local_file} decimer-mcp:/app/workspace/"
        #    if os.system(copy_cmd) == 0:
        #        print("✅ File copied successfully")
        #    else:
        #        print("❌ Failed to copy file")
        #        return False
        #else:
        #    print(f"❌ Local file not found: {caffeine_local_file}")
        #    return False
        
        print(f"🧪 Analyzing single chemical structure: {caffeine_container_path}")
        
        result2 = await client.call_tool("analyze_chemical_document", {
            "document_path": caffeine_container_path,
            "output_dir": "workspace/single_analysis_output"
        })
        
        tool_output2 = json.loads(result2.content[0].text)
        if tool_output2.get('status') == 'success':
            stdout_data2 = json.loads(tool_output2['stdout'])
            
            print("✅ Single structure analysis successful!")
            
            summary2 = stdout_data2.get('summary', {})
            print(f"📊 Analysis Summary:")
            print(f"   - Total segments: {summary2.get('total_segments', 'N/A')}")
            print(f"   - Chemical structures: {summary2.get('chemical_structures', 'N/A')}")
            
            results2 = stdout_data2.get('results', [])
            if results2:
                result_item = results2[0]  # Should be only one segment
                classification = result_item.get('classification', {})
                smiles_prediction = result_item.get('smiles_prediction', {})
                
                is_chemical = classification.get('is_chemical', False)
                confidence = classification.get('confidence_score', 'N/A')
                smiles = smiles_prediction.get('smiles', '')
                
                print(f"\n🔍 Single Structure Analysis:")
                print(f"   🧪 Is Chemical: {is_chemical}")
                print(f"   📊 Confidence: {confidence}")
                if smiles:
                    print(f"   🧬 SMILES: {smiles}")
                else:
                    print(f"   ⚠️ No SMILES generated")
            else:
                print("❌ No results returned")
                
        else:
            print(f"❌ Single structure analysis failed: {tool_output2.get('stderr', 'Unknown error')}")
            return False
        
        # Test 3: Error handling for non-existent file
        print("\n" + "=" * 70)
        print("TEST 3: Error Handling (Non-existent File)")
        print("=" * 70)
        
        result3 = await client.call_tool("analyze_chemical_document", {
            "document_path": "/app/workspace/nonexistent.pdf",
            "output_dir": "/app/workspace/error_test_output"
        })
        
        tool_output3 = json.loads(result3.content[0].text)
        if tool_output3.get('status') == 'error':
            print("✅ Error correctly detected:")
            print(f"   Message: {tool_output3.get('stderr', 'Unknown error')}")
        else:
            print(f"❌ Expected error, but got: {tool_output3}")
            return False
        
        print("\n" + "=" * 70)
        print("📊 ANALYZE CHEMICAL DOCUMENT TEST SUMMARY")
        print("=" * 70)
        
        # Count results
        tests_passed = 0
        tests_total = 3
        
        if tool_output.get('status') == 'success':
            print("✅ Test 1 (PDF Document Analysis): PASSED")
            tests_passed += 1
        else:
            print("❌ Test 1 (PDF Document Analysis): FAILED")
        
        if tool_output2.get('status') == 'success':
            print("✅ Test 2 (Single Structure Analysis): PASSED")
            tests_passed += 1
        else:
            print("❌ Test 2 (Single Structure Analysis): FAILED")
        
        if tool_output3.get('status') == 'error':
            print("✅ Test 3 (Error handling): PASSED")
            tests_passed += 1
        else:
            print("❌ Test 3 (Error handling): FAILED")
        
        print(f"\n🎯 Results: {tests_passed}/{tests_total} tests passed")
        
        if tests_passed == tests_total:
            print("🎉 All analyze_chemical_document tests passed!")
        else:
            print("⚠️ Some analyze_chemical_document tests failed!")
        
        return tests_passed == tests_total


async def main():
    """Main test function."""
    print("🚀 DECIMER analyze_chemical_document MCP Test Suite")
    print("=" * 60)
    print("Make sure the DECIMER MCP server is running on port 5150")
    print("Run: ./mcp_docker/decimer/run.sh")
    print()
    
    ## Check if container is running
    #try:
    #    result = subprocess.run(["docker", "ps", "--filter", "name=decimer-mcp", "--format", "{{.Names}}"], 
    #                           capture_output=True, text=True)
    #    if "decimer-mcp" not in result.stdout:
    #        print("❌ DECIMER MCP container is not running!")
    #        print("   Please start it first: ./mcp_docker/decimer/run.sh")
    #        return False
    #    else:
    #        print("✅ DECIMER MCP container is running")
    #except Exception as e:
    #    print(f"❌ Error checking container status: {e}")
    #    return False
    
    # Run analyze_chemical_document tests
    success = await test_analyze_chemical_document()
    
    if success:
        print("\n🎉 All analyze_chemical_document tests completed successfully!")
        return True
    else:
        print("\n⚠️ Some analyze_chemical_document tests failed!")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
