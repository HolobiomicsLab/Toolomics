# Nextflow Pipeline MCP Server Dockerfile
# Uses Apptainer (Singularity) for robust, nested container execution

FROM ubuntu:24.04

LABEL maintainer="Mimosa AI Team"
LABEL description="Nextflow Pipeline MCP Server with Apptainer integration"
LABEL version="2.1"

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless \
    python3 \
    python3-pip \
    curl \
    wget \
    git \
    procps \
    ca-certificates \
    software-properties-common \
    gnupg \
    gpg-agent \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# === CONFIGURE TIMEZONE BEFORE APPTAINER ===
# This is critical! Apptainer will try to bind mount /etc/localtime
# We must ensure it exists as a proper file, not just a symlink that might break
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

# === INSTALL APPTAINER (formerly Singularity) ===
RUN add-apt-repository -y ppa:apptainer/ppa \
    && apt-get update \
    && apt-get install -y apptainer \
    && rm -rf /var/lib/apt/lists/*

# === CONFIGURE APPTAINER ===
# Create apptainer config to disable problematic bind mounts
### These forced bind mounts cause GLIBC conflicts maybe
# RUN mkdir -p /etc/apptainer && \
#     echo "bind path = /tmp" > /etc/apptainer/apptainer.conf && \
#     echo "bind path = /usr/bin" >> /etc/apptainer/apptainer.conf && \
#     echo "bind path = /usr/lib" >> /etc/apptainer/apptainer.conf
# 

# Install Nextflow
ENV NXF_VER=25.10.4
RUN curl -s https://get.nextflow.io | bash && \
    mv nextflow /usr/local/bin/ && \
    chmod +x /usr/local/bin/nextflow && \
    nextflow -version

# Set Nextflow environment variables
ENV NXF_HOME=/root/.nextflow
ENV NXF_OPTS='-Xms512M -Xmx2G'

# Configure Singularity cache directory
ENV NXF_SINGULARITY_CACHEDIR=/app/workspace/singularity_images

# Create directory structure
RUN mkdir -p /app /app/workspace /app/workspace/nf-core /app/workspace/configs /app/pipelines_default /app/configs_default

# Install Python dependencies for MCP server
COPY mcp_host/nextflow/requirements.txt /tmp/requirements.txt
RUN pip3 install --break-system-packages --no-cache-dir -r /tmp/requirements.txt && \
    rm -rf /root/.cache/pip /tmp/requirements.txt

# Copy server files
COPY shared.py /app/shared.py
COPY mcp_host/nextflow/server.py /app/server.py


# Set Python path
ENV PYTHONPATH=/app:$PYTHONPATH

# Set workspace path
ENV WORKSPACE_PATH=/app/workspace
WORKDIR /app/workspace

# Copy pipelines and configs to a SEPARATE location (not in workspace - that gets volume mounted!)
# These will be copied to the workspace at runtime if they don't exist
COPY mcp_host/nextflow/pipelines /app/pipelines_default/
COPY mcp_host/nextflow/config /app/configs_default/

# Expose port range for MCP servers
EXPOSE 5000-5099

# Start the server directly
CMD ["python3", "/app/server.py"]
