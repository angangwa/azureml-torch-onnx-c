# GCC Environment for C compilation and testing
FROM mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    make \
    python3-pip \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up Python environment for scripts
RUN pip install --no-cache-dir numpy

# Set working directory
WORKDIR /code

# Set environment variables
ENV PYTHONUNBUFFERED=1