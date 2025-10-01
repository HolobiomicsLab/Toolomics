#!/usr/bin/env python3

"""
Python File Editor MCP Server

Provides comprehensive tools for reading, analyzing, and editing Python files.
Supports method/variable search, code replacement, method extraction, and more.

Author: HolobiomicsLab, CNRS
"""

import os
import sys
import ast
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from fastmcp import FastMCP

# Add project root to path for shared imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from shared import CommandResult, return_as_dict, get_workspace_path, run_bash_subprocess

description = """
Python File Editor MCP Server provides comprehensive tools for Python code manipulation.
It allows reading files, searching for methods/variables, replacing code sections, 
extracting method implementations, creating new methods, and writing complete files.
"""

mcp = FastMCP(
    name="Python File Editor MCP",
    instructions=description,
)

# Working directory for Python files - use shared workspace
WORKSPACE_DIR = get_workspace_path()


def _get_python_path(filename: str) -> Path:
    """Get the full path for a Python file, ensuring it's in our workspace."""
    # Sanitize filename
    safe_name = "".join(c for c in filename if c.isalnum() or c in "._-/")
    if not safe_name.endswith(".py"):
        safe_name += ".py"
    return WORKSPACE_DIR / safe_name


def _parse_python_file(filepath: Path) -> ast.AST:
    """Parse a Python file and return its AST."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return ast.parse(content)
    except Exception as e:
        raise ValueError(f"Failed to parse Python file: {e}")


def _get_node_source(content: str, node: ast.AST) -> str:
    """Extract source code for an AST node."""
    lines = content.split('\n')
    if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
        start_line = node.lineno - 1
        end_line = node.end_lineno
        return '\n'.join(lines[start_line:end_line])
    return ""


def _find_methods_and_classes(tree: ast.AST) -> Dict[str, List[Dict[str, Any]]]:
    """Find all methods and classes in an AST."""
    methods = []
    classes = []
    functions = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check if it's inside a class (method) or standalone (function)
            parent_class = None
            for parent in ast.walk(tree):
                if isinstance(parent, ast.ClassDef):
                    for child in ast.walk(parent):
                        if child is node:
                            parent_class = parent.name
                            break
            
            item = {
                "name": node.name,
                "line_start": node.lineno,
                "line_end": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                "args": [arg.arg for arg in node.args.args],
                "decorators": [ast.unparse(dec) for dec in node.decorator_list] if node.decorator_list else [],
                "docstring": ast.get_docstring(node)
            }
            
            if parent_class:
                item["class"] = parent_class
                methods.append(item)
            else:
                functions.append(item)
                
        elif isinstance(node, ast.ClassDef):
            classes.append({
                "name": node.name,
                "line_start": node.lineno,
                "line_end": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                "bases": [ast.unparse(base) for base in node.bases],
                "decorators": [ast.unparse(dec) for dec in node.decorator_list] if node.decorator_list else [],
                "docstring": ast.get_docstring(node)
            })
    
    return {
        "methods": methods,
        "functions": functions,
        "classes": classes
    }


def _find_variables(tree: ast.AST) -> List[Dict[str, Any]]:
    """Find all variable assignments in an AST."""
    variables = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    variables.append({
                        "name": target.id,
                        "line": node.lineno,
                        "value": ast.unparse(node.value) if hasattr(ast, 'unparse') else str(node.value)
                    })
                elif isinstance(target, ast.Tuple) or isinstance(target, ast.List):
                    for elt in target.elts:
                        if isinstance(elt, ast.Name):
                            variables.append({
                                "name": elt.id,
                                "line": node.lineno,
                                "value": f"part of {ast.unparse(node.value) if hasattr(ast, 'unparse') else str(node.value)}"
                            })
    
    return variables


@mcp.tool
@return_as_dict
def read_python_file(filename: str) -> Dict[str, Any]:
    """
    Read a Python file and return its content.
    
    Args:
        filename (str): Name of the Python file to read
    
    Returns:
        dict: CommandResult with file content and basic info
    """
    try:
        filepath = _get_python_path(filename)
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
            stderr=f"File info: {len(lines)} lines, {len(content)} characters",
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
def list_python_methods(filename: str) -> Dict[str, Any]:
    """
    List all methods, functions, and classes in a Python file.
    
    Args:
        filename (str): Name of the Python file to analyze
    
    Returns:
        dict: CommandResult with methods, functions, and classes info
    """
    try:
        filepath = _get_python_path(filename)
        if not filepath.exists():
            return CommandResult(
                status="error",
                stderr=f"File '{filename}' not found in workspace",
                exit_code=1
            )
        
        tree = _parse_python_file(filepath)
        code_elements = _find_methods_and_classes(tree)
        
        result = {
            "file": filename,
            "classes": code_elements["classes"],
            "functions": code_elements["functions"],
            "methods": code_elements["methods"],
            "summary": {
                "total_classes": len(code_elements["classes"]),
                "total_functions": len(code_elements["functions"]),
                "total_methods": len(code_elements["methods"])
            }
        }
        
        return CommandResult(
            status="success",
            stdout=f"Code structure analysis: {result}",
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
def search_in_python_file(filename: str, pattern: str, search_type: str = "text") -> Dict[str, Any]:
    """
    Search for patterns in a Python file.
    
    Args:
        filename (str): Name of the Python file to search
        pattern (str): Pattern to search for
        search_type (str): Type of search - "text", "method", "variable", "class"
    
    Returns:
        dict: CommandResult with search results
    """
    try:
        filepath = _get_python_path(filename)
        if not filepath.exists():
            return CommandResult(
                status="error",
                stderr=f"File '{filename}' not found in workspace",
                exit_code=1
            )
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        results = []
        
        if search_type == "text":
            # Simple text search
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if pattern in line:
                    results.append({
                        "line": i,
                        "content": line.strip(),
                        "match_type": "text"
                    })
        
        elif search_type in ["method", "variable", "class"]:
            # AST-based search
            tree = _parse_python_file(filepath)
            
            if search_type == "method":
                code_elements = _find_methods_and_classes(tree)
                for method in code_elements["methods"] + code_elements["functions"]:
                    if pattern.lower() in method["name"].lower():
                        results.append({
                            "name": method["name"],
                            "line_start": method["line_start"],
                            "line_end": method["line_end"],
                            "match_type": "method",
                            "class": method.get("class", "standalone function")
                        })
            
            elif search_type == "variable":
                variables = _find_variables(tree)
                for var in variables:
                    if pattern.lower() in var["name"].lower():
                        results.append({
                            "name": var["name"],
                            "line": var["line"],
                            "value": var["value"],
                            "match_type": "variable"
                        })
            
            elif search_type == "class":
                code_elements = _find_methods_and_classes(tree)
                for cls in code_elements["classes"]:
                    if pattern.lower() in cls["name"].lower():
                        results.append({
                            "name": cls["name"],
                            "line_start": cls["line_start"],
                            "line_end": cls["line_end"],
                            "match_type": "class"
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
def get_method_implementation(filename: str, method_name: str, class_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get the implementation of a specific method or function.
    
    Args:
        filename (str): Name of the Python file
        method_name (str): Name of the method/function
        class_name (Optional[str]): Name of the class (if it's a method)
    
    Returns:
        dict: CommandResult with method implementation
    """
    try:
        filepath = _get_python_path(filename)
        if not filepath.exists():
            return CommandResult(
                status="error",
                stderr=f"File '{filename}' not found in workspace",
                exit_code=1
            )
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = _parse_python_file(filepath)
        code_elements = _find_methods_and_classes(tree)
        
        # Search for the method
        target_method = None
        for method in code_elements["methods"] + code_elements["functions"]:
            if method["name"] == method_name:
                if class_name is None or method.get("class") == class_name:
                    target_method = method
                    break
        
        if not target_method:
            return CommandResult(
                status="error",
                stderr=f"Method '{method_name}' not found" + (f" in class '{class_name}'" if class_name else ""),
                exit_code=1
            )
        
        # Extract the method source code
        lines = content.split('\n')
        method_lines = lines[target_method["line_start"]-1:target_method["line_end"]]
        method_source = '\n'.join(method_lines)
        
        return CommandResult(
            status="success",
            stdout=f"Method implementation:\n{method_source}",
            stderr=f"Method '{method_name}' found at lines {target_method['line_start']}-{target_method['line_end']}",
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
def replace_line_range(filename: str, start_line: int, end_line: int, new_content: str) -> Dict[str, Any]:
    """
    Replace a range of lines in a Python file.
    
    Args:
        filename (str): Name of the Python file
        start_line (int): Starting line number (1-based)
        end_line (int): Ending line number (1-based, inclusive)
        new_content (str): New content to replace the lines
    
    Returns:
        dict: CommandResult with replacement status
    """
    try:
        filepath = _get_python_path(filename)
        if not filepath.exists():
            return CommandResult(
                status="error",
                stderr=f"File '{filename}' not found in workspace",
                exit_code=1
            )
        
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if start_line < 1 or end_line > len(lines) or start_line > end_line:
            return CommandResult(
                status="error",
                stderr=f"Invalid line range: {start_line}-{end_line} (file has {len(lines)} lines)",
                exit_code=1
            )
        
        # Replace the lines
        new_lines = lines[:start_line-1] + [new_content + '\n'] + lines[end_line:]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        return CommandResult(
            status="success",
            stdout=f"Replaced lines {start_line}-{end_line} in {filename}",
            stderr=f"New content: {new_content[:100]}{'...' if len(new_content) > 100 else ''}",
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
def replace_method_implementation(filename: str, method_name: str, new_implementation: str, class_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Replace the implementation of a specific method or function.
    
    Args:
        filename (str): Name of the Python file
        method_name (str): Name of the method/function to replace
        new_implementation (str): New implementation code
        class_name (Optional[str]): Name of the class (if it's a method)
    
    Returns:
        dict: CommandResult with replacement status
    """
    try:
        filepath = _get_python_path(filename)
        if not filepath.exists():
            return CommandResult(
                status="error",
                stderr=f"File '{filename}' not found in workspace",
                exit_code=1
            )
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = _parse_python_file(filepath)
        code_elements = _find_methods_and_classes(tree)
        
        # Find the method
        target_method = None
        for method in code_elements["methods"] + code_elements["functions"]:
            if method["name"] == method_name:
                if class_name is None or method.get("class") == class_name:
                    target_method = method
                    break
        
        if not target_method:
            return CommandResult(
                status="error",
                stderr=f"Method '{method_name}' not found" + (f" in class '{class_name}'" if class_name else ""),
                exit_code=1
            )
        
        # Replace the method
        lines = content.split('\n')
        new_lines = (lines[:target_method["line_start"]-1] + 
                    new_implementation.split('\n') + 
                    lines[target_method["line_end"]:])
        
        new_content = '\n'.join(new_lines)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return CommandResult(
            status="success",
            stdout=f"Replaced method '{method_name}' in {filename}",
            stderr=f"Method was at lines {target_method['line_start']}-{target_method['line_end']}",
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
def add_method_to_class(filename: str, class_name: str, method_implementation: str, position: str = "end") -> Dict[str, Any]:
    """
    Add a new method to an existing class.
    
    Args:
        filename (str): Name of the Python file
        class_name (str): Name of the class to add method to
        method_implementation (str): Complete method implementation
        position (str): Where to add - "start", "end", or "after_init"
    
    Returns:
        dict: CommandResult with addition status
    """
    try:
        filepath = _get_python_path(filename)
        if not filepath.exists():
            return CommandResult(
                status="error",
                stderr=f"File '{filename}' not found in workspace",
                exit_code=1
            )
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = _parse_python_file(filepath)
        code_elements = _find_methods_and_classes(tree)
        
        # Find the class
        target_class = None
        for cls in code_elements["classes"]:
            if cls["name"] == class_name:
                target_class = cls
                break
        
        if not target_class:
            return CommandResult(
                status="error",
                stderr=f"Class '{class_name}' not found in {filename}",
                exit_code=1
            )
        
        lines = content.split('\n')
        
        # Determine insertion point
        if position == "start":
            # After class definition line
            insert_line = target_class["line_start"]
        elif position == "after_init":
            # Find __init__ method and insert after it
            init_end = target_class["line_start"]
            for method in code_elements["methods"]:
                if method.get("class") == class_name and method["name"] == "__init__":
                    init_end = method["line_end"]
                    break
            insert_line = init_end
        else:  # "end"
            # Before class end
            insert_line = target_class["line_end"] - 1
        
        # Insert the method
        method_lines = method_implementation.split('\n')
        new_lines = lines[:insert_line] + method_lines + lines[insert_line:]
        
        new_content = '\n'.join(new_lines)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return CommandResult(
            status="success",
            stdout=f"Added method to class '{class_name}' in {filename}",
            stderr=f"Method added at position '{position}' around line {insert_line}",
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
def create_python_file(filename: str, content: str) -> Dict[str, Any]:
    """
    Create a new Python file with the given content.
    
    Args:
        filename (str): Name of the Python file to create
        content (str): Complete file content
    
    Returns:
        dict: CommandResult with creation status
    """
    try:
        filepath = _get_python_path(filename)
        
        # Check if file already exists
        if filepath.exists():
            return CommandResult(
                status="error",
                stderr=f"File '{filename}' already exists. Use replace_file to overwrite.",
                exit_code=1
            )
        
        # Create parent directories if needed
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Validate the Python syntax
        try:
            ast.parse(content)
            syntax_valid = True
        except SyntaxError as e:
            syntax_valid = False
            syntax_error = str(e)
        
        return CommandResult(
            status="success",
            stdout=f"Created Python file '{filename}' ({len(content)} characters)",
            stderr=f"Syntax valid: {syntax_valid}" + (f" - Error: {syntax_error}" if not syntax_valid else ""),
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
def list_python_files() -> Dict[str, Any]:
    """
    List all Python files in the workspace.
    
    Returns:
        dict: CommandResult with list of Python files
    """
    try:
        python_files = []
        
        for dirpath, dirnames, filenames in os.walk(WORKSPACE_DIR):
            for filename in filenames:
                if filename.endswith('.py'):
                    try:
                        # Create full path and get relative path
                        full_path = Path(dirpath) / filename
                        relative_path = full_path.relative_to(WORKSPACE_DIR)
                        python_files.append({
                            "name": str(relative_path)
                        })
                    except Exception as e:
                        python_files.append({
                            "name": filename,
                            "error": f"Could not process path: {str(e)}"
                        })
        
        return CommandResult(
            status="success",
            stdout=f"Python files in workspace: {python_files}",
            stderr=f"Found {len(python_files)} Python files",
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
def validate_python_syntax(filename: str) -> Dict[str, Any]:
    """
    Validate the syntax of a Python file.
    
    Args:
        filename (str): Name of the Python file to validate
    
    Returns:
        dict: CommandResult with syntax validation results
    """
    try:
        filepath = _get_python_path(filename)
        if not filepath.exists():
            return CommandResult(
                status="error",
                stderr=f"File '{filename}' not found in workspace",
                exit_code=1
            )
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
            return CommandResult(
                status="success",
                stdout=f"Python file '{filename}' has valid syntax",
                stderr="No syntax errors found",
                exit_code=0
            )
        except SyntaxError as e:
            return CommandResult(
                status="error",
                stdout=f"Syntax error in '{filename}'",
                stderr=f"Line {e.lineno}: {e.msg}",
                exit_code=1
            )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=str(e),
            exit_code=1
        )


if __name__ == "__main__":
    print("Starting Python File Editor MCP server with streamable-http transport...")
    
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
