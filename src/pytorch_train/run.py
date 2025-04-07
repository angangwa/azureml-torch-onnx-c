"""
Script for training PyTorch model and exporting to ONNX.
This will run inside the AML pipeline.
"""
import os
import argparse
import shutil
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split

# Copy your training script here, or import it
class SimpleTimeSeriesModel(nn.Module):
    def __init__(self):
        super(SimpleTimeSeriesModel, self).__init__()
        # Very simple network: input -> hidden layer (4 neurons) -> output
        self.model = nn.Sequential(
            nn.Linear(1, 4),
            nn.ReLU(),
            nn.Linear(4, 1)
        )
    
    def forward(self, x):
        return self.model(x)

def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", type=str, help="Output directory")
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Generate sample time series data
    time = np.arange(100)
    temperature = 20 + 0.1 * time + np.random.normal(0, 1, 100)

    # Split data and convert to PyTorch tensors
    X = time.reshape(-1, 1).astype(np.float32)  # Cast to float32 for PyTorch
    y = temperature.astype(np.float32)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Convert to PyTorch tensors
    X_train_tensor = torch.FloatTensor(X_train)
    y_train_tensor = torch.FloatTensor(y_train).view(-1, 1)  # Reshape for PyTorch
    X_test_tensor = torch.FloatTensor(X_test)
    y_test_tensor = torch.FloatTensor(y_test).view(-1, 1)

    # Create data loaders
    train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
    train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)

    # Initialize model, loss function, and optimizer
    model = SimpleTimeSeriesModel()
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)

    # Train the model
    epochs = 200
    losses = []

    print("Training neural network model...")
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        
        for batch_X, batch_y in train_loader:
            # Forward pass
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            
            # Backward pass and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / len(train_loader)
        losses.append(avg_loss)
        
        if (epoch + 1) % 50 == 0:
            print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")

    # Evaluate model
    model.eval()
    with torch.no_grad():
        test_predictions = model(X_test_tensor)
        test_loss = criterion(test_predictions, y_test_tensor)
        
        # Calculate R² score manually
        y_test_mean = torch.mean(y_test_tensor)
        total_variance = torch.sum((y_test_tensor - y_test_mean)**2)
        explained_variance = torch.sum((test_predictions - y_test_mean)**2)
        r2_score = explained_variance / total_variance
        
        print(f"Test Loss (MSE): {test_loss.item():.4f}")
        print(f"R² Score: {r2_score.item():.4f}")

    # Export model to ONNX
    onnx_path = os.path.join(args.output_dir, "simple_time_series_model.onnx")
    dummy_input = torch.randn(1, 1)  # Example input for tracing

    # Export the model
    torch.onnx.export(
        model,                     # model being run
        dummy_input,               # model input
        onnx_path,                 # where to save the model
        export_params=True,        # store the trained parameter weights inside the model file
        opset_version=11,          # ONNX version to use
        do_constant_folding=True,  # optimization
        input_names=['input'],     # model's input names
        output_names=['output'],   # model's output names
        dynamic_axes={'input': {0: 'batch_size'},  # variable length axes
                    'output': {0: 'batch_size'}}
    )
    print(f"Model saved as '{onnx_path}'")

    # Save test data for C++ implementation
    np.savetxt(os.path.join(args.output_dir, 'test_input.csv'), X_test, delimiter=',')
    np.savetxt(os.path.join(args.output_dir, 'expected_output.csv'), y_test, delimiter=',')
    print("Test data saved for C implementation")

    # Plot training results
    plt.figure(figsize=(12, 5))

    # Plot 1: Training loss
    plt.subplot(1, 2, 1)
    plt.plot(losses)
    plt.title('Training Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')

    # Plot 2: Predictions vs. Actual
    plt.subplot(1, 2, 2)
    plt.scatter(X_test, y_test, label='Actual data', alpha=0.5)
    plt.scatter(X_test, test_predictions.numpy(), label='Predictions', alpha=0.5, color='red')
    plt.title('Predictions vs. Actual')
    plt.xlabel('Time')
    plt.ylabel('Temperature')
    plt.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(args.output_dir, 'model_visualization.png'))
    
    # Save metrics to file for Azure ML to track
    with open(os.path.join(args.output_dir, 'metrics.txt'), 'w') as f:
        f.write(f"Test Loss (MSE): {test_loss.item():.4f}\n")
        f.write(f"R² Score: {r2_score.item():.4f}\n")

if __name__ == "__main__":
    main()