FROM yufree/xcmsrocker:latest

# Install Python dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install fastmcp
RUN pip3 install --break-system-packages fastmcp

# Copy shared utilities and server code
COPY shared.py /app/shared.py
COPY mcp_host/Rscript/server.py /app/server.py

# Set working directory to workspace
WORKDIR /app/workspace

# Set Python path to include /app for imports
ENV PYTHONPATH="/app:$PYTHONPATH"

# Expose MCP port range
EXPOSE 5000-5200

# Run the MCP server
CMD ["python3", "/app/server.py"]
