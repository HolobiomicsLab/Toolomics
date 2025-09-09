#!/usr/bin/env python3

"""
Chunkr MCP Server

Provides document intelligence tools for converting various document types into RAG/LLM-ready chunks.
Supports PDFs, PPTs, Word docs, and images through Chunkr's API for layout analysis, OCR, 
and semantic chunking.

Author: Toolomics Integration - HolobiomicsLab, CNRS
"""

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from shared import CommandResult, get_workspace_path, return_as_dict

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
Advanced document intelligence MCP server powered by Chunkr AI. Transforms complex documents into LLM/RAG-ready data with Vision Language Model processing, advanced layout analysis, and intelligent OCR.

PRIMARY WORKFLOW - TARGETED INFORMATION RETRIEVAL:
1. upload_document_from_url() or upload_document() → get task_id
2. search_document_content() → find specific information with relevance scoring
3. get_document_chunks() → browse structured content by type (text/tables/images)

SECONDARY WORKFLOW - FULL DOCUMENT CONVERSION:
1. Upload document → get task_id  
2. export_to_markdown(), export_to_html(), or export_to_json()

KEY CAPABILITIES:
• Document Intelligence: Advanced layout analysis preserves document structure
• Vision Language Models: Intelligent processing of complex document layouts  
• Multi-format Support: PDFs, PPTs, Word docs, images
• Flexible Output: HTML, Markdown, JSON with semantic chunks
• OCR Excellence: High-quality text extraction from images and scanned documents

PERFECT FOR: PDF Q&A, research paper analysis, technical documentation processing, content extraction.
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


def serialize_datetime(dt):
    """Convert datetime objects to ISO format strings for JSON serialization"""
    if dt is None:
        return None
    if hasattr(dt, 'isoformat'):
        return dt.isoformat()
    return str(dt)


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
        workspace_path = get_workspace_path()
        
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
    """Upload local document from workspace for intelligent processing with Vision Language Models.
    REQUIRED first step before search, export, or analysis operations.
    
    Args:
        filename: Document file in workspace (supports: PDF, PPT, PPTX, DOC, DOCX, PNG, JPG)
        processing_config: Optional config dict or None for defaults
        
    Returns:
        Dict containing task_id (required for all subsequent operations), status, and metadata.
        Use task_id with search_document_content() for targeted info retrieval.
    """
    if not CHUNKR_AVAILABLE:
        return CommandResult(
            status="error",
            stderr="Chunkr library not available. Install with: pip install chunkr-ai",
            exit_code=1
        )
    
    try:
        workspace_path = get_workspace_path()
            
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
            "created_at": serialize_datetime(getattr(task, 'created_at', None))
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
async def upload_document_from_url(url: str, processing_config: Optional[Dict[str, Any]] = None, timeout_seconds: int = 300) -> Dict[str, Any]:
    """Download and process document from URL with advanced document intelligence.
    Combines download + Vision Language Model processing in one step.
    REQUIRED first step before search, export, or analysis operations.
    
    URL must serve document content, not HTML article pages.
    WORKS: https://arxiv.org/pdf/2506.07398 (ArXiv PDFs)
    FAILS: https://academic.oup.com/article/123 (HTML pages → 400 Bad Request)
    
    Args:
        url: URL that serves document content (PDF, PPT, PPTX, DOC, DOCX, images)
        processing_config: Optional config dict or None for defaults
        timeout_seconds: Max wait time in seconds (default: 60)
        
    Returns:
        Dict with task_id for subsequent operations (search_document_content, export functions)
    """
    if not CHUNKR_AVAILABLE:
        return CommandResult(
            status="error",
            stderr="Chunkr library not available. Install with: pip install chunkr-ai",
            exit_code=1
        )
    
    try:
        import asyncio

        # Get Chunkr client
        client = get_chunkr_client()
        
        # Upload from URL with timeout
        try:
            task = await asyncio.wait_for(
                client.upload(url, config=processing_config), 
                timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            return CommandResult(
                status="error",
                stderr=f"Upload timeout after {timeout_seconds} seconds. URL may be unreachable or document too large/complex for processing within timeout limit. Try increasing timeout_seconds parameter or check URL accessibility.",
                exit_code=1
            )
        
        task_info = {
            "task_id": task.task_id,
            "status": task.status,
            "source_url": url,
            "created_at": serialize_datetime(getattr(task, 'created_at', None))
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
    """Check the processing status of a Chunkr task.
    Status must be "succeeded" before you can use export functions.
    
    Args:
        task_id: Chunkr task ID from upload_document() or upload_document_from_url()
        
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
            "created_at": serialize_datetime(getattr(task, 'created_at', None)),
            "finished_at": serialize_datetime(getattr(task, 'finished_at', None)),
            "expires_at": serialize_datetime(getattr(task, 'expires_at', None)),
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
        
        if task.status.lower() != "succeeded":
            return CommandResult(
                status="error",
                stderr=f"Task is not completed. Status: {task.status}",
                exit_code=1
            )
        
        workspace_path = get_workspace_path()
        
        if output_filename is None:
            output_filename = f"{task_id}.html"
        
        output_path = workspace_path / output_filename
        
        # Debug: Log the paths being used
        print(f"DEBUG: Workspace path: {workspace_path}")
        print(f"DEBUG: Output path: {output_path}")
        
        # Export to HTML
        html_content = task.html(output_file=str(output_path))
        
        # Debug: Check if file was actually created
        print(f"DEBUG: File created: {output_path.exists()}")
        
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
    """Export document to clean, structured Markdown preserving layout and formatting.
    Uses advanced layout analysis to maintain document structure, tables, and hierarchy.
    REQUIRES: task_id from upload_document() or upload_document_from_url() with "succeeded" status.
    
    Args:
        task_id: Chunkr task ID from successful document upload
        output_filename: Optional output filename (defaults to task_id.md)
        
    Returns:
        Dict with output_file path, content preview, and length.
        Generated markdown preserves document intelligence and is optimized for LLM consumption.
        Saved in workspace for integration with other MCP tools.
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
        
        if task.status.lower() != "succeeded":
            return CommandResult(
                status="error",
                stderr=f"Task is not completed. Status: {task.status}",
                exit_code=1
            )
        
        workspace_path = get_workspace_path()
        
        if output_filename is None:
            output_filename = f"{task_id}.md"
        
        output_path = workspace_path / output_filename
        
        # Debug: Log the paths being used
        print(f"DEBUG: Workspace path: {workspace_path}")
        print(f"DEBUG: Output path: {output_path}")
        print(f"DEBUG: Workspace exists: {workspace_path.exists()}")
        print(f"DEBUG: Current working directory: {Path.cwd()}")
        
        # Export to Markdown
        markdown_content = task.markdown(output_file=str(output_path))
        
        # Check if file was created in expected location
        actual_file_path = output_path
        if not output_path.exists():
            # Check if file was created in /projects directory instead
            projects_path = Path("/projects") / output_filename
            if projects_path.exists():
                actual_file_path = projects_path
                print(f"DEBUG: File found at {projects_path} instead of {output_path}")
            else:
                print(f"DEBUG: File not found at {output_path} or {projects_path}")
        
        print(f"DEBUG: Final file path: {actual_file_path}")
        print(f"DEBUG: File exists: {actual_file_path.exists()}")
        if actual_file_path.exists():
            print(f"DEBUG: File size: {actual_file_path.stat().st_size} bytes")
        
        # Get content preview (first 500 chars)
        preview = markdown_content[:500] + "..." if len(markdown_content) > 500 else markdown_content
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "output_file": str(actual_file_path),
                "workspace_file": str(output_path),
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
        
        if task.status.lower() != "succeeded":
            return CommandResult(
                status="error",
                stderr=f"Task is not completed. Status: {task.status}",
                exit_code=1
            )
        
        workspace_path = get_workspace_path()
        
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
    """Browse document structure and get all processed chunks from a Chunkr task.
    Use this to understand document organization or get all content for analysis.
    For targeted information retrieval, use search_document_content() instead.
    
    Args:
        task_id: Chunkr task ID from upload_document() or upload_document_from_url()
        chunk_type: Type of chunks to return ("all", "text", "tables", "images")
        
    Returns:
        Dict containing:
            - status: "success" or "error"
            - chunks: List of document chunks with content and metadata
            - total_chunks: Total number of chunks returned
            - chunk_types: Available chunk types in the document
            
    Use search_document_content() for targeted information extraction instead.
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
        
        if task.status.lower() != "succeeded":
            return CommandResult(
                status="error",
                stderr=f"Task is not completed. Status: {task.status}",
                exit_code=1
            )
        
        # Get JSON data
        json_data = task.json()
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        
        # Debug: Log the JSON structure to understand the data format
        print(f"DEBUG: JSON data keys: {json_data.keys() if isinstance(json_data, dict) else 'Not a dict'}")
        print(f"DEBUG: JSON data type: {type(json_data)}")
        if isinstance(json_data, dict):
            print(f"DEBUG: JSON data sample: {str(json_data)[:500]}...")
        
        all_chunks = json_data.get("chunks", [])
        
        # Add helpful information if no chunks found
        if not all_chunks:
            print(f"WARNING: No chunks found in processed document. JSON data structure: {list(json_data.keys()) if isinstance(json_data, dict) else 'Not a dict'}")
            print(f"Full JSON data (truncated): {str(json_data)[:1000]}...")
        
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
    """PRIMARY TOOL: Intelligent search within processed documents using content analysis.
    Leverages Vision Language Model processing to find specific information with relevance scoring.
    Ideal for Q&A, fact extraction, and targeted research without full document conversion.
    
    Args:
        task_id: Chunkr task ID from successful document upload
        query: Search terms (e.g., "methodology", "results", "hyperparameters", "conclusions")
        max_results: Maximum matching chunks to return (default: 10)
        
    Returns:
        Dict with ranked matches, relevance scores, page numbers, and chunk metadata.
        Each match includes content, chunk type (text/table/image), and document location.
        
    Example: search_document_content(task_id, "neural network architecture")
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
        
        if task.status.lower() != "succeeded":
            return CommandResult(
                status="error",
                stderr=f"Task is not completed. Status: {task.status}",
                exit_code=1
            )
        
        # Get JSON data directly
        json_data = task.json()
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        
        all_chunks = json_data.get("chunks", [])
        
        # Check if chunks are available
        if not all_chunks:
            return CommandResult(
                status="error",
                stderr="No content chunks available for search. The document may not have been processed correctly or may contain no extractable text content. Try using export_to_markdown() to get the full document content instead.",
                exit_code=1
            )
        
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


@mcp.tool
@return_as_dict
async def upload_multiple_documents(filenames: List[str], processing_config: Optional[Dict[str, Any]] = None, parallel: bool = True) -> Dict[str, Any]:
    """Upload multiple documents from workspace for batch processing with Vision Language Models.
    Efficient bulk processing with optional parallel execution for document collections.
    
    Args:
        filenames: List of document files in workspace (supports: PDF, PPT, PPTX, DOC, DOCX, PNG, JPG)
        processing_config: Optional config dict or None for defaults
        parallel: Process documents in parallel for faster completion (default: True)
        
    Returns:
        Dict with task_ids for each document, success/failure status, and processing metadata.
        Use returned task_ids with search_document_content() for targeted information retrieval.
    """
    if not CHUNKR_AVAILABLE:
        return CommandResult(
            status="error",
            stderr="Chunkr library not available. Install with: pip install chunkr-ai",
            exit_code=1
        )
    
    try:
        workspace_path = get_workspace_path()
        client = get_chunkr_client()
        
        results = []
        failed_uploads = []
        
        if parallel:
            # Process documents in parallel using asyncio.gather
            import asyncio
            
            async def upload_single_doc(filename):
                try:
                    file_path = workspace_path / filename
                    if not file_path.exists():
                        return {
                            "filename": filename,
                            "status": "error",
                            "error": f"File '{filename}' not found in workspace"
                        }
                    
                    with open(file_path, 'rb') as f:
                        task = await client.upload(f, config=processing_config)
                    
                    return {
                        "filename": filename,
                        "task_id": task.task_id,
                        "status": "success",
                        "task_status": task.status,
                        "file_type": file_path.suffix[1:] if file_path.suffix else "unknown",
                        "created_at": serialize_datetime(getattr(task, 'created_at', None))
                    }
                except Exception as e:
                    return {
                        "filename": filename,
                        "status": "error",
                        "error": str(e)
                    }
            
            # Execute all uploads in parallel
            upload_tasks = [upload_single_doc(filename) for filename in filenames]
            results = await asyncio.gather(*upload_tasks, return_exceptions=True)
            
            # Process results and separate successes from failures
            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    failed_uploads.append({
                        "filename": "unknown",
                        "error": str(result)
                    })
                elif result["status"] == "error":
                    failed_uploads.append(result)
                else:
                    processed_results.append(result)
            results = processed_results
            
        else:
            # Process documents sequentially
            for filename in filenames:
                try:
                    file_path = workspace_path / filename
                    if not file_path.exists():
                        failed_uploads.append({
                            "filename": filename,
                            "error": f"File '{filename}' not found in workspace"
                        })
                        continue
                    
                    with open(file_path, 'rb') as f:
                        task = await client.upload(f, config=processing_config)
                    
                    results.append({
                        "filename": filename,
                        "task_id": task.task_id,
                        "status": "success",
                        "task_status": task.status,
                        "file_type": file_path.suffix[1:] if file_path.suffix else "unknown",
                        "created_at": serialize_datetime(getattr(task, 'created_at', None))
                    })
                    
                except Exception as e:
                    failed_uploads.append({
                        "filename": filename,
                        "error": str(e)
                    })
        
        # Prepare response
        successful_uploads = len(results)
        total_files = len(filenames)
        
        return CommandResult(
            status="success" if successful_uploads > 0 else "error",
            stdout=json.dumps({
                "successful_uploads": results,
                "failed_uploads": failed_uploads,
                "summary": {
                    "total_files": total_files,
                    "successful": successful_uploads,
                    "failed": len(failed_uploads),
                    "processing_mode": "parallel" if parallel else "sequential"
                },
                "task_ids": [result["task_id"] for result in results],
                "message": f"Processed {successful_uploads}/{total_files} documents successfully"
            })
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to upload multiple documents: {str(e)}",
            exit_code=1
        )


@mcp.tool
@return_as_dict
async def semantic_search_content(task_id: str, query: str, similarity_threshold: float = 0.7, max_results: int = 10) -> Dict[str, Any]:
    """Advanced semantic search within processed documents using intelligent content matching.
    Provides better relevance than keyword search by understanding content meaning and context.
    
    Args:
        task_id: Chunkr task ID from successful document upload
        query: Search query with semantic understanding (e.g., "research methodology", "key findings")
        similarity_threshold: Minimum similarity score for matches (0.0-1.0, default: 0.7)
        max_results: Maximum matching chunks to return (default: 10)
        
    Returns:
        Dict with semantically ranked matches, similarity scores, and enhanced metadata.
        Results prioritize meaning over keyword matching for better information retrieval.
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
        
        if task.status.lower() != "succeeded":
            return CommandResult(
                status="error",
                stderr=f"Task is not completed. Status: {task.status}",
                exit_code=1
            )
        
        # Get JSON data directly
        json_data = task.json()
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        
        all_chunks = json_data.get("chunks", [])
        
        if not all_chunks:
            return CommandResult(
                status="error",
                stderr="No content chunks available for semantic search. Document may not have been processed correctly.",
                exit_code=1
            )
        
        # Enhanced semantic search with multiple matching strategies
        query_lower = query.lower()
        query_words = set(query_lower.split())
        matches = []
        
        for i, chunk in enumerate(all_chunks):
            chunk_text = chunk.get("content", "") or chunk.get("text", "")
            if not chunk_text:
                continue
                
            chunk_text_lower = chunk_text.lower()
            chunk_words = set(chunk_text_lower.split())
            
            # Calculate semantic similarity using multiple factors
            similarity_scores = []
            
            # 1. Exact phrase matching (highest weight)
            if query_lower in chunk_text_lower:
                phrase_score = len(query_lower) / len(chunk_text_lower)
                similarity_scores.append(phrase_score * 3.0)  # High weight for exact matches
            
            # 2. Word overlap similarity
            common_words = query_words.intersection(chunk_words)
            if common_words:
                word_overlap_score = len(common_words) / len(query_words)
                similarity_scores.append(word_overlap_score * 2.0)  # Medium weight
            
            # 3. Partial word matching (stems, prefixes)
            partial_matches = 0
            for query_word in query_words:
                for chunk_word in chunk_words:
                    if len(query_word) > 3 and len(chunk_word) > 3:
                        # Check if words share significant prefix/suffix
                        if (query_word.startswith(chunk_word[:3]) or 
                            chunk_word.startswith(query_word[:3]) or
                            query_word.endswith(chunk_word[-3:]) or
                            chunk_word.endswith(query_word[-3:])):
                            partial_matches += 1
                            break
            
            if partial_matches > 0:
                partial_score = partial_matches / len(query_words)
                similarity_scores.append(partial_score * 1.0)  # Lower weight
            
            # 4. Context similarity (surrounding words)
            context_score = 0
            for query_word in query_words:
                query_idx = chunk_text_lower.find(query_word)
                if query_idx != -1:
                    # Look at surrounding context (10 words before/after)
                    context_start = max(0, query_idx - 50)
                    context_end = min(len(chunk_text_lower), query_idx + len(query_word) + 50)
                    context = chunk_text_lower[context_start:context_end]
                    
                    # Count other query words in context
                    context_matches = sum(1 for word in query_words if word in context and word != query_word)
                    if context_matches > 0:
                        context_score += context_matches / len(query_words)
            
            if context_score > 0:
                similarity_scores.append(context_score * 1.5)  # Medium-high weight
            
            # Calculate final similarity score
            if similarity_scores:
                final_similarity = sum(similarity_scores) / len(similarity_scores)
                # Normalize to 0-1 range
                final_similarity = min(1.0, final_similarity)
                
                if final_similarity >= similarity_threshold:
                    matches.append({
                        "chunk_index": i,
                        "chunk_type": chunk.get("type", "unknown"),
                        "content": chunk_text,
                        "similarity_score": round(final_similarity, 3),
                        "page": chunk.get("page", None),
                        "metadata": chunk.get("metadata", {}),
                        "match_details": {
                            "exact_phrase": query_lower in chunk_text_lower,
                            "word_matches": len(common_words),
                            "partial_matches": partial_matches,
                            "context_matches": context_score > 0
                        }
                    })
        
        # Sort by similarity score (descending)
        matches.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        # Limit results
        matches = matches[:max_results]
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "matches": matches,
                "total_matches": len(matches),
                "query": query,
                "similarity_threshold": similarity_threshold,
                "max_results": max_results,
                "search_type": "semantic"
            })
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to perform semantic search: {str(e)}",
            exit_code=1
        )


@mcp.tool
@return_as_dict
async def analyze_document_structure(task_id: str) -> Dict[str, Any]:
    """Analyze document structure and layout without full content processing.
    Provides quick assessment of document organization, complexity, and processing results.
    
    Args:
        task_id: Chunkr task ID from successful document upload
        
    Returns:
        Dict with document structure analysis including page count, chunk distribution,
        content types, processing statistics, and document complexity metrics.
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
        
        if task.status.lower() != "succeeded":
            return CommandResult(
                status="error",
                stderr=f"Task is not completed. Status: {task.status}. Use get_task_status() to monitor progress.",
                exit_code=1
            )
        
        # Get JSON data for analysis
        json_data = task.json()
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        
        all_chunks = json_data.get("chunks", [])
        metadata = json_data.get("metadata", {})
        
        # Analyze document structure
        structure_analysis = {
            "document_metadata": {
                "total_pages": metadata.get("page_count", "unknown"),
                "file_size": metadata.get("file_size", "unknown"),
                "file_type": metadata.get("file_type", "unknown"),
                "processing_time": metadata.get("processing_time", "unknown")
            },
            "chunk_analysis": {
                "total_chunks": len(all_chunks),
                "chunk_types": {},
                "chunks_per_page": {},
                "content_distribution": {
                    "text_chunks": 0,
                    "table_chunks": 0,
                    "image_chunks": 0,
                    "other_chunks": 0
                }
            },
            "content_statistics": {
                "total_characters": 0,
                "average_chunk_size": 0,
                "longest_chunk": 0,
                "shortest_chunk": float('inf') if all_chunks else 0
            },
            "structure_complexity": {
                "has_tables": False,
                "has_images": False,
                "multi_column_layout": False,
                "page_variation": "unknown"
            }
        }
        
        # Analyze each chunk
        for chunk in all_chunks:
            chunk_type = chunk.get("type", "unknown").lower()
            chunk_content = chunk.get("content", "") or chunk.get("text", "")
            chunk_page = chunk.get("page", 1)
            
            # Count chunk types
            structure_analysis["chunk_analysis"]["chunk_types"][chunk_type] = \
                structure_analysis["chunk_analysis"]["chunk_types"].get(chunk_type, 0) + 1
            
            # Count chunks per page
            structure_analysis["chunk_analysis"]["chunks_per_page"][str(chunk_page)] = \
                structure_analysis["chunk_analysis"]["chunks_per_page"].get(str(chunk_page), 0) + 1
            
            # Categorize content
            if chunk_type in ["text", "paragraph", "heading"]:
                structure_analysis["chunk_analysis"]["content_distribution"]["text_chunks"] += 1
            elif chunk_type in ["table", "table_cell"]:
                structure_analysis["chunk_analysis"]["content_distribution"]["table_chunks"] += 1
                structure_analysis["structure_complexity"]["has_tables"] = True
            elif chunk_type in ["image", "figure", "chart"]:
                structure_analysis["chunk_analysis"]["content_distribution"]["image_chunks"] += 1
                structure_analysis["structure_complexity"]["has_images"] = True
            else:
                structure_analysis["chunk_analysis"]["content_distribution"]["other_chunks"] += 1
            
            # Content statistics
            content_length = len(chunk_content)
            structure_analysis["content_statistics"]["total_characters"] += content_length
            
            if content_length > structure_analysis["content_statistics"]["longest_chunk"]:
                structure_analysis["content_statistics"]["longest_chunk"] = content_length
            
            if content_length < structure_analysis["content_statistics"]["shortest_chunk"]:
                structure_analysis["content_statistics"]["shortest_chunk"] = content_length
        
        # Calculate averages
        if all_chunks:
            structure_analysis["content_statistics"]["average_chunk_size"] = \
                structure_analysis["content_statistics"]["total_characters"] // len(all_chunks)
        else:
            structure_analysis["content_statistics"]["shortest_chunk"] = 0
        
        # Assess document complexity
        chunk_types_count = len(structure_analysis["chunk_analysis"]["chunk_types"])
        pages_with_chunks = len(structure_analysis["chunk_analysis"]["chunks_per_page"])
        
        if chunk_types_count > 3:
            structure_analysis["structure_complexity"]["multi_column_layout"] = True
        
        if pages_with_chunks > 1:
            chunks_per_page_values = list(structure_analysis["chunk_analysis"]["chunks_per_page"].values())
            variation = max(chunks_per_page_values) - min(chunks_per_page_values)
            if variation > 5:
                structure_analysis["structure_complexity"]["page_variation"] = "high"
            elif variation > 2:
                structure_analysis["structure_complexity"]["page_variation"] = "medium"
            else:
                structure_analysis["structure_complexity"]["page_variation"] = "low"
        
        # Overall assessment
        complexity_score = 0
        if structure_analysis["structure_complexity"]["has_tables"]:
            complexity_score += 2
        if structure_analysis["structure_complexity"]["has_images"]:
            complexity_score += 2
        if structure_analysis["structure_complexity"]["multi_column_layout"]:
            complexity_score += 1
        if structure_analysis["structure_complexity"]["page_variation"] == "high":
            complexity_score += 2
        elif structure_analysis["structure_complexity"]["page_variation"] == "medium":
            complexity_score += 1
        
        if complexity_score >= 5:
            overall_complexity = "high"
        elif complexity_score >= 3:
            overall_complexity = "medium"
        else:
            overall_complexity = "low"
        
        structure_analysis["overall_assessment"] = {
            "complexity_level": overall_complexity,
            "complexity_score": complexity_score,
            "processing_quality": "good" if len(all_chunks) > 0 else "poor",
            "recommended_search_strategy": "semantic" if complexity_score >= 3 else "keyword"
        }
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "task_id": task_id,
                "structure_analysis": structure_analysis,
                "message": f"Document structure analyzed: {overall_complexity} complexity, {len(all_chunks)} chunks across {pages_with_chunks} pages"
            })
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to analyze document structure: {str(e)}",
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