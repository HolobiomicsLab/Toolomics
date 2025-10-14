FROM nvidia/cuda:13.0.1-cudnn-devel-ubuntu24.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create workspace directory with proper permissions
RUN mkdir -p /app/workspace && chmod 777 /app/workspace

# Create and use venv
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY shared.py /app/shared.py
COPY mcp_host/shell/server.py /app/server.py

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

RUN chmod +x /app/server.py

ENV PYTHONPATH="/app:$PYTHONPATH"

EXPOSE 5100-5200
CMD ["python3", "/app/server.py"]
