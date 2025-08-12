FROM python:3.10

# Install system dependencies for ARM64/AMD64 compatibility
RUN apt-get update && apt-get install -y --fix-missing \
    sudo \
    wget \
    curl \
    gnupg \
    unzip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Chromium and dependencies (ARM64 compatible)
RUN apt-get update && apt-get install -y --fix-missing \
    chromium \
    chromium-driver \
    xvfb \
    libnss3 \
    libatk-bridge2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgconf-2-4 \
    libxss1 \
    libxtst6 \
    && rm -rf /var/lib/apt/lists/*

# Install Docker Compose
RUN curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose \
    && ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# Create a user with sudo privileges and no password requirement
RUN useradd -m -s /bin/bash dockeruser && \
    echo "dockeruser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Copy the entire project to /app
COPY . /app/

# Install Python dependencies  
RUN pip3 install -r /app/requirements.txt

# Create and set workspace as working directory
RUN mkdir -p /workspace
WORKDIR /workspace

# Change ownership of both directories to dockeruser
RUN chown -R dockeruser:dockeruser /app /workspace

# Set display environment variable for headless Chrome
ENV DISPLAY=:99

# Switch to the dockeruser
USER dockeruser

# No CMD directive needed - ToolHive manages container execution via registry.json
# Each server is started individually by ToolHive with specific arguments