"""
Script to set up the Azure ML pipeline and all required resources.
Run this from your development environment after setting up the directory structure.
"""
import os
import shutil
import argparse
from azure.ai.ml import MLClient, command, dsl, Input, Output
from azure.ai.ml.entities import Environment, BuildContext, AmlCompute
from azure.identity import DefaultAzureCredential

from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Setup and optionally run an Azure ML pipeline')
    parser.add_argument('--run', action='store_true', help='Run the pipeline after setup')
    args = parser.parse_args()

    # Connect to your AML workspace
    ml_client = MLClient(
        DefaultAzureCredential(), 
        subscription_id=os.environ["subscription_id"],  # Replace with your subscription ID
        resource_group_name=os.environ["resource_group_name"],  # Replace with your resource group
        workspace_name=os.environ["workspace_name"]  # Replace with your workspace name
    )
    
    # Set up directory structure
    directories = [
        "environments/pytorch",
        "environments/onnx2c",
        "environments/gcc",
        "src/pytorch_train",
        "src/onnx2c",
        "src/compile_test",
        "src/minimal_binary"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Create compute resources
    print("Creating compute cluster...")
    if "cpu-cluster" not in [c.name for c in ml_client.compute.list()]:
        compute_cluster = AmlCompute(
            name="cpu-cluster",
            type="amlcompute",
            size="Standard_DS3_v2",
            min_instances=0,
            max_instances=4,
            idle_time_before_scale_down=120
        )
        ml_client.compute.begin_create_or_update(compute_cluster).result()
        print("Compute cluster created.")
    else:
        print("Compute cluster already exists.")
    
    # Create environments
    print("Creating environments...")
    env_configs = [
        ("pytorch-onnx-env", "environments/pytorch", "Environment for PyTorch training and ONNX export"),
        ("onnx2c-env", "environments/onnx2c", "Environment for ONNX to C conversion"),
        ("gcc-env", "environments/gcc", "Environment for C compilation and testing")
    ]
    
    # Dictionary to store the latest environment versions
    latest_envs = {}
    
    for env_name, env_dir, env_description in env_configs:
        # Create or update the environment
        env = Environment(
            name=env_name,
            description=env_description,
            build=BuildContext(path=env_dir)
        )
        registered_env = ml_client.environments.create_or_update(env)
        print(f"Environment {env_name} created/updated with version {registered_env.version}")
        
        # Store the latest version
        latest_envs[env_name] = f"{env_name}:{registered_env.version}"
    
    # Define components
    print("Creating pipeline components...")
    
    # 1. PyTorch Training Component
    train_pytorch_model = command(
        name="pytorch_train",
        display_name="Train PyTorch Model and Export to ONNX",
        description="Trains a PyTorch model and exports it to ONNX format",
        environment=latest_envs["pytorch-onnx-env"],
        compute="cpu-cluster",
        code="./src/pytorch_train",
        outputs=dict(
            output_dir=Output(type="uri_folder", description="Output directory for model and data")
        ),
        command="python run.py --output_dir ${{outputs.output_dir}}"
    )
    
    # 2. ONNX to C Conversion Component
    convert_onnx_to_c = command(
        name="onnx2c",
        display_name="Convert ONNX to C",
        description="Converts ONNX model to C code using onnx2c",
        environment=latest_envs["onnx2c-env"],
        compute="cpu-cluster",
        code="./src/onnx2c",
        inputs=dict(
            model_dir=Input(type="uri_folder", description="Directory containing ONNX model")
        ),
        outputs=dict(
            output_dir=Output(type="uri_folder", description="Output directory for C code")
        ),
        command="python run.py --model_dir ${{inputs.model_dir}} --output_dir ${{outputs.output_dir}}"
    )
    
    # 3. C Compilation and Testing Component
    compile_and_test = command(
        name="compile_and_test",
        display_name="Compile C Code and Run Tests",
        description="Compiles C code and runs tests",
        environment=latest_envs["gcc-env"],
        compute="cpu-cluster",
        code="./src/compile_test",
        inputs=dict(
            c_code_dir=Input(type="uri_folder", description="Directory containing C code")
        ),
        outputs=dict(
            output_dir=Output(type="uri_folder", description="Output directory for test results")
        ),
        command="python run.py --c_code_dir ${{inputs.c_code_dir}} --output_dir ${{outputs.output_dir}}"
    )
    
    # 4. Build Minimal Binary Component
    build_minimal_binary = command(
        name="build_minimal",
        display_name="Build Minimal Binary",
        description="Creates minimal binary for deployment",
        environment=latest_envs["gcc-env"],
        compute="cpu-cluster",
        code="./src/minimal_binary",
        inputs=dict(
            c_code_dir=Input(type="uri_folder", description="Directory containing C code")
        ),
        outputs=dict(
            output_dir=Output(type="uri_folder", description="Output directory for minimal binary")
        ),
        command="python run.py --c_code_dir ${{inputs.c_code_dir}} --output_dir ${{outputs.output_dir}}"
    )
    
    # Define the pipeline
    @dsl.pipeline(
        name="pytorch-onnx-c-pipeline",
        description="Pipeline for training PyTorch model, converting to ONNX, C, and building minimal binary",
        compute="cpu-cluster"
    )
    def nn_pipeline():
        # Train PyTorch model
        train_step = train_pytorch_model()
        
        # Convert ONNX to C
        onnx2c_step = convert_onnx_to_c(model_dir=train_step.outputs.output_dir)
        
        # Compile and test C code
        compile_step = compile_and_test(c_code_dir=onnx2c_step.outputs.output_dir)
        
        # Build minimal binary
        binary_step = build_minimal_binary(c_code_dir=onnx2c_step.outputs.output_dir)
        
        # Return all outputs
        return {
            "training_output": train_step.outputs.output_dir,
            "c_code_output": onnx2c_step.outputs.output_dir,
            "test_results": compile_step.outputs.output_dir,
            "minimal_binary": binary_step.outputs.output_dir
        }
    
    # Create pipeline
    pipeline = nn_pipeline()
    
    print("\nSetup complete! Pipeline is ready to be submitted.")
    print("To submit the pipeline, uncomment the following lines at the end of this script:")
    print("""
    # Submit pipeline to Azure ML
    pipeline_job = ml_client.jobs.create_or_update(pipeline)
    print(f"Pipeline job submitted with ID: {pipeline_job.name}")
    """)
    
    # Run the pipeline if the --run flag is provided
    if args.run:
        pipeline_job = ml_client.jobs.create_or_update(pipeline)
        print(f"Pipeline job submitted with ID: {pipeline_job.name}")

if __name__ == "__main__":
    main()