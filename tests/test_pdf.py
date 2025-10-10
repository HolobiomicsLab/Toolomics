#!/usr/bin/env python3

"""
Test client for PDF MCP Server
Demonstrates all functionality with realistic test scenarios including
navigation, RAG queries, text extraction, and keyword search.
"""

import asyncio
import json
import tempfile
import os
import sys
from pathlib import Path
from fastmcp import Client

def get_stdout_as_json(result):
    tool_output = json.loads(result.content[0].text) if result else {}
    stdout = tool_output.get('stdout', '{}')
    return json.loads(stdout)

async def test_pdf_operations(port=5002):
    """Test all PDF operations comprehensively."""
    
    # Connect to the MCP server
    async with Client(f"http://localhost:{port}/mcp") as client:
        print("🚀 Connected to PDF MCP Server")
        
        # List available tools
        tools = await client.list_tools()
        print(f"📋 Available tools: {[tool.name for tool in tools]}")
        print()
        
        # Test 1: List PDF files and get first one for testing
        print("=" * 50)
        print("TEST 1: Listing PDF files and selecting first one")
        print("=" * 50)
        
        result = await client.call_tool("list_pdf_files", {})
        files_data = get_stdout_as_json(result)
        print(f"📁 Found {files_data.get('count', 0)} PDF files:")
        for filename in files_data.get('files', []):
            print(f"  - {filename}")
        
        # Get the first PDF file for testing
        pdf_files = files_data.get('files', [])
        if not pdf_files:
            print("❌ No PDF files found in workspace. Please add a PDF file to test.")
            return
        
        test_pdf_filename = pdf_files[0]
        print(f"📄 Using '{test_pdf_filename}' for testing")
        print()
        
        # Test 2: Initialize PDF navigation
        print("=" * 50)
        print("TEST 2: Initialize PDF navigation")
        print("=" * 50)
        
        result = await client.call_tool("initialize_pdf_navigation", {
            "filename": test_pdf_filename
        })
        nav_data = get_stdout_as_json(result)
        session_id = nav_data.get('session_id')
        print(f"📖 Navigation initialized:")
        print(f"  Session ID: {session_id}")
        print(f"  Total pages: {nav_data.get('total_pages', 0)}")
        print(f"  Current page: {nav_data.get('current_page', 0)}")
        print()
        
        if not session_id:
            print("❌ Failed to initialize navigation. Stopping tests.")
            return
        
        # Test 3: Get current page
        print("=" * 50)
        print("TEST 3: Get current page content")
        print("=" * 50)
        
        result = await client.call_tool("get_current_page", {
            "session_id": session_id
        })
        page_data = get_stdout_as_json(result)
        print(f"📄 Current page {page_data.get('current_page', 0)}:")
        content = page_data.get('page_content', '')
        print(f"  Content preview: {content[:100]}...")
        print(f"  Has previous: {page_data.get('navigation_info', {}).get('has_previous', False)}")
        print(f"  Has next: {page_data.get('navigation_info', {}).get('has_next', False)}")
        print()
        
        # Test 4: Navigate to next page
        print("=" * 50)
        print("TEST 4: Navigate to next page")
        print("=" * 50)
        
        result = await client.call_tool("navigate_next_page", {
            "session_id": session_id
        })
        next_page_data = get_stdout_as_json(result)
        print(f"➡️ Navigated to page {next_page_data.get('current_page', 0)}")
        content = next_page_data.get('page_content', '')
        print(f"  Content preview: {content[:100]}...")
        print()
        
        # Test 5: Navigate to specific page (use last page or page 2 if available)
        print("=" * 50)
        print("TEST 5: Navigate to specific page")
        print("=" * 50)
        
        total_pages = nav_data.get('total_pages', 1)
        target_page = min(total_pages, max(2, total_pages))  # Go to last page or page 2, whichever is valid
        
        result = await client.call_tool("navigate_to_page", {
            "session_id": session_id,
            "page_number": target_page
        })
        specific_page_data = get_stdout_as_json(result)

        print(f"🎯 Navigated to page {specific_page_data.get('current_page', 0)}")
        content = specific_page_data.get('page_content', '')
        print(f"  Content preview: {content[:100]}...")
        print()
        
        # Test 6: Add bookmarks
        print("=" * 50)
        print("TEST 6: Add bookmarks")
        print("=" * 50)
        
        # Bookmark current page
        result = await client.call_tool("add_bookmark", {
            "session_id": session_id
        })
        bookmark_data = get_stdout_as_json(result)
        print(f"🔖 Added bookmark to page {bookmark_data.get('bookmarked_page', 0)}")
        
        # Bookmark page 1
        result = await client.call_tool("add_bookmark", {
            "session_id": session_id,
            "page_number": 1
        })
        bookmark_data = get_stdout_as_json(result)
        print(f"🔖 Added bookmark to page {bookmark_data.get('bookmarked_page', 0)}")
        print(f"  All bookmarks: {bookmark_data.get('all_bookmarks', [])}")
        print()
        
        # Test 7: Navigate to previous page
        print("=" * 50)
        print("TEST 7: Navigate to previous page")
        print("=" * 50)
        
        result = await client.call_tool("navigate_previous_page", {
            "session_id": session_id
        })
        prev_page_data = get_stdout_as_json(result)
        print(f"⬅️ Navigated to page {prev_page_data.get('current_page', 0)}")
        content = prev_page_data.get('page_content', '')
        print(f"  Content preview: {content[:100]}...")
        print()
        
        # Test 8: Search in current session (use common words)
        print("=" * 50)
        print("TEST 8: Search in current session")
        print("=" * 50)
        
        result = await client.call_tool("search_in_current_session", {
            "session_id": session_id,
            "query": "the"
        })
        search_data = get_stdout_as_json(result)
        print(f"🔍 Search for 'the': {search_data.get('total_matches', 0)} matches")
        print(f"  Navigated to first match on page: {search_data.get('current_page', 0)}")
        for i, match in enumerate(search_data.get('matches', [])[:3]):  # Show first 3 matches
            print(f"  Match {i+1} on page {match.get('page_number', 0)}: {match.get('context', '')[:50]}...")
        print()
        
        # Test 9: RAG query in current session (use generic terms)
        print("=" * 50)
        print("TEST 9: RAG query in current session")
        print("=" * 50)
        
        result = await client.call_tool("rag_query_current_session", {
            "session_id": session_id,
            "query": "analysis and data",
            "top_k": 2
        })
        rag_data = get_stdout_as_json(result)
        print(f"🤖 RAG query results: {len(rag_data.get('results', []))} chunks")
        print(f"  Searched {rag_data.get('total_chunks_searched', 0)} chunks")
        print(f"  Navigated to most relevant page: {rag_data.get('current_page', 0)}")
        for i, result_chunk in enumerate(rag_data.get('results', [])):
            print(f"  Result {i+1} (page {result_chunk.get('page_number', 0)}, score: {result_chunk.get('similarity_score', 0):.3f}):")
            print(f"    {result_chunk.get('text', '')[:80]}...")
        print()
        
        # Test 10: RAG query with different scopes
        print("=" * 50)
        print("TEST 10: RAG query with bookmarks scope")
        print("=" * 50)
        
        result = await client.call_tool("rag_query_current_session", {
            "session_id": session_id,
            "query": "information and results",
            "top_k": 2,
            "search_scope": "bookmarks"
        })
        rag_bookmarks_data = get_stdout_as_json(result)
        print(f"🔖 RAG query on bookmarks: {len(rag_bookmarks_data.get('results', []))} chunks")
        print(f"  Search scope: {rag_bookmarks_data.get('search_scope', 'unknown')}")
        for i, result_chunk in enumerate(rag_bookmarks_data.get('results', [])):
            print(f"  Result {i+1} (page {result_chunk.get('page_number', 0)}, score: {result_chunk.get('similarity_score', 0):.3f})")
        print()
        
        # Test 11: Get navigation status
        print("=" * 50)
        print("TEST 11: Get navigation status")
        print("=" * 50)
        
        result = await client.call_tool("get_navigation_status", {
            "session_id": session_id
        })
        status_data = get_stdout_as_json(result)
        print(f"📊 Navigation Status:")
        print(f"  Current page: {status_data.get('current_page', 0)}/{status_data.get('total_pages', 0)}")
        print(f"  Progress: {status_data.get('navigation_info', {}).get('progress_percentage', 0)}%")
        print(f"  Bookmarks: {status_data.get('bookmarks', [])}")
        print(f"  Search history: {status_data.get('search_history', [])}")
        print()
        
        # Test 12: Extract text from PDF (standalone function)
        print("=" * 50)
        print("TEST 12: Extract text from PDF")
        print("=" * 50)
        
        result = await client.call_tool("extract_text_from_pdf", {
            "filename": test_pdf_filename,
            "start_page": 1,
            "end_page": 2
        })
        extract_data = get_stdout_as_json(result)
        print(f"📄 Text extraction:")
        print(f"  Pages processed: {extract_data.get('pages_processed', 0)}")
        print(f"  Total pages: {extract_data.get('total_pages', 0)}")
        extracted_text = extract_data.get('text', '')
        print(f"  Text preview: {extracted_text[:200]}...")
        print()
        
        # Test 13: Search keywords in PDF
        print("=" * 50)
        print("TEST 13: Search keywords in PDF")
        print("=" * 50)
        
        result = await client.call_tool("search_keywords_in_pdf", {
            "filename": test_pdf_filename,
            "keywords": "the, and, of, to, in",
            "case_sensitive": False
        })
        keyword_data = get_stdout_as_json(result)
        print(f"🔍 Keyword search results:")
        print(f"  Total matches: {keyword_data.get('total_matches', 0)}")
        print(f"  Keywords searched: {keyword_data.get('keywords_searched', [])}")
        for i, match in enumerate(keyword_data.get('matches', [])[:5]):  # Show first 5 matches
            print(f"  Match {i+1}: '{match.get('keyword', '')}' on page {match.get('page', 0)}")
            print(f"    Context: {match.get('context', '')[:60]}...")
        print()
        
        # Test 15: Close navigation session
        print("=" * 50)
        print("TEST 15: Close navigation session")
        print("=" * 50)
        
        result = await client.call_tool("close_navigation_session", {
            "session_id": session_id
        })
        close_data = get_stdout_as_json(result)
        print(f"Session closed:")
        print(f"  Session ID: {close_data.get('session_id', 'unknown')}")
        print(f"  Message: {close_data.get('message', 'No message')}")
        print()
        
        # Test 16: Verify session is closed
        print("=" * 50)
        print("TEST 16: Verify session cleanup")
        print("=" * 50)
        
        result = await client.call_tool("get_navigation_status", {
            "session_id": session_id
        })
        print(f"✅ Session cleanup verification: {result.content[0].text}")
        print()
        
        print("\n🎉 All PDF tests completed successfully!")

def help():
    print("USAGE")
    print(f"\t{sys.argv[0]} <port>")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        help()
        exit()
    print("🧪 Starting PDF MCP Server Tests\n")
    port = sys.argv[1]
    asyncio.run(test_pdf_operations(port))
