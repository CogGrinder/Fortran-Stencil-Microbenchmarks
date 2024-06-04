#define DEBUG

#define ARRAY_LEN 1024

MODULE benchmark_implementations
    use benchmark_names
    use perf_regions_fortran
    implicit none
    
    contains
        SUBROUTINE TEST_COMPUTATION_0(bench_id,bench_str)
            integer, intent(in) :: bench_id
            character(len=7), intent(in) :: bench_str
        end SUBROUTINE TEST_COMPUTATION_0
        SUBROUTINE TEST_COMPUTATION_1()
        end SUBROUTINE TEST_COMPUTATION_1

end MODULE


SUBROUTINE TEST_COMPUTATION_0(bench_id,bench_str)
    use tools
    use perf_regions_fortran
#include "perf_regions_defines.h"
    
    ! stencil must be odd length
    integer, dimension(1:3) :: stencil
    integer, intent(in) :: bench_id
    character(len=7), intent(in) :: bench_str
    integer :: sten_sum, sten_len
    real, dimension(ARRAY_LEN) :: array
    real, dimension(ARRAY_LEN) :: result

    stencil = (/ 1, 0, 1/)

    CALL stencil_characteristics(stencil,sten_sum,sten_len)

    do i = 1, ARRAY_LEN
        call RANDOM_NUMBER(array(i))
    end do
    
#ifdef DEBUG
    ! example for formatting :
    ! I5 for a 5-digit integer.
    ! F10.4 for a floating-point number with 10 total characters, including 4 digits after the decimal point.
    ! A for a character string.
    ! 100 format(I5, F10.4, A)
    1 format(I2, I2)
#endif
    write (*,*) 'TIMING START'

        !!!!!!!! start timing here
    CALL perf_region_start(bench_id, bench_str//achar(0))

        
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    do i = 1, ARRAY_LEN-sten_len+1
        result(i + sten_len/2) = 0
        do j = 1,sten_len
#ifdef DEBUG
        write(6, 1, advance="no") j, i-sten_len/2 + j
#endif
            ! TODO : is there a += operator ?
            result(i + sten_len/2) = result(i + sten_len/2) + stencil(j) * array(i-sten_len/2 + j)
        end do
#ifdef DEBUG        
    write(*,*) " at index " , i + sten_len/2
#endif
    end do
    ! we ignore edges in the computation which explains the shift in indexes

    ! normalize by sten_sum
    do i = 1, ARRAY_LEN
        result(i) = result(i)/sten_sum
    end do
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    !!!!!!!! end timing here
    CALL perf_region_stop(bench_id)

        

    PRINT *, 'array(', modulo(42,ARRAY_LEN) , ')', array(modulo(42,ARRAY_LEN))
    
    PRINT *, 'result(', modulo(42,ARRAY_LEN) , ')', result(modulo(42,ARRAY_LEN))

end SUBROUTINE
SUBROUTINE TEST_COMPUTATION_1()
end SUBROUTINE