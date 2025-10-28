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
import logging
from pathlib import Path
from fastmcp import FastMCP
import tempfile
import shutil

# Add project root to path for shared utilities
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from shared import CommandResult, return_as_dict, get_workspace_path

shared_path = get_workspace_path()

# Configure logging for debug information
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/app/debug.log')
    ]
)
logger = logging.getLogger('decimer_mcp')

# Add connection monitoring
import threading
import time
from collections import defaultdict

# Connection tracking
connection_stats = {
    'active_connections': 0,
    'total_connections': 0,
    'failed_connections': 0,
    'connection_times': [],
    'last_activity': time.time()
}

def log_connection_event(event_type, details=""):
    """Log connection events for debugging."""
    connection_stats['last_activity'] = time.time()
    if event_type == 'connect':
        connection_stats['active_connections'] += 1
        connection_stats['total_connections'] += 1
    elif event_type == 'disconnect':
        connection_stats['active_connections'] = max(0, connection_stats['active_connections'] - 1)
    elif event_type == 'failed':
        connection_stats['failed_connections'] += 1
    
    logger.info(f"🔗 Connection {event_type.upper()}: {details} | Active: {connection_stats['active_connections']} | Total: {connection_stats['total_connections']} | Failed: {connection_stats['failed_connections']}")

def log_system_resources():
    """Log system resource usage."""
    try:
        import psutil
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        logger.info(f"💻 System Resources: CPU: {cpu_percent}% | Memory: {memory.percent}% ({memory.used/1024/1024/1024:.1f}GB/{memory.total/1024/1024/1024:.1f}GB)")
    except ImportError:
        logger.warning("psutil not available for resource monitoring")

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
            logger.info("🔄 Loading DECIMER Image Classifier...")
            # Import the official DECIMER Image Classifier package
            from decimer_image_classifier import DecimerImageClassifier
            _classifier = DecimerImageClassifier()
            logger.info("✅ DECIMER Image Classifier loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load DECIMER Image Classifier: {e}")
            raise
    return _classifier

def get_transformer():
    """Lazy load the DECIMER Image Transformer."""
    global _transformer
    if _transformer is None:
        try:
            logger.info("🔄 Loading DECIMER Image Transformer...")
            # Import the official DECIMER package
            import DECIMER
            _transformer = DECIMER
            logger.info("✅ DECIMER Image Transformer loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load DECIMER Image Transformer: {e}")
            raise
    return _transformer

def get_segmentation():
    """Lazy load the DECIMER Segmentation."""
    global _segmentation
    if _segmentation is None:
        try:
            logger.info("🔄 Loading DECIMER Segmentation...")
            # Import the official DECIMER Segmentation package
            import decimer_segmentation
            _segmentation = decimer_segmentation
            logger.info("✅ DECIMER Segmentation loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load DECIMER Segmentation: {e}")
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
    logger.info(f"🔍 Starting classify_chemical_structure for image: {image_path}")
    logger.debug(f"Input parameters - image_path: {image_path}")
    
    try:
        # Validate input file
        logger.debug(f"🔍 Checking if image file exists: {image_path}")
        if not os.path.exists(image_path):
            error_msg = f"Image file not found: {image_path}"
            logger.error(f"❌ {error_msg}")
            return CommandResult(
                status="error",
                stderr=error_msg,
                exit_code=1
            )
        
        logger.info(f"✅ Image file exists: {image_path}")
        logger.debug(f"File size: {os.path.getsize(image_path)} bytes")
        logger.debug(f"File extension: {Path(image_path).suffix}")
        
        # Load classifier
        logger.info("🔄 Loading DECIMER Image Classifier...")
        classifier = get_classifier()
        logger.debug("✅ Classifier loaded successfully")
        
        # Get classifier score
        logger.info("🧮 Calculating classifier score...")
        logger.debug(f"Running get_classifier_score on: {image_path}")
        score = classifier.get_classifier_score(image_path)
        logger.info(f"✅ Classifier score calculated: {score}")
        logger.debug(f"Score type: {type(score)}, Score value: {score}")
        
        # Determine if chemical structure
        logger.info("🔬 Determining if image contains chemical structure...")
        logger.debug(f"Running is_chemical_structure on: {image_path}")
        is_chemical = classifier.is_chemical_structure(image_path)
        logger.info(f"✅ Chemical structure determination completed: {is_chemical}")
        logger.debug(f"Is chemical type: {type(is_chemical)}, Is chemical value: {is_chemical}")
        
        # Prepare result data
        threshold = 0.000089  # Default threshold used by is_chemical_structure
        logger.debug(f"Using threshold: {threshold}")
        
        result_data = {
            "is_chemical": is_chemical,
            "confidence_score": float(score),
            "threshold": threshold,
            "message": f"Image {'contains' if is_chemical else 'does not contain'} a chemical structure"
        }
        
        logger.info(f"📊 Classification Results:")
        logger.info(f"   - Is chemical structure: {is_chemical}")
        logger.info(f"   - Confidence score: {score}")
        logger.info(f"   - Threshold: {threshold}")
        logger.info(f"   - Message: {result_data['message']}")
        
        logger.debug(f"Final result data: {result_data}")
        logger.info("🎉 classify_chemical_structure completed successfully!")
        
        return CommandResult(
            status="success",
            stdout=json.dumps(result_data, indent=2),
            exit_code=0
        )
        
    except Exception as e:
        error_msg = f"Error classifying image: {str(e)}"
        logger.error(f"❌ {error_msg}")
        logger.exception("Full exception details:")
        return CommandResult(
            status="error",
            stderr=error_msg,
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

    IMPORTANT:
    Segmentation may hang due to memory fragmentation when called after classifier/transformer tools.
    This function now includes memory cleanup to prevent hanging issues.
    
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
    logger.info(f"🔍 Starting segment_chemical_structures for file: {file_path}")
    logger.debug(f"Input parameters - file_path: {file_path}, output_dir: {output_dir}")
    logger.debug(f"Current working directory: {os.getcwd()}")
    
    # Force garbage collection to free memory before segmentation
    import gc
    logger.info("🧹 Cleaning up memory before segmentation...")
    gc.collect()
    
    try:
        # Validate input file
        logger.debug(f"🔍 Checking if input file exists: {file_path}")
        if not os.path.exists(file_path):
            error_msg = f"Image file not found: {file_path}"
            logger.error(f"❌ {error_msg}")
            return CommandResult(
                status="error",
                stderr=error_msg,
                exit_code=1
            )
        
        logger.info(f"✅ Input file exists: {file_path}")
        logger.debug(f"File size: {os.path.getsize(file_path)} bytes")
        logger.debug(f"File extension: {Path(file_path).suffix}")
        
        # Set output directory
        if output_dir is None:
            output_dir = os.path.dirname(file_path)
            logger.debug(f"Output directory not specified, using input file directory: {output_dir}")
        
        logger.info(f"📁 Output directory: {output_dir}")
        logger.debug(f"Creating output directory if it doesn't exist: {output_dir}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        logger.debug(f"✅ Output directory created/verified: {output_dir}")
        
        # Load segmentation module
        logger.info("🔄 Loading DECIMER Segmentation module...")
        segmentation = get_segmentation()
        logger.debug("✅ Segmentation module loaded successfully")
        
        # Perform segmentation with single-threaded approach to avoid TensorFlow conflicts
        logger.info("🔬 Starting chemical structure segmentation...")
        logger.info("🔧 Using single-threaded processing to avoid TensorFlow session conflicts...")
        
        # Import the individual segmentation function directly
        from decimer_segmentation.decimer_segmentation import segment_chemical_structures
        
        # Read the file and process individually
        import pymupdf
        import cv2
        import numpy as np
        
        if file_path.lower().endswith('.pdf'):
            logger.info("📄 Processing PDF with single-threaded approach...")
            pdf_document = pymupdf.open(file_path)
            all_segments = []
            
            for page_num in range(pdf_document.page_count):
                logger.info(f"🔄 Processing page {page_num + 1}/{pdf_document.page_count}")
                page = pdf_document[page_num]
                matrix = pymupdf.Matrix(300 / 72, 300 / 72)
                pix = page.get_pixmap(matrix=matrix, alpha=False)
                img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
                
                # Process this page individually (no multiprocessing)
                page_segments = segment_chemical_structures(img_array, expand=True)
                all_segments.extend(page_segments)
                logger.info(f"✅ Page {page_num + 1} processed - found {len(page_segments)} segments")
            
            pdf_document.close()
            segments = all_segments
        else:
            # For single images, use the original function
            logger.info("🖼️ Processing single image file...")
            segments = segmentation.segment_chemical_structures_from_file(file_path)
        
        logger.info(f"✅ Segmentation completed - found {len(segments)} chemical structures")
        logger.debug(f"Segment types: {[type(seg).__name__ for seg in segments]}")
        
        # Import required modules for saving
        logger.debug("📦 Importing PIL, numpy, and time modules...")
        from PIL import Image
        import numpy as np
        import time
        from datetime import datetime
        
        # Prepare for saving segments
        saved_files = []
        timestamp = int(time.time())
        base_name = Path(file_path).stem  # Extract filename without extension
        
        logger.info(f"💾 Starting to save {len(segments)} chemical structures as PNG files...")
        logger.debug(f"Using timestamp: {timestamp}, base_name: {base_name}")
        logger.debug(f"Output directory: {output_dir}")
        
        # Save each segment as PNG file
        for i, segment in enumerate(segments):
            output_path = os.path.join(output_dir, f"{base_name}_segment_{i+1}_{timestamp}.png")
            logger.debug(f"Processing segment {i+1}/{len(segments)}: {os.path.basename(output_path)}")
            
            if isinstance(segment, np.ndarray):
                logger.debug(f"Segment {i+1} is numpy array with shape: {segment.shape}, dtype: {segment.dtype}")
                
                # Convert to PIL Image and save
                logger.debug(f"Converting segment {i+1} to PIL Image...")
                img = Image.fromarray(segment.astype('uint8'))
                logger.debug(f"PIL Image created with mode: {img.mode}, size: {img.size}")
                
                logger.debug(f"Saving segment {i+1} to: {output_path}")
                img.save(output_path)
                saved_files.append(output_path)
                logger.debug(f"✅ Segment {i+1} saved successfully")
                
                # Log file size for verification
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    logger.debug(f"Saved file size: {file_size} bytes")
            else:
                logger.warning(f"⚠️ Segment {i+1} is not a numpy array: {type(segment)}")
                logger.debug(f"Segment {i+1} content: {segment}")
        
        logger.info(f"✅ All chemical structures saved - {len(saved_files)} PNG files created")
        logger.debug(f"Saved files: {saved_files}")
        
        # Prepare result data
        result_data = {
            "segments": saved_files,
            "total_segments": len(saved_files),
            "output_dir": output_dir,
            "message": f"Segmented {len(saved_files)} chemical structures"
        }
        
        logger.info(f"📊 Segmentation Results:")
        logger.info(f"   - Total segments found: {len(segments)}")
        logger.info(f"   - Successfully saved: {len(saved_files)}")
        logger.info(f"   - Output directory: {output_dir}")
        logger.info(f"   - Message: {result_data['message']}")
        
        logger.debug(f"Final result data: {result_data}")
        logger.info("🎉 segment_chemical_structures completed successfully!")
        
        return CommandResult(
            status="success",
            stdout=json.dumps(result_data, indent=2),
            exit_code=0
        )
        
    except Exception as e:
        error_msg = f"Error segmenting structures: {str(e)}"
        logger.error(f"❌ {error_msg}")
        logger.exception("Full exception details:")
        return CommandResult(
            status="error",
            stderr=error_msg,
            exit_code=1
        )


@mcp.tool
@return_as_dict
def analyze_chemical_document(document_path: str, output_dir: str = None) -> dict:
    """
    Complete analysis of a PDF document: segment chemical structures, classify them, and generate SMILES.
    
    IMPORTANT:
    For unclear reasons, segmentation will hang when classifer tool or SMILES transformer tool is used.
    For this reason, make sure to restart the docker container before using this tool.
    
    This tool processes PDF documents containing chemical structures and performs:
    1. Chemical structure segmentation from the PDF
    2. Classification of each segment to determine if it's a chemical structure
    3. SMILES generation for confirmed chemical structures
    4. Comprehensive results with statistics
    
    Args:
        document_path (str): Path to the PDF document containing chemical structures
        output_dir (str, optional): Directory for outputs. Defaults to same directory as input.
        
    Returns:
        dict: {
            "status": "success" or "error",
            "results": list of dict with structure analysis,
            "summary": dict with counts and statistics
        }
        
    Example:
        analyze_chemical_document(document_path="workspace/chemistry_paper.pdf")
    """
    logger.info(f"🔍 Starting analyze_chemical_document for PDF: {document_path}")
    logger.debug(f"Input parameters - document_path: {document_path}, output_dir: {output_dir}")
    
    try:
        # Validate input file
        if not os.path.exists(document_path):
            error_msg = f"PDF document not found: {document_path}"
            logger.error(error_msg)
            return CommandResult(
                status="error",
                stderr=error_msg,
                exit_code=1
            )
        
        # Check if it's a PDF file
        if not document_path.lower().endswith('.pdf'):
            logger.warning(f"⚠️ File may not be a PDF: {document_path}")
        
        logger.info(f"✅ PDF document exists: {document_path}")
        logger.debug(f"File size: {os.path.getsize(document_path)} bytes")
        
        # Set output directory
        if output_dir is None:
            output_dir = os.path.dirname(document_path)
        
        logger.info(f"📁 Output directory: {output_dir}")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        logger.debug(f"✅ Output directory created/verified: {output_dir}")
        
        # Step 1: Segment structures from PDF using the internal implementation
        logger.info("🔬 Step 1: Starting chemical structure segmentation from PDF...")
        
        # Force garbage collection to free memory before segmentation
        import gc
        logger.info("🧹 Cleaning up memory before segmentation...")
        gc.collect()
        
        segmentation = get_segmentation()
        logger.debug("✅ Segmentation module loaded")
        
        # Use single-threaded processing to avoid TensorFlow multiprocessing conflicts
        logger.info("🔧 Using single-threaded processing to avoid TensorFlow session conflicts...")
        
        # Import the individual segmentation function directly
        from decimer_segmentation.decimer_segmentation import segment_chemical_structures
        
        # Read the PDF and process each page individually
        import pymupdf
        import cv2
        import numpy as np
        
        if document_path.lower().endswith('.pdf'):
            logger.info("📄 Processing PDF with single-threaded approach...")
            pdf_document = pymupdf.open(document_path)
            all_segments = []
            
            for page_num in range(pdf_document.page_count):
                logger.info(f"🔄 Processing page {page_num + 1}/{pdf_document.page_count}")
                page = pdf_document[page_num]
                matrix = pymupdf.Matrix(300 / 72, 300 / 72)
                pix = page.get_pixmap(matrix=matrix, alpha=False)
                img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
                
                # Process this page individually (no multiprocessing)
                page_segments = segment_chemical_structures(img_array, expand=True)
                all_segments.extend(page_segments)
                logger.info(f"✅ Page {page_num + 1} processed - found {len(page_segments)} segments")
            
            pdf_document.close()
            segments = all_segments
        else:
            # For single images, use the original function
            segments = segmentation.segment_chemical_structures_from_file(document_path)
        logger.info(f"✅ PDF segmentation completed - found {len(segments)} chemical structures")
        logger.debug(f"Segment types: {[type(seg).__name__ for seg in segments]}")
        
        # Save segments as PNG files
        from PIL import Image
        import numpy as np
        import time
        
        saved_files = []
        # Create unique timestamp suffix to avoid filename conflicts
        timestamp = int(time.time())
        base_name = Path(document_path).stem  # Extract filename without extension
        
        logger.info(f"💾 Step 2: Saving {len(segments)} chemical structures as PNG files...")
        logger.debug(f"Using timestamp: {timestamp}, base_name: {base_name}")
        
        for i, segment in enumerate(segments):
            output_path = os.path.join(output_dir, f"{base_name}_structure_{i+1}_{timestamp}.png")
            logger.debug(f"Saving chemical structure {i+1} to: {output_path}")
            
            if isinstance(segment, np.ndarray):
                img = Image.fromarray(segment.astype('uint8'))
                img.save(output_path)
                saved_files.append(output_path)
                logger.debug(f"✅ Chemical structure {i+1} saved successfully")
            else:
                logger.warning(f"⚠️ Segment {i+1} is not a numpy array: {type(segment)}")
        
        logger.info(f"✅ All chemical structures saved - {len(saved_files)} PNG files created")
        
        # Step 3: Analyze each segmented chemical structure
        logger.info("🧪 Step 3: Starting classification and SMILES generation for chemical structures...")
        results = []
        chemical_count = 0
        
        classifier = get_classifier()
        transformer = get_transformer()
        logger.debug("✅ Classifier and transformer modules loaded")
        
        for i, seg_file in enumerate(saved_files):
            logger.info(f"🔍 Analyzing chemical structure {i+1}/{len(saved_files)}: {os.path.basename(seg_file)}")
            
            # Classify
            try:
                logger.debug(f"Running classification on: {seg_file}")
                score = classifier.get_classifier_score(seg_file)
                is_chemical = classifier.is_chemical_structure(seg_file)
                
                logger.info(f"Classification result - Is chemical: {is_chemical}, Score: {score}")
                
                classify_data = {
                    "is_chemical": is_chemical,
                    "confidence_score": float(score)
                }
            except Exception as e:
                logger.error(f"❌ Classification failed for chemical structure {i+1}: {str(e)}")
                classify_data = {"is_chemical": False, "error": str(e)}
            
            # Generate SMILES if it's a chemical structure
            smiles_data = {}
            if classify_data.get("is_chemical", False):
                chemical_count += 1
                logger.info(f"🧬 Generating SMILES for chemical structure {i+1}...")
                
                try:
                    logger.debug(f"Running SMILES prediction on: {seg_file}")
                    smiles = transformer.predict_SMILES(seg_file)
                    smiles_data = {"smiles": smiles}
                    logger.info(f"✅ SMILES generated: {smiles}")
                except Exception as e:
                    logger.error(f"❌ SMILES generation failed for chemical structure {i+1}: {str(e)}")
                    smiles_data = {"error": str(e)}
            else:
                logger.info(f"📝 Chemical structure {i+1} classified as non-chemical - skipping SMILES generation")
            
            result_item = {
                "image_path": seg_file,
                "classification": classify_data,
                "smiles_prediction": smiles_data
            }
            results.append(result_item)
            
            logger.debug(f"✅ Chemical structure {i+1} analysis completed")
        
        # Generate summary
        summary = {
            "total_segments": len(saved_files),
            "chemical_structures": chemical_count,
            "non_chemical": len(saved_files) - chemical_count
        }
        
        logger.info(f"📊 PDF Analysis Summary:")
        logger.info(f"   - Total chemical structures found: {summary['total_segments']}")
        logger.info(f"   - Confirmed chemical structures: {summary['chemical_structures']}")
        logger.info(f"   - Non-chemical segments: {summary['non_chemical']}")
        
        final_result = {
            "results": results,
            "summary": summary,
            "message": f"Analyzed PDF document: found {len(saved_files)} chemical structures, {chemical_count} confirmed with SMILES"
        }
        
        logger.info("🎉 analyze_chemical_document completed successfully!")
        logger.debug(f"Final result structure: {list(final_result.keys())}")
        
        return CommandResult(
            status="success",
            stdout=json.dumps(final_result, indent=2),
            exit_code=0
        )
        
    except Exception as e:
        error_msg = f"Error analyzing PDF document: {str(e)}"
        logger.error(f"❌ {error_msg}")
        logger.exception("Full exception details:")
        return CommandResult(
            status="error",
            stderr=error_msg,
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
