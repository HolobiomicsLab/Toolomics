FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy shared.py from project root
COPY shared.py /app/shared.py

# Copy the shell MCP server code
COPY mcp_host/shell /app

# Install Python dependencies
RUN pip3 install -r /app/requirements.txt

# Expose ports, from 5100 to 5200 as MCP might use all this range depending on number of tools deployed
EXPOSE 5100-5200

# Command to run the application
CMD ["python3", "server.py"]
