#!/usr/bin/env python3

"""
PDF Tools MCP Server

Provides comprehensive tools for PDF manipulation, reading, and analysis including
keyword search, basic RAG functionality, text extraction, and metadata handling.

Author:  Martin Legrand - HolobiomicsLab, CNRS
"""

import sys
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import hashlib
import string

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from workspace.shared.shared import CommandResult, return_as_dict

# PDF processing imports
try:
    import PyPDF2
    import fitz  # PyMuPDF
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    PDF_LIBS_AVAILABLE = True
        
except ImportError as e:
    print(f"Warning: Some PDF libraries not available: {e}")
    print("Install with: pip install PyPDF2 PyMuPDF sentence-transformers scikit-learn nltk")
    PDF_LIBS_AVAILABLE = False

from fastmcp import FastMCP

description = """
PDF Tools MCP Server provides comprehensive tools for PDF manipulation and analysis.
Features include text extraction, keyword search, basic RAG (Retrieval-Augmented Generation),
metadata extraction, page manipulation, and content analysis.
All operations work with files in the centralized workspace directory.
"""

mcp = FastMCP(
    name="PDF Processing MCP",
    instructions=description,
)

# Global variables for RAG functionality
_embedding_model = None
_document_embeddings = {}
_document_chunks = {}

def get_embedding_model():
    """Lazy load the embedding model"""
    global _embedding_model
    if _embedding_model is None and PDF_LIBS_AVAILABLE:
        try:
            _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Failed to load embedding model: {e}")
    return _embedding_model

@dataclass
class PDFInfo:
    """Information about a PDF file"""
    filename: str
    num_pages: int
    title: str
    author: str
    subject: str
    creator: str
    producer: str
    creation_date: str
    modification_date: str
    file_size: int

@mcp.tool
def get_mcp_name() -> str:
    """Get the name of this MCP server
    
    Returns:
        str: The name of this MCP server ("PDF Processing MCP")
    """
    return "PDF Processing MCP"

@mcp.tool
@return_as_dict
def list_pdf_files() -> Dict[str, Any]:
    """List all PDF files in the workspace directory
    
    Returns:
        Dict containing:
            - status: "success" or "error"
            - files: List of PDF filenames
            - count: Number of PDF files found
            - message: Error message if applicable
    """
    try:
        workspace_path = Path.cwd()
        pdf_files = list(workspace_path.glob("*.pdf"))
        pdf_filenames = [f.name for f in pdf_files]
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "files": pdf_filenames,
                "count": len(pdf_filenames),
                "workspace": str(workspace_path)
            })
        )
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to list PDF files: {str(e)}",
            exit_code=1
        )

@mcp.tool
@return_as_dict
def extract_text_from_pdf(filename: str, start_page: int = 1, end_page: Optional[int] = None) -> Dict[str, Any]:
    """Extract text content from a PDF file, limited to 32000 characters
    
    Args:
        filename: Name of the PDF file in workspace
        start_page: Starting page number (1-indexed)
        end_page: Ending page number (1-indexed), None for all pages
        
    Returns:
        Dict containing:
            - status: "success" or "error"
            - text: Extracted text content
            - pages_processed: Number of pages processed
            - message: Error message if applicable
    """
    if not PDF_LIBS_AVAILABLE:
        return CommandResult(
            status="error",
            stderr="PDF libraries not available. Install PyPDF2 and PyMuPDF.",
            exit_code=1
        )
    
    try:
        pdf_path = Path.cwd() / filename
        if not pdf_path.exists():
            return CommandResult(
                status="error",
                stderr=f"PDF file '{filename}' not found in workspace",
                exit_code=1
            )
        
        text_content = []
        pages_processed = 0
        
        try:
            doc = fitz.open(str(pdf_path))
            total_pages = len(doc)
            
            if end_page is None:
                end_page = total_pages
            
            start_page = max(1, start_page)
            end_page = min(total_pages, end_page)
            
            for page_num in range(start_page - 1, end_page):
                page = doc[page_num]
                text = page.get_text()
                if text.strip():
                    text_content.append(f"--- Page {page_num + 1} ---\n{text}")
                pages_processed += 1
            doc.close()

        except Exception as e:
            return CommandResult(
                status="error",
                stderr=f"Failed to extract text using PyMuPDF: {str(e)}",
                exit_code=1
            )
        
        full_text = "\n\n".join(text_content[:32384])
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "text": full_text,
                "pages_processed": pages_processed,
                "total_pages": total_pages,
                "filename": filename
            })
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to extract text from PDF: {str(e)}",
            exit_code=1
        )

@mcp.tool
@return_as_dict
def search_keywords_in_pdf(filename: str, keywords: str, case_sensitive: bool = False) -> Dict[str, Any]:
    """Search for keywords in a PDF file and return matches with context
    
    Args:
        filename: Name of the PDF file in workspace
        keywords: Comma-separated keywords to search for
        case_sensitive: Whether search should be case sensitive
        
    Returns:
        Dict containing:
            - status: "success" or "error"
            - matches: List of matches with page numbers and context
            - total_matches: Total number of matches found
            - keywords_searched: List of keywords that were searched
    """
    try:
        # First extract text
        extract_result = extract_text_from_pdf(filename)
        if extract_result["status"] != "success":
            return extract_result
        
        text_data = json.loads(extract_result["stdout"])
        full_text = text_data["text"]
        
        # Parse keywords
        keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
        if not keyword_list:
            return CommandResult(
                status="error",
                stderr="No valid keywords provided",
                exit_code=1
            )
        
        matches = []
        total_matches = 0
        
        # Split text by pages
        pages = full_text.split("--- Page ")
        
        for page_content in pages[1:]:  # Skip first empty split
            lines = page_content.split("\n")
            page_num = int(lines[0].split(" ---")[0])
            page_text = "\n".join(lines[1:])
            
            for keyword in keyword_list:
                # Create regex pattern
                pattern = re.escape(keyword) if case_sensitive else re.escape(keyword)
                flags = 0 if case_sensitive else re.IGNORECASE
                
                for match in re.finditer(pattern, page_text, flags):
                    # Get context around match
                    start = max(0, match.start() - 100)
                    end = min(len(page_text), match.end() + 100)
                    context = page_text[start:end].strip()
                    
                    matches.append({
                        "keyword": keyword,
                        "page": page_num,
                        "position": match.start(),
                        "context": context,
                        "match_text": match.group()
                    })
                    total_matches += 1
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "matches": matches,
                "total_matches": total_matches,
                "keywords_searched": keyword_list,
                "filename": filename
            })
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to search keywords in PDF: {str(e)}",
            exit_code=1
        )

def _create_pdf_embeddings(filename: str, chunk_size: int = 500) -> Dict[str, Any]:
    """Create embeddings for PDF content to enable RAG functionality
    
    Args:
        filename: Name of the PDF file in workspace
        chunk_size: Size of text chunks for embedding (in characters)
        
    Returns:
        Dict containing embedding creation results
    """
    if not PDF_LIBS_AVAILABLE:
        return CommandResult(
            status="error",
            stderr="PDF libraries not available. Install required packages.",
            exit_code=1
        )
    
    try:
        model = get_embedding_model()
        if model is None:
            return CommandResult(
                status="error",
                stderr="Failed to load embedding model",
                exit_code=1
            )
        
        extract_result = extract_text_from_pdf(filename)
        if extract_result["status"] != "success":
            return extract_result
        
        text_data = json.loads(extract_result["stdout"])
        full_text = text_data["text"]
        
        chunks = []
        for i in range(0, len(full_text), chunk_size):
            chunk = full_text[i:i + chunk_size]
            if chunk.strip():
                chunks.append({
                    "text": chunk,
                    "start_pos": i,
                    "end_pos": min(i + chunk_size, len(full_text))
                })
        chunk_texts = [chunk["text"] for chunk in chunks]
        embeddings = model.encode(chunk_texts)
        doc_key = f"{filename}_{hashlib.md5(full_text.encode()).hexdigest()[:8]}"
        _document_embeddings[doc_key] = embeddings
        _document_chunks[doc_key] = chunks
    except Exception as e:
        raise RuntimeError(f"Failed to create PDF embeddings: {str(e)}")

@mcp.tool
@return_as_dict
def query_pdf_rag(filename: str, query: str, top_k: int = 3) -> Dict[str, Any]:
    """Query PDF content using RAG (Retrieval-Augmented Generation)
    
    Args:
        filename: Name of the PDF file in workspace
        query: Query string to search for relevant content
        top_k: Number of most relevant chunks to return
        
    Returns:
        Dict containing most relevant text chunks for the query
    """
    if not PDF_LIBS_AVAILABLE:
        return CommandResult(
            status="error",
            stderr="PDF libraries not available. Install required packages.",
            exit_code=1
        )
    
    try:
        model = get_embedding_model()
        if model is None:
            return CommandResult(
                status="error",
                stderr="Failed to load embedding model",
                exit_code=1
            )
        
        # Find document embeddings
        doc_key = None
        for key in _document_embeddings.keys():
            if key.startswith(filename + "_"):
                doc_key = key
                break
        
        if doc_key is None:
            embed_result = _create_pdf_embeddings(filename)
            if embed_result["status"] != "success":
                return CommandResult(
                    status="error",
                    stderr="No embeddings found. Create embeddings first using create_pdf_embeddings.",
                    exit_code=1
                )
            
            embed_data = json.loads(embed_result["stdout"])
            doc_key = embed_data["document_key"]
        
        embeddings = _document_embeddings[doc_key]
        chunks = _document_chunks[doc_key]
        query_embedding = model.encode([query])
        similarities = cosine_similarity(query_embedding, embeddings)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        results = []
        for idx in top_indices:
            results.append({
                "chunk_index": int(idx),
                "similarity_score": float(similarities[idx]),
                "text": chunks[idx]["text"],
                "start_position": chunks[idx]["start_pos"],
                "end_position": chunks[idx]["end_pos"]
            })
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "query": query,
                "filename": filename,
                "results": results,
                "total_chunks": len(chunks)
            })
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to query PDF with RAG: {str(e)}",
            exit_code=1
        )

# Port handling for deployment
if len(sys.argv) > 1 and sys.argv[1].isdigit():
    port = int(sys.argv[1])
else:
    port = int(input("Enter port number: "))

print(f"Starting PDF Processing MCP server on port {port}...")
if not PDF_LIBS_AVAILABLE:
    print("Warning: PDF libraries not fully available. Some features may not work.")
    print("Install with: pip install PyPDF2 PyMuPDF sentence-transformers scikit-learn")

mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path="/mcp")
