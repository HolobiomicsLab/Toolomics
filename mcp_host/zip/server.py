#!/usr/bin/env python3

"""
Zip File Operations MCP Server

Provides tools for creating, extracting, and manipulating ZIP archives.

Author: Cline AI Assistant - HolobiomicsLab, CNRS
"""

import sys
import os
import zipfile
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from shared import CommandResult, get_workspace_path, return_as_dict

description = """Zip File Operations MCP Server provides comprehensive tools for working with ZIP archives.
It allows users to create ZIP files from directories or individual files, extract ZIP archives, 
list contents of ZIP files, add files to existing archives, and perform various ZIP file operations.
All operations work within the centralized workspace directory for seamless integration with other MCP servers.
"""

mcp = FastMCP(
    name="Zip File Operations MCP",
    instructions=description,
)

# Default working directory for ZIP operations - use shared workspace
ZIP_DIR = get_workspace_path()
ZIP_DIR.mkdir(exist_ok=True)


def _get_zip_path(name: str) -> Path:
    """Get the full path for a ZIP file, ensuring it's in our workspace directory."""
    # Sanitize filename
    safe_name = "".join(c for c in name if c.isalnum() or c in "._-")
    if not safe_name.endswith(".zip"):
        safe_name += ".zip"
    return ZIP_DIR / safe_name


def _get_file_path(name: str) -> Path:
    """Get the full path for a file in the workspace directory."""
    return ZIP_DIR / name


@mcp.tool
@return_as_dict
def create_zip_from_directory(
    directory_path: str, 
    zip_name: str,
    include_hidden: bool = False
) -> Dict[str, Any]:
    """
    Create a ZIP archive from a directory.

    Args:
        directory_path: Path to the directory to compress (relative to workspace)
        zip_name: Name of the ZIP file to create
        include_hidden: Whether to include hidden files (starting with .)

    Returns:
        Dictionary with ZIP creation info
    """
    try:
        source_dir = _get_file_path(directory_path)
        zip_path = _get_zip_path(zip_name)
        
        if not source_dir.exists() or not source_dir.is_dir():
            return CommandResult(
                status="error",
                stderr=f"Directory '{directory_path}' not found in workspace",
                exit_code=1
            )
        
        file_count = 0
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    # Skip hidden files if not included
                    if not include_hidden and any(part.startswith('.') for part in file_path.parts):
                        continue
                    
                    # Calculate relative path from source directory
                    relative_path = file_path.relative_to(source_dir)
                    zipf.write(file_path, relative_path)
                    file_count += 1
        
        return CommandResult(
            status="success",
            stdout=f"Created ZIP archive '{zip_name}' with {file_count} files from directory '{directory_path}'",
            exit_code=0
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to create ZIP archive: {str(e)}",
            exit_code=1
        )


@mcp.tool
@return_as_dict
def create_zip_from_files(
    file_paths: List[str], 
    zip_name: str
) -> Dict[str, Any]:
    """
    Create a ZIP archive from a list of files.

    Args:
        file_paths: List of file paths to include in the ZIP (relative to workspace)
        zip_name: Name of the ZIP file to create

    Returns:
        Dictionary with ZIP creation info
    """
    try:
        zip_path = _get_zip_path(zip_name)
        
        added_files = []
        missing_files = []
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path_str in file_paths:
                file_path = _get_file_path(file_path_str)
                
                if file_path.exists() and file_path.is_file():
                    # Use just the filename in the archive
                    zipf.write(file_path, file_path.name)
                    added_files.append(file_path_str)
                else:
                    missing_files.append(file_path_str)
        
        result_msg = f"Created ZIP archive '{zip_name}' with {len(added_files)} files"
        if missing_files:
            result_msg += f". Missing files: {', '.join(missing_files)}"
        
        return CommandResult(
            status="success" if added_files else "error",
            stdout=result_msg,
            stderr="" if not missing_files else f"Missing files: {', '.join(missing_files)}",
            exit_code=0 if added_files else 1
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to create ZIP archive: {str(e)}",
            exit_code=1
        )


@mcp.tool
@return_as_dict
def extract_zip(
    zip_name: str, 
    extract_to: Optional[str] = None,
    overwrite: bool = False
) -> Dict[str, Any]:
    """
    Extract a ZIP archive.

    Args:
        zip_name: Name of the ZIP file to extract
        extract_to: Directory to extract to (relative to workspace). If None, extracts to a directory named after the ZIP file
        overwrite: Whether to overwrite existing files

    Returns:
        Dictionary with extraction info
    """
    try:
        zip_path = _get_zip_path(zip_name)
        
        if not zip_path.exists():
            return CommandResult(
                status="error",
                stderr=f"ZIP file '{zip_name}' not found in workspace",
                exit_code=1
            )
        
        # Determine extraction directory
        if extract_to:
            extract_dir = _get_file_path(extract_to)
        else:
            # Use ZIP filename without extension as directory name
            extract_dir = _get_file_path(zip_path.stem)
        
        # Create extraction directory
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        extracted_files = []
        skipped_files = []
        
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            for member in zipf.namelist():
                target_path = extract_dir / member
                
                # Check if file exists and overwrite setting
                if target_path.exists() and not overwrite:
                    skipped_files.append(member)
                    continue
                
                # Extract the file
                zipf.extract(member, extract_dir)
                extracted_files.append(member)
        
        result_msg = f"Extracted {len(extracted_files)} files from '{zip_name}' to '{extract_dir.name}'"
        if skipped_files:
            result_msg += f". Skipped {len(skipped_files)} existing files (use overwrite=true to replace)"
        
        return CommandResult(
            status="success",
            stdout=result_msg,
            exit_code=0
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to extract ZIP archive: {str(e)}",
            exit_code=1
        )


@mcp.tool
@return_as_dict
def list_zip_contents(zip_name: str) -> Dict[str, Any]:
    """
    List the contents of a ZIP archive.

    Args:
        zip_name: Name of the ZIP file to inspect

    Returns:
        Dictionary with ZIP contents info
    """
    try:
        zip_path = _get_zip_path(zip_name)
        
        if not zip_path.exists():
            return CommandResult(
                status="error",
                stderr=f"ZIP file '{zip_name}' not found in workspace",
                exit_code=1
            )
        
        files_info = []
        total_compressed_size = 0
        total_uncompressed_size = 0
        
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            for info in zipf.infolist():
                if not info.is_dir():
                    files_info.append({
                        "filename": info.filename,
                        "compressed_size": info.compress_size,
                        "uncompressed_size": info.file_size,
                        "compression_ratio": round((1 - info.compress_size / info.file_size) * 100, 1) if info.file_size > 0 else 0,
                        "date_time": f"{info.date_time[0]}-{info.date_time[1]:02d}-{info.date_time[2]:02d} {info.date_time[3]:02d}:{info.date_time[4]:02d}:{info.date_time[5]:02d}"
                    })
                    total_compressed_size += info.compress_size
                    total_uncompressed_size += info.file_size
        
        overall_compression = round((1 - total_compressed_size / total_uncompressed_size) * 100, 1) if total_uncompressed_size > 0 else 0
        
        return CommandResult(
            status="success",
            stdout={
                "zip_name": zip_name,
                "file_count": len(files_info),
                "total_compressed_size": total_compressed_size,
                "total_uncompressed_size": total_uncompressed_size,
                "overall_compression_ratio": overall_compression,
                "files": files_info
            },
            exit_code=0
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to list ZIP contents: {str(e)}",
            exit_code=1
        )


@mcp.tool
@return_as_dict
def add_files_to_zip(
    zip_name: str, 
    file_paths: List[str]
) -> Dict[str, Any]:
    """
    Add files to an existing ZIP archive.

    Args:
        zip_name: Name of the ZIP file to modify
        file_paths: List of file paths to add (relative to workspace)

    Returns:
        Dictionary with operation info
    """
    try:
        zip_path = _get_zip_path(zip_name)
        
        if not zip_path.exists():
            return CommandResult(
                status="error",
                stderr=f"ZIP file '{zip_name}' not found in workspace",
                exit_code=1
            )
        
        added_files = []
        missing_files = []
        
        # Create a temporary file to work with
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            temp_path = Path(temp_file.name)
        
        try:
            # Copy existing ZIP to temp file and add new files
            with zipfile.ZipFile(zip_path, 'r') as source_zip:
                with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as target_zip:
                    # Copy existing files
                    for item in source_zip.infolist():
                        data = source_zip.read(item.filename)
                        target_zip.writestr(item, data)
                    
                    # Add new files
                    for file_path_str in file_paths:
                        file_path = _get_file_path(file_path_str)
                        
                        if file_path.exists() and file_path.is_file():
                            target_zip.write(file_path, file_path.name)
                            added_files.append(file_path_str)
                        else:
                            missing_files.append(file_path_str)
            
            # Replace original ZIP with updated one
            temp_path.replace(zip_path)
            
        finally:
            # Clean up temp file if it still exists
            if temp_path.exists():
                temp_path.unlink()
        
        result_msg = f"Added {len(added_files)} files to ZIP archive '{zip_name}'"
        if missing_files:
            result_msg += f". Missing files: {', '.join(missing_files)}"
        
        return CommandResult(
            status="success" if added_files else "error",
            stdout=result_msg,
            stderr="" if not missing_files else f"Missing files: {', '.join(missing_files)}",
            exit_code=0 if added_files else 1
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to add files to ZIP archive: {str(e)}",
            exit_code=1
        )


@mcp.tool
@return_as_dict
def extract_specific_files(
    zip_name: str, 
    file_names: List[str],
    extract_to: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extract specific files from a ZIP archive.

    Args:
        zip_name: Name of the ZIP file
        file_names: List of file names to extract from the ZIP
        extract_to: Directory to extract to (relative to workspace). If None, extracts to workspace root

    Returns:
        Dictionary with extraction info
    """
    try:
        zip_path = _get_zip_path(zip_name)
        
        if not zip_path.exists():
            return CommandResult(
                status="error",
                stderr=f"ZIP file '{zip_name}' not found in workspace",
                exit_code=1
            )
        
        # Determine extraction directory
        if extract_to:
            extract_dir = _get_file_path(extract_to)
            extract_dir.mkdir(parents=True, exist_ok=True)
        else:
            extract_dir = ZIP_DIR
        
        extracted_files = []
        missing_files = []
        
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            available_files = zipf.namelist()
            
            for file_name in file_names:
                if file_name in available_files:
                    zipf.extract(file_name, extract_dir)
                    extracted_files.append(file_name)
                else:
                    missing_files.append(file_name)
        
        result_msg = f"Extracted {len(extracted_files)} specific files from '{zip_name}'"
        if missing_files:
            result_msg += f". Files not found in archive: {', '.join(missing_files)}"
        
        return CommandResult(
            status="success" if extracted_files else "error",
            stdout=result_msg,
            stderr="" if not missing_files else f"Files not found: {', '.join(missing_files)}",
            exit_code=0 if extracted_files else 1
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to extract specific files: {str(e)}",
            exit_code=1
        )


@mcp.tool
@return_as_dict
def list_zip_files() -> Dict[str, Any]:
    """
    List all ZIP files in the workspace.

    Returns:
        Dictionary with list of ZIP files and their info
    """
    try:
        zip_files = []
        
        for zip_file in ZIP_DIR.glob("*.zip"):
            try:
                file_size = zip_file.stat().st_size
                
                # Get basic info about the ZIP
                with zipfile.ZipFile(zip_file, 'r') as zipf:
                    file_count = len([f for f in zipf.infolist() if not f.is_dir()])
                
                zip_files.append({
                    "name": zip_file.name,
                    "size_bytes": file_size,
                    "size_mb": round(file_size / (1024 * 1024), 2),
                    "file_count": file_count
                })
                
            except Exception as e:
                zip_files.append({
                    "name": zip_file.name,
                    "error": f"Failed to read ZIP info: {str(e)}"
                })
        
        return CommandResult(
            status="success",
            stdout={
                "zip_files": zip_files,
                "total_count": len(zip_files)
            },
            exit_code=0
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to list ZIP files: {str(e)}",
            exit_code=1
        )


@mcp.tool
@return_as_dict
def delete_zip_file(zip_name: str) -> Dict[str, Any]:
    """
    Delete a ZIP file from the workspace.

    Args:
        zip_name: Name of the ZIP file to delete

    Returns:
        Dictionary with deletion status
    """
    try:
        zip_path = _get_zip_path(zip_name)
        
        if zip_path.exists():
            zip_path.unlink()
            return CommandResult(
                status="success",
                stdout=f"ZIP file '{zip_name}' deleted successfully",
                exit_code=0
            )
        else:
            return CommandResult(
                status="error",
                stderr=f"ZIP file '{zip_name}' not found in workspace",
                exit_code=1
            )
            
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to delete ZIP file: {str(e)}",
            exit_code=1
        )


print("Starting Zip File Operations MCP server with streamable-http transport...")
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
