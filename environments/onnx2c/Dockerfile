# ONNX2C conversion environment
FROM mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu22.04

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    cmake \
    python3-pip \
    python3-dev \
    llvm \
    clang \
    llvm-dev \
    curl \
    unzip \
    libprotobuf-dev \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

# # Install Protocol Buffers 30.2
# RUN PB_REL="https://github.com/protocolbuffers/protobuf/releases" && \
#     curl -LO $PB_REL/download/v30.2/protoc-30.2-linux-x86_64.zip && \
#     unzip protoc-30.2-linux-x86_64.zip -d /usr/local && \
#     chmod 755 /usr/local/bin/protoc && \
#     rm protoc-30.2-linux-x86_64.zip

# Verify protoc version
RUN protoc --version

# Clone and build onnx2c
RUN git clone https://github.com/kraiskil/onnx2c.git /onnx2c && \
    cd /onnx2c && \
    git submodule update --init && \
    mkdir -p build && \
    cd build && \
    cmake -DCMAKE_BUILD_TYPE=Debug .. && \
    make -j$(nproc) onnx2c && \
    cp onnx2c /usr/local/bin/

# Set up Python environment for scripts
RUN pip install --no-cache-dir numpy onnx onnxruntime

# Set working directory
WORKDIR /code

# Set environment variables
ENV PYTHONUNBUFFERED=1