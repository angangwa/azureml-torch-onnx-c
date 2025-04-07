#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "time_series_model.h"

// Function to read CSV file containing float values
float* read_csv(const char* filename, int* size) {
    // Add debug message to see what's happening
    printf("Attempting to open file: %s\n", filename);
    
    FILE* file = fopen(filename, "r");
    if (!file) {
        printf("Error: Could not open file %s\n", filename);
        return NULL;
    }
    
    printf("Successfully opened file\n");
    
    // Count lines first to allocate proper memory
    int count = 0;
    char buffer[100];
    
    // More reliable way to count lines
    while (fgets(buffer, sizeof(buffer), file)) {
        count++;
    }
    
    printf("Found %d lines in file\n", count);
    
    // Reset file position
    rewind(file);
    
    // Allocate memory
    float* data = (float*)malloc(count * sizeof(float));
    if (!data) {
        printf("Error: Memory allocation failed\n");
        fclose(file);
        return NULL;
    }
    
    // Read data
    int i = 0;
    while (fgets(buffer, sizeof(buffer), file) && i < count) {
        // Convert string to float
        data[i++] = atof(buffer);
    }
    
    fclose(file);
    *size = count;
    
    printf("Successfully loaded %d values\n", count);
    return data;
}

int main() {
    printf("Testing the time series neural network model\n");
    
    // Try current directory first (instead of parent directory)
    int input_size = 0, output_size = 0;
    float* test_inputs = read_csv("test_input.csv", &input_size);
    
    // If that fails, try the parent directory
    if (!test_inputs) {
        printf("Trying parent directory...\n");
        test_inputs = read_csv("../test_input.csv", &input_size);
    }
    
    float* expected_outputs = NULL;
    if (test_inputs) {
        // Use the same directory that worked for inputs
        if (input_size > 0) {
            expected_outputs = read_csv("expected_output.csv", &output_size);
            if (!expected_outputs) {
                expected_outputs = read_csv("../expected_output.csv", &output_size);
            }
        }
    }
    
    if (!test_inputs || !expected_outputs) {
        printf("Failed to read test data\n");
        return 1;
    }
    
    if (input_size != output_size) {
        printf("Error: Input and output size mismatch (%d vs %d)\n", 
               input_size, output_size);
        free(test_inputs);
        free(expected_outputs);
        return 1;
    }
    
    printf("Successfully loaded %d test samples\n", input_size);
    
    // Initialize the model
    time_series_model_init();
    
    // Test model with each input
    float total_error = 0.0f;
    int display_count = input_size < 5 ? input_size : 5;
    
    printf("\nDisplaying first %d results:\n", display_count);
    printf("--------------------------------------------------\n");
    printf("   Input   |   Expected   |   Predicted   | Error  \n");
    printf("--------------------------------------------------\n");
    
    for (int i = 0; i < input_size; i++) {
        float input = test_inputs[i];
        float expected = expected_outputs[i];
        float output = 0.0f;
        
        // Run model inference
        time_series_model_run(&input, &output);
        
        // Calculate error
        float error = fabs(output - expected);
        total_error += error;
        
        // Print first few results
        if (i < display_count) {
            printf("%10.4f | %12.4f | %13.4f | %6.4f\n", 
                   input, expected, output, error);
        }
    }
    
    // Print summary
    float avg_error = total_error / input_size;
    printf("--------------------------------------------------\n");
    printf("Average prediction error: %f\n", avg_error);

    // Write results to output file
    FILE* result_file = fopen("test_results.txt", "w");
    if (result_file) {
        fprintf(result_file, "Average prediction error: %f\n", avg_error);
        fclose(result_file);
    }
    
    // Clean up
    time_series_model_terminate();
    free(test_inputs);
    free(expected_outputs);
    
    printf("\nTest completed successfully!\n");
    return 0;
}