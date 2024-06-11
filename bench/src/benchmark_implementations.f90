! #define DEBUG
#define DEBUG_PERF

#define ARRAY_LEN 1024*128

MODULE benchmark_implementations
    use benchmark_names
    use perf_regions_fortran
    use tools
    implicit none
    
    contains
        SUBROUTINE COMPUTATION_ALLOCATABLE_ARRAY_MODULE(bench_id,bench_str)
            integer, intent(in) :: bench_id
            character(len=7), intent(in) :: bench_str
        end SUBROUTINE COMPUTATION_ALLOCATABLE_ARRAY_MODULE

end MODULE


SUBROUTINE COMPUTATION_ALLOCATABLE_ARRAY_MODULE(bench_id,bench_str)
    use tools
    use perf_regions_fortran
#include "perf_regions_defines.h"
    
    ! stencil must be odd length
    integer, dimension(-1:1) :: stencil
    integer, intent(in) :: bench_id
    character(len=7), intent(in) :: bench_str
    real    :: sten_sum
    integer :: sten_len
    real(dp), allocatable :: array(:), result(:)
    allocate(array(ARRAY_LEN))
    allocate(result(ARRAY_LEN) , source=0.0_dp)

#ifdef DEBUG_PERF
    CALL perf_regions_init()
#endif

    stencil = (/ 1, 0, 1/)

    CALL stencil_characteristics(stencil,sten_sum,sten_len)

    do i = 1, ARRAY_LEN
        call RANDOM_NUMBER(array(i))
    end do
    
        !!!!!!!! start timing here
    CALL perf_region_start(bench_id, bench_str//achar(0))

        
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    do i = 1 + sten_len/2, ARRAY_LEN - sten_len/2
        result(i + sten_len/2) = 0
        do k = -sten_len/2,sten_len/2
            ! TODO : is there a += operator ?
            result(i) = result(i) + stencil(k) * array(i + k)
        end do
        ! normalize by sten_sum
        result(i) = result(i)/sten_sum
    end do
    ! we ignore edges in the computation which explains the shift in indexes

    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    !!!!!!!! end timing here
    CALL perf_region_stop(bench_id)
    
#ifdef DEBUG_PERF
    CALL perf_regions_finalize()
#endif

        

    CALL ANTI_OPTIMISATION_WRITE(array(modulo(42,ARRAY_LEN)))
    CALL ANTI_OPTIMISATION_WRITE(result(modulo(42,ARRAY_LEN)))

end SUBROUTINE COMPUTATION_ALLOCATABLE_ARRAY_MODULE