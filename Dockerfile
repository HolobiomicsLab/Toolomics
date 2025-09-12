FROM python:3.10

# Install dependencies
# RUN apt-get update && apt-get install -y \
#     python3 \
#     python3-pip \
#     && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

COPY workspace /app/

# Copy the application code
COPY mcp_docker/requirements.txt /app/requirements.txt
#COPY . /app

# Install Python dependencies
RUN pip3 install -r /app/requirements.txt

# Expose ports, from 5100 to 5200 as MCP might use all this range depending on number of tools deployed
EXPOSE 5100-5200

# Command to run the application
CMD ["python3", "deploy.py", "--config", "config.json", "--mcp-dir", "mcp_docker", "--starting-port", "5100"]