# Use build argument to select base image
ARG BASE_IMAGE=ubuntu:24.04
FROM ${BASE_IMAGE}

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create home directory for the user that will run the container
RUN mkdir -p /home/appuser && \
    chown -R 1000:1000 /home/appuser && \
    chmod -R 755 /home/appuser

# Create workspace directory with proper permissions
RUN mkdir -p /app/workspace && chmod 777 /app/workspace

# Install pip packages system-wide (no venv needed in container)
# Use --break-system-packages flag for Ubuntu 24.04
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --break-system-packages -r /app/requirements.txt

COPY shared.py /app/shared.py
COPY mcp_host/shell/server.py /app/server.py

RUN chmod +x /app/server.py

# Ensure /app is accessible by non-root users
RUN chmod -R 755 /app

ENV PYTHONPATH="/app:$PYTHONPATH"
ENV HOME="/home/appuser"

EXPOSE 5100-5200
CMD ["python3", "/app/server.py"]
