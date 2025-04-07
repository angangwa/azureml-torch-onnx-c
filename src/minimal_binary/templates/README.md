# Minimal Neural Network Binary

This directory contains the minimal binary for deploying the time series neural network model.

Files:
- `minimal_nn`: Unstripped binary with debug symbols
- `minimal_nn_stripped`: Stripped binary for production deployment
- `minimal_example.c`: Example code showing how to use the model
- `nn_wrapper.h`: Header providing a simple API for the neural network
- `time_series_model.c`: The neural network implementation generated from ONNX

## Usage

The minimal binary demonstrates how to run a prediction with the model.
For actual deployment, you would typically integrate the C code into your application.

## Memory Usage

See build_output.txt for detailed memory usage information.