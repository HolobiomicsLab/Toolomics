#!/usr/bin/env python3

"""
Skills MCP Server
Provides tools for accessing Claude Scientific Skills documentation.
Author: HolobiomicsLab
"""

import os
import sys
from pathlib import Path
import json
from typing import Dict, List, Optional, Any
from fastmcp import FastMCP

# Add parent directory to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from shared import return_as_dict

# Skills directory path
SKILLS_DIR = Path(__file__).parent / "scientific-skills" / "scientific-skills"

# Initialize FastMCP
description = """
Skills MCP Server provides tools for accessing Scientific Skills documentation.
It allows browsing and retrieving skill documentation and references for scientific computing tasks.
"""

mcp = FastMCP(
    name="Skills MCP",
    instructions=description,
)

def get_all_skill_names() -> List[str]:
    """Get list of all available skill names."""
    if not SKILLS_DIR.exists():
        return []
    
    skills = []
    for item in SKILLS_DIR.iterdir():
        if item.is_dir() and (item / "SKILL.md").exists():
            skills.append(item.name)
    
    return sorted(skills)

def get_skill_path(skill_name: str) -> Optional[Path]:
    """Get the path to a skill directory."""
    skill_path = SKILLS_DIR / skill_name
    if skill_path.exists() and skill_path.is_dir():
        return skill_path
    return None

def get_skill_references(skill_name: str) -> List[str]:
    """Get list of reference files for a skill."""
    skill_path = get_skill_path(skill_name)
    if not skill_path:
        return []
    
    references_dir = skill_path / "references"
    if not references_dir.exists() or not references_dir.is_dir():
        return []
    
    references = []
    for item in references_dir.iterdir():
        if item.is_file() and item.suffix == ".md":
            references.append(item.stem)
    
    return sorted(references)

@mcp.tool
def list_all_skills() -> Dict[str, Any]:
    """
    List all available Claude Scientific Skills.
    
    This tool returns a comprehensive list of all scientific skills available in the system.
    Each skill represents a scientific library, tool, database, or technique with detailed 
    documentation and usage examples.
    
    Returns:
        Dict[str, Any]: Dictionary containing:
            - status: "success" or "error"
            - count: Total number of skills available
            - skills: List of skill names (folder names)
            - message: Additional information or error details
    
    Examples:
        >>> list_all_skills()
        {
            "status": "success",
            "count": 120,
            "skills": [
                "anndata",
                "biopython",
                "matplotlib",
                "pandas",
                "scanpy",
                ...
            ]
        }
    
    Notes:
        - Use show_skill() to view detailed documentation for a specific skill
        - Skill names correspond to Python packages or scientific tools
    """
    try:
        skills = get_all_skill_names()
        
        if not skills:
            return {
                "status": "error",
                "count": 0,
                "skills": [],
                "message": f"No skills found in {SKILLS_DIR}"
            }
        
        return {
            "status": "success",
            "count": len(skills),
            "skills": skills,
            "message": f"Found {len(skills)} skills. Use show_skill(skill_name) to view details."
        }
    except Exception as e:
        return {
            "status": "error",
            "count": 0,
            "skills": [],
            "message": f"Failed to list skills: {str(e)}"
        }

@mcp.tool
def show_skill(skill_name: str) -> Dict[str, Any]:
    """
    Show the main documentation for a specific skill.
    
    This tool retrieves and displays the comprehensive documentation for a scientific skill,
    including overview, installation instructions, quick start guide, core capabilities,
    common workflows, troubleshooting, and additional resources.
    
    Args:
        skill_name (str): The name of the skill to retrieve. Use list_all_skills() to see
                         available options. Examples: "anndata", "biopython", "scanpy"
    
    Returns:
        Dict[str, Any]: Dictionary containing:
            - status: "success" or "error"
            - skill_name: The requested skill name
            - content: Full markdown content of the SKILL.md file
            - has_references: Boolean indicating if skill has additional reference docs
            - references: List of available reference topics (if any)
            - message: Additional information or error details
    
    Examples:
        >>> show_skill("anndata")
        {
            "status": "success",
            "skill_name": "anndata",
            "content": "# AnnData\\n\\n## Overview\\n...",
            "has_references": True,
            "references": ["io_operations", "data_structure", "concatenation", ...],
            "message": "Skill documentation retrieved successfully"
        }
    
    Notes:
        - The content includes complete markdown documentation
        - If has_references is True, use list_skill_references() for more details
        - Use show_skill_reference() to view specific reference documentation
    """
    try:
        skill_path = get_skill_path(skill_name)
        
        if not skill_path:
            available_skills = get_all_skill_names()
            return {
                "status": "error",
                "skill_name": skill_name,
                "content": "",
                "has_references": False,
                "references": [],
                "message": f"Skill '{skill_name}' not found. Available skills: {', '.join(available_skills[:10])}..."
            }
        
        skill_file = skill_path / "SKILL.md"
        if not skill_file.exists():
            return {
                "status": "error",
                "skill_name": skill_name,
                "content": "",
                "has_references": False,
                "references": [],
                "message": f"SKILL.md not found for '{skill_name}'"
            }
        
        # Read skill content
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for references
        references = get_skill_references(skill_name)
        has_references = len(references) > 0
        
        return {
            "status": "success",
            "skill_name": skill_name,
            "content": content,
            "has_references": has_references,
            "references": references,
            "message": f"Skill documentation retrieved successfully. {'Additional references available.' if has_references else 'No additional references.'}"
        }
    except Exception as e:
        return {
            "status": "error",
            "skill_name": skill_name,
            "content": "",
            "has_references": False,
            "references": [],
            "message": f"Failed to retrieve skill: {str(e)}"
        }

@mcp.tool
def list_skill_references(skill_name: str) -> Dict[str, Any]:
    """
    List all reference documentation available for a specific skill.
    
    Many skills have additional detailed reference documentation covering specific topics,
    advanced features, or specialized use cases. This tool lists all available reference
    documents for a given skill.
    
    Args:
        skill_name (str): The name of the skill. Use list_all_skills() to see available options.
    
    Returns:
        Dict[str, Any]: Dictionary containing:
            - status: "success" or "error"
            - skill_name: The requested skill name
            - count: Number of reference documents available
            - references: List of reference document names (without .md extension)
            - message: Additional information or error details
    
    Examples:
        >>> list_skill_references("anndata")
        {
            "status": "success",
            "skill_name": "anndata",
            "count": 5,
            "references": [
                "best_practices",
                "concatenation",
                "data_structure",
                "io_operations",
                "manipulation"
            ],
            "message": "Found 5 reference documents"
        }
        
        >>> list_skill_references("simple-skill")
        {
            "status": "success",
            "skill_name": "simple-skill",
            "count": 0,
            "references": [],
            "message": "No reference documents found for this skill"
        }
    
    Notes:
        - Use show_skill_reference() to view the content of a specific reference
        - Not all skills have reference documents; some only have the main SKILL.md
    """
    try:
        skill_path = get_skill_path(skill_name)
        
        if not skill_path:
            return {
                "status": "error",
                "skill_name": skill_name,
                "count": 0,
                "references": [],
                "message": f"Skill '{skill_name}' not found"
            }
        
        references = get_skill_references(skill_name)
        
        if not references:
            return {
                "status": "success",
                "skill_name": skill_name,
                "count": 0,
                "references": [],
                "message": "No reference documents found for this skill"
            }
        
        return {
            "status": "success",
            "skill_name": skill_name,
            "count": len(references),
            "references": references,
            "message": f"Found {len(references)} reference documents"
        }
    except Exception as e:
        return {
            "status": "error",
            "skill_name": skill_name,
            "count": 0,
            "references": [],
            "message": f"Failed to list references: {str(e)}"
        }

@mcp.tool
def show_skill_reference(skill_name: str, reference_name: str) -> Dict[str, Any]:
    """
    Show detailed reference documentation for a specific topic within a skill.
    
    This tool retrieves in-depth documentation for specific aspects of a skill, such as
    I/O operations, best practices, advanced features, or specialized use cases.
    
    Args:
        skill_name (str): The name of the skill. Use list_all_skills() to see available skills.
        reference_name (str): The name of the reference document (without .md extension).
                             Use list_skill_references() to see available references for a skill.
    
    Returns:
        Dict[str, Any]: Dictionary containing:
            - status: "success" or "error"
            - skill_name: The skill name
            - reference_name: The reference document name
            - content: Full markdown content of the reference document
            - message: Additional information or error details
    
    Examples:
        >>> show_skill_reference("anndata", "io_operations")
        {
            "status": "success",
            "skill_name": "anndata",
            "reference_name": "io_operations",
            "content": "# Input/Output Operations\\n\\nAnnData provides...",
            "message": "Reference documentation retrieved successfully"
        }
        
        >>> show_skill_reference("biopython", "sequence_io")
        {
            "status": "success",
            "skill_name": "biopython",
            "reference_name": "sequence_io",
            "content": "# Sequence I/O\\n\\nBiopython provides...",
            "message": "Reference documentation retrieved successfully"
        }
    
    Notes:
        - Reference documents provide detailed, topic-specific documentation
        - They complement the main SKILL.md with in-depth coverage of specific areas
    """
    try:
        skill_path = get_skill_path(skill_name)
        
        if not skill_path:
            return {
                "status": "error",
                "skill_name": skill_name,
                "reference_name": reference_name,
                "content": "",
                "message": f"Skill '{skill_name}' not found"
            }
        
        reference_file = skill_path / "references" / f"{reference_name}.md"
        
        if not reference_file.exists():
            available_refs = get_skill_references(skill_name)
            if available_refs:
                return {
                    "status": "error",
                    "skill_name": skill_name,
                    "reference_name": reference_name,
                    "content": "",
                    "message": f"Reference '{reference_name}' not found. Available references: {', '.join(available_refs)}"
                }
            else:
                return {
                    "status": "error",
                    "skill_name": skill_name,
                    "reference_name": reference_name,
                    "content": "",
                    "message": f"No references folder found for skill '{skill_name}'"
                }
        
        # Read reference content
        with open(reference_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "status": "success",
            "skill_name": skill_name,
            "reference_name": reference_name,
            "content": content,
            "message": "Reference documentation retrieved successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "skill_name": skill_name,
            "reference_name": reference_name,
            "content": "",
            "message": f"Failed to retrieve reference: {str(e)}"
        }

print("Starting Skills MCP server with streamable-http transport...")

if __name__ == "__main__":
    # Get port from environment variable or command line argument as fallback
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

    # Verify skills directory exists
    if not SKILLS_DIR.exists():
        print(f"WARNING: Skills directory not found at {SKILLS_DIR}")
        print("Skills functionality may be limited.")
    else:
        skill_count = len(get_all_skill_names())
        print(f"Found {skill_count} skills in {SKILLS_DIR}")

    print(f"Starting server on port {port}")
    mcp.run(transport="streamable-http", port=port, host="0.0.0.0")
