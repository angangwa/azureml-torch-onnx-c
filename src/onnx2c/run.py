"""
Script for converting ONNX model to C code using onnx2c.
This will run inside the AML pipeline.
"""
import os
import argparse
import subprocess
import glob
import shutil

def read_template_file(filename):
    """Read a template file from the templates directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(script_dir, "templates", filename)
    with open(template_path, "r") as f:
        return f.read()

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
    
    # Save the C code to file
    with open(c_output_path, "w") as f:
        f.write(result.stdout)
    
    print(f"C code saved to {c_output_path}")
    
    # Load and write only core model implementation template files
    model_impl_content = read_template_file("model_impl.c")
    header_content = read_template_file("time_series_model.h")
    
    # Write core model implementation files
    with open(os.path.join(args.output_dir, "model_impl.c"), "w") as f:
        f.write(model_impl_content)
        
    with open(os.path.join(args.output_dir, "time_series_model.h"), "w") as f:
        f.write(header_content)
    
    # Copy test data for use by later components
    for csv_file in ["test_input.csv", "expected_output.csv"]:
        csv_path = os.path.join(args.model_dir, csv_file)
        if os.path.exists(csv_path):
            shutil.copy(csv_path, args.output_dir)
            print(f"Copied {csv_file} to output directory")
    
    print("ONNX to C conversion completed successfully")

if __name__ == "__main__":
    main()