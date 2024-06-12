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

### Notes on CUDA compilation with OpenMP
According to IDRIS at page http://www.idris.fr/media/formations/openacc/openmp_gpu_idris_c.pdf , the right way to compile is with nvidia's HPC SDK :
``nvfortran -mp=gpu -gpu=sm_75 -o test test.f90``

Replace ``sm_75`` in ``-gpu=sm_75`` by your gpu's name (see https://arnon.dk/matching-sm-architectures-arch-and-gencode-for-various-nvidia-cards/)

To compile, use NVidia's HPC SDK, see installation guide at https://docs.nvidia.com/hpc-sdk//hpc-sdk-install-guide/index.html and https://developer.nvidia.com/hpc-sdk-downloads
- In ``make``, use the following :
```makefile
NVARCH=Linux_x86_64
NVRELEASE=24.5
export NVARCH
NVCOMPILERS=/opt/nvidia/hpc_sdk
export NVCOMPILERS
export MANPATH:=$(MANPATH):$(NVCOMPILERS)/$(NVARCH)/$(NVRELEASE)/compilers/man
export PATH:=$(NVCOMPILERS)/$(NVARCH)/$(NVRELEASE)/compilers/bin:$(PATH)
export PATH:=/usr/local/cuda:/usr/local/cuda/bin:$(PATH)
export LD_LIBRARY_PATH:=/usr/local/cuda:/usr/local/cuda/lib:$(LD_LIBRARY_PATH)
```
/usr/share/keyrings/ is the directory for signature of nvidia repos. Need to remove https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64 from ``/etc/apt/sources.list.d/`` to prevent downloading of wrong Ubuntu 18 repo

If you have trouble installing the right cuda and cuda-drivers, go see https://forums.developer.nvidia.com/t/ubuntu-install-specific-old-cuda-drivers-combo/214601/5

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

Done on 06/03 :

- [X] make a way to have more than one benchmark
    - [X] make a dummy benchmark selector
        - [X] get inspired by Martin's OpenMP benchmarking from the HPC course
        - [X] implement a selector at execution time - note : must set selection of benchmarks in ``run_benches.sh``
- [ ] transform into modules for clearer code organisation
    - [X] make a ``tools`` module
    - [X] make a ``.a`` library
    - [ ] make a module for benchmarks
    note : module aborted 06/04 because of bad linking with ``perf_regions``, all subroutines are in mainfile

Done on 06/04 :
- [ ] implement an actual second benchmark, array type to be determined
    - [X] implement a library version of 2 dummy benchmarks
        - [X] decide : do we make different versions of the computation in a module and insert it into the SUBROUTINE TEST_BENCH - renamed BENCHMARK ?
        - answer : module does not work, going back to main.f90
- [ ] fix bench
    - [X] fix stencil
    - [ ] fix "preheating" cache and check constant results
        - [X] attempted fix that uses fixed stencil size in a computation - may be improved upon, L3 PAPI misses still irregular at 128*1024 size and 1024 iterations
    - [ ] sanity check, especially if preheating cache does not work
        - [ ] implement 2D bench
- [ ] -> once bench is fixed, do the allocatable version of the baseline code

Done on 06/05 :
- [ ] fix bench
    - [X] fix stencil
        - [X] check in MG code 
    - [ ] fix "preheating" cache and check constant results
        - [X] attempted fix that uses fixed stencil size in a computation - may be improved upon, L3 PAPI misses still irregular at 128*1024 size and 
        1024 iterations
        - [X] -> current version still has irregular L3 PAPI misses but by no more than a factor of 2 it seems. Maybe increasing iterations and making longer benchmarks will help with smoothing out data
            - [ ] proposed : make a flush_L3 function that allocates big enough data and uses L3 cache entirely
    - [X] sanity check, especially if preheating cache does not work
        - [X] implement 2D bench in ij and ji variant
- [X] -> once bench is fixed, do the allocatable version of the baseline code
    - [X] Utiliser les allocatable (declaration allocatable puis allocate) pour
comparer les resultats de performance aux allocations statiques (ce qui
est deja present dans le code)
    - [ ] -> to go further, make a python script that parses and plots the comparison data
- [ ] documenter les differents bench et donner des noms explicites aux bench
    - [X] better naming
    - [X] more clear passing of number of iterations
    - [ ] documentation
- [ ] retry module implementation
    - [ ] use ``library_base.a`` for compilation before making ``library.a``
    - [X] compilation and execution
    - [ ] find out why the ``perf_regions`` is not working


To do on 07/05 :
- [ ] investigate GPU computation

### Objectives from discussion on the 06/04
- [X] Comme convenu il serait interessant de modifier le code de stencil
pour qu'il "ressemble" au code de stencil classique:

    - [X] piece jointe NPB code MG - Multi-Grid on a sequence of meshes,
long- and short-distance communication, memory intensive

- [X] Utiliser les allocatable (declaration allocatable puis allocate) pour
comparer les resultats de performance aux allocations statiques (ce qui
est deja present dans le code)

- [ ] Verifier qu'en "chauffant" le cache on obtient des resultats plus
constant.

- [X] Chercher a modifier le bench pour obtenir des valeur de cache miss
differente et expliquer la difference (sanity check with 2d ij and ji variants
)

- [ ] documenter les differents bench et donner des noms explicites aux bench

### Nice-to-have features
- [ ] use ``call cpu_time(e)`` to make alternative timing code for non-PAPI systems