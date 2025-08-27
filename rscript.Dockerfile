# Dockerfile for Rscript service
# Based on yufree/xcmsrocker:latest

ARG TARGETPLATFORM=linux/amd64
FROM --platform=$TARGETPLATFORM yufree/xcmsrocker:latest

# Set working directory
WORKDIR /app

COPY requirements.txt .

# Install Python and pip for the MCP server
#RUN apt-get update && apt-get install -y \
#    python3 \
#    python3-pip \
#    && pip install --no-cache-dir --break-system-packages fastmcp \
#    && rm -rf /var/lib/apt/lists/* \
#    && apt-get clean


RUN apt-get update \
&& apt-get install -y --no-install-recommends \
    sudo \
    curl \
    wget \
    git \
    ca-certificates \
    gnupg \
    unzip \
    python3 \
    python3-pip \
    python-is-python3 \
&& curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
&& chmod +x /usr/local/bin/docker-compose \
&& ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose \
&& pip install --no-cache-dir --break-system-packages fastmcp \
&& useradd -m -s /bin/bash dockeruser \
&& echo "dockeruser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers \
&& mkdir -p /projects \
&& rm -rf /var/lib/apt/lists/* \
&& apt-get clean


# Copy the server.py file
COPY --chown=dockeruser:dockeruser . .


# Expose port for the MCP server (adjust if needed)
#EXPOSE 8000

# The base image already exposes port 8787 for RStudio Server

# Keep the container running
#CMD ["rserver"]
RUN usermod -u 1001 dockeruser && \
    groupmod -g 1001 dockeruser && \
    chown -R dockeruser:dockeruser /projects /app

USER dockeruser
WORKDIR /projects