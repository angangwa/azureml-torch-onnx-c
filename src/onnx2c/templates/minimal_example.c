#include "nn_wrapper.h"

/**
 * Minimal example of using the neural network
 * This represents the code that would run on the microcontroller
 */
int main(void) {
    // Example input value (would come from sensors in real deployment)
    float input_value = 42.0f;
    float prediction = 0.0f;
    
    // Run neural network inference
    nn_run(input_value, &prediction);
    
    // On a microcontroller, you would use the prediction here
    // e.g., control an actuator, make a decision, etc.
    
    return 0;
}