# Fortran microbenchmarks internship at LJK
The goal is to develop microbenchmarks in Fortran to assess the performance of different finite difference kernels within Fortran

## File structure
``bench/`` subdirectory :
- contains benchmark files

``tuto/`` subdirectory :
- contains hello world and tutorial files used to learn Fortran

### Compilation

``Makefile`` compiles all subdirectories, and has options:
- ``run`` to do ``make run`` in all subdirectories, executing the main files and scripts
    - ``run_bench`` and ``run_tuto`` to ``make run`` specifically the bench folder or the tuto folder
- ``clean`` to clean all executable files and temporary files in the subdirectories from the current OS
- use preprocessing macro ``DEBUG=1`` in ``main.f90`` if you are debugging

## Current roadmap
Done on 05/28 :
- [X] hello world in Fortran
    - [X] global Makefile and ``tuto`` folder containing hello worlds (works on Linux and windows)

To do on 05/30 :
- [ ] write objectives and problematique in ``README.md``
    - [X] basic roadmap
- [X] make a first complete "template" benchmark, using simple basic allocation and a simple stencil operation
    - note : will not yet make a benchmark selector switch, all basic imperative programming
    - [X] allocate an array (precise type TBD) randomly and display a value
    - [ ] import timing library and output time
        - [ ] in the ``make run`` make the output get saved in a ``.csv`` file