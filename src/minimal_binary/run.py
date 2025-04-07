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
    
    # Load the compile script from the template and use it as a base for the modified script
    compile_script_content = read_template_file("compile_minimal.sh") if os.path.exists(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "compile_minimal.sh")) else ""
    
    # If we couldn't load the template, use the original file from the c_code_dir
    if not compile_script_content and os.path.exists("compile_minimal.sh"):
        with open("compile_minimal.sh", "r") as f:
            compile_script_content = f.read()
    
    # Modify the compile_minimal.sh script to use the current directory for all paths
    # This is a temporary file we'll use for execution
    with open("compile_minimal_mod.sh", "w") as f:
        f.write(compile_script_content)
    
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
    readme_content = read_template_file("README.md")
    
    with open(os.path.join(args.output_dir, "README.md"), "w") as f:
        f.write(readme_content)
    
    print("Minimal binary build completed")

if __name__ == "__main__":
    main()