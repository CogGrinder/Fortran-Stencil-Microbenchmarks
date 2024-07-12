Welcome to the documentation files for Fortran Microbenchmarks. The goal here is to make a heuristic overview of performance of stencil operations. It is meant to be consulted as a reference in adjusting implementations to increase performance, when the opportunity cost is low enough for change and maintainance of code.

It is done with AIRSEA's common needs with stencil operations in mind but may be adapted to other kernel operations within Fortran using arrays.

## Our methodology
Our mode of operation is to compare the performance at multiple memory sizes
 - one which is much smaller than the L3 cache on the current machine (about the size of L2)
 - one which is only slightly smaller  to see the effects of cache associativity (#TODO : 1/64th less or a few bytes?)
 - one which is only slightly larger than L3 smaller to see if their is a significant break in performance (#TODO : same decision)
 - one which is much larger than the L3 cache (3x)

We benchmark relative to a baseline CPU computation using all that is commonly effective to optimize with little effort, in other words an "ideally easy" scenario, discussed below. The goal is to measure which tradeoffs are worthwhile. #TODO discuss baseline

### Baseline
Our current baseline is called ``COMPUTATION_2D_MODULE``.
The baseline uses
- dynamic arrays (``allocatable``)
- in-module implementation with same-file computation kernel
- ``contiguous`` arrays #TODO not yet implemented
- no ``reshape``
- double precision

#TODO : for 2D allocate vs static, use module version