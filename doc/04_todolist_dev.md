*[HB]: Hugo Brunie
*[MS]: Martin Schreiber
*[VM]: Vincent Meduski
# TODO list preface
VM: This todolist is structured to help prioritize reliability > high relevance value > low opportunity cost. The current author perceived this as the order of the most desirable features. The tradeoff between high value and low cost determines how prioritised a feature is in practice.
# Reliability
- [ ] No more than couple hours, only on one bench. Check memory with memory checker of valgrind
  - was not possible until recent preprocessing macro ``NO_PERF_REGIONS`` 
# New relevant features
## High value
### Low cost
- [ ] show all compiler optimisations To check compiler optimisations, there is ``-vomp`` or ``-vompgpu`` in [run_bench_tree.sh](../bench/preprocess/run_bench_tree.sh).
- [ ] Steps to check for benchmarks:
    - [ ] Pinning?
        - For single-core executions, you can use, e.g., `taskset -c 0`.
        - For parallel programming model (OpenMP), you need to work with places where you set the places individually. You can find some documentation here: https://docs.oracle.com/cd/E60778_01/html/E60751/goztg.html


    - [ ] Disable frequency scaling (Either with command line tools or permanently)
        - Enable performance mode / or at least try to fix the frequence
            - diable turbo boost:
                - `echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo`
            - Note that it might not be useful if we trash the first iterations anyway
        - disable hyperthreading (= don't use hyperthreading cores for parallel runs):
            - https://serverfault.com/questions/235825/disable-hyperthreading-from-within-linux-no-access-to-bios (might do the trick)
            - https://cloud.ibm.com/docs/vpc?topic=vpc-disabling-hyper-threading

    - [ ] First touch policies required for OpenMP. 
        - Maybe support both options. It's quite tricky... (HB: I don't see the point)
        - Either during dummy setup in parallel (@Hugo looks like best option to me)
        - Or ugly workaround to use initial iteration (HB: I don't get the difference)
### Medium cost
- [ ] higher dimension : 3D arrays
    - only medium cost because mostly involves copy pasting existing code and using already implemented ``DIM`` macro in [``main.F90``](../bench/main.F90), and adding it as an option for [``codegen.py``](../bench/preprocess/codegen.py)
- [ ] kernel fusion : 2 kernels
    - note : probably add as an option, do not include in "all" and use
- [ ] GPU parallel vs CPU parallel
  - [ ] add option to deactivate OpenMp optimisation when not using GPU or as a separate option
### High cost
- [ ] Execute same benchmark multiple times
    - reason for high cost: rethinking [``codegen.py``](../bench/preprocess/codegen.py) ``main`` function and ``codegen_bench_tree_branch`` file structure, circumventing errors from duplicate data in [``generate_graph.py``](../bench/postprocess/generate_graph.py), configuring graphing in a smart way to adapt to available data
    - [ ] E.g, about 10 times (follow your intuition (or statistical quantilles :-) )
    - [ ] Plot average, minimum and maximum values.

## Medium value
### Low cost
- [ ] Add non-module version for GPU
- [ ] Figure improvements
    - [ ] debug sorting bars reliably eg: size in increasing order
### Medium cost
- [ ] pointers to arrays : add as functionality
### High cost
- [ ] Make a web view (https://plotly.com/python/) do not use Dash
    - reason for high cost: translating code, learning curve of plotly, debugging responsiveness and ease of use of UI

## Low value
- [ ] rename kernels from ``.h`` to ``.f90`` files to signify that they are Fortran code without preprocessing