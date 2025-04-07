"""
Script for building a minimal binary from C code.
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
    parser.add_argument("--output_dir", type=str, help="Output directory for minimal binary")
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"C code directory: {args.c_code_dir}")
    print(f"Output directory: {args.output_dir}")
    
    # Create a temporary work directory
    work_dir = os.path.join(args.output_dir, "work")
    os.makedirs(work_dir, exist_ok=True)
    
    # Copy only the model C file from c_code_dir to work directory
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
        minimal_example_content = read_template_file("minimal_example.c")
        nn_wrapper_content = read_template_file("nn_wrapper.h")
        compile_script_content = read_template_file("compile_minimal.sh")
        readme_content = read_template_file("README.md")
        
        # Write template files to work directory
        with open(os.path.join(work_dir, "model_impl.c"), "w") as f:
            f.write(model_impl_content)
            
        with open(os.path.join(work_dir, "time_series_model.h"), "w") as f:
            f.write(header_content)
            
        with open(os.path.join(work_dir, "minimal_example.c"), "w") as f:
            f.write(minimal_example_content)
            
        with open(os.path.join(work_dir, "nn_wrapper.h"), "w") as f:
            f.write(nn_wrapper_content)
            
        with open(os.path.join(work_dir, "compile_minimal.sh"), "w") as f:
            f.write(compile_script_content)
    except FileNotFoundError as e:
        print(f"Error loading template files: {e}")
        raise
    
    # Make the compile script executable
    os.chmod(os.path.join(work_dir, "compile_minimal.sh"), 0o755)
    
    # Change to the work directory
    os.chdir(work_dir)
    
    # Run the compile script
    print("Building minimal binary...")
    
    result = subprocess.run(
        ["./compile_minimal.sh"],
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
    
    # Copy only the compiled binaries and necessary output files to the output directory
    for binary in ["minimal_nn", "minimal_nn_stripped"]:
        if os.path.exists(binary):
            shutil.copy(binary, os.path.join(args.output_dir, binary))
            print(f"Copied {binary} to output directory")
    
    # Include minimal_example.c in the output for reference
    shutil.copy("minimal_example.c", os.path.join(args.output_dir, "minimal_example.c"))
    
    # Copy the README.md to the output directory
    with open(os.path.join(args.output_dir, "README.md"), "w") as f:
        f.write(readme_content)
    
    print("Minimal binary build completed")

if __name__ == "__main__":
    main()