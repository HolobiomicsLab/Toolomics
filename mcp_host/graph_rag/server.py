import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
from fastmcp import FastMCP
import pymupdf
import os
import sys
import shutil

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from shared import get_workspace_path


def convert_pdf_txt(fname: str):
    # fname = "s11306-019-1612-4.pdf"
    with pymupdf.open(fname) as doc:  # open document
        text = chr(12).join([page.get_text() for page in doc])
    # write as a binary file to support non-ASCII characters
    output_path = get_workspace_path() / "rag" / "input" / f"{fname.removesuffix('.pdf')}.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(text.encode())


def move_files_to_rag(file: str):
    output_dir = get_workspace_path() / "rag" / "input"
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(file, output_dir / file)
    print(f"Moved {file} to {output_dir}")


description = """
GraphRAG is a retrieval-augmented generation (RAG) system that uses a knowledge graph to enhance the capabilities of large language models (LLMs). 
It combines document retrieval, knowledge graph querying, and LLMs to provide accurate and contextually relevant responses to user queries.
"""

mcp = FastMCP(
    name="GraphRAG MCP",
    instructions=description,
)

executor = ThreadPoolExecutor(max_workers=2)

@mcp.tool
async def files_to_graph(filenames: list[str]):
    """Process files and add them to the GraphRAG knowledge graph
    
    Args:
        filenames: List of filenames to process and add to the graph
        
    Returns:
        String confirmation message that files were processed for GraphRAG
    """
    # Process files first
    for filename in filenames:
        if filename.lower().endswith(".txt"):
            move_files_to_rag(filename)
        elif filename.lower().endswith(".pdf"):
            convert_pdf_txt(filename)
        else:
            raise ValueError(f"Unsupported file type: {filename}")
    
    # Define function to run in thread pool
    def run_indexing():
        try:
            result = subprocess.run(
                ["graphrag", "index", "--root", "./rag"],
                encoding="utf-8",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=300,
            )
            return result
        except Exception as e:
            return None, str(e), -1
    
    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, run_indexing)
    
    # Handle potential errors
    if isinstance(result, tuple):  # Error case
        return f"Error during indexing: {result[1]}"
    
    if result.returncode != 0:
        return f"Error during indexing: {result.stderr}"
    
    return "Files processed and indexed for GraphRAG successfully."



@mcp.tool
async def query(query: str) -> str:
    """Query the GraphRAG knowledge graph with a natural language query"""
    
    def run_query():
        try:
            result = subprocess.run(
                [
                    "graphrag",
                    "query",
                    "--root",
                    "./rag",
                    "--method",
                    "local",
                    "--query",
                    query,
                ],
                encoding="utf-8",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=300,
            )
            return result
        except Exception as e:
            return None, str(e), -1
    
    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, run_query)
    
    if isinstance(result, tuple):  # Error case
        return f"Error: {result[1]}"
    
    if result.returncode != 0:
        return f"Error: {result.stderr}"
    
    return result.stdout


print(f"Starting {mcp.name} server with streamable-http transport...")

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
    mcp.run(transport="http", port=port, host="0.0.0.0")
