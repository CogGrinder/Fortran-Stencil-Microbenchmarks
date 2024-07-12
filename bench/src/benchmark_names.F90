MODULE BENCHMARK_NAMES
    implicit none
    ! Determines the order of the output
    ! All benchmark identifiers need to be unique
    ! see https://pages.mtu.edu/~shene/COURSES/cs201/NOTES/chap02/param.html
    integer, parameter :: BENCH_FIXED_ARRAY = 0
    integer, parameter :: BENCH_ALLOCATABLE_ARRAY = 1
    integer, parameter :: BENCH_ALLOCATABLE_ARRAY_MODULE = 2
    
    integer, parameter :: BENCH_2D_CPU_JI = 3
    integer, parameter :: BENCH_2D_CPU_IJ = 4
    integer, parameter :: BENCH_2D_CPU_MODULE_STATIC = 5
    integer, parameter :: BENCH_2D_CPU_MODULE = 6
    
    integer, parameter :: BENCH_2D_GPU_OMP_BASE = 7

    ! mode numbering
    ! modes up to 99 are number of Mb
    integer, parameter :: smaller_than_l3           = 100
    integer, parameter :: slightly_smaller_than_l3  = 101
    integer, parameter :: slightly_bigger_than_l3   = 102
    integer, parameter :: bigger_than_l3            = 103
    ! see benchmark_parameters.F90 for usage in practice

END MODULE BENCHMARK_NAMES