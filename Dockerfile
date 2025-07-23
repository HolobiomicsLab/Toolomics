FROM python:3.10

# Install sudo
RUN apt-get update && apt-get install -y sudo && rm -rf /var/lib/apt/lists/*

# Create a user with sudo privileges and no password requirement
RUN useradd -m -s /bin/bash dockeruser && \
    echo "dockeruser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set the working directory
WORKDIR /app

COPY workspace /app/workspace

# Copy the application code
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip3 install -r /app/requirements.txt

# Change ownership of the app directory to dockeruser
RUN chown -R dockeruser:dockeruser /app

# Switch to the dockeruser
USER dockeruser

# Expose ports, from 5100 to 5200 as MCP might use all this range depending on number of tools deployed
EXPOSE 5100-5200

# Command to run the application
CMD ["python3", "deploy.py", "--config", "config.json", "--mcp-dir", "mcp_docker", "--starting-port", "5100"]