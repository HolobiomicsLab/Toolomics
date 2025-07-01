FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the application code
COPY . /app

# Install Python dependencies
RUN pip3 install -r /app/requirements.txt

# Expose ports, from 5000 to 5100 as MCP might use all this range depending on number of tools deployed
EXPOSE 5000-5100

# Command to run the application
CMD ["python3", "deploy.py", "--config", "config_docker.json", "--mcp-dir", "mcp_servers", "--starting-port", "5000", "--no-docker"]