FROM python:3.10

# Install system dependencies including Chrome
RUN apt-get update && apt-get install -y \
    sudo \
    wget \
    gnupg \
    unzip \
    xvfb \
    libxss1 \
    libgconf-2-4 \
    libxtst6 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcairo-gobject2 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libnss3 \
    libcups2 \
    libxrandr2 \
    && apt-get install -y chromium \
    && rm -rf /var/lib/apt/lists/*

# Create a user with sudo privileges and no password requirement
RUN useradd -m -s /bin/bash dockeruser && \
    echo "dockeruser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set the working directory
WORKDIR /app

# Copy the entire project
COPY . /app/

# Install Python dependencies  
RUN pip3 install -r /app/requirements.txt

# Create workspace directory
RUN mkdir -p /app/workspace

# Change ownership of the app directory to dockeruser
RUN chown -R dockeruser:dockeruser /app

# Set display environment variable for headless Chrome
ENV DISPLAY=:99

# Switch to the dockeruser
USER dockeruser

# Expose ports, from 5100 to 5200 as MCP might use all this range depending on number of tools deployed
EXPOSE 5100-5200

# Command to run the application
CMD ["python3", "deploy.py", "--config", "config.json", "--mcp-dir", "mcp_docker", "--starting-port", "5100"]