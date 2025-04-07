"""
Script for converting ONNX model to C code using onnx2c.
This will run inside the AML pipeline.
"""
import os
import argparse
import subprocess
import glob

def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_dir", type=str, help="Directory containing ONNX model")
    parser.add_argument("--output_dir", type=str, help="Output directory for C code")
    args = parser.parse_args()
    
    print("Starting ONNX to C conversion process...")
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Find ONNX model file
    onnx_files = glob.glob(os.path.join(args.model_dir, "*.onnx"))
    if not onnx_files:
        raise FileNotFoundError(f"No ONNX model found in {args.model_dir}")
    
    onnx_model_path = onnx_files[0]
    print(f"Found ONNX model: {onnx_model_path}")
    
    # Output C file path
    c_output_path = os.path.join(args.output_dir, "time_series_model.c")
    
    # Convert ONNX to C using onnx2c
    print(f"Converting ONNX model to C code...")
    
    result = subprocess.run(
        ["onnx2c", onnx_model_path],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"onnx2c failed with error: {result.stderr}")
    
    # Save the C code to file - this is the only actual output of this step
    with open(c_output_path, "w") as f:
        f.write(result.stdout)
    
    print(f"C code saved to {c_output_path}")
    print("ONNX to C conversion completed successfully")

if __name__ == "__main__":
    main()