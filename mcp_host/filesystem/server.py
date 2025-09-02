#!/usr/bin/env python3

"""
Filesystem Operations MCP Server

Provides comprehensive filesystem tools similar to Python's os module for file and directory
operations including listing, moving, copying, path verification, permissions, and metadata.

Author: Martin Legrand - HolobiomicsLab, CNRS
"""

import sys
import os
import shutil
import json
import stat
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import glob

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from shared import CommandResult, return_as_dict

from fastmcp import FastMCP

description = """
Filesystem Operations MCP Server provides comprehensive filesystem tools for file and directory
operations. Features include listing files/directories, moving/copying files, path verification,
permission management, metadata extraction, and file content operations. All operations work
within the centralized workspace directory for security.
"""

mcp = FastMCP(
    name="Filesystem Operations MCP",
    instructions=description,
)

# Base workspace directory for all operations
WORKSPACE_DIR = Path.cwd()

def _resolve_path(path: str) -> Path:
    """Resolve a path relative to the workspace directory and ensure it's within workspace."""
    if os.path.isabs(path):
        # Convert absolute path to relative if it's within workspace
        abs_path = Path(path)
        try:
            rel_path = abs_path.relative_to(WORKSPACE_DIR)
            return WORKSPACE_DIR / rel_path
        except ValueError:
            # Path is outside workspace, restrict to workspace
            return WORKSPACE_DIR / Path(path).name
    else:
        # Relative path, resolve within workspace
        resolved = WORKSPACE_DIR / path
        # Ensure the resolved path is still within workspace
        try:
            resolved.resolve().relative_to(WORKSPACE_DIR.resolve())
            return resolved
        except ValueError:
            # Path tries to escape workspace, restrict to workspace
            return WORKSPACE_DIR / Path(path).name

def _get_file_info(file_path: Path) -> Dict[str, Any]:
    """Get comprehensive file information."""
    try:
        stat_info = file_path.stat()
        return {
            "name": file_path.name,
            "path": str(file_path.relative_to(WORKSPACE_DIR)),
            "absolute_path": str(file_path),
            "size": stat_info.st_size,
            "is_file": file_path.is_file(),
            "is_dir": file_path.is_dir(),
            "is_symlink": file_path.is_symlink(),
            "permissions": oct(stat_info.st_mode)[-3:],
            "owner_readable": bool(stat_info.st_mode & stat.S_IRUSR),
            "owner_writable": bool(stat_info.st_mode & stat.S_IWUSR),
            "owner_executable": bool(stat_info.st_mode & stat.S_IXUSR),
            "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            "accessed": datetime.fromtimestamp(stat_info.st_atime).isoformat(),
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool
def get_mcp_name() -> str:
    """Get the name of this MCP server
    
    Returns:
        str: The name of this MCP server ("Filesystem Operations MCP")
    """
    return "Filesystem Operations MCP"

@mcp.tool
@return_as_dict
def list_directory(path: str = ".", recursive: bool = False, include_hidden: bool = False, 
                  file_pattern: Optional[str] = None) -> Dict[str, Any]:
    """List files and directories in the specified path
    
    Args:
        path: Directory path to list (relative to workspace)
        recursive: Whether to list recursively
        include_hidden: Whether to include hidden files (starting with .)
        file_pattern: Glob pattern to filter files (e.g., "*.txt", "*.py")
        
    Returns:
        Dict containing:
            - status: "success" or "error"
            - files: List of file information dictionaries
            - directories: List of directory information dictionaries
            - total_files: Number of files found
            - total_directories: Number of directories found
    """
    try:
        target_path = _resolve_path(path)
        
        if not target_path.exists():
            return CommandResult(
                status="error",
                stderr=f"Directory '{path}' not found",
                exit_code=1
            )
        
        if not target_path.is_dir():
            return CommandResult(
                status="error",
                stderr=f"'{path}' is not a directory",
                exit_code=1
            )
        
        files = []
        directories = []
        
        if recursive:
            pattern = "**/*" if not file_pattern else f"**/{file_pattern}"
            items = target_path.glob(pattern)
        else:
            pattern = "*" if not file_pattern else file_pattern
            items = target_path.glob(pattern)
        
        for item in items:
            # Skip hidden files if not requested
            if not include_hidden and item.name.startswith('.'):
                continue
                
            file_info = _get_file_info(item)
            if "error" not in file_info:
                if item.is_file():
                    files.append(file_info)
                elif item.is_dir():
                    directories.append(file_info)
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "path": path,
                "files": files,
                "directories": directories,
                "total_files": len(files),
                "total_directories": len(directories),
                "recursive": recursive,
                "include_hidden": include_hidden,
                "file_pattern": file_pattern
            })
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to list directory: {str(e)}",
            exit_code=1
        )

@mcp.tool
@return_as_dict
def get_file_info(path: str) -> Dict[str, Any]:
    """Get detailed information about a file or directory
    
    Args:
        path: Path to the file or directory
        
    Returns:
        Dict containing detailed file information including size, permissions, timestamps
    """
    try:
        target_path = _resolve_path(path)
        
        if not target_path.exists():
            return CommandResult(
                status="error",
                stderr=f"Path '{path}' not found",
                exit_code=1
            )
        
        file_info = _get_file_info(target_path)
        
        if "error" in file_info:
            return CommandResult(
                status="error",
                stderr=f"Failed to get file info: {file_info['error']}",
                exit_code=1
            )
        
        # Add additional info for files
        if target_path.is_file():
            try:
                # Get file hash for integrity checking
                with open(target_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                file_info["md5_hash"] = file_hash
                
                # Try to determine file type
                suffix = target_path.suffix.lower()
                file_info["extension"] = suffix
                file_info["file_type"] = _get_file_type(suffix)
                
            except Exception as e:
                file_info["hash_error"] = str(e)
        
        return CommandResult(
            status="success",
            stdout=json.dumps(file_info)
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to get file info: {str(e)}",
            exit_code=1
        )

def _get_file_type(extension: str) -> str:
    """Determine file type based on extension."""
    type_map = {
        '.txt': 'text',
        '.md': 'markdown',
        '.py': 'python',
        '.js': 'javascript',
        '.html': 'html',
        '.css': 'css',
        '.json': 'json',
        '.xml': 'xml',
        '.csv': 'csv',
        '.pdf': 'pdf',
        '.doc': 'document',
        '.docx': 'document',
        '.xls': 'spreadsheet',
        '.xlsx': 'spreadsheet',
        '.jpg': 'image',
        '.jpeg': 'image',
        '.png': 'image',
        '.gif': 'image',
        '.mp4': 'video',
        '.avi': 'video',
        '.mp3': 'audio',
        '.wav': 'audio',
        '.zip': 'archive',
        '.tar': 'archive',
        '.gz': 'archive'
    }
    return type_map.get(extension, 'unknown')

@mcp.tool
@return_as_dict
def path_exists(path: str) -> Dict[str, Any]:
    """Check if a path exists
    
    Args:
        path: Path to check
        
    Returns:
        Dict containing existence status and path type
    """
    try:
        target_path = _resolve_path(path)
        exists = target_path.exists()
        
        result = {
            "path": path,
            "exists": exists,
            "resolved_path": str(target_path.relative_to(WORKSPACE_DIR))
        }
        
        if exists:
            result.update({
                "is_file": target_path.is_file(),
                "is_directory": target_path.is_dir(),
                "is_symlink": target_path.is_symlink()
            })
        
        return CommandResult(
            status="success",
            stdout=json.dumps(result)
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to check path existence: {str(e)}",
            exit_code=1
        )

@mcp.tool
@return_as_dict
def create_directory(path: str, parents: bool = True, exist_ok: bool = True) -> Dict[str, Any]:
    """Create a directory
    
    Args:
        path: Directory path to create
        parents: Whether to create parent directories if they don't exist
        exist_ok: Whether to raise an error if directory already exists
        
    Returns:
        Dict containing creation status
    """
    try:
        target_path = _resolve_path(path)
        
        if target_path.exists() and not exist_ok:
            return CommandResult(
                status="error",
                stderr=f"Directory '{path}' already exists",
                exit_code=1
            )
        
        target_path.mkdir(parents=parents, exist_ok=exist_ok)
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "path": path,
                "created": str(target_path.relative_to(WORKSPACE_DIR)),
                "message": f"Directory '{path}' created successfully"
            })
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to create directory: {str(e)}",
            exit_code=1
        )

@mcp.tool
@return_as_dict
def move_file(source: str, destination: str, overwrite: bool = False) -> Dict[str, Any]:
    """Move a file or directory to a new location
    
    Args:
        source: Source path
        destination: Destination path
        overwrite: Whether to overwrite if destination exists
        
    Returns:
        Dict containing move operation status
    """
    try:
        source_path = _resolve_path(source)
        dest_path = _resolve_path(destination)
        
        if not source_path.exists():
            return CommandResult(
                status="error",
                stderr=f"Source '{source}' not found",
                exit_code=1
            )
        
        if dest_path.exists() and not overwrite:
            return CommandResult(
                status="error",
                stderr=f"Destination '{destination}' already exists. Use overwrite=True to replace.",
                exit_code=1
            )
        
        # If destination exists and overwrite is True, remove it first
        if dest_path.exists() and overwrite:
            if dest_path.is_dir():
                shutil.rmtree(dest_path)
            else:
                dest_path.unlink()
        
        shutil.move(str(source_path), str(dest_path))
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "source": source,
                "destination": destination,
                "moved_to": str(dest_path.relative_to(WORKSPACE_DIR)),
                "message": f"Successfully moved '{source}' to '{destination}'"
            })
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to move file: {str(e)}",
            exit_code=1
        )

@mcp.tool
@return_as_dict
def copy_file(source: str, destination: str, overwrite: bool = False) -> Dict[str, Any]:
    """Copy a file or directory to a new location
    
    Args:
        source: Source path
        destination: Destination path
        overwrite: Whether to overwrite if destination exists
        
    Returns:
        Dict containing copy operation status
    """
    try:
        source_path = _resolve_path(source)
        dest_path = _resolve_path(destination)
        
        if not source_path.exists():
            return CommandResult(
                status="error",
                stderr=f"Source '{source}' not found",
                exit_code=1
            )
        
        if dest_path.exists() and not overwrite:
            return CommandResult(
                status="error",
                stderr=f"Destination '{destination}' already exists. Use overwrite=True to replace.",
                exit_code=1
            )
        
        if source_path.is_dir():
            if dest_path.exists() and overwrite:
                shutil.rmtree(dest_path)
            shutil.copytree(str(source_path), str(dest_path))
        else:
            shutil.copy2(str(source_path), str(dest_path))
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "source": source,
                "destination": destination,
                "copied_to": str(dest_path.relative_to(WORKSPACE_DIR)),
                "message": f"Successfully copied '{source}' to '{destination}'"
            })
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to copy file: {str(e)}",
            exit_code=1
        )

@mcp.tool
@return_as_dict
def delete_file(path: str, recursive: bool = False) -> Dict[str, Any]:
    """Delete a file or directory
    
    Args:
        path: Path to delete
        recursive: Whether to delete directories recursively
        
    Returns:
        Dict containing deletion status
    """
    try:
        target_path = _resolve_path(path)
        
        if not target_path.exists():
            return CommandResult(
                status="error",
                stderr=f"Path '{path}' not found",
                exit_code=1
            )
        
        if target_path.is_dir():
            if not recursive:
                return CommandResult(
                    status="error",
                    stderr=f"'{path}' is a directory. Use recursive=True to delete directories.",
                    exit_code=1
                )
            shutil.rmtree(target_path)
        else:
            target_path.unlink()
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "path": path,
                "message": f"Successfully deleted '{path}'"
            })
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to delete file: {str(e)}",
            exit_code=1
        )

@mcp.tool
@return_as_dict
def find_files(pattern: str, path: str = ".", case_sensitive: bool = False, 
               file_type: Optional[str] = None) -> Dict[str, Any]:
    """Find files matching a pattern
    
    Args:
        pattern: Glob pattern to search for (e.g., "*.txt", "**/test_*.py")
        path: Directory to search in
        case_sensitive: Whether pattern matching should be case sensitive
        file_type: Filter by file type ("file", "directory", or None for both)
        
    Returns:
        Dict containing list of matching files
    """
    try:
        search_path = _resolve_path(path)
        
        if not search_path.exists():
            return CommandResult(
                status="error",
                stderr=f"Search path '{path}' not found",
                exit_code=1
            )
        
        if not search_path.is_dir():
            return CommandResult(
                status="error",
                stderr=f"Search path '{path}' is not a directory",
                exit_code=1
            )
        
        # Use glob to find matching files
        matches = []
        
        if case_sensitive:
            found_paths = search_path.glob(pattern)
        else:
            # For case-insensitive search, we need to manually check
            found_paths = search_path.rglob("*") if "**" in pattern else search_path.glob("*")
            pattern_lower = pattern.lower()
            found_paths = [p for p in found_paths if p.name.lower() == pattern_lower or 
                          (pattern_lower.replace("*", "") in p.name.lower() and "*" in pattern)]
        
        for match_path in found_paths:
            # Filter by file type if specified
            if file_type == "file" and not match_path.is_file():
                continue
            elif file_type == "directory" and not match_path.is_dir():
                continue
            
            file_info = _get_file_info(match_path)
            if "error" not in file_info:
                matches.append(file_info)
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "pattern": pattern,
                "search_path": path,
                "matches": matches,
                "total_matches": len(matches),
                "case_sensitive": case_sensitive,
                "file_type_filter": file_type
            })
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to find files: {str(e)}",
            exit_code=1
        )

@mcp.tool
@return_as_dict
def get_directory_size(path: str = ".") -> Dict[str, Any]:
    """Get the total size of a directory and its contents
    
    Args:
        path: Directory path to analyze
        
    Returns:
        Dict containing size information
    """
    try:
        target_path = _resolve_path(path)
        
        if not target_path.exists():
            return CommandResult(
                status="error",
                stderr=f"Path '{path}' not found",
                exit_code=1
            )
        
        if target_path.is_file():
            size = target_path.stat().st_size
            return CommandResult(
                status="success",
                stdout=json.dumps({
                    "path": path,
                    "size_bytes": size,
                    "size_human": _format_bytes(size),
                    "is_file": True
                })
            )
        
        total_size = 0
        file_count = 0
        dir_count = 0
        
        for item in target_path.rglob("*"):
            if item.is_file():
                total_size += item.stat().st_size
                file_count += 1
            elif item.is_dir():
                dir_count += 1
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "path": path,
                "total_size_bytes": total_size,
                "total_size_human": _format_bytes(total_size),
                "file_count": file_count,
                "directory_count": dir_count,
                "is_directory": True
            })
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to get directory size: {str(e)}",
            exit_code=1
        )

def _format_bytes(bytes_size: int) -> str:
    """Format bytes into human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"

@mcp.tool
@return_as_dict
def change_permissions(path: str, permissions: str) -> Dict[str, Any]:
    """Change file or directory permissions
    
    Args:
        path: Path to change permissions for
        permissions: Permissions in octal format (e.g., "755", "644")
        
    Returns:
        Dict containing permission change status
    """
    try:
        target_path = _resolve_path(path)
        
        if not target_path.exists():
            return CommandResult(
                status="error",
                stderr=f"Path '{path}' not found",
                exit_code=1
            )
        
        # Convert octal string to integer
        try:
            perm_int = int(permissions, 8)
        except ValueError:
            return CommandResult(
                status="error",
                stderr=f"Invalid permissions format '{permissions}'. Use octal format like '755' or '644'.",
                exit_code=1
            )
        
        target_path.chmod(perm_int)
        
        # Get new permissions to confirm
        new_stat = target_path.stat()
        new_perms = oct(new_stat.st_mode)[-3:]
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "path": path,
                "old_permissions": permissions,
                "new_permissions": new_perms,
                "message": f"Successfully changed permissions of '{path}' to {permissions}"
            })
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to change permissions: {str(e)}",
            exit_code=1
        )

@mcp.tool
@return_as_dict
def get_workspace_info() -> Dict[str, Any]:
    """Get information about the current workspace directory
    
    Returns:
        Dict containing workspace information
    """
    try:
        workspace_info = _get_file_info(WORKSPACE_DIR)
        
        # Add additional workspace-specific info
        workspace_info.update({
            "workspace_path": str(WORKSPACE_DIR),
            "is_workspace": True
        })
        
        # Get summary statistics
        total_files = 0
        total_dirs = 0
        total_size = 0
        
        for item in WORKSPACE_DIR.rglob("*"):
            if item.is_file():
                total_files += 1
                total_size += item.stat().st_size
            elif item.is_dir():
                total_dirs += 1
        
        workspace_info.update({
            "total_files": total_files,
            "total_directories": total_dirs,
            "total_size_bytes": total_size,
            "total_size_human": _format_bytes(total_size)
        })
        
        return CommandResult(
            status="success",
            stdout=json.dumps(workspace_info)
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to get workspace info: {str(e)}",
            exit_code=1
        )

# Port handling for deployment
if len(sys.argv) > 1 and sys.argv[1].isdigit():
    port = int(sys.argv[1])
else:
    port = int(input("Enter port number: "))

print(f"Starting Filesystem Operations MCP server on port {port}...")
print(f"Workspace directory: {WORKSPACE_DIR}")
mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path="/mcp")
