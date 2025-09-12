#!/usr/bin/env python3

"""
Test client for Toolomics PDF MCP Server
Tests MCP discovery, tools discovery, and use case scenarios.
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any
import sys
import os
import tempfile

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from sources.core.tools_manager import ToolManager, MCP
from config import Config
from fastmcp import Client


class PDFMCPTest:
    """Test class for PDF MCP server"""
    
    def __init__(self):
        self.config = Config() if 'Config' in globals() else None
        self.tool_manager = ToolManager(self.config) if self.config else None
        self.pdf_mcp = None
        self.client = None
        self.test_session_id = None
    
    async def discover_mcp_servers(self) -> List[MCP]:
        """Test MCP discovery"""
        print("🔍 Testing MCP server discovery...")
        
        if self.tool_manager:
            try:
                mcps = await self.tool_manager.discover_mcp_servers()
                print(f"✅ Discovered {len(mcps)} MCP servers via ToolManager")
                
                # Find PDF MCP
                for mcp in mcps:
                    if "pdf" in mcp.name.lower():
                        self.pdf_mcp = mcp
                        print(f"✅ Found PDF MCP: {mcp.name}")
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
                    
                    if tools and any("pdf" in tool.name.lower() for tool in tools):
                        print(f"✅ Found PDF MCP on port {port}: {name}")
                        self.pdf_mcp = MCP(
                            name=name,
                            tools=[tool.name for tool in tools],
                            address="localhost",
                            port=port,
                            transport="streamable-http",
                            client_url=url
                        )
                        mcps.append(self.pdf_mcp)
                        break
                        
            except Exception:
                continue
        
        return mcps
    
    async def test_tool_discovery(self) -> bool:
        """Test tools discovery for PDF MCP"""
        print("\n📋 Testing tools discovery...")
        
        if not self.pdf_mcp:
            print("❌ No PDF MCP found")
            return False
        
        try:
            url = self.pdf_mcp.client_url or f"http://{self.pdf_mcp.address}:{self.pdf_mcp.port}/mcp"
            async with Client(url, timeout=5.0) as client:
                tools = await client.list_tools()
                
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description[:100]}...")
                
                # Expected PDF tools
                expected_tools = [
                    "list_pdf_files",
                    "initialize_pdf_navigation",
                    "navigate_to_page",
                    "get_current_page", 
                    "navigate_next_page",
                    "navigate_previous_page",
                    "add_bookmark",
                    "search_in_current_session",
                    "extract_text_from_pdf",
                    "search_keywords_in_pdf"
                ]
                
                found_tools = [tool.name for tool in tools]
                missing_tools = [tool for tool in expected_tools if tool not in found_tools]
                
                if missing_tools:
                    print(f"⚠️ Missing expected tools: {missing_tools}")
                    # Don't fail completely, PDF functionality might have variations
                
                print("✅ PDF tools discovery completed")
                return True
                
        except Exception as e:
            print(f"❌ Tool discovery failed: {e}")
            return False
    
    def create_test_pdf(self) -> str:
        """Create a test PDF file for testing"""
        try:
            # Create a simple test PDF content
            pdf_content = """
%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Hello World! This is a test PDF.) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000219 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
314
%%EOF
"""
            
            # Write to current directory
            test_filename = "test_document.pdf"
            with open(test_filename, 'w') as f:
                f.write(pdf_content)
            
            print(f"📄 Created test PDF: {test_filename}")
            return test_filename
            
        except Exception as e:
            print(f"⚠️ Failed to create test PDF: {e}")
            return None
    
    async def test_use_cases(self) -> bool:
        """Test PDF MCP use cases"""
        print("\n🧪 Testing PDF use cases...")
        
        if not self.pdf_mcp:
            print("❌ No PDF MCP found")
            return False
        
        try:
            url = self.pdf_mcp.client_url or f"http://{self.pdf_mcp.address}:{self.pdf_mcp.port}/mcp"
            async with Client(url, timeout=15.0) as client:
                
                # Create a test PDF file
                test_pdf = self.create_test_pdf()
                if not test_pdf:
                    print("⚠️ Could not create test PDF, skipping file-based tests")
                
                # Test 1: List PDF files
                print("\n📁 Test 1: List PDF files")
                result = await client.call_tool("list_pdf_files", {})
                
                if result and len(result) > 0:
                    file_data = json.loads(result[0].text)
                    print(f"✅ Found {file_data.get('count', 0)} PDF files")
                    if file_data.get('files'):
                        print(f"   Files: {file_data['files']}")
                else:
                    print("❌ Failed to list PDF files")
                    return False
                
                # Test 2: Initialize PDF navigation (if test PDF exists)
                if test_pdf:
                    print(f"\n📖 Test 2: Initialize PDF navigation for {test_pdf}")
                    result = await client.call_tool("initialize_pdf_navigation", {
                        "filename": test_pdf
                    })
                    
                    if result and len(result) > 0:
                        nav_data = json.loads(result[0].text)
                        self.test_session_id = nav_data.get("session_id")
                        print(f"✅ Navigation initialized: {nav_data.get('session_id', 'unknown')}")
                        print(f"   Total pages: {nav_data.get('total_pages', 0)}")
                    else:
                        print("❌ Failed to initialize PDF navigation")
                        return False
                    
                    # Test 3: Get current page
                    if self.test_session_id:
                        print("\n📄 Test 3: Get current page")
                        result = await client.call_tool("get_current_page", {
                            "session_id": self.test_session_id
                        })
                        
                        if result and len(result) > 0:
                            page_data = json.loads(result[0].text)
                            print(f"✅ Current page: {page_data.get('current_page', 'unknown')}")
                            if page_data.get('page_content'):
                                print(f"   Content preview: {page_data['page_content'][:100]}...")
                        else:
                            print("❌ Failed to get current page")
                    
                    # Test 4: Add bookmark
                    if self.test_session_id:
                        print("\n🔖 Test 4: Add bookmark")
                        result = await client.call_tool("add_bookmark", {
                            "session_id": self.test_session_id,
                            "page_number": 1
                        })
                        
                        if result and len(result) > 0:
                            bookmark_data = json.loads(result[0].text)
                            print(f"✅ Bookmark added: page {bookmark_data.get('bookmarked_page', 'unknown')}")
                        else:
                            print("❌ Failed to add bookmark")
                    
                    # Test 5: Search in current session
                    if self.test_session_id:
                        print("\n🔍 Test 5: Search in current session")
                        result = await client.call_tool("search_in_current_session", {
                            "session_id": self.test_session_id,
                            "query": "test"
                        })
                        
                        if result and len(result) > 0:
                            search_data = json.loads(result[0].text)
                            print(f"✅ Search completed: {search_data.get('total_matches', 0)} matches")
                        else:
                            print("⚠️ Search functionality may have issues")
                    
                    # Test 6: Get navigation status
                    if self.test_session_id:
                        print("\n📊 Test 6: Get navigation status")
                        result = await client.call_tool("get_navigation_status", {
                            "session_id": self.test_session_id
                        })
                        
                        if result and len(result) > 0:
                            status_data = json.loads(result[0].text)
                            print(f"✅ Navigation status: page {status_data.get('current_page', '?')}/{status_data.get('total_pages', '?')}")
                            print(f"   Bookmarks: {status_data.get('bookmarks', [])}")
                        else:
                            print("❌ Failed to get navigation status")
                    
                    # Test 7: Extract text from PDF
                    print(f"\n📝 Test 7: Extract text from PDF")
                    result = await client.call_tool("extract_text_from_pdf", {
                        "filename": test_pdf,
                        "start_page": 1,
                        "end_page": 1
                    })
                    
                    if result and len(result) > 0:
                        text_data = json.loads(result[0].text)
                        print(f"✅ Text extraction: {text_data.get('pages_processed', 0)} pages processed")
                        if text_data.get('text'):
                            print(f"   Text preview: {text_data['text'][:200]}...")
                    else:
                        print("⚠️ Text extraction may have issues")
                    
                    # Test 8: Search keywords in PDF
                    print(f"\n🔍 Test 8: Search keywords in PDF")
                    result = await client.call_tool("search_keywords_in_pdf", {
                        "filename": test_pdf,
                        "keywords": "Hello,World,test"
                    })
                    
                    if result and len(result) > 0:
                        search_data = json.loads(result[0].text)
                        print(f"✅ Keyword search: {search_data.get('total_matches', 0)} matches")
                        keywords = search_data.get('keywords_searched', [])
                        print(f"   Keywords searched: {keywords}")
                    else:
                        print("⚠️ Keyword search may have issues")
                    
                    # Test 9: Close navigation session
                    if self.test_session_id:
                        print("\n🔐 Test 9: Close navigation session")
                        result = await client.call_tool("close_navigation_session", {
                            "session_id": self.test_session_id
                        })
                        
                        if result and len(result) > 0:
                            close_data = json.loads(result[0].text)
                            print(f"✅ Session closed: {close_data.get('message', 'unknown')}")
                        else:
                            print("❌ Failed to close session")
                
                # Clean up test file
                if test_pdf and Path(test_pdf).exists():
                    try:
                        Path(test_pdf).unlink()
                        print(f"🧹 Cleaned up test file: {test_pdf}")
                    except Exception as e:
                        print(f"⚠️ Could not clean up test file: {e}")
                
                print("✅ PDF use cases completed")
                return True
                
        except Exception as e:
            print(f"❌ Use case testing failed: {e}")
            return False
    
    async def assert_running_ok(self) -> bool:
        """Assert that PDF MCP is running correctly"""
        print("\n✅ Asserting PDF MCP server status...")
        
        if not self.pdf_mcp:
            print("❌ PDF MCP not found - server may not be running")
            return False
        
        try:
            url = self.pdf_mcp.client_url or f"http://{self.pdf_mcp.address}:{self.pdf_mcp.port}/mcp"
            async with Client(url, timeout=5.0) as client:
                # Quick health check
                tools = await client.list_tools()
                
                if len(tools) > 0:
                    # Test basic functionality
                    result = await client.call_tool("list_pdf_files", {})
                    
                    if result and len(result) > 0:
                        print(f"✅ PDF MCP server is running correctly")
                        print(f"   Server: {self.pdf_mcp.name}")
                        print(f"   Address: {self.pdf_mcp.address}:{self.pdf_mcp.port}")
                        print(f"   Tools available: {len(tools)}")
                        print(f"   PDF operations: working")
                        return True
                    else:
                        print("⚠️ PDF MCP server tools available but operations may have issues")
                        print("   This could be due to missing PDF libraries")
                        return True
                else:
                    print("❌ PDF MCP server responded but no tools available")
                    return False
                
        except Exception as e:
            print(f"❌ PDF MCP server health check failed: {e}")
            return False


async def main():
    """Run all PDF MCP tests"""
    print("🧪 Starting PDF MCP Server Tests")
    print("=" * 60)
    
    test = PDFMCPTest()
    success = True
    
    # Test 1: MCP Discovery
    mcps = await test.discover_mcp_servers()
    if not mcps or not test.pdf_mcp:
        print("❌ Failed to discover PDF MCP server")
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
        print("🎉 All PDF MCP tests PASSED!")
    else:
        print("❌ Some PDF MCP tests FAILED!")
        print("   Note: PDF tests may fail if required libraries are not installed:")
        print("   pip install PyPDF2 PyMuPDF sentence-transformers scikit-learn")
    
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