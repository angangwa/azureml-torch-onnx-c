# Integrating the Neural Network on a Microcontroller

This guide explains how to integrate the onnx2c-generated neural network into your microcontroller project.

- This job runs `templates/complie_minimal.sh`. The following files in the output of this job show minimal example:
    - `minimal_nn`: Unstripped binary with debug symbols
    - `minimal_nn_stripped`: Stripped binary for production deployment
    - `minimal_example.c`: Example code showing how to use the model
    - `nn_wrapper.h`: Header providing a simple API for the neural network
    - `time_series_model.c`: The neural network implementation generated from ONNX
- The minimal binary demonstrates how to run a prediction with the model.
- For actual deployment, you would typically integrate the C code into your application.
- See `build_output.txt` for detailed memory usage information on Azure ML job output. 
    - See [binary-size-guide.ml](./binary-size-guide.md) for explanation of this output.


## File Structure

You need to include these files in your microcontroller project:

1. **time_series_model.c** - The automatically generated neural network from onnx2c
2. **nn_wrapper.h** - A minimal wrapper providing a clean API for the neural network

## Integration Steps

### 1. Include the Wrapper Header

In your microcontroller application code:

```c
#include "nn_wrapper.h"
```

### 2. Call the Neural Network

```c
float sensor_value = read_sensor();  // Your function to read sensor data
float prediction = 0.0f;

// Run neural network inference
nn_run(sensor_value, &prediction);

// Use the prediction
if (prediction > THRESHOLD) {
    // Take action
}
```

### 3. Memory Considerations

The neural network requires:
- ROM/Flash: For code and weights (check the compilation output for exact size)
- RAM: For temporary calculations during inference

### 4. Platform-Specific Adaptations

For specific microcontrollers, you may need to:

1. **Arduino**: Include both files in your sketch and call as shown above
2. **STM32**: Add files to your CubeIDE or STM32CubeMX project
3. **MSP430**: Add files to your Code Composer Studio project

### 5. Further Optimizations

For extremely constrained devices, consider:

1. **Quantization**: Convert weights to fixed-point (int8/int16)
2. **Memory placement**: Place constant weights in ROM/Flash, not RAM
3. **Custom math**: Replace floating-point with fixed-point operations