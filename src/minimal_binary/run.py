"""
Script for building a minimal binary from C code.
This will run inside the AML pipeline.
"""
import os
import argparse
import subprocess
import shutil

def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--c_code_dir", type=str, help="Directory containing C code")
    parser.add_argument("--output_dir", type=str, help="Output directory for minimal binary")
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"C code directory: {args.c_code_dir}")
    print(f"Output directory: {args.output_dir}")
    
    # Copy necessary files to the output directory
    print("Copying source files to output directory...")
    for file_name in ["time_series_model.c", "minimal_example.c", "nn_wrapper.h", "compile_minimal.sh"]:
        source_path = os.path.join(args.c_code_dir, file_name)
        if os.path.exists(source_path):
            shutil.copy(source_path, args.output_dir)
            print(f"Copied {file_name}")
    
    # Make the compile script executable in the output directory
    os.chmod(os.path.join(args.output_dir, "compile_minimal.sh"), 0o755)
    
    # Change to the output directory where we have write permissions
    os.chdir(args.output_dir)
    
    # Modify the compile_minimal.sh script to use the current directory for all paths
    # This is a temporary file we'll use for execution
    with open("compile_minimal_mod.sh", "w") as f:
        f.write("""#!/bin/bash

echo "Compiling minimal neural network implementation using original onnx2c output..."

# Compile with size optimization
gcc -Os -fdata-sections -ffunction-sections -Wl,--gc-sections \\
    minimal_example.c time_series_model.c -o minimal_nn -lm

# Check if compilation succeeded
if [ $? -eq 0 ]; then
    echo "Compilation successful!"
    
    # Create stripped version
    cp minimal_nn minimal_nn_stripped
    strip minimal_nn_stripped
    
    # Show the size of both binaries
    echo -e "\\nBinary size information:"
    ls -lh minimal_nn | awk '{print "Normal size: " $5}'
    ls -lh minimal_nn_stripped | awk '{print "Stripped size: " $5}'
    
    # Show detailed size breakdown
    echo -e "\\nDetailed size breakdown:"
    size minimal_nn
    
    echo -e "\\nStripped binary size breakdown:"
    size minimal_nn_stripped
    
    # Show sections size
    echo -e "\\nSection size details:"
    objdump -h minimal_nn_stripped | grep -E '\\.text|\\.data|\\.bss|\\.rodata'
    
    # Estimate microcontroller ROM/RAM usage
    TEXT_SIZE=$(objdump -h minimal_nn_stripped | grep "\\\.text" | awk '{print $3}')
    RODATA_SIZE=$(objdump -h minimal_nn_stripped | grep "\\\.rodata" | awk '{print $3}')
    DATA_SIZE=$(objdump -h minimal_nn_stripped | grep "\\\.data" | awk '{print $3}')
    BSS_SIZE=$(objdump -h minimal_nn_stripped | grep "\\\.bss" | awk '{print $3}')
    
    # Convert hex to decimal
    TEXT_DEC=$((16#$TEXT_SIZE))
    RODATA_DEC=$((16#${RODATA_SIZE:-0}))
    DATA_DEC=$((16#${DATA_SIZE:-0}))
    BSS_DEC=$((16#${BSS_SIZE:-0}))
    
    echo -e "\\nEstimated microcontroller memory usage:"
    echo "ROM (Flash) usage: ~$((TEXT_DEC + RODATA_DEC + DATA_DEC)) bytes"
    echo "RAM usage: ~$((DATA_DEC + BSS_DEC)) bytes"
    
    echo -e "\\nNote: This is the minimal size using the original onnx2c output."
    echo "For actual microcontroller deployment, you may need additional platform-specific code."
else
    echo "Compilation failed!"
fi
""")
    
    # Make the modified script executable
    os.chmod("compile_minimal_mod.sh", 0o755)
    
    # Run the modified compile script
    print("Building minimal binary...")
    
    result = subprocess.run(
        ["./compile_minimal_mod.sh"],
        capture_output=True,
        text=True
    )
    
    # Save the build output
    build_output_path = os.path.join(args.output_dir, "build_output.txt")
    with open(build_output_path, "w") as f:
        f.write(result.stdout)
        if result.stderr:
            f.write("\nErrors:\n")
            f.write(result.stderr)
    
    print(f"Build output saved to {build_output_path}")
    
    # Create a README file in the output directory
    readme_content = """# Minimal Neural Network Binary

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
"""
    
    with open(os.path.join(args.output_dir, "README.md"), "w") as f:
        f.write(readme_content)
    
    print("Minimal binary build completed")

if __name__ == "__main__":
    main()