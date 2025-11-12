#!/usr/bin/env python3

"""
Image Analysis MCP Server using GPT-4O

Provides tools for analyzing images using OpenAI's GPT-4O vision model.

Author: Toolomics - Image Analysis Tool
"""

import sys
import os
import json
import base64
from pathlib import Path
from typing import Dict, Any, Optional

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from shared import CommandResult, return_as_dict, get_workspace_path

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed")
    print("Install with: pip install openai")
    sys.exit(1)

from fastmcp import FastMCP

description = """
Image Analysis MCP Server provides tools for analyzing images using OpenAI's GPT-4O vision model.
It can describe images and answer questions about them. Images must be accessible in the workspace directory.
"""

mcp = FastMCP(
    name="Image Analysis MCP",
    instructions=description,
)

WORKSPACE = get_workspace_path()

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY environment variable not set")
    print("The server will start but tools will fail without a valid API key")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def encode_image_to_base64(image_path: Path) -> str:
    """Encode image file to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def get_image_mime_type(image_path: Path) -> str:
    """Determine MIME type from file extension"""
    extension = image_path.suffix.lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    return mime_types.get(extension, 'image/jpeg')


def analyze_image_with_gpt4o(image_path: Path, prompt: str, detail: str = "auto") -> Dict[str, Any]:
    """
    Analyze an image using GPT-4O vision model
    
    Args:
        image_path: Path to the image file
        prompt: The prompt/question to ask about the image
        detail: Level of detail ("low", "high", or "auto")
    
    Returns:
        Dict with analysis results
    """
    if not client:
        raise ValueError("OpenAI API key not configured")
    
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    # Encode image to base64
    base64_image = encode_image_to_base64(image_path)
    mime_type = get_image_mime_type(image_path)
    
    # Create the message with image
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}",
                            "detail": detail
                        }
                    }
                ]
            }
        ],
        max_tokens=1000
    )
    
    return {
        "description": response.choices[0].message.content,
        "model": response.model,
        "usage": {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }
    }


@mcp.tool
@return_as_dict
def describe_image(
    filename: str,
    detail: str = "auto"
) -> Dict[str, Any]:
    """
    Automatically describe an image in detail using GPT-4O vision model.
    
    Args:
        filename: Name of the image file in the workspace directory (e.g., "photo.jpg")
        detail: Level of detail for analysis - "low" for faster/cheaper, "high" for more detailed, "auto" for automatic selection (default: "auto")
    
    Returns:
        Dict containing:
            - status: "success" or "error"
            - description: Detailed description of the image
            - filename: Name of the analyzed file
            - model: Model used for analysis
            - usage: Token usage statistics
    """
    try:
        image_path = WORKSPACE / filename
        
        # Default prompt for general description
        prompt = """Please provide a detailed description of this image. Include:
- Main subject(s) or objects
- Setting and environment
- Colors, lighting, and mood
- Any text or notable details
- Overall composition and style"""
        
        result = analyze_image_with_gpt4o(image_path, prompt, detail)
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "description": result["description"],
                "filename": filename,
                "model": result["model"],
                "usage": result["usage"]
            })
        )
    
    except FileNotFoundError as e:
        return CommandResult(
            status="error",
            stderr=f"Image file not found: {str(e)}",
            exit_code=1
        )
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to analyze image: {str(e)}",
            exit_code=1
        )


@mcp.tool
@return_as_dict
def ask_about_image(
    filename: str,
    question: str,
    detail: str = "auto"
) -> Dict[str, Any]:
    """
    Ask a specific question about an image using GPT-4O vision model.
    
    Args:
        filename: Name of the image file in the workspace directory (e.g., "photo.jpg")
        question: The specific question to ask about the image
        detail: Level of detail for analysis - "low" for faster/cheaper, "high" for more detailed, "auto" for automatic selection (default: "auto")
    
    Returns:
        Dict containing:
            - status: "success" or "error"
            - answer: Answer to the question
            - question: The question that was asked
            - filename: Name of the analyzed file
            - model: Model used for analysis
            - usage: Token usage statistics
    """
    try:
        image_path = WORKSPACE / filename
        
        result = analyze_image_with_gpt4o(image_path, question, detail)
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "answer": result["description"],
                "question": question,
                "filename": filename,
                "model": result["model"],
                "usage": result["usage"]
            })
        )
    
    except FileNotFoundError as e:
        return CommandResult(
            status="error",
            stderr=f"Image file not found: {str(e)}",
            exit_code=1
        )
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to analyze image: {str(e)}",
            exit_code=1
        )


@mcp.tool
@return_as_dict
def list_images() -> Dict[str, Any]:
    """
    List all image files in the workspace directory.
    
    Returns:
        Dict containing:
            - status: "success" or "error"
            - images: List of image filenames
            - count: Number of images found
    """
    try:
        # Common image extensions
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'}
        
        images = [
            f.name for f in WORKSPACE.iterdir()
            if f.is_file() and f.suffix.lower() in image_extensions
        ]
        
        return CommandResult(
            status="success",
            stdout=json.dumps({
                "images": sorted(images),
                "count": len(images),
                "workspace": str(WORKSPACE)
            })
        )
    
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Failed to list images: {str(e)}",
            exit_code=1
        )


print("Starting Image Analysis MCP server with streamable-http transport...")

if __name__ == "__main__":
    # Get port from environment variable or command line argument
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
    
    if not OPENAI_API_KEY:
        print("\nWARNING: OPENAI_API_KEY not set. Tools will fail without API key.")
        print("Set the environment variable before deployment.\n")
        exit(0)
    
    print(f"Starting server on port {port}")
    print(f"Workspace directory: {WORKSPACE}")
    mcp.run(transport="streamable-http", port=port, host="0.0.0.0")
