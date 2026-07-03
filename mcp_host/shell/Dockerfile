ARG BASE_IMAGE=ubuntu:24.04
FROM ${BASE_IMAGE}

ARG DEBIAN_FRONTEND=noninteractive

# Two interpreters on purpose:
#   - python3.12 (system python on noble) runs server.py — fastmcp env
#   - python3.10 (deadsnakes) is what user shell commands must get
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.12 \
    python3.12-dev \
    python3.12-venv \
    python3.10 \
    python3.10-dev \
    python3.10-venv \
    python3-pip \
    r-base \
    sudo \
    && rm -rf /var/lib/apt/lists/* \
    && python3.12 --version \
    && python3.10 --version

# fastmcp and its dependencies for the server, in a dedicated python3.12 venv
# (same version constraint as requirements.txt); isolated from apt-managed
# packages like the PPA tooling's PyJWT, which pip cannot upgrade in place
RUN python3.12 -m venv /opt/venv312 \
    && /opt/venv312/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv312/bin/pip install --no-cache-dir "fastmcp>=2.12.0,<3.0.0"

# Python 3.10 venv placed first on PATH so that `python`/`python3`/`pip` in
# shell commands resolve to 3.10 while /usr/bin/python3 stays 3.12 for the system
RUN python3.10 -m venv /opt/venv310 \
    && /opt/venv310/bin/pip install --no-cache-dir --upgrade pip \
    && chown -R ubuntu:ubuntu /opt/venv310

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

ENV PATH="/opt/venv310/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"
ENV R_LIBS_USER="/home/ubuntu/R/library"

EXPOSE 5100-5200
CMD ["/opt/venv312/bin/python", "/app/server.py"]
