> ⚠️ **Note:** This document is a work in progress. ⚙️

# MCU selection

- Most popular methods like `tflite`, `deepC`, and `onnx2c` either recommend or have more support for **floating point 32-bit hardware**.
    - Quantization techniques can be leveraged if this this is not possible. These techniques impact model performance.

- MCU's available Flash and RAM impacts models selection.

- There is extensive testing on ARM Cortex based devices such as MSP432 and STM32F411. See for example - [LiteRT supported platforms](https://ai.google.dev/edge/litert/microcontrollers/overview#supported_platforms), [onnx2c Tests](https://github.com/kraiskil/onnx2c/blob/fdba85bd1346d9551e28d46b9431374fc9f9c4fa/scripts/measure_stm32f411_nucleo.sh#L6)

# TensorFlow Lite vs ONNX2C vs Other tools: A Comparison

This document provides a detailed comparison between [TensorFlow Lite (TFLite)](https://ai.google.dev/edge/litert/microcontrollers/overview) and [ONNX2C](https://github.com/kraiskil/onnx2c) for resource-constrained environments.

- We also considered [deepC](https://github.com/ai-techsystems/deepC) but it doesn't seem to be in active development.
- We also considered [cONNXr](https://github.com/alrevuelta/cONNXr) but it doesn't seem to be in active development.
- [Keras2c](https://github.com/PlasmaControl/keras2c) is similar to onnx2c but was not reviewed.

There are several other Tensorflow and Pytorch specific options that were not considered:
- Tensorflow based
    - [TinyEngine](https://github.com/mit-han-lab/tinyengine/tree/main) - Good alternative to onnx2c and has a larger community.
    - CMSIS-NN
    - TinyMaix
    - Nnom – Relatively active project. Small footprint and portable.
- Pytorch based
    - PyTorch Edge / Executorch
    - microTVM
    - Meta Glow Machine learning compiler

There are also MCU family specific solutions like https://stm32ai.st.com/stm32-cube-ai/ that were not considered.


## Basic Overview

### TensorFlow Lite (TFLite)
TensorFlow Lite is a lightweight solution from Google designed for deploying machine learning models on mobile, embedded, and IoT devices. It's an inference framework that enables on-device machine learning with low latency.

### ONNX2C
ONNX2C is a tool that converts Open Neural Network Exchange (ONNX) models to C code. It allows for direct compilation of neural networks into native C code that can run without dependencies on large ML frameworks.

## Key Differences

| Feature | TensorFlow Lite | ONNX2C |
|---------|----------------|--------|
| **Primary Function** | Runtime inference engine | Model-to-code converter |
| **Input Format** | TensorFlow models (converted to .tflite) | ONNX models |
| **Output** | Optimized model for TFLite interpreter | Pure C code |
| **Dependencies** | Requires TFLite runtime | No runtime dependencies after compilation |
| **Flexibility** | Works with TensorFlow ecosystem | Works with any framework that exports to ONNX |

## Detailed Comparison

### Purpose and Functionality

**TensorFlow Lite:**
- Serves as a runtime inference engine
- Interprets and executes pre-compiled models
- Includes tools for model optimization (quantization, pruning)
- Provides a consistent API across platforms

**ONNX2C:**
- Generates human-readable C code from models
- Eliminates the need for a runtime interpreter
- Focuses on direct translation of model operations to code
- Allows for compile-time optimizations

### Model Format and Conversion

**TensorFlow Lite:**
- Uses a proprietary .tflite format
- Requires conversion from TensorFlow models
- Supports various optimization techniques during conversion
- Maintains model structure for interpreter execution

**ONNX2C:**
- Takes ONNX models as input
- Translates model operations to C code
- Produces standalone execution code
- Allows for platform-specific compiler optimizations

### Target Platforms

**TensorFlow Lite:**
- Mobile devices (Android, iOS)
- Embedded systems
- Microcontrollers (with TFLite Micro)
- IoT devices
- Has specific optimizations for different hardware accelerators

**ONNX2C:**
- Any platform with a C compiler
- Particularly suited for bare-metal systems
- Embedded systems without OS
- Systems where installing a runtime is impractical
- Custom hardware with specific C compilers

### Integration and Deployment

**TensorFlow Lite:**
- Requires integration of TFLite runtime
- Provides consistent API across platforms
- Offers delegate system for hardware acceleration
- Supports Android Neural Networks API

**ONNX2C:**
- Generated C code can be directly compiled into applications
- No additional runtime libraries needed
- Easier integration with existing C/C++ codebases
- More transparent compile-time optimizations

### Performance Characteristics

**TensorFlow Lite:**
- Optimized interpreter performance
- Hardware acceleration via delegates
- Runtime memory management
- Quantized and reduced precision operations
- Some overhead from interpreter execution

**ONNX2C:**
- Potential for better performance through direct execution
- Compile-time optimizations from C compiler
- Static memory allocation possible
- No interpreter overhead
- Potentially larger binary size for complex models

### Development and Community

**TensorFlow Lite:**
- Large, active community
- Comprehensive documentation
- Regular updates from Google
- Extensive tutorials and examples
- Wide adoption in industry

**ONNX2C:**
- Smaller community
- More specialized use cases
- Open-source development
- Less comprehensive documentation
- Growing adoption in embedded systems

## Use Cases

### When to Use TensorFlow Lite
- When working primarily within the TensorFlow ecosystem
- When targeting mainstream mobile platforms
- When hardware acceleration is critical
- When model updates need to be deployed without app updates
- When developing for platforms with official TFLite support

### When to Use ONNX2C
- When working with various ML frameworks that support ONNX export
- When targeting highly constrained embedded systems
- When runtime dependencies must be minimized
- When transparency of execution code is required
- When integration with C/C++ codebases is a priority
- When deploying to platforms without ML framework support

## Limitations

### TensorFlow Lite Limitations
- Limited to TensorFlow model ecosystem
- Requires runtime interpreter overhead
- May not support all TensorFlow operations
- Different optimization path from main TensorFlow

### ONNX2C Limitations
- May generate large C files for complex models
- Limited optimizations compared to specialized runtimes
- Less support for dynamic shapes and operations
- Requires recompilation for model updates
- May not support all ONNX operations

# Conclusion

Oxxn2c is much simpler to use than TFLite. If the model you plan to implement is relatively small and doesn’t have strict latency requirements, this option is much more attractive.
