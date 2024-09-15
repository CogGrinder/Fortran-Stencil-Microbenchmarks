Welcome to the documentation files for Fortran Microbenchmarks.

## Our methodology

We aim to study empirically the performance of programming choices on our stencil operation benchmarks.

We benchmark relative to a baseline (default: CPU) computation using all our perceived common practices used for optimizing in Fortran, in other words an ideal scenario, discussed below. The goal is to measure which tradeoffs are worth taking.

Once results are generated, it is meant to be consulted as reference in adjusting implementations to increase performance, when the opportunity cost is low enough for change and maintainance of code.

It is done with AIRSEA's common needs with stencil operations in mind but may be adapted to other kernel operations within Fortran using arrays.

### Baseline
The default baseline benchmark is
- dynamic arrays (``allocatable``)
- in-module implementation with same-file computation kernel
- ``contiguous`` arrays #TODO not yet implemented
- no ``reshape``
- double precision
- size 3 kernel