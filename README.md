# Fortran microbenchmarks internship at LJK
The goal is to develop microbenchmarks in Fortran to assess the performance of different finite difference kernels within Fortran
## Documentation
See [documentation markdown file](doc/main.md) for further details.

### [0 - Introduction to Fortran Microbenchmarks](doc/00_introduction.md)
### [1 - Installation](doc/01_installation.md)
### [2 - Notes for users](doc/02_user.md)
### [3 - Notes for devs](doc/03_dev.md)

For further developments to come, see [TODOlist](doc/04_todolist_dev.md)
For a full summary made for a presentation, see [summary](doc/05_full_presentation.md)

## File structure
``bench/`` subdirectory :
- contains benchmark files
    - ``preprocess/`` contains a codegen Python script and a Bash script to generate the benchmark variation tree and its output data

``doc/`` subdirectory :
- contains documentation

``bench/src/perf_regions/`` subdirectory :
- contains necessary files from eponymous library (see [requirements](#requirements))

``tuto/`` subdirectory :
- contains hello world and tutorial files used to learn Fortran

## Requirements
Timing libraries
- PAPI
- ``perf_regions`` code annotation library https://github.com/schreiberx/perf_regions, installed in main folder

### Compilation

``Makefile`` compiles all subdirectories, and has options:
- ``preprocessing`` or ``pre`` to run preprocessing scripts that execute all relevant benchmark variations in the generated benchmark variation tree
- ``run`` to do ``make run`` in all subdirectories, executing the main files and scripts
    - ``run_bench`` and ``run_tuto`` to ``make run`` specifically the bench folder or the tuto folder
- ``clean`` to clean all executable files and temporary files in the subdirectories from the current OS
- set ``PERF_REGIONS=<relative directory of PerfRegions>`` if PerfRegions is moved
Other options:
- use preprocessing macro ``DEBUG=1`` in ``main.F90`` if you are debugging

### Notes on CUDA compilation with OpenMP
The right way to compile CUDA code with OpenMP is with nvidia's HPC SDK as other solutions lack reliable support as of 2024, due to the proprietary nature of CUDA (see IDRIS at page http://www.idris.fr/media/formations/openacc/openmp_gpu_idris_c.pdf)

See installation guide at https://docs.nvidia.com/hpc-sdk//hpc-sdk-install-guide/index.html and https://developer.nvidia.com/hpc-sdk-downloads

If you have trouble installing the right cuda and cuda-drivers, go see https://forums.developer.nvidia.com/t/ubuntu-install-specific-old-cuda-drivers-combo/214601/5

An example compilation is as follows :
``nvfortran -mp=gpu -gpu=sm_75 -o foo foo.F90``
Replace ``sm_75`` in ``-gpu=sm_75`` by your gpu's name (see https://arnon.dk/matching-sm-architectures-arch-and-gencode-for-various-nvidia-cards/)

- In ``make``, use the following lines :
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
Change the NVRELEASE line as well as the NVARCH as needed.