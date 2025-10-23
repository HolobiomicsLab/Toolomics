ARG BASE_IMAGE=ubuntu:24.04
FROM ${BASE_IMAGE}

RUN apt-get update && apt-get install -y \
    python3 \
    r-base \
    python3-pip \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages globally as root
COPY requirements.txt /tmp/
RUN pip3 install --break-system-packages --no-cache-dir -r /tmp/requirements.txt

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
WORKDIR /app

ENV PYTHONPATH="/app:$PYTHONPATH"
ENV R_LIBS_USER="/home/ubuntu/R/library"

EXPOSE 5100-5200
CMD ["python3", "/app/server.py"]
