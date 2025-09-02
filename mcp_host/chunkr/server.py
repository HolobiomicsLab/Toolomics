#!/usr/bin/env python3

"""
Chunkr MCP Server

Provides document intelligence tools for converting various document types into RAG/LLM-ready chunks.
Supports PDFs, PPTs, Word docs, and images through Chunkr's API for layout analysis, OCR, 
and semantic chunking.

Author: Toolomics Integration - HolobiomicsLab, CNRS
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests
from dataclasses import dataclass

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from shared import CommandResult, return_as_dict

# Chunkr imports
try:
    from chunkr_ai import Chunkr
    CHUNKR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Chunkr library not available: {e}")
    print("Install with: pip install chunkr-ai")
    CHUNKR_AVAILABLE = False

from fastmcp import FastMCP

description = """
Chunkr MCP Server provides document intelligence tools for converting various document types 
into RAG/LLM-ready chunks. Features include layout analysis, OCR, semantic chunking, and 
export to multiple formats (HTML, Markdown, JSON). Supports PDFs, PPTs, Word docs, and images.
All operations work with files in the centralized workspace directory.
"""

mcp = FastMCP(
    name="Chunkr Document Intelligence",
    instructions=description,
)

# Global Chunkr client instance
_chunkr_client = None


def get_chunkr_client():
    """Get or create Chunkr client instance"""
    global _chunkr_client
    if _chunkr_client is None:
        api_key = os.environ.get("CHUNKR_API_KEY")
        if not api_key:
            raise ValueError(
                "CHUNKR_API_KEY environment variable not set. Get your API key from chunkr.ai"
            )
        _chunkr_client = Chunkr(api_key=api_key)
    return _chunkr_client


def check_api_key_available():
    """Check if Chunkr API key is available"""
    api_key = os.environ.get("CHUNKR_API_KEY")
    return api_key is not None and api_key.strip() != ""


@dataclass
class ChunkrTask:
    """Information about a Chunkr processing task"""
    task_id: str
    status: str
    filename: str
    file_type: str
    created_at: str
    expires_at: Optional[str] = None


@mcp.tool
def get_mcp_name() -> str:
    """Get the name of this MCP server
    
    Returns:
        str: The name of this MCP server ("Chunkr Document Intelligence")
    """
    return "Chunkr Document Intelligence"


@mcp.tool
@return_as_dict
def list_workspace_documents() -> Dict[str, Any]:
    """List all supported documents in the workspace directory
    
    Returns:
        Dict containing:
            - status: "success" or "error"
            - files: List of document filenames with their types
            - count: Number of documents found
            - supported_types: List of supported file extensions
    """
    try:
        workspace_path = Path("/workspace")
        if not workspace_path.exists():
            workspace_path = Path.cwd()
        
        # Supported file types by Chunkr
        supported_extensions = ['.pdf', '.ppt', '.pptx', '.doc', '.docx', '.png', '.jpg', '.jpeg']
        
        documents = []
        for ext in supported_extensions:
            files = list(workspace_path.glob(f"*{ext}"))
            for file in files:
                documents.append({
                    "filename": file.name,
                    "type": ext[1:],  # Remove the dot
                    "size": file.stat().st_size,
                    "path": str(file)
                })
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "files": documents,
                "count": len(documents),
                "supported_types": [ext[1:] for ext in supported_extensions],
                "workspace": str(workspace_path)
            })
        )
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to list workspace documents: {str(e)}",
            exit_code=1
        )


@mcp.tool
@return_as_dict
async def upload_document(filename: str, processing_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Upload a document to Chunkr for processing
    
    Args:
        filename: Name of the document file in workspace
        processing_config: Optional processing configuration (OCR settings, chunk size, etc.)
        
    Returns:
        Dict containing:
            - status: "success" or "error"
            - task_id: Chunkr task ID for tracking processing
            - task_info: Task information including status and metadata
    """
    if not CHUNKR_AVAILABLE:
        return CommandResult(
            status="error",
            stderr="Chunkr library not available. Install with: pip install chunkr-ai",
            exit_code=1
        )
    
    try:
        workspace_path = Path("/workspace")
        if not workspace_path.exists():
            workspace_path = Path.cwd()
            
        file_path = workspace_path / filename
        if not file_path.exists():
            return CommandResult(
                status="error",
                stderr=f"Document '{filename}' not found in workspace",
                exit_code=1
            )
        
        # Get Chunkr client
        client = get_chunkr_client()
        
        # Upload file
        with open(file_path, 'rb') as f:
            task = await client.upload(f, config=processing_config)
        
        task_info = {
            "task_id": task.task_id,
            "status": task.status,
            "filename": filename,
            "file_type": file_path.suffix[1:] if file_path.suffix else "unknown",
            "created_at": task.created_at if hasattr(task, 'created_at') else None
        }
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "task_id": task.task_id,
                "task_info": task_info,
                "message": f"Document '{filename}' uploaded successfully"
            })
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to upload document: {str(e)}",
            exit_code=1
        )


@mcp.tool
@return_as_dict
async def upload_document_from_url(url: str, processing_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Upload a document from URL to Chunkr for processing
    
    Args:
        url: URL of the document to process
        processing_config: Optional processing configuration
        
    Returns:
        Dict containing task information for the uploaded document
    """
    if not CHUNKR_AVAILABLE:
        return CommandResult(
            status="error",
            stderr="Chunkr library not available. Install with: pip install chunkr-ai",
            exit_code=1
        )
    
    try:
        # Get Chunkr client
        client = get_chunkr_client()
        
        # Upload from URL
        task = await client.upload(url, config=processing_config)
        
        task_info = {
            "task_id": task.task_id,
            "status": task.status,
            "source_url": url,
            "created_at": task.created_at if hasattr(task, 'created_at') else None
        }
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "task_id": task.task_id,
                "task_info": task_info,
                "message": f"Document from URL uploaded successfully"
            })
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to upload document from URL: {str(e)}",
            exit_code=1
        )


@mcp.tool
@return_as_dict
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get the processing status of a Chunkr task
    
    Args:
        task_id: Chunkr task ID
        
    Returns:
        Dict containing:
            - status: "success" or "error"
            - task_status: Current processing status
            - task_info: Complete task information
    """
    if not CHUNKR_AVAILABLE:
        return CommandResult(
            status="error",
            stderr="Chunkr library not available. Install with: pip install chunkr-ai",
            exit_code=1
        )
    
    try:
        client = get_chunkr_client()
        task = await client.get_task(task_id)
        
        task_info = {
            "task_id": task.task_id,
            "status": task.status,
            "progress": getattr(task, 'progress', None),
            "created_at": getattr(task, 'created_at', None),
            "finished_at": getattr(task, 'finished_at', None),
            "expires_at": getattr(task, 'expires_at', None),
        }
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "task_status": task.status,
                "task_info": task_info
            })
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to get task status: {str(e)}",
            exit_code=1
        )


@mcp.tool
@return_as_dict
async def export_to_html(task_id: str, output_filename: Optional[str] = None) -> Dict[str, Any]:
    """Export processed document to HTML format
    
    Args:
        task_id: Chunkr task ID
        output_filename: Optional output filename (defaults to task_id.html)
        
    Returns:
        Dict containing:
            - status: "success" or "error"
            - output_file: Path to the generated HTML file
            - content_preview: Preview of the HTML content
    """
    if not CHUNKR_AVAILABLE:
        return CommandResult(
            status="error",
            stderr="Chunkr library not available. Install with: pip install chunkr-ai",
            exit_code=1
        )
    
    try:
        client = get_chunkr_client()
        task = await client.get_task(task_id)
        
        if task.status != "succeeded":
            return CommandResult(
                status="error",
                stderr=f"Task is not completed. Status: {task.status}",
                exit_code=1
            )
        
        workspace_path = Path("/workspace")
        if not workspace_path.exists():
            workspace_path = Path.cwd()
        
        if output_filename is None:
            output_filename = f"{task_id}.html"
        
        output_path = workspace_path / output_filename
        
        # Export to HTML
        html_content = task.html(output_file=str(output_path))
        
        # Get content preview (first 500 chars)
        preview = html_content[:500] + "..." if len(html_content) > 500 else html_content
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "output_file": str(output_path),
                "content_preview": preview,
                "content_length": len(html_content),
                "message": f"HTML exported to {output_filename}"
            })
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to export to HTML: {str(e)}",
            exit_code=1
        )


@mcp.tool
@return_as_dict
async def export_to_markdown(task_id: str, output_filename: Optional[str] = None) -> Dict[str, Any]:
    """Export processed document to Markdown format
    
    Args:
        task_id: Chunkr task ID
        output_filename: Optional output filename (defaults to task_id.md)
        
    Returns:
        Dict containing:
            - status: "success" or "error"
            - output_file: Path to the generated Markdown file
            - content_preview: Preview of the Markdown content
    """
    if not CHUNKR_AVAILABLE:
        return CommandResult(
            status="error",
            stderr="Chunkr library not available. Install with: pip install chunkr-ai",
            exit_code=1
        )
    
    try:
        client = get_chunkr_client()
        task = await client.get_task(task_id)
        
        if task.status != "succeeded":
            return CommandResult(
                status="error",
                stderr=f"Task is not completed. Status: {task.status}",
                exit_code=1
            )
        
        workspace_path = Path("/workspace")
        if not workspace_path.exists():
            workspace_path = Path.cwd()
        
        if output_filename is None:
            output_filename = f"{task_id}.md"
        
        output_path = workspace_path / output_filename
        
        # Export to Markdown
        markdown_content = task.markdown(output_file=str(output_path))
        
        # Get content preview (first 500 chars)
        preview = markdown_content[:500] + "..." if len(markdown_content) > 500 else markdown_content
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "output_file": str(output_path),
                "content_preview": preview,
                "content_length": len(markdown_content),
                "message": f"Markdown exported to {output_filename}"
            })
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to export to Markdown: {str(e)}",
            exit_code=1
        )


@mcp.tool
@return_as_dict
async def export_to_json(task_id: str, output_filename: Optional[str] = None) -> Dict[str, Any]:
    """Export processed document to JSON format with chunks and metadata
    
    Args:
        task_id: Chunkr task ID
        output_filename: Optional output filename (defaults to task_id.json)
        
    Returns:
        Dict containing:
            - status: "success" or "error"
            - output_file: Path to the generated JSON file
            - chunks_count: Number of chunks extracted
            - metadata: Document metadata
    """
    if not CHUNKR_AVAILABLE:
        return CommandResult(
            status="error",
            stderr="Chunkr library not available. Install with: pip install chunkr-ai",
            exit_code=1
        )
    
    try:
        client = get_chunkr_client()
        task = await client.get_task(task_id)
        
        if task.status != "succeeded":
            return CommandResult(
                status="error",
                stderr=f"Task is not completed. Status: {task.status}",
                exit_code=1
            )
        
        workspace_path = Path("/workspace")
        if not workspace_path.exists():
            workspace_path = Path.cwd()
        
        if output_filename is None:
            output_filename = f"{task_id}.json"
        
        output_path = workspace_path / output_filename
        
        # Export to JSON
        json_content = task.json(output_file=str(output_path))
        
        # Parse JSON to get metadata
        if isinstance(json_content, str):
            json_data = json.loads(json_content)
        else:
            json_data = json_content
        
        chunks_count = len(json_data.get("chunks", []))
        metadata = json_data.get("metadata", {})
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "output_file": str(output_path),
                "chunks_count": chunks_count,
                "metadata": metadata,
                "message": f"JSON exported to {output_filename}"
            })
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to export to JSON: {str(e)}",
            exit_code=1
        )


@mcp.tool
@return_as_dict
async def get_document_chunks(task_id: str, chunk_type: str = "all") -> Dict[str, Any]:
    """Get processed chunks from a Chunkr task
    
    Args:
        task_id: Chunkr task ID
        chunk_type: Type of chunks to return ("all", "text", "tables", "images")
        
    Returns:
        Dict containing:
            - status: "success" or "error"
            - chunks: List of document chunks with metadata
            - total_chunks: Total number of chunks
            - chunk_types: Available chunk types in the document
    """
    if not CHUNKR_AVAILABLE:
        return CommandResult(
            status="error",
            stderr="Chunkr library not available. Install with: pip install chunkr-ai",
            exit_code=1
        )
    
    try:
        client = get_chunkr_client()
        task = await client.get_task(task_id)
        
        if task.status != "succeeded":
            return CommandResult(
                status="error",
                stderr=f"Task is not completed. Status: {task.status}",
                exit_code=1
            )
        
        # Get JSON data
        json_data = task.json()
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        
        all_chunks = json_data.get("chunks", [])
        
        # Filter chunks by type
        if chunk_type == "all":
            filtered_chunks = all_chunks
        else:
            filtered_chunks = [
                chunk for chunk in all_chunks 
                if chunk.get("type", "").lower() == chunk_type.lower()
            ]
        
        # Get available chunk types
        chunk_types = list(set(chunk.get("type", "unknown") for chunk in all_chunks))
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "chunks": filtered_chunks,
                "total_chunks": len(filtered_chunks),
                "all_chunks_count": len(all_chunks),
                "chunk_types": chunk_types,
                "requested_type": chunk_type
            })
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to get document chunks: {str(e)}",
            exit_code=1
        )


@mcp.tool
@return_as_dict
async def search_document_content(task_id: str, query: str, max_results: int = 10) -> Dict[str, Any]:
    """Search for content within processed document chunks
    
    Args:
        task_id: Chunkr task ID
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        Dict containing:
            - status: "success" or "error"
            - matches: List of matching chunks with relevance scores
            - total_matches: Total number of matches found
            - query: The original search query
    """
    if not CHUNKR_AVAILABLE:
        return CommandResult(
            status="error",
            stderr="Chunkr library not available. Install with: pip install chunkr-ai",
            exit_code=1
        )
    
    try:
        # Get chunks from the task
        chunks_result = await get_document_chunks(task_id)
        if chunks_result["status"] != "success":
            return chunks_result
        
        chunks_data = json.loads(chunks_result["stdout"])
        all_chunks = chunks_data["chunks"]
        
        # Simple text-based search (case-insensitive)
        query_lower = query.lower()
        matches = []
        
        for i, chunk in enumerate(all_chunks):
            chunk_text = chunk.get("content", "") or chunk.get("text", "")
            if query_lower in chunk_text.lower():
                # Calculate simple relevance score based on query frequency
                occurrences = chunk_text.lower().count(query_lower)
                relevance_score = occurrences / len(chunk_text.split()) if chunk_text else 0
                
                matches.append({
                    "chunk_index": i,
                    "chunk_type": chunk.get("type", "unknown"),
                    "content": chunk_text,
                    "relevance_score": relevance_score,
                    "page": chunk.get("page", None),
                    "metadata": chunk.get("metadata", {})
                })
        
        # Sort by relevance score (descending)
        matches.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Limit results
        matches = matches[:max_results]
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "matches": matches,
                "total_matches": len(matches),
                "query": query,
                "max_results": max_results
            })
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to search document content: {str(e)}",
            exit_code=1
        )


if __name__ == "__main__":
    # Check if API key is available
    if not check_api_key_available():
        print("CHUNKR_API_KEY not found in environment variables.")
        print("Please set CHUNKR_API_KEY in .env file or environment to enable Chunkr server.")
        print("Get your API key from https://chunkr.ai")
        sys.exit(1)

    print("Starting Chunkr Document Intelligence MCP server with streamable-http transport...")
    if not CHUNKR_AVAILABLE:
        print("Warning: Chunkr library not available. Install with: pip install chunkr-ai")
        sys.exit(1)

    # Get port from environment variable (set by ToolHive) or command line argument as fallback
    port = None
    if "MCP_PORT" in os.environ:
        port = int(os.environ["MCP_PORT"])
        print(f"Using port from MCP_PORT environment variable: {port}")
    elif "FASTMCP_PORT" in os.environ:
        port = int(os.environ["FASTMCP_PORT"])
        print(f"Using port from FASTMCP_PORT environment variable: {port}")
    elif len(sys.argv) == 2:
        port = int(sys.argv[1])
        print(f"Using port from command line argument: {port}")
    else:
        print("Usage: python server.py <port>")
        print("Or set MCP_PORT/FASTMCP_PORT environment variable")
        sys.exit(1)

    print(f"Starting server on port {port}")
    mcp.run(transport="streamable-http", port=port, host="0.0.0.0")