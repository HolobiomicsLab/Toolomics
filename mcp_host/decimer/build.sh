#!/bin/bash

# Build script for DECIMER MCP Docker container
# This script builds the Docker image with all DECIMER dependencies isolated
# Installation order: Classifier → Segmentation → Transformer (as recommended)

set -e

echo "🔨 Building DECIMER MCP Docker container..."
echo "📦 Installation order: Classifier → Segmentation → Transformer"
echo "📥 DECIMER packages will be installed from official sources:"
echo "   - DECIMER Image Classifier: pip install from GitHub"
echo "   - DECIMER Segmentation: pip install decimer-segmentation (PyPI)"
echo "   - DECIMER Transformer: pip install decimer (PyPI)"
echo ""
echo "🎯 Pre-downloaded models will be copied to their proper locations:"
echo "   - Classifier: models/classifier/ → /usr/local/lib/python3.10/site-packages/decimer_image_classifier/model/"
echo "   - Segmentation: models/segmentation/mask_rcnn_molecule.h5 → /usr/local/lib/python3.10/site-packages/decimer_segmentation/"
echo "   - Transformer: models/transformer/DECIMER-V2/ → /root/.data/pystow/"

# Check if models directory exists
if [ ! -d "mcp_host/decimer/models" ]; then
    echo "❌ Error: models directory not found at mcp_host/decimer/models/"
    echo "   Please ensure you have downloaded the models first."
    echo "   Run this script from the project root directory."
    exit 1
fi

# Check if each model directory exists
for model_type in classifier segmentation transformer; do
    if [ ! -d "mcp_host/decimer/models/$model_type" ]; then
        echo "❌ Error: missing model directory: mcp_host/decimer/models/$model_type/"
        echo "   Please download all required models."
        exit 1
    fi
done

echo "✅ All model directories found"

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "📁 Script directory: $SCRIPT_DIR"
echo "📁 Project root: $PROJECT_ROOT"

# Build the Docker image from the project root for proper context
cd "$PROJECT_ROOT"
docker build -t toolomics-decimer:latest -f mcp_host/decimer/Dockerfile .

echo "✅ DECIMER MCP Docker container built successfully!"
echo ""
echo "🎉 Build complete! Models are embedded in the Docker image."
echo "   No runtime downloads required - models load instantly!"
echo ""
echo "🚀 To run the server:"
echo "   ./mcp_host/decimer/run.sh [port]"
echo ""
echo "Or manually:"
echo "   docker run -d --name decimer-mcp -p 5150:5150 \\"
echo "     -v \"\$(pwd)/workspace:/app/workspace\" \\"
echo "     toolomics-decimer:latest python /app/server.py 5150"
echo ""
echo "💡 Models are now embedded in the Docker image"
echo "   Pre-downloaded models eliminate startup delays!"
echo ""
echo "📋 Available MCP tools in this container:"
echo "   - classify_chemical_structure: Detect if image contains chemical structures"
echo "   - predict_smiles: Generate SMILES from chemical structure images"
echo "   - segment_chemical_structures: Extract structures from documents"
echo "   - analyze_chemical_document: Complete document analysis pipeline"
