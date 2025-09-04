#!/usr/bin/env python3

"""
PDF Tools MCP Server

Provides comprehensive tools for PDF manipulation, reading, and analysis including
agentic RAG functionality with page-by-page navigation, keyword search, text extraction,
and metadata handling.

Author:  Martin Legrand - HolobiomicsLab, CNRS
"""

import sys
import os
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import hashlib

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from shared import CommandResult, return_as_dict, get_workspace_path

# PDF processing imports
try:
    import fitz  # PyMuPDF
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity

    PDF_LIBS_AVAILABLE = True

except ImportError as e:
    print(f"Warning: Some PDF libraries not available: {e}")
    print(
        "Install with: pip install PyPDF2 PyMuPDF sentence-transformers scikit-learn nltk"
    )
    PDF_LIBS_AVAILABLE = False

from fastmcp import FastMCP

description = """
PDF Tools MCP Server provides comprehensive tools for PDF manipulation and analysis.
Features include agentic RAG with page-by-page navigation, text extraction, keyword search,
metadata extraction, and content analysis. All operations work with files in the 
centralized workspace directory.
"""

mcp = FastMCP(
    name="PDF Processing MCP",
    instructions=description,
)

# Global variables for RAG functionality and navigation state
_embedding_model = None
_document_embeddings = {}
_document_chunks = {}
_document_pages = {}
_navigation_state = {}


def get_embedding_model():
    """Lazy load the embedding model"""
    global _embedding_model
    if _embedding_model is None and PDF_LIBS_AVAILABLE:
        try:
            _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
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


@dataclass
class NavigationState:
    """Track navigation state for a PDF document"""

    filename: str
    current_page: int
    total_pages: int
    session_id: str
    bookmarks: List[int]
    search_history: List[str]


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
        workspace_path = get_workspace_path()
        pdf_files = list(workspace_path.glob("*.pdf"))
        pdf_filenames = [f.name for f in pdf_files]

        return CommandResult(
            status="success",
            stdout=json.dumps(
                {
                    "files": pdf_filenames,
                    "count": len(pdf_filenames),
                    "workspace": str(workspace_path),
                }
            ),
        )
    except Exception as e:
        return CommandResult(
            status="error", stderr=f"Failed to list PDF files: {str(e)}", exit_code=1
        )


@mcp.tool
@return_as_dict
def initialize_pdf_navigation(
    filename: str, session_id: Optional[str] = None
) -> Dict[str, Any]:
    """Initialize navigation for a PDF document

    Args:
        filename: Name of the PDF file in workspace
        session_id: Optional session identifier for tracking navigation state

    Returns:
        Dict containing:
            - status: "success" or "error"
            - session_id: Session identifier for this navigation session
            - total_pages: Total number of pages in the PDF
            - current_page: Current page (starts at 1)
            - filename: Name of the PDF file
    """
    if not PDF_LIBS_AVAILABLE:
        return CommandResult(
            status="error",
            stderr="PDF libraries not available. Install PyPDF2 and PyMuPDF.",
            exit_code=1,
        )

    try:
        pdf_path = get_workspace_path() / filename
        if not pdf_path.exists():
            return CommandResult(
                status="error",
                stderr=f"PDF file '{filename}' not found in workspace",
                exit_code=1,
            )

        # Get PDF info
        doc = fitz.open(str(pdf_path))
        total_pages = len(doc)

        # Extract and store all pages
        pages_content = {}
        for page_num in range(total_pages):
            page = doc[page_num]
            text = page.get_text()
            pages_content[page_num + 1] = {"text": text, "page_number": page_num + 1}

        doc.close()

        # Generate session ID if not provided
        if session_id is None:
            session_id = hashlib.md5(
                f"{filename}_{hash(str(pages_content))}".encode()
            ).hexdigest()[:12]

        # Store document pages and navigation state
        doc_key = f"{filename}_{session_id}"
        _document_pages[doc_key] = pages_content
        _navigation_state[session_id] = NavigationState(
            filename=filename,
            current_page=1,
            total_pages=total_pages,
            session_id=session_id,
            bookmarks=[],
            search_history=[],
        )

        return CommandResult(
            status="success",
            stdout=json.dumps(
                {
                    "session_id": session_id,
                    "filename": filename,
                    "total_pages": total_pages,
                    "current_page": 1,
                    "doc_key": doc_key,
                }
            ),
        )

    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to initialize PDF navigation: {str(e)}",
            exit_code=1,
        )


@mcp.tool
@return_as_dict
def navigate_to_page(session_id: str, page_number: int) -> Dict[str, Any]:
    """Navigate to a specific page in the PDF

    Args:
        session_id: Session identifier for the navigation session
        page_number: Page number to navigate to (1-indexed)

    Returns:
        Dict containing:
            - status: "success" or "error"
            - current_page: Current page number
            - page_content: Text content of the current page
            - total_pages: Total number of pages
            - navigation_info: Navigation context
    """
    try:
        if session_id not in _navigation_state:
            return CommandResult(
                status="error",
                stderr=f"Navigation session '{session_id}' not found. Initialize navigation first.",
                exit_code=1,
            )

        nav_state = _navigation_state[session_id]
        doc_key = f"{nav_state.filename}_{session_id}"

        if doc_key not in _document_pages:
            return CommandResult(
                status="error",
                stderr=f"Document pages not found for session '{session_id}'",
                exit_code=1,
            )

        if page_number < 1 or page_number > nav_state.total_pages:
            return CommandResult(
                status="error",
                stderr=f"Page number {page_number} out of range (1-{nav_state.total_pages})",
                exit_code=1,
            )

        # Update navigation state
        nav_state.current_page = page_number
        page_content = _document_pages[doc_key][page_number]

        return CommandResult(
            status="success",
            stdout=json.dumps(
                {
                    "session_id": session_id,
                    "current_page": page_number,
                    "total_pages": nav_state.total_pages,
                    "page_content": page_content["text"],
                    "filename": nav_state.filename,
                    "navigation_info": {
                        "has_previous": page_number > 1,
                        "has_next": page_number < nav_state.total_pages,
                        "bookmarks": nav_state.bookmarks,
                    },
                }
            ),
        )

    except Exception as e:
        return CommandResult(
            status="error", stderr=f"Failed to navigate to page: {str(e)}", exit_code=1
        )


@mcp.tool
@return_as_dict
def get_current_page(session_id: str) -> Dict[str, Any]:
    """Get the current page content and navigation state

    Args:
        session_id: Session identifier for the navigation session

    Returns:
        Dict containing current page information and navigation state
    """
    try:
        if session_id not in _navigation_state:
            return CommandResult(
                status="error",
                stderr=f"Navigation session '{session_id}' not found. Initialize navigation first.",
                exit_code=1,
            )

        nav_state = _navigation_state[session_id]
        doc_key = f"{nav_state.filename}_{session_id}"

        if doc_key not in _document_pages:
            return CommandResult(
                status="error",
                stderr=f"Document pages not found for session '{session_id}'",
                exit_code=1,
            )

        current_page_num = nav_state.current_page
        page_content = _document_pages[doc_key][current_page_num]

        return CommandResult(
            status="success",
            stdout=json.dumps(
                {
                    "session_id": session_id,
                    "current_page": current_page_num,
                    "total_pages": nav_state.total_pages,
                    "page_content": page_content["text"],
                    "filename": nav_state.filename,
                    "navigation_info": {
                        "has_previous": current_page_num > 1,
                        "has_next": current_page_num < nav_state.total_pages,
                        "bookmarks": nav_state.bookmarks,
                    },
                }
            ),
        )

    except Exception as e:
        return CommandResult(
            status="error", stderr=f"Failed to get current page: {str(e)}", exit_code=1
        )


@mcp.tool
@return_as_dict
def navigate_next_page(session_id: str) -> Dict[str, Any]:
    """Navigate to the next page in the PDF

    Args:
        session_id: Session identifier for the navigation session

    Returns:
        Dict containing next page information
    """
    try:
        if session_id not in _navigation_state:
            return CommandResult(
                status="error",
                stderr=f"Navigation session '{session_id}' not found. Initialize navigation first.",
                exit_code=1,
            )

        nav_state = _navigation_state[session_id]
        next_page = nav_state.current_page + 1

        if next_page > nav_state.total_pages:
            return CommandResult(
                status="error",
                stderr=f"Already at last page ({nav_state.total_pages})",
                exit_code=1,
            )

        return navigate_to_page(session_id, next_page)

    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to navigate to next page: {str(e)}",
            exit_code=1,
        )


@mcp.tool
@return_as_dict
def navigate_previous_page(session_id: str) -> Dict[str, Any]:
    """Navigate to the previous page in the PDF

    Args:
        session_id: Session identifier for the navigation session

    Returns:
        Dict containing previous page information
    """
    try:
        if session_id not in _navigation_state:
            return CommandResult(
                status="error",
                stderr=f"Navigation session '{session_id}' not found. Initialize navigation first.",
                exit_code=1,
            )

        nav_state = _navigation_state[session_id]
        prev_page = nav_state.current_page - 1

        if prev_page < 1:
            return CommandResult(
                status="error", stderr="Already at first page (1)", exit_code=1
            )

        return navigate_to_page(session_id, prev_page)

    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to navigate to previous page: {str(e)}",
            exit_code=1,
        )


@mcp.tool
@return_as_dict
def add_bookmark(session_id: str, page_number: Optional[int] = None) -> Dict[str, Any]:
    """Add a bookmark to the current or specified page

    Args:
        session_id: Session identifier for the navigation session
        page_number: Page number to bookmark (defaults to current page)

    Returns:
        Dict containing bookmark information
    """
    try:
        if session_id not in _navigation_state:
            return CommandResult(
                status="error",
                stderr=f"Navigation session '{session_id}' not found. Initialize navigation first.",
                exit_code=1,
            )

        nav_state = _navigation_state[session_id]
        bookmark_page = (
            page_number if page_number is not None else nav_state.current_page
        )

        if bookmark_page < 1 or bookmark_page > nav_state.total_pages:
            return CommandResult(
                status="error",
                stderr=f"Page number {bookmark_page} out of range (1-{nav_state.total_pages})",
                exit_code=1,
            )

        if bookmark_page not in nav_state.bookmarks:
            nav_state.bookmarks.append(bookmark_page)
            nav_state.bookmarks.sort()

        return CommandResult(
            status="success",
            stdout=json.dumps(
                {
                    "session_id": session_id,
                    "bookmarked_page": bookmark_page,
                    "all_bookmarks": nav_state.bookmarks,
                    "message": f"Bookmarked page {bookmark_page}",
                }
            ),
        )

    except Exception as e:
        return CommandResult(
            status="error", stderr=f"Failed to add bookmark: {str(e)}", exit_code=1
        )


@mcp.tool
@return_as_dict
def search_in_current_session(
    session_id: str, query: str, context_pages: int = 1
) -> Dict[str, Any]:
    """Search for text within the current PDF session and navigate to results

    Args:
        session_id: Session identifier for the navigation session
        query: Search query string
        context_pages: Number of pages around matches to include in results

    Returns:
        Dict containing search results with page navigation information
    """
    try:
        if session_id not in _navigation_state:
            return CommandResult(
                status="error",
                stderr=f"Navigation session '{session_id}' not found. Initialize navigation first.",
                exit_code=1,
            )

        nav_state = _navigation_state[session_id]
        doc_key = f"{nav_state.filename}_{session_id}"

        if doc_key not in _document_pages:
            return CommandResult(
                status="error",
                stderr=f"Document pages not found for session '{session_id}'",
                exit_code=1,
            )

        # Add to search history
        if query not in nav_state.search_history:
            nav_state.search_history.append(query)

        # Search through all pages
        matches = []
        pages_content = _document_pages[doc_key]

        for page_num, page_data in pages_content.items():
            page_text = page_data["text"]

            # Case-insensitive search
            if query.lower() in page_text.lower():
                # Find all occurrences in this page
                start = 0
                while True:
                    pos = page_text.lower().find(query.lower(), start)
                    if pos == -1:
                        break

                    # Get context around match
                    context_start = max(0, pos - 200)
                    context_end = min(len(page_text), pos + len(query) + 200)
                    context = page_text[context_start:context_end].strip()

                    matches.append(
                        {
                            "page_number": page_num,
                            "position": pos,
                            "context": context,
                            "match_text": page_text[pos : pos + len(query)],
                        }
                    )

                    start = pos + 1

        # If matches found, navigate to first match
        if matches:
            first_match_page = matches[0]["page_number"]
            nav_state.current_page = first_match_page

        return CommandResult(
            status="success",
            stdout=json.dumps(
                {
                    "session_id": session_id,
                    "query": query,
                    "matches": matches,
                    "total_matches": len(matches),
                    "current_page": nav_state.current_page,
                    "navigated_to_first_match": len(matches) > 0,
                    "search_history": nav_state.search_history,
                }
            ),
        )

    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to search in current session: {str(e)}",
            exit_code=1,
        )


@mcp.tool
@return_as_dict
def rag_query_current_session(
    session_id: str, query: str, top_k: int = 3, search_scope: str = "all"
) -> Dict[str, Any]:
    """Perform RAG query within the current PDF session with semantic search

    Args:
        session_id: Session identifier for the navigation session
        query: Query string for semantic search
        top_k: Number of most relevant chunks to return
        search_scope: "all" for entire document, "current" for current page, "bookmarks" for bookmarked pages

    Returns:
        Dict containing semantically relevant content chunks with navigation info
    """
    if not PDF_LIBS_AVAILABLE:
        return CommandResult(
            status="error",
            stderr="PDF libraries not available. Install required packages.",
            exit_code=1,
        )

    try:
        if session_id not in _navigation_state:
            return CommandResult(
                status="error",
                stderr=f"Navigation session '{session_id}' not found. Initialize navigation first.",
                exit_code=1,
            )

        model = get_embedding_model()
        if model is None:
            return CommandResult(
                status="error", stderr="Failed to load embedding model", exit_code=1
            )

        nav_state = _navigation_state[session_id]
        doc_key = f"{nav_state.filename}_{session_id}"

        if doc_key not in _document_pages:
            return CommandResult(
                status="error",
                stderr=f"Document pages not found for session '{session_id}'",
                exit_code=1,
            )

        # Determine search scope
        pages_to_search = []
        if search_scope == "current":
            pages_to_search = [nav_state.current_page]
        elif search_scope == "bookmarks":
            pages_to_search = (
                nav_state.bookmarks if nav_state.bookmarks else [nav_state.current_page]
            )
        else:  # "all"
            pages_to_search = list(_document_pages[doc_key].keys())

        # Create chunks from selected pages
        chunks = []
        chunk_size = 500

        for page_num in pages_to_search:
            page_text = _document_pages[doc_key][page_num]["text"]

            # Split page into chunks
            for i in range(0, len(page_text), chunk_size):
                chunk_text = page_text[i : i + chunk_size]
                if chunk_text.strip():
                    chunks.append(
                        {
                            "text": chunk_text,
                            "page_number": page_num,
                            "chunk_start": i,
                            "chunk_end": min(i + chunk_size, len(page_text)),
                        }
                    )

        if not chunks:
            return CommandResult(
                status="error", stderr="No content found in search scope", exit_code=1
            )

        # Create embeddings for chunks
        chunk_texts = [chunk["text"] for chunk in chunks]
        chunk_embeddings = model.encode(chunk_texts)

        # Create query embedding and find similarities
        query_embedding = model.encode([query])
        similarities = cosine_similarity(query_embedding, chunk_embeddings)[0]

        # Get top-k results
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            chunk = chunks[idx]
            results.append(
                {
                    "page_number": chunk["page_number"],
                    "similarity_score": float(similarities[idx]),
                    "text": chunk["text"],
                    "chunk_start": chunk["chunk_start"],
                    "chunk_end": chunk["chunk_end"],
                }
            )

        # Navigate to the most relevant page
        if results:
            most_relevant_page = results[0]["page_number"]
            nav_state.current_page = most_relevant_page

        return CommandResult(
            status="success",
            stdout=json.dumps(
                {
                    "session_id": session_id,
                    "query": query,
                    "search_scope": search_scope,
                    "results": results,
                    "total_chunks_searched": len(chunks),
                    "current_page": nav_state.current_page,
                    "navigated_to_most_relevant": len(results) > 0,
                }
            ),
        )

    except Exception as e:
        return CommandResult(
            status="error", stderr=f"Failed to perform RAG query: {str(e)}", exit_code=1
        )


@mcp.tool
@return_as_dict
def get_navigation_status(session_id: str) -> Dict[str, Any]:
    """Get current navigation status and session information

    Args:
        session_id: Session identifier for the navigation session

    Returns:
        Dict containing complete navigation status
    """
    try:
        if session_id not in _navigation_state:
            return CommandResult(
                status="error",
                stderr=f"Navigation session '{session_id}' not found. Initialize navigation first.",
                exit_code=1,
            )

        nav_state = _navigation_state[session_id]

        return CommandResult(
            status="success",
            stdout=json.dumps(
                {
                    "session_id": session_id,
                    "filename": nav_state.filename,
                    "current_page": nav_state.current_page,
                    "total_pages": nav_state.total_pages,
                    "bookmarks": nav_state.bookmarks,
                    "search_history": nav_state.search_history,
                    "navigation_info": {
                        "has_previous": nav_state.current_page > 1,
                        "has_next": nav_state.current_page < nav_state.total_pages,
                        "progress_percentage": round(
                            (nav_state.current_page / nav_state.total_pages) * 100, 1
                        ),
                    },
                }
            ),
        )

    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to get navigation status: {str(e)}",
            exit_code=1,
        )


@mcp.tool
@return_as_dict
def close_navigation_session(session_id: str) -> Dict[str, Any]:
    """Close a navigation session and clean up resources

    Args:
        session_id: Session identifier for the navigation session to close

    Returns:
        Dict containing session closure confirmation
    """
    try:
        if session_id not in _navigation_state:
            return CommandResult(
                status="error",
                stderr=f"Navigation session '{session_id}' not found",
                exit_code=1,
            )

        nav_state = _navigation_state[session_id]
        filename = nav_state.filename
        doc_key = f"{filename}_{session_id}"

        # Clean up resources
        if doc_key in _document_pages:
            del _document_pages[doc_key]
        if doc_key in _document_embeddings:
            del _document_embeddings[doc_key]
        if doc_key in _document_chunks:
            del _document_chunks[doc_key]
        del _navigation_state[session_id]

        return CommandResult(
            status="success",
            stdout=json.dumps(
                {
                    "session_id": session_id,
                    "filename": filename,
                    "message": f"Navigation session '{session_id}' closed successfully",
                }
            ),
        )

    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to close navigation session: {str(e)}",
            exit_code=1,
        )


@mcp.tool
@return_as_dict
def extract_text_from_pdf(
    filename: str, start_page: int = 1, end_page: Optional[int] = None
) -> Dict[str, Any]:
    """Extract text content from a PDF file, limited to 32000 characters, preserving page breaks.
    Always navigate 2-3 pages at a time, avoid using this tool for large documents.

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
            exit_code=1,
        )

    try:
        pdf_path = get_workspace_path() / filename
        if not pdf_path.exists():
            return CommandResult(
                status="error",
                stderr=f"PDF file '{filename}' not found in workspace",
                exit_code=1,
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
                exit_code=1,
            )

        full_text = "\n\n".join(text_content[:32384])

        return CommandResult(
            status="success",
            stdout=json.dumps(
                {
                    "text": full_text,
                    "pages_processed": pages_processed,
                    "total_pages": total_pages,
                    "filename": filename,
                }
            ),
        )

    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to extract text from PDF: {str(e)}",
            exit_code=1,
        )


@mcp.tool
@return_as_dict
def search_keywords_in_pdf(
    filename: str, keywords: str, case_sensitive: bool = False
) -> Dict[str, Any]:
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
                status="error", stderr="No valid keywords provided", exit_code=1
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

                    matches.append(
                        {
                            "keyword": keyword,
                            "page": page_num,
                            "position": match.start(),
                            "context": context,
                            "match_text": match.group(),
                        }
                    )
                    total_matches += 1

        return CommandResult(
            status="success",
            stdout=json.dumps(
                {
                    "matches": matches,
                    "total_matches": total_matches,
                    "keywords_searched": keyword_list,
                    "filename": filename,
                }
            ),
        )

    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to search keywords in PDF: {str(e)}",
            exit_code=1,
        )


print("Starting PDF Processing MCP server with streamable-http transport...")
if not PDF_LIBS_AVAILABLE:
    print("Warning: PDF libraries not fully available. Some features may not work.")
    print("Install with: pip install PyPDF2 PyMuPDF sentence-transformers scikit-learn")

if __name__ == "__main__":
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
