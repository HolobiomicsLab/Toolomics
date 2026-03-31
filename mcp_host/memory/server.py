#!/usr/bin/env python3

"""
Memory MCP Server
Provides tools for storing and retrieving memories using RAG (Retrieval-Augmented Generation).
Author: HolobiomicsLab
"""

import os
import sys
from pathlib import Path
import json
import re
from typing import Dict, List, Optional, Any
from fastmcp import FastMCP

# Add parent directory to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from shared import return_as_dict

# Memory database - stored as an in-memory list initially, could be extended to use
MEMORY_DB_PATH = Path("memory_db.json")
memories = []

def load_memories():
    """Load memories from file if it exists"""
    global memories
    try:
        if MEMORY_DB_PATH.exists():
            with open(MEMORY_DB_PATH, "r") as f:
                memories = json.load(f)
            print(f"Loaded {len(memories)} memories from {MEMORY_DB_PATH}")
        else:
            print(f"Memory database file {MEMORY_DB_PATH} does not exist. Starting with empty memory.")
            memories = []
    except Exception as e:
        print(f"Error loading memories: {e}")
        memories = []

def save_memories():
    """Save memories to file"""
    try:
        with open(MEMORY_DB_PATH, "w") as f:
            json.dump(memories, f, indent=2)
        print(f"Saved {len(memories)} memories to {MEMORY_DB_PATH}")
    except Exception as e:
        print(f"Error saving memories: {e}")

# Simple text-based similarity for now (could be replaced with embeddings)
def similarity_score(query: str, memory: str) -> float:
    """
    Calculate simple similarity score between query and memory.
    
    Args:
        query: The search query string
        memory: The memory string to compare against
        
    Returns:
        float: Similarity score between 0 and 1
    """
    # Normalize text (lowercase, remove punctuation)
    query = re.sub(r'[^\w\s]', '', query.lower())
    memory = re.sub(r'[^\w\s]', '', memory.lower())
    
    # Split into words
    query_words = set(query.split())
    memory_words = set(memory.split())
    
    # Calculate Jaccard similarity
    if not query_words or not memory_words:
        return 0.0
    
    intersection = len(query_words.intersection(memory_words))
    union = len(query_words.union(memory_words))
    
    return intersection / union

# Initialize FastMCP
description = """
Memory MCP Server provides tools for storing and retrieving memories using RAG.
It allows an agent to save learned information and later retrieve the most relevant memories for a given query.
"""

mcp = FastMCP(
    name="Memory MCP",
    instructions=description,
)

@mcp.tool
def lookup_memory(query: str) -> List[str]:
    """
    Look up memories that are most relevant to the provided query.
    This tool searches through all stored memories and returns the top 5 most relevant results based on 
    their similarity to your query string. It's particularly useful for retrieving previously encountered
    errors solutions.
    
    Args:
        query (str): The search query string. Be as specific as possible for better results.
                    For example: "failure of download_file tool with non pdf download link"
    
    Returns:
        List[str]: List of the top 5 most relevant memory strings, ranked by relevance.
                  An empty list is returned if no memories match the query or if the memory database is empty.
    
    Examples:
        >>> lookup_memory("how to fix permission denied errors")
        [
            "When facing 'permission denied' errors with file operations, try using chmod +x to make the file executable or sudo for admin privileges.",
            "Permission denied errors often happen when trying to access protected directories. Use sudo or run as administrator.",
        ]
    """
    if not memories:
        return []
    # Calculate similarity scores
    scored_memories = [(memory, similarity_score(query, memory)) for memory in memories]
    # Sort by score (descending) and take top 5
    scored_memories.sort(key=lambda x: x[1], reverse=True)
    # Return only memories with non-zero scores, up to 5
    return [memory for memory, score in scored_memories[:5] if score > 0]

@mcp.tool 
def save_learned(memory: str) -> Dict[str, Any]:
    """
    Save a new piece of knowledge or insight to the memory database.
    This tool allows you to store important information, patterns, solutions, or knowledge
    that might be useful to retrieve later. Please use extensively every time you learn something / fix an error after many attempt.
    
    Args:
        memory (str): The memory text to store. Should be a complete, self-contained piece of information.
                     For example: "It appears that for download_file to work with non-PDF links, 
                     the URL must point directly to a downloadable file rather than a webpage that contains a download button."
    
    Returns:
        Dict[str, Any]: Dictionary containing:
            - status: "success" or "error"
            - message: Confirmation message or error details
            - total_memories: Total number of memories now stored
    
    Examples:
        
        >>> save_learned("When working with pandas DataFrames, use df.loc[] for label-based indexing and df.iloc[] for position-based indexing.")
        {
            "status": "success", 
            "message": "Memory successfully saved", 
            "total_memories": 43
        }
    Notes:
        - Each memory should be a complete, standalone piece of information
        - Providing clear, concise, and well-structured memories improves retrievability
    """
    if not memory or not memory.strip():
        return {
            "status": "error",
            "message": "Cannot save empty memory",
            "total_memories": len(memories)
        }
    
    try:
        # Add timestamp to the memory (could be used for recency scoring in the future)
        memories.append(memory.strip())
        # Save to disk for persistence
        save_memories()
        return {
            "status": "success",
            "message": "Memory successfully saved",
            "total_memories": len(memories)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to save memory: {str(e)}",
            "total_memories": len(memories)
        }

@mcp.tool
def list_all_memories() -> Dict[str, Any]:
    """
    List all stored memories with their index numbers.
    
    This tool is helpful for reviewing all stored memories, understanding what information
    is available, or identifying memories that might need to be removed.
    
    Returns:
        Dict[str, Any]: Dictionary containing:
            - status: "success" or "error"
            - count: Total number of memories
            - memories: List of all memories with index numbers
    
    Example:
        >>> list_all_memories()
        {
            "status": "success",
            "count": 3,
            "memories": [
                "1. Python dict.get(key, default) method returns the value for key if key is in the dictionary, else default.",
                "2. When working with pandas DataFrames, use df.loc[] for label-based indexing and df.iloc[] for position-based indexing.",
                "3. Git commit --amend can be used to modify the most recent commit message."
            ]
        }
        
    Notes:
        - Returns an empty list if no memories are stored
        - Memories are listed with their index number for reference
    """
    try:
        numbered_memories = [f"{i+1}. {memory}" for i, memory in enumerate(memories)]
        
        return {
            "status": "success",
            "count": len(memories),
            "memories": numbered_memories
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to list memories: {str(e)}",
            "count": 0,
            "memories": []
        }

# Load memories on startup
load_memories()

print("Starting Memory MCP server with streamable-http transport...")

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

    print(f"Starting server on port {port}")
    mcp.run(transport="streamable-http", port=port, host="0.0.0.0")