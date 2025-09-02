FROM python:3.10-slim

# Set working directory early
WORKDIR /app

# Copy only requirements first for better layer caching
COPY requirements.txt .

# Install all dependencies in a single layer to minimize image size
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        g++ \
        sudo \
        curl \
        wget \
        git \
        ca-certificates \
        gnupg \
        unzip \
        chromium \
        chromium-driver \
        xvfb \
        libnss3-dev \
        libatk-bridge2.0-0 \
        libxcomposite1 \
        libxdamage1 \
        libxrandr2 \
        libxss1 \
        libxtst6 \
    && pip install -r requirements.txt \
    && mkdir -p /projects \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && useradd -m -s /bin/bash dockeruser \
    && echo "dockeruser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Copy application code (dockerignore excludes .venv, workspace, etc)
COPY . .

#RUN usermod -u 1001 dockeruser && \
#    groupmod -g 1001 dockeruser && \
#    chown -R dockeruser:dockeruser /projects /app
# Set environment for headless Chrome
ENV DISPLAY=:99

# Set final permissions and switch to non-root user
#RUN chown -R dockeruser:dockeruser /app /projects
# USER dockeruser

RUN usermod -u 1001 dockeruser && \
    groupmod -g 1001 dockeruser 

USER dockeruser

WORKDIR /projects

# No CMD directive needed - ToolHive manages container execution via registry.json