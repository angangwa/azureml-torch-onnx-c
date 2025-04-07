"""
Script for compiling C code and running tests.
This will run inside the AML pipeline.
"""
import os
import argparse
import subprocess
import glob
import shutil

def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--c_code_dir", type=str, help="Directory containing C code")
    parser.add_argument("--output_dir", type=str, help="Output directory for test results")
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"C code directory: {args.c_code_dir}")
    print(f"Output directory: {args.output_dir}")
    
    # First, copy all source files to the output directory
    print("Copying source files to output directory...")
    for file_name in ["test_model.c", "time_series_model.c", "model_impl.c", "time_series_model.h"]:
        source_path = os.path.join(args.c_code_dir, file_name)
        if os.path.exists(source_path):
            shutil.copy(source_path, args.output_dir)
            print(f"Copied {file_name}")
    
    # Also copy test data files
    for csv_file in ["test_input.csv", "expected_output.csv"]:
        source_path = os.path.join(args.c_code_dir, csv_file)
        if os.path.exists(source_path):
            shutil.copy(source_path, args.output_dir)
            print(f"Copied {csv_file}")
    
    # Change to the output directory where we have write permissions
    os.chdir(args.output_dir)
    
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
    
    # Save the test output
    test_output_path = os.path.join(args.output_dir, "test_output.txt")
    with open(test_output_path, "w") as f:
        f.write(test_result.stdout)
        if test_result.stderr:
            f.write("\nErrors:\n")
            f.write(test_result.stderr)
    
    print(f"Test output saved to {test_output_path}")
    
    # Check if test_results.txt was created by the test program
    if os.path.exists("test_results.txt"):
        # It's already in the output directory since we changed directories
        print("Test results file created successfully")
    
    print("C code compilation and testing completed successfully")

if __name__ == "__main__":
    main()