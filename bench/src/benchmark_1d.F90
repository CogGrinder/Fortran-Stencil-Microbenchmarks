#include "include/compilation_fixed_parameters.h"

MODULE BENCHMARK_1D
    use perf_regions_fortran
    USE TOOLS
    implicit none
    
    contains
    
    
! to test 1D stencils in a module
SUBROUTINE COMPUTATION_1D_MODULE(bench_id,bench_str,array_len)
    USE TOOLS
    use perf_regions_fortran
#include "perf_regions_defines.h"
    
    ! stencil must be odd length
    integer, dimension(-1:1) :: stencil
    integer(KIND=4), intent(in) :: bench_id
    character(len=7), intent(in) :: bench_str
    integer, intent(in) :: array_len
    real    :: sten_sum
    integer :: sten_len, i, k
#if ALLOC_MODE == ALLOCATABLE
    real(dp), allocatable :: array(:), result(:)
    allocate(array(array_len))
    allocate(result(array_len) , source=0.0_dp)
#elif ALLOC_MODE == STATIC
    real(dp), dimension(array_len) :: array
    real(dp), dimension(array_len) :: result
#else
    real(dp), dimension(array_len) :: array
    real(dp), dimension(array_len) :: result
#endif /*ALLOC_MODE*/

#ifdef DEBUG_PERF
#ifndef NO_PERF_REGIONS
    CALL perf_regions_init()
#endif
#endif

    stencil = (/ 1, 0, 1/)

    CALL stencil_characteristics(stencil,sten_sum,sten_len)

    do i = 1, array_len
        call RANDOM_NUMBER(array(i))
    end do
    
        !!!!!!!! start timing here
#ifndef NO_PERF_REGIONS
    CALL perf_region_start(bench_id, bench_str//achar(0))
#endif

        
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    do i = 1 + sten_len/2, array_len - sten_len/2
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

        

    CALL ANTI_OPTIMISATION_WRITE(array(modulo(42,array_len)))
    CALL ANTI_OPTIMISATION_WRITE(result(modulo(42,array_len)))

end SUBROUTINE COMPUTATION_1D_MODULE

end MODULE