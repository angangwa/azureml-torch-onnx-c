#ifndef NN_WRAPPER_H
#define NN_WRAPPER_H

#ifdef __cplusplus
extern "C" {
#endif

// Forward declaration of the entry function from onnx2c output
extern void entry(const float input[1][1], float output[1][1]);

/**
 * Run the neural network inference
 * 
 * @param input_value Single input value
 * @param output_value Pointer to store the output
 */
static inline void nn_run(float input_value, float* output_value) {
    float input_array[1][1] = {{input_value}};
    float output_array[1][1];
    
    // Call the entry function from the onnx2c generated code
    entry(input_array, output_array);
    
    // Copy output
    *output_value = output_array[0][0];
}

#ifdef __cplusplus
}
#endif

#endif /* NN_WRAPPER_H */