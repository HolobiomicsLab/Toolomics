#!/usr/bin/env python3

"""
HTML Code Extraction MCP Server

Provides tools for extracting code blocks from HTML files, particularly
from notebook exports that contain code in <pre class="language"><code> format.

Author: Martin Legrand - HolobiomicsLab, CNRS
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from shared import CommandResult, return_as_dict, get_workspace_path

# Import our HTML parsing logic
from html_parser import HTMLCodeExtractor

description = """HTML Code Extraction MCP Server provides tools for extracting code blocks from HTML files.
It is particularly useful for processing notebook exports that contain code in <pre class="language"><code> format.
The server can extract code blocks, filter by language, combine them, and save the results to files.
"""

mcp = FastMCP(
    name="HTML Code Extraction MCP",
    instructions=description,
)

# Default working directory - use shared workspace
WORKSPACE_DIR = get_workspace_path()

# Initialize the HTML code extractor
extractor = HTMLCodeExtractor()


def _get_file_path(filename: str) -> Path:
    """Get the full path for a file, ensuring it's in our workspace directory."""
    # Sanitize filename
    safe_name = "".join(c for c in filename if c.isalnum() or c in "._-/")
    return WORKSPACE_DIR / safe_name


@mcp.tool
@return_as_dict
def extract_code_from_html(
    html_file: str,
    language: Optional[str] = None,
    save_combined: Optional[str] = None,
    separator: str = "\n\n"
) -> Dict[str, Any]:
    """
    Extract code blocks from an HTML file.

    Args:
        html_file: Path to the HTML file (relative to workspace)
        language: Optional language filter (e.g., 'r', 'python', 'sql')
        save_combined: Optional filename to save combined code to
        separator: Separator to use when combining code blocks

    Returns:
        Dictionary with extracted code blocks and metadata
    """
    try:
        file_path = _get_file_path(html_file)
        
        if not file_path.exists():
            return CommandResult(
                status="error",
                stderr=f"HTML file not found: {html_file}",
                exit_code=1
            )
        
        # Extract code blocks
        code_blocks = extractor.extract_from_file(str(file_path), language)
        
        # Get summary statistics
        summary = extractor.get_code_summary(code_blocks)
        
        result_data = {
            "html_file": html_file,
            "language_filter": language,
            "code_blocks": code_blocks,
            "summary": summary
        }
        
        # Save combined code if requested
        if save_combined and code_blocks:
            combined_code = extractor.combine_code_blocks(code_blocks, separator)
            output_path = _get_file_path(save_combined)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(combined_code)
            
            result_data["combined_code_saved"] = save_combined
            result_data["combined_code_path"] = str(output_path)
            result_data["combined_code_preview"] = combined_code[:500] + "..." if len(combined_code) > 500 else combined_code
        
        return CommandResult(
            status="success",
            stdout=json.dumps(result_data)
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to extract code from HTML: {str(e)}",
            exit_code=1
        )

@mcp.tool
@return_as_dict
def combine_code_blocks(
    html_file: str,
    language: Optional[str] = None,
    output_file: str = "combined_code.txt",
    separator: str = "\n\n",
    include_comments: bool = True
) -> Dict[str, Any]:
    """
    Extract and combine code blocks from an HTML file into a single output file.

    Args:
        html_file: Path to the HTML file (relative to workspace)
        language: Optional language filter (e.g., 'r', 'python', 'sql')
        output_file: Name of the output file to save combined code
        separator: Separator to use between code blocks
        include_comments: Whether to include comments with block information

    Returns:
        Dictionary with operation status and file information
    """
    try:
        file_path = _get_file_path(html_file)
        
        if not file_path.exists():
            return CommandResult(
                status="error",
                stderr=f"HTML file not found: {html_file}",
                exit_code=1
            )
        
        # Extract code blocks
        code_blocks = extractor.extract_from_file(str(file_path), language)
        
        if not code_blocks:
            return CommandResult(
                status="success",
                stdout=json.dumps({
                    "message": "No code blocks found",
                    "html_file": html_file,
                    "language_filter": language,
                    "code_blocks_found": 0
                })
            )
        
        # Prepare combined content
        combined_parts = []
        
        for i, block in enumerate(code_blocks):
            if include_comments:
                comment_prefix = "#" if block['language'] in ['r', 'python', 'bash'] else "//"
                combined_parts.append(f"{comment_prefix} Code block {i+1} ({block['language']})")
            
            combined_parts.append(block['code'])
        
        combined_code = separator.join(combined_parts)
        
        # Save to output file
        output_path = _get_file_path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(combined_code)
        
        # Get summary
        summary = extractor.get_code_summary(code_blocks)
        
        result_data = {
            "html_file": html_file,
            "output_file": output_file,
            "output_path": str(output_path),
            "language_filter": language,
            "code_blocks_found": len(code_blocks),
            "summary": summary,
            "combined_code_preview": combined_code[:500] + "..." if len(combined_code) > 500 else combined_code
        }
        
        return CommandResult(
            status="success",
            stdout=json.dumps(result_data)
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to combine code blocks: {str(e)}",
            exit_code=1
        )


@mcp.tool
@return_as_dict
def list_html_files() -> Dict[str, Any]:
    """
    List all HTML files in the workspace directory.

    Returns:
        Dictionary with list of HTML files
    """
    try:
        html_files = []
        
        # Search for HTML files recursively
        for html_file in WORKSPACE_DIR.rglob("*.html"):
            try:
                file_size = html_file.stat().st_size
                relative_path = html_file.relative_to(WORKSPACE_DIR)
                
                html_files.append({
                    "filename": str(relative_path),
                    "full_path": str(html_file),
                    "size_bytes": file_size,
                    "size_mb": round(file_size / (1024 * 1024), 2)
                })
            except Exception as e:
                html_files.append({
                    "filename": str(html_file.name),
                    "error": f"Failed to read file info: {str(e)}"
                })
        
        result_data = {
            "html_files": html_files,
            "total_count": len(html_files),
            "workspace": str(WORKSPACE_DIR)
        }
        
        return CommandResult(
            status="success",
            stdout=json.dumps(result_data)
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to list HTML files: {str(e)}",
            exit_code=1
        )


@mcp.tool
@return_as_dict
def analyze_html_code_content(html_file: str) -> Dict[str, Any]:
    """
    Analyze an HTML file to get a summary of its code content without extracting.

    Args:
        html_file: Path to the HTML file (relative to workspace)

    Returns:
        Dictionary with analysis results
    """
    try:
        file_path = _get_file_path(html_file)
        
        if not file_path.exists():
            return CommandResult(
                status="error",
                stderr=f"HTML file not found: {html_file}",
                exit_code=1
            )
        
        # Extract all code blocks (no language filter)
        code_blocks = extractor.extract_from_file(str(file_path))
        
        # Get detailed summary
        summary = extractor.get_code_summary(code_blocks)
        
        # Get sample of each language
        language_samples = {}
        for block in code_blocks:
            lang = block['language']
            if lang not in language_samples:
                # Take first 200 characters as sample
                sample = block['code'][:200]
                if len(block['code']) > 200:
                    sample += "..."
                language_samples[lang] = sample
        
        result_data = {
            "html_file": html_file,
            "file_size_bytes": file_path.stat().st_size,
            "summary": summary,
            "language_samples": language_samples
        }
        
        return CommandResult(
            status="success",
            stdout=json.dumps(result_data)
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to analyze HTML code content: {str(e)}",
            exit_code=1
        )


print("Starting HTML Code Extraction MCP server with streamable-http transport...")
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
