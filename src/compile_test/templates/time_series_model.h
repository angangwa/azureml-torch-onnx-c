#ifndef TIME_SERIES_MODEL_H
#define TIME_SERIES_MODEL_H

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Initialize the model (if needed)
 * For this simple model, this is a no-op, but included for API completeness
 */
void time_series_model_init(void);

/**
 * Run inference with the neural network model
 * 
 * @param input_data Pointer to a single float value (the time input)
 * @param output_data Pointer to a float where the prediction will be stored
 */
void time_series_model_run(const float* input_data, float* output_data);

/**
 * Clean up any resources used by the model (if needed)
 * For this simple model, this is a no-op, but included for API completeness
 */
void time_series_model_terminate(void);

#ifdef __cplusplus
}
#endif

#endif /* TIME_SERIES_MODEL_H */