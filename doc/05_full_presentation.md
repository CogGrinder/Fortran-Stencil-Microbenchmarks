see https://tex.stackexchange.com/questions/452552/algorithm-pseudocode-in-markdown for pseudocode in pandoc

## Qualities of proposed benchmark suite
### Problematique
The object of my internship project was to create the framework to run empirical experiments that determine the best practices for implementing memory-bound multidimensional array stencil operations in Fortran, the tradeoff of using CPUs vs GPUs or different compilers, and find machine-specific performance optimisations. In practice, our empirical tests question how much optimisation is going after compilation on different systems, depending on the way the source code is written.

The mock computations done by these benchmarks ressemble the costly stencil operations in (TODO: CROCO and ?). In the AIRSEA team, it was a common concern to get more understanding of optimisation and best practices of this type of computation in Fortran, notably for use in future developments in PsyClone (TODO: verify this information). Another concern is comparing CPU and GPU platforms on available systems, such as Sharky and (TODO: Martin's platform).

The choice of allocatable vs static allocation was the first motivator for these benchmarks.
TODO: check existing AIRSEA code
### Relevance
Why would you use these benchmarks ?
- it is useful for experiments with different compilers
  - to make sure compilers optimise your code containing kernel computations in the way you anticipated
  - to gain knowledge of systematic performance properties

Why would you extend this framework ?
- it is designed to be flexible, robust, and generate useful graphs in a modular approach
### Flexibility
- Configurability
- Example of use
- Based around dictionaries and independent code (modularity)
- Dictionaries
  - -> easy renaming of variables for .csv data and .json metadata for compatibility graphing
  - -> easy to add measurements thanks to configuration of PerfRegions and graphing

## Features
### Summary of benchmark suite structure
TODO : UML
#### Fortran source robustness
The Fortran code is structured in a way that makes a small amount of function calls. All the parameters that are tested, such as allocation type, are managed outside of the Fortran code except selecting the type of computation and use of a module.

All other parameters are either configured through:
- ``-cpp`` preprocessor
  - inlining code snippets
  - simple if else macros
  - replacing runtime variables by constants through macros
Preprocessing enables us to make less error-prone code that can be verified simply, without using and unnecessary if branches or function calls in Fortran code.
- runtime variables initialised through program arguments
  - number of iterations
  - non-compiled array sizes
Program arguments are used consciously when possible, when it does not impact measured performance.

In Fortran computation functions and modules, all performance sensitive sections in functions with performance metric counters contain only computations and no output.

Performance metrics scope only encompasses single instances of benchmarks. Benchmarks are repeated a certain amount of iterations and summed to output total metrics on the amount of iterations chosen in program parameters.

TODO: see pseudocode

To ensure our compiler does not remove zero-closure computations, values from the input and output are written to a temporary file.

#### Job tree
In the job tree stage, benchmarks are configured independently in their respective bash script ``run.sh`` with local exports for compilation parameters such as preprocessor and execution parameters.

Each instance of ``run.sh`` creates compiles all the sources in order to apply the correct parameters through the preprocessor. 

All compilation errors and output are accessible after running in ``compile.log`` files.
(To check compiler optimisations, use -vomp or -vompgpu TODO: all compiler optimisations)

Graph generation will put ``None`` values where no valid benchmark was found and gives user feedback when an option is not properly configured for predictable results.

#### Graphing
The raw performance data collected from the benchmark job tree must be collected into a single ``<data>.csv``, identified by the path to the ``run.sh`` file with [collect_data_csv.sh](../bench/postprocess/collect_data_csv.sh).

Joining the generated benchmark jobs metadata json ``<all_benchmark_parameters>.json`` with the ``.csv`` data using ``pandas`` lets us generate graphs using any of the existing data.

### Pseudocode
Available computation functions:
```
1D
├module COMPUTATION_1D_MODULE
└no module COMPUTATION_1D
2D
├CPU
|├module COMPUTATION_2D_MODULE
|└no module COMPUTATION_2D_JI
└GPU OpenMP target offload
  └module COMPUTATION_GPU_OMP_BASE
```
Benchmark executable pseudo-code:
```python
-> : preprocessor options using macros NI, NJ, etc
macro NI, NJ # used in computation_function
def benchmark(iters, ni, nj)
  warmup_iters = max(iters / 10, 1)
  
  import perf_regions
  call perf_regions_init # initialise perf_regions

  # warmup loop
  for i_bench from 1 to warmup_iters
    insert computation function call based on preprocessor options
      call -> computation_function("<warmup identifier>")
  
  # bench loop
  for i_bench from 1 to iters
    insert computation function call based on preprocessor options
      call -> computation_function("<benchmark identifier>")

  perf_regions_finalize call # finalize perf_regions data for output
  return performance metrics attributed to <benchmark identifier> (through perf_regions_finalize output)

def computation_function("<identifier>")
  int loop_bound_ni, loop_bound_nj
  
  # array size and loop bound macros
  insert array sizes, one of following macros
    -> no inserting
    -> apply macros
      ni replaced by NI
      nj replaced by NJ
  insert loop bounds, one of following macros
    -> insert code
      loop_bound_ni = ni
      loop_bound_nj = nj
    -> apply macros
      loop_bound_ni replaced by NI
      loop_bound_nj replaced by NJ

  multidim float array : array, result
  # allocation macro
  insert array, result allocation
    -> allocatable variant
    -> static variant

  array : arbitrary initialisation

  # starts or restarts counting performance metrics using <identifier>
  call perf_region_start("<identifier>")
  for j from 2 to loop_bound_nj - 2
    for i from 2 to loop_bound_ni - 2
      insert inlined kernel
        -> default variant
        result(i,j) = 1.0_dp * array(i - 1, j - 1) &
                    + 2.0_dp * array(i - 1, j + 1) &
                    + 3.0_dp * array(i    , j    ) &
                    + 4.0_dp * array(i + 1, j - 1) &
                    + 5.0_dp * array(i + 1, j + 1)
        result(i,j) = result(i,j)/15.0_dp
        -> other variants
  # pauses and accumulates performance metrics using <identifier>
  call perf_region_stop("<identifier>")

  # write arbitrary location in file
  output array(42,42)
  output result(42,42)
  return # performance metrics accumulated in perf_regions using <identifier>
```
### ? VM: should I remove this : Relevant code details
- Codegen
- Job tree
- Scripts (do not modify)
- Libraries

## Further developments
Will be extracted from current [todolist](04_todolist_dev.md)

## (Remove this)
### (For devs)
- (for devs: ``' '`` in output used for ignoring - Fortran already adds spaces everywhere in standard output)
- (compilation uses exports for selecting options. Compiling without any options will use default exports set by Makefiles)