# Executing a benchmark
## Warnings
You must clean before generating code to avoid keeping compiled files made with the wrong compiler.

Using non-nvfortran with GPUs is not supported as of now.

## Variants
Once everything is installed, you may execute and plot benchmarks in multiple ways.
The default mode is run when you use the commands:
```bash
$ make pre
$ make post
```

For more specific modes, check [``codegen.py --help``](../bench/preprocess/codegen.py).

### Example
To run a streamlined GPU vs CPU comparison, run this as a bash script:
```bash
# replace with your installation directory
cd ~/Fortran-Stencil-Microbenchmarks/bench/postprocess
mkdir -p gpu_cpu_bench_test
make -C .. clean --silent
# if the size is too big for your machine, you will get segmentation faults or Out of memory errors
for size in 4 16 512 1024
do
    cd ../preprocess
    # this command will generate a tree of benchmarks using the specified options
    # TODO: --module True set because non-module not yet implemented and graphing can break
    python3 codegen.py --size $size --kernel-mode DEFAULT_KERNEL -c -nv --module True -A
    # this command will run all your benchmarks
    # the flag -vompgpu will output the OpenMP optimisations on the GPU benchmarks
    ./run_bench_tree.sh -vompgpu
    cd ../postprocess
    ./collect_data_csv.sh -nv
    # this command will generate graphs with hardware as their plotted data
    python3 generate_graph.py -D gpu_cpu_bench_test/gpu_cpu_$(printf $size)Mb -sp -G hardware -sG all
done
```


To run an nvfortran compiler version on 1, 2, 3 Mb sizes with allocatable arrays, compiled array size and size 5 kernels, use these commands:
```bash
cd bench/preprocess
python3 codegen.py --range 3 -nv --alloc ALLOC --compile-size True -c --kernel-mode SIZE_5_KERNEL
./run_bench_tree.sh
cd ../postprocess
./collect_data_csv.sh
python3 generate_graph.py
```

# Results

For tracing results
For example, we can trace size_option data with alloc_option rows like this:
```bash
python3 generate_graph.py -sp -G size_option -sG alloc_option
```
Or maybe alloc_option with is_module rows:
```bash
python3 generate_graph.py -sp -c -G alloc_option -sG is_module
```
TODO: explain this
python3 generate_graph.py -sp -sG alloc_option

## Normalisation of data
For graphing, data is normalized by dividing by array size dimensions and by number of iterations executed.
The number of iterations roughly compensates the size for most small sizes, however it is preferable to normalise everything for more comparable data.
Beware, the data is not normalised relative to stencil type.


## Accuracy of results
To obtain more accurate results, the code generation has a speed parameter which scales the number of iterations.

In order to get more accurate results, you may set this speed to be lower than 1.0. In can be set in multiple ways:
- if using make, set SPEED=<float> as a suffix for ``make pre``
- if directly using scripts, look at the help for [``codegen.py``](../bench/preprocess/codegen.py) with ``python3 codegen.py --help``
    hint: use -A flag


11/07/24 Out of date
# ``allocatable`` benchmark : ``allocatable`` allocated vs constant arrays
To use, set your CPU L3 cache size in [``benchmark_parameters.F90``](../bench/src/benchmark_parameters.F90)
Set the desired type of array size by passing ``sizemode=<value>`` at execution (note: parameter has to be passed before any other) or changing ``#define BENCHMARK_SIZE_MODE`` in [``main.F90``](../bench/main.F90) at compilation and setting them to a value between 0 and 4, using the following table :

|  BENCHMARK_SIZE_MODE  | Percentage of L3 Cache |
| --------------------- | ---------------------- |
| 0                     | 1.5%                   |
| 1                     | 96.7%                  |
| 2                     | 103.1%                 |
| 3                     | 290.6%                 |

Numbers of iterations are normalized to work on the same total amount of stencil operations, minus the ignored edges.