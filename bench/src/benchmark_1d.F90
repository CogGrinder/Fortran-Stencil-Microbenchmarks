#include "include/compilation_fixed_parameters.h"

MODULE BENCHMARK_1D
    use perf_regions_fortran
    USE TOOLS
    USE BENCHMARK_PARAMETERS
    implicit none
    
    contains
    
    
! to test 1D stencils in a module
SUBROUTINE COMPUTATION_1D_MODULE(bench_id,bench_str)
    USE TOOLS
    use perf_regions_fortran
    USE BENCHMARK_PARAMETERS
#include "perf_regions_defines.h"
    
    ! stencil must be odd length
    integer, dimension(-1:1) :: stencil
    integer(KIND=4), intent(in) :: bench_id
    character(len=7), intent(in) :: bench_str
    real    :: sten_sum
    integer :: sten_len, i, k
#if ALLOC_MODE == ALLOCATABLE
    real(dp), allocatable :: array(:), result(:)
    allocate(array(n1d))
    allocate(result(n1d) , source=0.0_dp)
#elif ALLOC_MODE == STATIC
    real(dp), dimension(n1d) :: array
    real(dp), dimension(n1d) :: result
#endif /*ALLOC_MODE*/

#ifdef DEBUG_PERF
#ifndef NO_PERF_REGIONS
    CALL perf_regions_init()
#endif
#endif

    stencil = (/ 1, 0, 1/)

    CALL stencil_characteristics(stencil,sten_sum,sten_len)

    do i = 1, n1d
        call RANDOM_NUMBER(array(i))
    end do
    
        !!!!!!!! start timing here
#ifndef NO_PERF_REGIONS
    CALL perf_region_start(bench_id, bench_str)
#endif

        
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    do i = 1 + sten_len/2, n1d - sten_len/2
        result(i + sten_len/2) = 0
        do k = -sten_len/2,sten_len/2
            result(i) = result(i) + stencil(k) * array(i + k)
        end do
        ! normalize by sten_sum
        result(i) = result(i)/sten_sum
    end do
    ! we ignore edges in the computation which explains the shift in indexes

    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    !!!!!!!! end timing here
#ifndef NO_PERF_REGIONS
    CALL perf_region_stop(bench_id)
#endif
    
#ifdef DEBUG_PERF
#ifndef NO_PERF_REGIONS
    CALL perf_regions_finalize()
#endif
#endif

        

CALL ANTI_OPTIMISATION_WRITE(array(5),"array_tmp.txt")
CALL ANTI_OPTIMISATION_WRITE(result(5),"result_tmp.txt")

end SUBROUTINE COMPUTATION_1D_MODULE

end MODULE