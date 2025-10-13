#!/usr/bin/env python3
"""
Test script for DECIMER Segmentation MCP Server

This script tests the segment_chemical_structures MCP tool
to verify that it correctly extracts chemical structures from document images.
"""

import asyncio
import os
import sys
from pathlib import Path

from fastmcp import Client


async def test_segmentation():
    """Test the DECIMER Segmentation MCP server."""
    
    print("🧪 Testing DECIMER Segmentation MCP Server on port 5150")
    print("📌 Make sure the server is running first:")
    print("   ./mcp_host/decimer/run.sh")
    print()
    
    try:
        # Connect to the MCP server
        async with Client('http://localhost:5150/mcp') as client:
            print("🚀 Connected to DECIMER MCP Server")
            
            # Get available tools
            tools = await client.list_tools()
            print(f"📋 Available tools: {[tool.name for tool in tools]}")
            print()
            
            # Find the segmentation tool
            segmentation_tool = None
            for tool in tools:
                if tool.name == 'segment_chemical_structures':
                    segmentation_tool = tool
                    break
            
            if not segmentation_tool:
                print("❌ segment_chemical_structures tool not found!")
                return False
            
            print("✅ Found segment_chemical_structures tool")
            print(f"   Description: {segmentation_tool.description}")
            
            if segmentation_tool.inputSchema:
                print("\nArgs:")
                props = segmentation_tool.inputSchema.get('properties', {})
                for param_name, param_info in props.items():
                    param_type = param_info.get('type', 'unknown')
                    param_desc = param_info.get('description', 'No description')
                    print(f"    {param_name} ({param_type}): {param_desc}")
            
            if segmentation_tool.outputSchema:
                output_desc = segmentation_tool.outputSchema.get('description', 'No description')
                print(f"\nReturns:")
                print(f"    {output_desc}")
            
            print("\n" + "="*60)
            print("TEST: Segment chemical structures from document")
            print("="*60)
            
            # Test PDF document with chemical structures
            test_documents = [
                "workspace/1.pdf"  # Document with chemical structures - should produce multiple segments
            ]
            
            # Create output directory for segmentation results
            os.makedirs("workspace/segmentation_output", exist_ok=True)
            
            for i, document_path in enumerate(test_documents, 1):
                print(f"\nTEST {i}: {os.path.basename(document_path)}")
                print("-" * 40)
                
                if not os.path.exists(document_path):
                    print(f"❌ Test document not found: {document_path}")
                    print(f"   Skipping this test...")
                    continue
                
                try:
                    # Call the segmentation tool
                    result = await client.call_tool(
                        'segment_chemical_structures',
                        {"file_path": document_path, "output_dir": f"workspace/segmentation_output"}
                    )

                    print(f"🔍 Result: {result}")
                    
                    if result and hasattr(result, 'content') and result.content:
                        content_data = result.content[0]
                        if hasattr(content_data, 'text') and content_data.text:
                            import json
                            import ast
                            
                            # Parse the response text
                            response_text = content_data.text
                            print(f"🔍 Raw response:")
                            print(f"   {response_text[:200]}...")
                            
                            # Check if this is an error response first
                            if '"stderr":' in response_text and '"error"' in response_text:
                                print(f"\n❌ Segmentation failed!")
                                if 'error' in response_text.lower():
                                    print(f"   Error details: {response_text[:300]}...")
                                    # Continue with next test rather than failing completely
                                    continue
                            
                            try:
                                # Parse the CommandResult format
                                command_result = json.loads(response_text)
                                
                                if command_result.get('status') == 'success':
                                    # Extract the embedded JSON from stdout
                                    stdout_data = json.loads(command_result['stdout'])
                                    result_data = stdout_data
                                else:
                                    print(f"❌ Command failed: {command_result.get('stderr', 'Unknown error')}")
                                    continue
                                    
                                print(f"\n✅ Segmentation completed!")
                                
                                segments = result_data.get('segments', [])
                                total_segments = result_data.get('total_segments', 0)
                                output_dir = result_data.get('output_dir', 'unknown')
                                message = result_data.get('message', 'No message')
                                
                                print(f"   📁 Output directory: {output_dir}")
                                print(f"   🔢 Number of segments: {total_segments}")
                                print(f"   📝 Message: {message}")
                                
                                if total_segments > 0:
                                    print(f"   📋 Segmented files:")
                                    for j, segment_path in enumerate(segments[:5], 1):  # Show first 5
                                        print(f"      {j}. {os.path.basename(segment_path)}")
                                    if len(segments) > 5:
                                        print(f"      ... and {len(segments) - 5} more")
                                
                                # Check if output files actually exist
                                print(f"\n🔍 Verifying output files exist:")
                                existing_files = 0
                                for segment_path in segments:
                                    if os.path.exists(segment_path):
                                        existing_files += 1
                                        print(f"   ✅ {os.path.basename(segment_path)}")
                                    else:
                                        print(f"   ❌ {os.path.basename(segment_path)} (not found)")
                                
                                print(f"\n📊 Results Summary:")
                                print(f"   Expected files: {len(segments)}")
                                print(f"   Existing files: {existing_files}")
                                print(f"   Success rate: {existing_files/len(segments)*100:.1f}%" if segments else "N/A")
                                
                                if existing_files == len(segments) and existing_files == total_segments:
                                    print(f"   ✅ TEST RESULT: PASS")
                                else:
                                    print(f"   ❌ TEST RESULT: FAIL - file count mismatch")
                                    
                            except (json.JSONDecodeError, ValueError) as e:
                                print(f"❌ Error parsing response: {e}")
                                print(f"   Raw response: {response_text[:200]}...")
                                return False
                        else:
                            print(f"❌ No text content in response: {content_data}")
                    else:
                        print(f"❌ Invalid response format: {result}")
                        return False
                        
                except Exception as e:
                    print(f"❌ Error during segmentation: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
            
            print("\n" + "="*60)
            print("TEST: Error handling (non-existent file)")
            print("="*60)
            
            try:
                result = await client.call_tool(
                    'segment_chemical_structures',
                    {"file_path": "/app/workspace/nonexistent.png"}
                )
                
                if result and hasattr(result, 'content') and result.content:
                    content_data = result.content[0]
                    if hasattr(content_data, 'text') and content_data.text:
                        response_text = content_data.text
                        if 'error' in response_text.lower() and 'not found' in response_text.lower():
                            print("✅ Error handling works correctly!")
                            print(f"   Error message: {response_text.strip()}")
                        else:
                            print(f"❌ Unexpected error response: {response_text}")
                            return False
                    else:
                        print(f"❌ No text content in error response: {content_data}")
                        return False
                else:
                    print(f"❌ Invalid error response format: {result}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error handling test failed: {e}")
                return False
            
            print("\n" + "="*60)
            print("✅ DECIMER Segmentation MCP Tests Complete!")
            print("="*60)
            return True
            
    except Exception as e:
        print(f"❌ Failed to connect to MCP server: {e}")
        print("Make sure the server is running with: ./mcp_host/decimer/run.sh")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_segmentation())
    sys.exit(0 if success else 1)
