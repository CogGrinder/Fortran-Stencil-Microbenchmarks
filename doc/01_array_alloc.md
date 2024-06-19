# ``allocatable`` benchmark : ``allocatable`` allocated vs constant arrays
To use, set your CPU L3 cache size in [``benchmark_parameters.f90``](../bench/src/benchmark_parameters.f90)
Set the desired type of array size by changing ``#define BENCHMARK_SIZE_MODE`` in [``main.f90``](../bench/main.f90) and setting it to a value between 0 and 4, using the following table :

|  BENCHMARK_SIZE_MODE  | Percentage of L3 Cache |
| --------------------- | ---------------------- |
| 0                     | 1.5%                   |
| 1                     | 96.7%                  |
| 2                     | 103.1%                 |
| 3                     | 290.6%                 |

Numbers of iterations are normalized to work on the same total amount of stencil operations, minus the ignored edges.

## More accurate results
To obtain more accurate results for comparison, use a smaller factor ``#define BENCHMARK_ACCELERATION`` in [``benchmark_parameters.f90``](../bench/src/benchmark_parameters.f90) - value is a power of 2 between 1 and $32 = 2^5$.