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
    with open(template_path, "r") as f:
        return f.read()

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
    
    # Copy only core model implementation files to the output directory
    print("Copying core model files to output directory...")
    for file_name in ["time_series_model.c", "model_impl.c", "time_series_model.h"]:
        source_path = os.path.join(args.c_code_dir, file_name)
        if os.path.exists(source_path):
            shutil.copy(source_path, args.output_dir)
            print(f"Copied {file_name}")
    
    # Load and write minimal binary-specific templates
    minimal_example_content = read_template_file("minimal_example.c")
    nn_wrapper_content = read_template_file("nn_wrapper.h")
    compile_script_content = read_template_file("compile_minimal.sh")
    readme_content = read_template_file("README.md")
    
    # Write templates to output directory
    with open(os.path.join(args.output_dir, "minimal_example.c"), "w") as f:
        f.write(minimal_example_content)
        
    with open(os.path.join(args.output_dir, "nn_wrapper.h"), "w") as f:
        f.write(nn_wrapper_content)
        
    with open(os.path.join(args.output_dir, "compile_minimal.sh"), "w") as f:
        f.write(compile_script_content)
    
    with open(os.path.join(args.output_dir, "README.md"), "w") as f:
        f.write(readme_content)
    
    # Make the compile script executable
    os.chmod(os.path.join(args.output_dir, "compile_minimal.sh"), 0o755)
    
    # Change to the output directory where we have write permissions
    os.chdir(args.output_dir)
    
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
    
    print(f"Build output saved to {build_output_path}")
    print("Minimal binary build completed")

if __name__ == "__main__":
    main()