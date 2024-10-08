# Developer info
## Technical report
### READ ME
Do not modify generated files. Beware, VSCode tends to open copied source files when looking for function definitions.

``make`` target binary names contain all information about compilation parameters. The
refore, if modifying generated scripts by hand, one must change the makefile call by changing the target.
This has reliability purposes. Encoding the compilation parameters twice has the advantage of detecting a modification or discrepancy in the scripts or in the makefile.

### Parameters passing
Environment variables are used for everything fixed at compilation.

The parameters that are not fixed at compilation with make are :
- array sizes and loop bounds when benchmarking without size fixed at compilation (``SIZE_AT_COMPILATION`` set to 0)
- number of iterations

All parameters are set in JSON file [``all_benchmark_parameters.json`](../bench/preprocess/all_benchmark_parameters.json) generated by codegen script and can be processed by importing the JSON as a dictionary in python. See postprocess code for reference.

TODO : add a further check to assert that the target in the makefile made from the parameters corresponds to the code-generated target.

### Miscellaneous
- ``' '`` as output prefix used for ignoring non-mule output for Fortran output - Fortran already adds spaces everywhere in standard output
- (compilation uses exports for selecting options. Compiling without any options will use default exports set by Makefiles)

## Checklist for adding new parameters to benchmark
*[preliminary]* marked items should be prioritized for testing new parameter implementation to see if anything breaks.

*[interface]* marked items are not necessary and should be done last, for user experience.

### Source and compilation update
- [preliminary] if compilation parameter
    - in source files: add preprocessor option in targets if at compilation
    - in both [``Makefile``](../bench/Makefile) and [``src/Makefile``](../bench/src/Makefile)
        - update CPPMACROS in CFLAGS with new preprocessor directive
        - add default value as export
- [preliminary] if execution time parameter
    - add parsing in main function of [``main.F90``](../bench/main.F90)
    - TODO: explain this better: add in generated scripts as execution parameter
### Preprocessing update
- [``codegen.py``](../bench/preprocess/codegen.py), [``run_bench_tree.sh``](../bench/preprocess/run_bench_tree.sh) and [``collect_data_csv.sh``](../bench/postprocess/collect_data_csv.sh):
    - update the ``TREE_DEPTH`` parameter in   by adding 1 (one)
    - [``run_bench_tree.sh``](../bench/preprocess/run_bench_tree.sh) and [``collect_data_csv.sh``](../bench/postprocess/): add nested loop depth ( copy code, indent and shift all parameter indexes)
- [``codegen.py``](../bench/preprocess/codegen.py):
    - update dictionaries at the top of the file
    - ``codegen_bench_tree_branch``:
        - [preliminary] add parameter to signature, setting a default value
            - add new export line in bash fstring
            - if the new parameter involves using calculated values like array dimensions, make sure these values are exported or passed to the executable when needed
        - add a layer of folder creation
            - translate the new parameter's values to a suffix using a global dictionary or string manipulation
            - add this suffix to the ``directory`` string and create a corresponding directory on the chosen depth, as was done for other parameters
    - add new parameter as a loop in ``main``, using ``iterator(..)`` function
    - [interface] update the passing of the new parameter by creating an argparse entry and passing the parameter to the newly created parameter of ``codegen_bench_tree_branch`` in [``codegen.py``](../bench/preprocess/codegen.py) in all execution modes.
        - modify the iterator you created above using the argparse entry
    - in the main function, add it to the benchmark metadata .JSON file in the for loops
### Postprocessing update
- increment tree depth in [``collect_data_csv.sh``](../bench/postprocess/collect_data_csv.sh)
- [``collect_data_csv.sh``](../bench/postprocess/):
    - add loop depth and shift all parameter indexes
    - add directory to ``fullpath()`` function
    - process is similar to [``run_bench_tree.sh``](../bench/preprocess/run_bench_tree.sh)
- in [``generate_graph.py``](../bench/postprocess/generate_graph.py), add the new parameter in the dictionaries ``all_metadata_columns``, ``metadata_types``, ``baseline_for_comparison`` and ``format_string`` at the top of the file. Pay attention to having the same naming convention as in [``codegen.py``](../bench/preprocess/codegen.py) (used in .JSON file)

## Checklist for adding new stencil to benchmark
### ``src/`` update
#### add a new preprocessing option
add an entry in 
#### implement kernel
make a new ``.h`` file in [``bench/src/kernels/``](../bench/src/kernels/):
update [``select_kernel_2D.h``](../bench/src/kernels/select_kernel_2D.h) or 3D selector respectively.