MODULE benchmark_names
    implicit none
    ! Determines the order of the output
    ! All benchmark identifiers need to be unique
    ! see https://pages.mtu.edu/~shene/COURSES/cs201/NOTES/chap02/param.html
    integer, parameter :: BENCH_FIXED_ARRAY = 0
    integer, parameter :: BENCH_ALLOCATABLE_ARRAY = 1
    integer, parameter :: BENCH_ALLOCATABLE_ARRAY_MODULE = 2
    integer, parameter :: BENCH_2D_CPU_JI = 3
    integer, parameter :: BENCH_2D_CPU_IJ = 4
    integer, parameter :: BENCH_2D_CPU_MODULE = 5
    integer, parameter :: BENCH_2D_GPU_OMP_BASE = 6
END MODULE benchmark_names