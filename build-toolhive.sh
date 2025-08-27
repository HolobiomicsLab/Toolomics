#!/bin/bash

# Toolomics Docker Build Script for ToolHive
# Builds the Docker image and validates the registry

set -e  # Exit on any error

echo "🏗️  Building Toolomics Docker image for ToolHive"
echo "================================================"

# Configuration
IMAGE_NAME="holobiomicslab/toolomics"
IMAGE_TAG="local"
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"
REGISTRY_FILE="$(pwd)/registry/registry.json"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Dockerfile exists
if [[ ! -f "Dockerfile" ]]; then
    echo "❌ Dockerfile not found in current directory"
    exit 1
fi

# Check if registry/registry.json exists
if [[ ! -f "$REGISTRY_FILE" ]]; then
    echo "❌ Registry file not found: $REGISTRY_FILE"
    echo "💡 Run this script from the toolomics root directory"
    exit 1
fi

echo "✅ Docker is running"
echo "✅ Found Dockerfile"
echo "✅ Found registry file"

# Build the Docker image
echo ""
echo "🏗️  Building Docker image: $FULL_IMAGE_NAME"
echo "============================================"

if docker build -t "$FULL_IMAGE_NAME" .; then
    echo "✅ Docker image built successfully: $FULL_IMAGE_NAME"
else
    echo "❌ Docker build failed"
    exit 1
fi

# Verify the image exists
if docker images "$FULL_IMAGE_NAME" --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" | grep -v "REPOSITORY"; then
    echo "✅ Image verified in local Docker registry"
else
    echo "❌ Image not found in local Docker registry"
    exit 1
fi

# Rscript configuration
RSCRIPT_IMAGE_NAME="holobiomicslab/rscript"
RSCRIPT_IMAGE_TAG="local"
RSCRIPT_FULL_IMAGE_NAME="${RSCRIPT_IMAGE_NAME}:${RSCRIPT_IMAGE_TAG}"

# Build the Rscript Docker image
echo ""
echo "🏗️  Building Rscript Docker image: $RSCRIPT_FULL_IMAGE_NAME"
echo "============================================"

if docker build -t "$RSCRIPT_FULL_IMAGE_NAME" . -f rscript.Dockerfile; then
    echo "✅ Rscript Docker image built successfully: $RSCRIPT_FULL_IMAGE_NAME"
else
    echo "❌ Rscript Docker build failed"
    exit 1
fi

# Verify the Rscript image exists
if docker images "$RSCRIPT_FULL_IMAGE_NAME" --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" | grep -v "REPOSITORY"; then
    echo "✅ Rscript image verified in local Docker registry"
else
    echo "❌ Rscript image not found in local Docker registry"
    exit 1
fi

# Check if ToolHive CLI is available for registry validation
if command -v thv &> /dev/null; then
    echo ""
    echo "🔍 Validating ToolHive registry"
    echo "==============================="
    
    # Set registry if not already configured
    CURRENT_REGISTRY=$(thv config get-registry 2>/dev/null || echo "")
    if [[ "$CURRENT_REGISTRY" != "$REGISTRY_FILE" ]]; then
        echo "📋 Configuring registry for validation..."
        thv config set-registry "$REGISTRY_FILE"
    fi
    
    # List available servers from registry
    if thv registry list >/dev/null 2>&1; then
        echo "✅ Registry validation passed"
        echo ""
        echo "📋 Available servers in registry:"
        thv registry list | grep -E "^[a-z]" | sed 's/^/   - /'
    else
        echo "⚠️  Registry validation warning (but image build was successful)"
        echo "💡 You can still run servers with: thv run <server-name>"
    fi
else
    echo ""
    echo "⚠️  ToolHive CLI not found - skipping registry validation"
    echo "💡 Install with: curl -sSL https://get.toolhive.dev | sh"
fi

echo ""
echo "🎉 Build Process Complete!"
echo "=========================="
echo "🐳 Docker images: $FULL_IMAGE_NAME, $RSCRIPT_FULL_IMAGE_NAME"
echo "📋 Registry file: $REGISTRY_FILE"
echo ""
echo "🚀 Next steps:"
echo "   1. Start all servers: ./start.sh"
echo "   2. Or start individual server: thv run toolomics-browser"
echo ""
echo "🔧 Useful commands:"
echo "   - List available servers:  thv registry list"
echo "   - Check running servers:   thv list"
echo "   - View server logs:        thv logs <server-name>"
echo "   - Stop a server:          thv mcp tools --server <server-url>"s