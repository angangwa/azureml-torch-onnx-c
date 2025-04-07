"""
Script for compiling C code and running tests.
This will run inside the AML pipeline.
"""
import os
import argparse
import subprocess
import shutil

def read_template_file(filename):
    """Read a template file from the templates directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(script_dir, "templates", filename)
    
    if os.path.exists(template_path):
        with open(template_path, "r") as f:
            return f.read()
    else:
        raise FileNotFoundError(f"Template file {filename} not found in {os.path.join(script_dir, 'templates')}")

def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--c_code_dir", type=str, help="Directory containing C code")
    parser.add_argument("--model_dir", type=str, help="Directory containing ONNX model and test data")
    parser.add_argument("--output_dir", type=str, help="Output directory for test results")
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"C code directory: {args.c_code_dir}")
    print(f"Model directory: {args.model_dir}")
    print(f"Output directory: {args.output_dir}")
    
    # Create a temporary work directory
    work_dir = os.path.join(args.output_dir, "work")
    os.makedirs(work_dir, exist_ok=True)
    
    # Copy the model C file from c_code_dir to work directory
    model_c_file = os.path.join(args.c_code_dir, "time_series_model.c")
    if os.path.exists(model_c_file):
        shutil.copy(model_c_file, work_dir)
        print(f"Copied time_series_model.c")
    else:
        raise FileNotFoundError(f"Required file time_series_model.c not found in {args.c_code_dir}")
    
    # Load template files from local templates directory
    try:
        model_impl_content = read_template_file("model_impl.c")
        header_content = read_template_file("time_series_model.h")
        test_model_content = read_template_file("test_model.c")
        
        # Write template files to work directory
        with open(os.path.join(work_dir, "model_impl.c"), "w") as f:
            f.write(model_impl_content)
            
        with open(os.path.join(work_dir, "time_series_model.h"), "w") as f:
            f.write(header_content)
            
        with open(os.path.join(work_dir, "test_model.c"), "w") as f:
            f.write(test_model_content)
    except FileNotFoundError as e:
        print(f"Error loading template files: {e}")
        raise
    
    # Copy test data from model directory to work directory
    for csv_file in ["test_input.csv", "expected_output.csv"]:
        source_path = os.path.join(args.model_dir, csv_file)
        if os.path.exists(source_path):
            shutil.copy(source_path, work_dir)
            print(f"Copied {csv_file}")
        else:
            print(f"Warning: {csv_file} not found in {args.model_dir}")
    
    # Change to the work directory
    os.chdir(work_dir)
    
    # Compile the test code
    print("Compiling C code for testing...")
    result = subprocess.run(
        ["gcc", "test_model.c", "time_series_model.c", "model_impl.c", "-o", "test_model", "-lm"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        error_msg = f"Compilation failed with error:\n{result.stderr}"
        print(error_msg)
        with open(os.path.join(args.output_dir, "compilation_error.txt"), "w") as f:
            f.write(error_msg)
        raise RuntimeError("Compilation failed")
    
    print("Compilation successful. Running tests...")
    
    # Run the test program
    test_result = subprocess.run(
        ["./test_model"],
        capture_output=True,
        text=True
    )
    
    # Save the test output and binary to final output directory
    test_output_path = os.path.join(args.output_dir, "test_output.txt")
    with open(test_output_path, "w") as f:
        f.write(test_result.stdout)
        if test_result.stderr:
            f.write("\nErrors:\n")
            f.write(test_result.stderr)
    
    # Copy only the binary and necessary output files to the output directory
    shutil.copy("test_model", os.path.join(args.output_dir, "test_model"))
    
    # Save test results if generated
    if os.path.exists("test_results.txt"):
        shutil.copy("test_results.txt", os.path.join(args.output_dir, "test_results.txt"))
        print("Test results file created successfully")
    
    print("C code compilation and testing completed successfully")

if __name__ == "__main__":
    main()