# Executing a benchmark

Once everything is installed, you may use one of two modes.
The default mode is when you use the commands:
```bash
$ make pre
$ make post
```

## Accuracy of results
To obtain more accurate results, the code generation has a speed parameter which scales the number of iterations.

In order to get more accurate results, you may set this speed to be lower than 1.0. In can be set in multiple ways:
- if using make, set SPEED=<float> as a suffix for ``make pre``
- if directly using scripts, look at the help for [``codegen.py``](../bench/preprocess/codegen.py) with ``python3 codegen.py --help``
    hint: use --speed flag


11/07/24 Out of date
# ``allocatable`` benchmark : ``allocatable`` allocated vs constant arrays
To use, set your CPU L3 cache size in [``benchmark_parameters.f90``](../bench/src/benchmark_parameters.f90)
Set the desired type of array size by passing ``sizemode=<value>`` at execution (note: parameter has to be passed before any other) or changing ``#define BENCHMARK_SIZE_MODE`` in [``main.f90``](../bench/main.f90) at compilation and setting them to a value between 0 and 4, using the following table :

|  BENCHMARK_SIZE_MODE  | Percentage of L3 Cache |
| --------------------- | ---------------------- |
| 0                     | 1.5%                   |
| 1                     | 96.7%                  |
| 2                     | 103.1%                 |
| 3                     | 290.6%                 |

Numbers of iterations are normalized to work on the same total amount of stencil operations, minus the ignored edges.