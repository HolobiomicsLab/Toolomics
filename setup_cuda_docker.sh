#!/bin/bash
set -e

echo "=== NVIDIA Docker Setup Script ==="
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "Don't run as root - script will use sudo when needed"
   exit 1
fi

# Verify NVIDIA driver is installed
echo "[1/6] Checking NVIDIA driver..."
if ! command -v nvidia-smi &> /dev/null; then
    echo "ERROR: nvidia-smi not found. Install NVIDIA drivers first."
    exit 1
fi
nvidia-smi --query-gpu=name --format=csv,noheader
echo "✓ NVIDIA driver found"
echo ""

# Verify Docker is installed
echo "[2/6] Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker not found. Install Docker first."
    exit 1
fi
docker --version
echo "✓ Docker found"
echo ""

# Add NVIDIA container toolkit repository
echo "[3/6] Adding NVIDIA container toolkit repository..."
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
echo "✓ Repository added"
echo ""

# Install nvidia-container-toolkit
echo "[4/6] Installing nvidia-container-toolkit..."
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
echo "✓ Toolkit installed"
echo ""

# Configure Docker runtime
echo "[5/6] Configuring Docker runtime..."
sudo nvidia-ctk runtime configure --runtime=docker
echo "✓ Runtime configured"
echo ""

# Restart Docker
echo "[6/6] Restarting Docker daemon..."
sudo systemctl restart docker
sleep 2
echo "✓ Docker restarted"
echo ""

# Verify installation
echo "=== Verification ==="
echo "Checking Docker runtime configuration..."
if docker info 2>/dev/null | grep -q "nvidia"; then
    echo "✓ NVIDIA runtime registered in Docker"
else
    echo "⚠ WARNING: NVIDIA runtime not found in Docker info"
fi
echo ""

echo "Testing GPU access in container..."
if docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi &> /dev/null; then
    echo "✓ GPU access working!"
    echo ""
    docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi
else
    echo "✗ GPU access test failed"
    exit 1
fi

echo ""
echo "=== Setup Complete ==="
echo "You can now use GPU in Docker with:"
echo "  docker run --gpus all ..."
echo "  or in compose with deploy.resources.reservations.devices"