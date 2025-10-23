ARG BASE_IMAGE=ubuntu:24.04
FROM ${BASE_IMAGE}

RUN apt-get update && apt-get install -y \
    python3 \
    r-base \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages globally as root
COPY requirements.txt /tmp/
RUN pip3 install --break-system-packages --no-cache-dir -r /tmp/requirements.txt

# Create non-root user
RUN useradd -m -u 1001 appuser

# Copy application files and set ownership
COPY --chown=appuser:appuser shared.py /app/shared.py
COPY --chown=appuser:appuser mcp_host/shell/server.py /app/server.py

# Create workspace with proper ownership
RUN mkdir -p /app/workspace && chown -R appuser:appuser /app

USER appuser
WORKDIR /app

ENV PYTHONPATH="/app:$PYTHONPATH"

EXPOSE 5100-5200
CMD ["python3", "/app/server.py"]