# PyTorch Environment with ONNX export capabilities
FROM mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-pip \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up Python environment
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Set working directory
WORKDIR /code

# Set environment variables
ENV PYTHONUNBUFFERED=1