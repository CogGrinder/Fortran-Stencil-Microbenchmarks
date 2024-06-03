# Fortran microbenchmarks internship at LJK
The goal is to develop microbenchmarks in Fortran to assess the performance of different finite difference kernels within Fortran

## File structure
``bench/`` subdirectory :
- contains benchmark files

``tuto/`` subdirectory :
- contains hello world and tutorial files used to learn Fortran
## Requirements
Timing libraries
- PAPI
- ``perf_regions`` code annotation library https://github.com/schreiberx/perf_regions, installed in main folder

### Compilation

``Makefile`` compiles all subdirectories, and has options:
- ``run`` to do ``make run`` in all subdirectories, executing the main files and scripts
    - ``run_bench`` and ``run_tuto`` to ``make run`` specifically the bench folder or the tuto folder
- ``clean`` to clean all executable files and temporary files in the subdirectories from the current OS
- set ``PERF_REGIONS=<relative directory of PerfRegions>`` if PerfRegions is not installed in the main folder 
Other options:
- use preprocessing macro ``DEBUG=1`` in ``main.f90`` if you are debugging

## Current roadmap
Done on 05/28 :
- [X] hello world in Fortran
    - [X] global Makefile and ``tuto`` folder containing hello worlds (works on Linux and windows)

Done on 05/30 :
- [ ] write objectives and problematique in ``README.md``
    - more detailed objectives to come after basic functionalities are implemented
    - [X] basic roadmap
- [X] make a first complete "template" benchmark, using simple basic allocation and a simple stencil operation
    - note : will not yet make a benchmark selector switch, all basic imperative programming
    - [X] allocate an array (precise type TBD) randomly and display a value
    - timing not finished as of 05/30, but included ``perf_regions`` in the make compilation

Done on 05/31 :
- [X] import timing library and output time
    - [X] included ``perf_regions`` in the make compilation
    - [X] in the ``make run`` make the output get saved in a ``.csv`` file
- [ ] make a way to have more than one benchmark
    - [X] investigate adding subroutines
    - [ ] implement a second benchmark, array type to be determined
    - [ ] get inspired by Martin's OpenMP benchmarking from the HPC course
- [ ] transform into modules for clearer code organisation

To do on 06/03 :

- [ ] make a way to have more than one benchmark
    - [ ] make a dummy benchmark selector
        - [X] get inspired by Martin's OpenMP benchmarking from the HPC course
    - [ ] implement an actual second benchmark, array type to be determined
- [ ] transform into modules for clearer code organisation