#!/bin/bash

echo "Compiling minimal neural network implementation using original onnx2c output..."

# Compile with size optimization
gcc -Os -fdata-sections -ffunction-sections -Wl,--gc-sections \
    minimal_example.c time_series_model.c -o minimal_nn -lm

# Check if compilation succeeded
if [ $? -eq 0 ]; then
    echo "Compilation successful!"
    
    # Create stripped version
    cp minimal_nn minimal_nn_stripped
    strip minimal_nn_stripped
    
    # Show the size of both binaries
    echo -e "\nBinary size information:"
    ls -lh minimal_nn | awk '{print "Normal size: " $5}'
    ls -lh minimal_nn_stripped | awk '{print "Stripped size: " $5}'
    
    # Show detailed size breakdown
    echo -e "\nDetailed size breakdown:"
    size minimal_nn
    
    echo -e "\nStripped binary size breakdown:"
    size minimal_nn_stripped
    
    # Show sections size
    echo -e "\nSection size details:"
    objdump -h minimal_nn_stripped | grep -E '\.text|\.data|\.bss|\.rodata'
    
    # Estimate microcontroller ROM/RAM usage
    TEXT_SIZE=$(objdump -h minimal_nn_stripped | grep "\.text" | awk '{print $3}')
    RODATA_SIZE=$(objdump -h minimal_nn_stripped | grep "\.rodata" | awk '{print $3}')
    DATA_SIZE=$(objdump -h minimal_nn_stripped | grep "\.data" | awk '{print $3}')
    BSS_SIZE=$(objdump -h minimal_nn_stripped | grep "\.bss" | awk '{print $3}')
    
    # Convert hex to decimal
    TEXT_DEC=$((16#$TEXT_SIZE))
    RODATA_DEC=$((16#${RODATA_SIZE:-0}))
    DATA_DEC=$((16#${DATA_SIZE:-0}))
    BSS_DEC=$((16#${BSS_SIZE:-0}))
    
    echo -e "\nEstimated microcontroller memory usage:"
    echo "ROM (Flash) usage: ~$((TEXT_DEC + RODATA_DEC + DATA_DEC)) bytes"
    echo "RAM usage: ~$((DATA_DEC + BSS_DEC)) bytes"
    
    echo -e "\nNote: This is the minimal size using the original onnx2c output."
    echo "For actual microcontroller deployment, you may need additional platform-specific code."
else
    echo "Compilation failed!"
fi