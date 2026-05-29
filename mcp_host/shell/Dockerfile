ARG BASE_IMAGE=ubuntu:24.04
FROM ${BASE_IMAGE}

RUN apt-get update && apt-get install -y \
    python3.12 \
    python3.12-dev \
    python3.12-venv \
    python3-pip \
    r-base \
    sudo \
    && rm -rf /var/lib/apt/lists/* \
    && python3 --version

# install fastmcp and its dependencies
RUN pip3 install --break-system-packages --no-cache-dir fastmcp

# Grant ubuntu passwordless sudo access
RUN echo "ubuntu ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Copy application files and set ownership
COPY --chown=ubuntu:ubuntu shared.py /app/shared.py
COPY --chown=ubuntu:ubuntu mcp_host/shell/server.py /app/server.py

# Create workspace with proper ownership
RUN mkdir -p /app/workspace && chown -R ubuntu:ubuntu /app

# Create R library directory in user's home directory with proper permissions

RUN mkdir -p /home/ubuntu/R/library && \
    chown -R ubuntu:ubuntu /home/ubuntu/R && \
    chmod -R 777 /home/ubuntu/

USER ubuntu
WORKDIR /app/workspace

ENV PYTHONPATH="/app:$PYTHONPATH"
ENV R_LIBS_USER="/home/ubuntu/R/library"

EXPOSE 5100-5200
CMD ["python3", "/app/server.py"]
