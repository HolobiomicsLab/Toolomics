# Use Python 3.10 base image for compatibility with DECIMER requirements
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for ML libraries and PDF processing
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libfontconfig1-dev \
    libfreetype6-dev \
    git \
    wget \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install base dependencies first
COPY mcp_docker/decimer/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install DECIMER packages in the recommended order: Classifier → Segmentation → Transformer
# This prevents dependency conflicts

# 1. Install DECIMER Image Classifier (from GitHub - not available on PyPI)
RUN pip install git+https://github.com/Iagea/DECIMER-Image-Classifier.git

# 2. Install DECIMER Segmentation (from PyPI, requires poppler-utils installed above)
RUN pip install decimer-segmentation

# 3. Install DECIMER Transformer (from PyPI - official release)
RUN pip install decimer

# Copy model download script
COPY mcp_docker/decimer/download_models.py /app/download_models.py

# Copy pre-downloaded models to their proper locations
# This avoids runtime downloads and speeds up first-time usage
COPY mcp_docker/decimer/models/classifier /tmp/classifier_models
COPY mcp_docker/decimer/models/segmentation /tmp/segmentation_models  
COPY mcp_docker/decimer/models/transformer /tmp/transformer_models

# Install models to their proper locations
RUN cp -r /tmp/classifier_models/* /usr/local/lib/python3.10/site-packages/decimer_image_classifier/model/ && \
    cp /tmp/segmentation_models/mask_rcnn_molecule.h5 /usr/local/lib/python3.10/site-packages/decimer_segmentation/mask_rcnn_molecule.h5 && \
    mkdir -p /root/.data/pystow && \
    cp -r /tmp/transformer_models/DECIMER-V2 /root/.data/pystow/ && \
    rm -rf /tmp/classifier_models /tmp/segmentation_models /tmp/transformer_models && \
    echo "✅ Pre-downloaded models installed successfully"

# Copy shared utilities from the project
COPY shared.py /app/shared.py

# Copy the MCP server
COPY mcp_docker/decimer/server.py /app/server.py

# Make server executable
RUN chmod +x /app/server.py

# Create workspace directory
RUN mkdir -p /app/workspace

# Set Python path to include the app directory
ENV PYTHONPATH="/app:$PYTHONPATH"

# Expose port range for MCP servers
EXPOSE 5100-5200

# Default command
CMD ["python", "/app/server.py"]
