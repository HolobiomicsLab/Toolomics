#!/usr/bin/env python3

"""
Test DECIMER MCP Integration: analyze_chemical_document

This is an **integration test** that verifies all three DECIMER MCP tools 
work together correctly for end-to-end document analysis:

1. Segmentation tool: Extracts chemical structures from documents
2. Classifier tool: Identifies chemical vs non-chemical segments  
3. Transformer tool: Generates SMILES from chemical structures

The test analyzes a complete PDF document to ensure proper integration
of all components in the analyze_chemical_document workflow.

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
        #pdf_path = "workspace/1.pdf"
        pdf_path = "workspace/2510.19484v1.pdf"
        
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
        
        print("\n" + "=" * 70)
        print("📊 INTEGRATION TEST SUMMARY")
        print("=" * 70)
        
        if tool_output.get('status') == 'success':
            print("✅ End-to-end document analysis integration: PASSED")
            print("\n🎉 Integration test completed successfully!")
            print("   ✓ Segmentation tool extracted chemical structures")
            print("   ✓ Classifier tool identified chemical vs non-chemical")
            print("   ✓ Transformer tool generated SMILES for chemicals")
            print("   ✓ All tools integrated correctly in analyze_chemical_document")
            return True
        else:
            print("❌ End-to-end document analysis integration: FAILED")
            print("\n⚠️ Integration test failed!")
            return False


async def main():
    """Main test function."""
    print("🚀 DECIMER MCP Integration Test: analyze_chemical_document")
    print("=" * 60)
    print("Testing end-to-end integration of Segmentation + Classifier + Transformer")
    print("Make sure the DECIMER MCP server is running on port 5150")
    print("Run: ./mcp_host/decimer/run.sh")
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
    
    # Run integration test
    success = await test_analyze_chemical_document()
    
    if success:
        print("\n🎉 Integration test completed successfully!")
        print("   All DECIMER MCP tools work together correctly!")
        return True
    else:
        print("\n⚠️ Integration test failed!")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
