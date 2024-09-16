#ifndef CPU_FUZZ_TEST_H
#define CPU_FUZZ_TEST_H

// Students must implement these functions
void matrixMultiplyCPU_float(float* A, float* B, float* C, int M, int N, int P);

// Fuzz test function that students can use without seeing the implementation
void fuzzTestMatrixMultiplication(int num_tests, int max_size);

#endif
