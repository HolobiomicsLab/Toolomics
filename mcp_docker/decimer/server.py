#!/usr/bin/env python3

"""
DECIMER Tools MCP Server

Provides tools for chemical structure analysis using DECIMER models.
This server runs in Docker to isolate ML dependencies from the main toolomics package.

Author: Generated for HolobiomicsLab, CNRS
"""

import os
import sys
import json
from pathlib import Path
from fastmcp import FastMCP
import tempfile
import shutil

# Add project root to path for shared utilities
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from shared import CommandResult, return_as_dict, get_workspace_path

shared_path = get_workspace_path()

description = """
DECIMER Tools MCP Server provides chemical structure analysis capabilities.
It includes:
- Image classification (chemical structure detection)
- Structure segmentation from documents
- SMILES generation from chemical structure images

This server runs in Docker with isolated ML dependencies to avoid conflicts.
"""

mcp = FastMCP(
    name="DECIMER Chemical Analysis MCP",
    instructions=description,
)

# Configuration for external model storage
DECIMER_MODEL_ROOT = os.environ.get("DECIMER_MODEL_ROOT", "/app/models")
CLASSIFIER_MODEL_PATH = os.path.join(DECIMER_MODEL_ROOT, "classifier")
TRANSFORMER_MODEL_PATH = os.path.join(DECIMER_MODEL_ROOT, "transformer")

# Global variables for lazy loading
_classifier = None
_transformer = None
_segmentation = None

def get_classifier():
    """Lazy load the DECIMER Image Classifier."""
    global _classifier
    if _classifier is None:
        try:
            # Import the official DECIMER Image Classifier package
            from decimer_image_classifier import DecimerImageClassifier
            _classifier = DecimerImageClassifier()
            print("✅ DECIMER Image Classifier loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load DECIMER Image Classifier: {e}")
            raise
    return _classifier

def get_transformer():
    """Lazy load the DECIMER Image Transformer."""
    global _transformer
    if _transformer is None:
        try:
            # Import the official DECIMER package
            import DECIMER
            _transformer = DECIMER
            print("✅ DECIMER Image Transformer loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load DECIMER Image Transformer: {e}")
            raise
    return _transformer

def get_segmentation():
    """Lazy load the DECIMER Segmentation."""
    global _segmentation
    if _segmentation is None:
        try:
            # Import the official DECIMER Segmentation package
            import decimer_segmentation
            _segmentation = decimer_segmentation
            print("✅ DECIMER Segmentation loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load DECIMER Segmentation: {e}")
            raise
    return _segmentation


@mcp.tool
@return_as_dict
def classify_chemical_structure(image_path: str) -> dict:
    """
    Classify whether an image contains a chemical structure.
    
    Args:
        image_path (str): Path to the image file to classify
        
    Returns:
        dict: {
            "status": "success" or "error",
            "is_chemical": bool,
            "confidence_score": float,
            "threshold": float,
            "message": str
        }
        
    Example:
        classify_chemical_structure(image_path="/workspace/molecule.png")
    """
    try:
        if not os.path.exists(image_path):
            return CommandResult(
                status="error",
                stderr=f"Image file not found: {image_path}",
                exit_code=1
            )
        
        classifier = get_classifier()
        score = classifier.get_classifier_score(image_path)
        is_chemical = classifier.is_chemical_structure(image_path)
        
        result_data = {
            "is_chemical": is_chemical,
            "confidence_score": float(score),
            "threshold": 0.000089,  # Default threshold used by is_chemical_structure
            "message": f"Image {'contains' if is_chemical else 'does not contain'} a chemical structure"
        }
        
        return CommandResult(
            status="success",
            stdout=json.dumps(result_data, indent=2),
            exit_code=0
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Error classifying image: {str(e)}",
            exit_code=1
        )


@mcp.tool
@return_as_dict
def predict_smiles(image_path: str) -> dict:
    """
    Generate SMILES string from a chemical structure image.
    
    Args:
        image_path (str): Path to the chemical structure image
        
    Returns:
        dict: {
            "status": "success" or "error",
            "smiles": str,
            "message": str
        }
        
    Example:
        predict_smiles(image_path="/workspace/caffeine.png")
    """
    try:
        if not os.path.exists(image_path):
            return CommandResult(
                status="error",
                stderr=f"Image file not found: {image_path}",
                exit_code=1
            )
        
        transformer = get_transformer()
        smiles = transformer.predict_SMILES(image_path)
        
        result_data = {
            "smiles": smiles,
            "message": f"Generated SMILES: {smiles}"
        }
        
        return CommandResult(
            status="success",
            stdout=json.dumps(result_data, indent=2),
            exit_code=0
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Error predicting SMILES: {str(e)}",
            exit_code=1
        )


@mcp.tool
@return_as_dict
def segment_chemical_structures(file_path: str, output_dir: str = None) -> dict:
    """
    Segment chemical structures from a document image.
    
    Args:
        file_path (str): Path to the document image containing chemical structures
        output_dir (str, optional): Directory to save segmented structures. Defaults to same directory as input.
        
    Returns:
        dict: {
            "status": "success" or "error",
            "segmented_structures": list of str (paths to segmented images),
            "count": int,
            "message": str
        }
        
    Example:
        segment_chemical_structures(file_path="/workspace/document.pdf")
    """
    try:
        if not os.path.exists(file_path):
            return CommandResult(
                status="error",
                stderr=f"Image file not found: {file_path}",
                exit_code=1
            )
        
        if output_dir is None:
            output_dir = os.path.dirname(file_path)
        
        os.makedirs(output_dir, exist_ok=True)
        
        segmentation = get_segmentation()
        
        # Use DECIMER segmentation to extract structures (returns numpy arrays)
        segments = segmentation.segment_chemical_structures_from_file(file_path)
        
        # save segments as PNG files
        from PIL import Image
        import numpy as np
        import time
        from datetime import datetime
        
        saved_files = []
        # Create unique timestamp suffix to avoid filename conflicts
        timestamp = int(time.time())
        base_name = Path(file_path).stem  # Extract filename without extension
        
        for i, segment in enumerate(segments):
            output_path = os.path.join(output_dir, f"{base_name}_segment_{i+1}_{timestamp}.png")
            if isinstance(segment, np.ndarray):
                img = Image.fromarray(segment.astype('uint8'))
                img.save(output_path)
                saved_files.append(output_path)
        
        result_data = {
            "segments": saved_files,
            "total_segments": len(saved_files),
            "output_dir": output_dir,
            "message": f"Segmented {len(saved_files)} chemical structures"
        }
        
        return CommandResult(
            status="success",
            stdout=json.dumps(result_data, indent=2),
            exit_code=0
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Error segmenting structures: {str(e)}",
            exit_code=1
        )


@mcp.tool
@return_as_dict
def analyze_chemical_document(image_path: str, output_dir: str = None) -> dict:
    """
    Complete analysis of a document: segment structures, classify them, and generate SMILES.
    
    Args:
        image_path (str): Path to the document image
        output_dir (str, optional): Directory for outputs. Defaults to same directory as input.
        
    Returns:
        dict: {
            "status": "success" or "error",
            "results": list of dict with structure analysis,
            "summary": dict with counts and statistics
        }
        
    Example:
        analyze_chemical_document(image_path="/workspace/chemistry_paper.png")
    """
    try:
        if not os.path.exists(image_path):
            return CommandResult(
                status="error",
                stderr=f"Image file not found: {image_path}",
                exit_code=1
            )
        
        if output_dir is None:
            output_dir = os.path.dirname(image_path)
        
        # Step 1: Segment structures using the internal implementation
        segmentation = get_segmentation()
        segments = segmentation.segment_chemical_structures_from_file(image_path)
        
        # Save segments as PNG files
        from PIL import Image
        import numpy as np
        import time
        
        os.makedirs(output_dir, exist_ok=True)
        saved_files = []
        # Create unique timestamp suffix to avoid filename conflicts
        timestamp = int(time.time())
        base_name = Path(image_path).stem  # Extract filename without extension
        
        for i, segment in enumerate(segments):
            output_path = os.path.join(output_dir, f"{base_name}_segment_{i+1}_{timestamp}.png")
            if isinstance(segment, np.ndarray):
                img = Image.fromarray(segment.astype('uint8'))
                img.save(output_path)
                saved_files.append(output_path)
        
        # Step 2: Analyze each segmented structure
        results = []
        chemical_count = 0
        
        classifier = get_classifier()
        transformer = get_transformer()
        
        for seg_file in saved_files:
            # Classify
            try:
                score = classifier.get_classifier_score(seg_file)
                is_chemical = classifier.is_chemical_structure(seg_file)
                classify_data = {
                    "is_chemical": is_chemical,
                    "confidence_score": float(score)
                }
            except Exception as e:
                classify_data = {"is_chemical": False, "error": str(e)}
            
            # Generate SMILES if it's a chemical structure
            smiles_data = {}
            if classify_data.get("is_chemical", False):
                chemical_count += 1
                try:
                    smiles = transformer.predict_SMILES(seg_file)
                    smiles_data = {"smiles": smiles}
                except Exception as e:
                    smiles_data = {"error": str(e)}
            
            results.append({
                "image_path": seg_file,
                "classification": classify_data,
                "smiles_prediction": smiles_data
            })
        
        summary = {
            "total_segments": len(saved_files),
            "chemical_structures": chemical_count,
            "non_chemical": len(saved_files) - chemical_count
        }
        
        final_result = {
            "results": results,
            "summary": summary,
            "message": f"Analyzed {len(saved_files)} segments, found {chemical_count} chemical structures"
        }
        
        return CommandResult(
            status="success",
            stdout=json.dumps(final_result, indent=2),
            exit_code=0
        )
        
    except Exception as e:
        return CommandResult(
            status="error",
            stderr=f"Error analyzing document: {str(e)}",
            exit_code=1
        )


print("Starting DECIMER MCP server with streamable-http transport...")
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

    print(f"Starting DECIMER server on port {port}")
    mcp.run(transport="streamable-http", port=port, host="0.0.0.0")
