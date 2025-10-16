#!/usr/bin/env python3

"""
Text File Editor MCP Server

Provides comprehensive tools for reading, analyzing, and editing text files.
Supports searching, replacing, appending, line-based operations, and more.

Author: HolobiomicsLab, CNRS
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP

# Add project root to path for shared imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from shared import CommandResult, return_as_dict, get_workspace_path

description = """
Text File Editor MCP Server provides comprehensive tools for text file manipulation.
It allows reading files, searching for patterns, replacing text, appending content,
line-based operations, and managing text files in the workspace.
"""

mcp = FastMCP(
    name="Text File Editor MCP",
    instructions=description,
)

# Working directory for text files - use shared workspace
WORKSPACE_DIR = get_workspace_path()


def _get_txt_path(filename: str) -> Path:
    """Get the full path for a text file, ensuring it's in our workspace."""
    # Sanitize filename
    safe_name = "".join(c for c in filename if c.isalnum() or c in "._-/")
    return WORKSPACE_DIR / safe_name


@mcp.tool
@return_as_dict
def read_txt_file(filename: str) -> Dict[str, Any]:
    """
    Read a text file and return its content.
    
    Args:
        filename (str): Name of the text file to read
    
    Returns:
        dict: CommandResult with file content and basic info
    """
    try:
        filepath = _get_txt_path(filename)
        if not filepath.exists():
            return CommandResult(
                status="error",
                stderr=f"File '{filename}' not found in workspace",
                exit_code=1
            )
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        return CommandResult(
            status="success",
            stdout=f"File content:\n{content}",
            stderr=f"File info: {len(lines)} lines, {len(content)} characters, {len(content.split())} words",
            exit_code=0
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=str(e),
            exit_code=1
        )


@mcp.tool
@return_as_dict
def write_txt_file(filename: str, content: str, overwrite: bool = False) -> Dict[str, Any]:
    """
    Create or write to a text file.
    
    Args:
        filename (str): Name of the text file to write
        content (str): Content to write
        overwrite (bool): Whether to overwrite if file exists (default: False)
    
    Returns:
        dict: CommandResult with write status
    """
    try:
        filepath = _get_txt_path(filename)
        
        # Check if file already exists
        if filepath.exists() and not overwrite:
            return CommandResult(
                status="error",
                stderr=f"File '{filename}' already exists. Set overwrite=true to replace it.",
                exit_code=1
            )
        
        # Create parent directories if needed
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return CommandResult(
            status="success",
            stdout=f"Successfully wrote to '{filename}' ({len(content)} characters)",
            stderr=f"File {'overwritten' if overwrite and filepath.exists() else 'created'}",
            exit_code=0
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=str(e),
            exit_code=1
        )


@mcp.tool
@return_as_dict
def append_to_txt_file(filename: str, content: str, newline: bool = True) -> Dict[str, Any]:
    """
    Append content to an existing text file.
    
    Args:
        filename (str): Name of the text file
        content (str): Content to append
        newline (bool): Whether to add a newline before content (default: True)
    
    Returns:
        dict: CommandResult with append status
    """
    try:
        filepath = _get_txt_path(filename)
        if not filepath.exists():
            return CommandResult(
                status="error",
                stderr=f"File '{filename}' not found. Use write_txt_file to create it first.",
                exit_code=1
            )
        
        with open(filepath, 'a', encoding='utf-8') as f:
            if newline:
                f.write('\n' + content)
            else:
                f.write(content)
        
        return CommandResult(
            status="success",
            stdout=f"Successfully appended to '{filename}' ({len(content)} characters)",
            exit_code=0
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=str(e),
            exit_code=1
        )


@mcp.tool
@return_as_dict
def search_in_txt_file(filename: str, pattern: str, case_sensitive: bool = False, use_regex: bool = False) -> Dict[str, Any]:
    """
    Search for a pattern in a text file.
    
    Args:
        filename (str): Name of the text file to search
        pattern (str): Pattern to search for
        case_sensitive (bool): Whether search is case sensitive (default: False)
        use_regex (bool): Whether to use regex pattern matching (default: False)
    
    Returns:
        dict: CommandResult with search results
    """
    try:
        filepath = _get_txt_path(filename)
        if not filepath.exists():
            return CommandResult(
                status="error",
                stderr=f"File '{filename}' not found in workspace",
                exit_code=1
            )
        
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        results = []
        
        for i, line in enumerate(lines, 1):
            matched = False
            
            if use_regex:
                flags = 0 if case_sensitive else re.IGNORECASE
                if re.search(pattern, line, flags):
                    matched = True
            else:
                search_line = line if case_sensitive else line.lower()
                search_pattern = pattern if case_sensitive else pattern.lower()
                if search_pattern in search_line:
                    matched = True
            
            if matched:
                results.append({
                    "line_number": i,
                    "content": line.rstrip('\n'),
                    "match_type": "regex" if use_regex else "text"
                })
        
        return CommandResult(
            status="success",
            stdout=f"Search results for '{pattern}' in {filename}: {results}",
            stderr=f"Found {len(results)} matches",
            exit_code=0
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=str(e),
            exit_code=1
        )

@mcp.tool
@return_as_dict
def list_txt_files() -> Dict[str, Any]:
    """
    List all text files in the workspace.
    
    Returns:
        dict: CommandResult with list of text files
    """
    try:
        txt_files = []
        
        for dirpath, dirnames, filenames in os.walk(WORKSPACE_DIR):
            for filename in filenames:
                if filename.endswith('.txt'):
                    try:
                        # Create full path and get relative path
                        full_path = Path(dirpath) / filename
                        relative_path = full_path.relative_to(WORKSPACE_DIR)
                        
                        # Get file size
                        size = full_path.stat().st_size
                        
                        txt_files.append({
                            "name": str(relative_path),
                            "size_bytes": size,
                            "size_kb": round(size / 1024, 2)
                        })
                    except Exception as e:
                        txt_files.append({
                            "name": filename,
                            "error": f"Could not process: {str(e)}"
                        })
        
        return CommandResult(
            status="success",
            stdout=f"Text files in workspace: {txt_files}",
            stderr=f"Found {len(txt_files)} text files",
            exit_code=0
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=str(e),
            exit_code=1
        )

if __name__ == "__main__":
    print("Starting Text File Editor MCP server with streamable-http transport...")
    
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
