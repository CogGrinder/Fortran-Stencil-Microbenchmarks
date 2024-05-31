!#define DEBUG

#define MAX_SIZE 1024*1024*128

#define ARRAY_LEN 1024
#ifdef ARRAY_LEN_OVERRIDE
    #define ARRAY_LEN ARRAY_LEN_OVERRIDE
#endif

PROGRAM main
    ! thank you to https://www.tutorialspoint.com/fortran/fortran_arrays.htm

USE perf_regions_fortran

#include "perf_regions_defines.h"

    integer :: iters
    ! stencil must be odd length
    integer, dimension(1:3) :: stencil
    integer :: sten_sum, sten_len
    INTERFACE
        SUBROUTINE TEST_BENCH(iters,stencil)
            integer, dimension(:), intent(in) :: stencil
            integer, intent(in) :: iters
        end SUBROUTINE TEST_BENCH
    end INTERFACE


    iters = 1024
    stencil = (/ 1, 0, 1/)


    !!!!!!!! initialize timing here
    CALL perf_regions_init()

    CALL TEST_BENCH(iters,stencil)

    !!!!!!!! finalize timing here
    CALL perf_regions_finalize()

END PROGRAM main



SUBROUTINE stencil_characteristics(stencil, sum, length)
    integer, dimension(:), intent(in) :: stencil
    integer, intent(out) :: sum, length
    length = size(stencil)
    WRITE(*,*) "length", length
    sum = 0
    do i = 1, length
        sum = sum + stencil(i)
    end do
END SUBROUTINE stencil_characteristics

SUBROUTINE TEST_BENCH(iters,stencil)
    USE perf_regions_fortran
    
    integer, dimension(:), intent(in) :: stencil
    integer, intent(in) :: iters
    integer :: sten_sum, sten_len
    real, dimension(ARRAY_LEN) :: array
    real, dimension(ARRAY_LEN) :: result

    INTERFACE
        SUBROUTINE stencil_characteristics(stencil, sum, length)
            integer, dimension(:), intent(in) :: stencil
            integer, intent(out) :: sum, length
        end SUBROUTINE stencil_characteristics
    end INTERFACE

    CALL stencil_characteristics(stencil,sten_sum,sten_len)

    
    ! example for formatting :
    ! I5 for a 5-digit integer.
    ! F10.4 for a floating-point number with 10 total characters, including 4 digits after the decimal point.
    ! A for a character string.
    ! 100 format(I5, F10.4, A)
    
#ifdef DEBUG
1 format(I2, I2)
#endif

    
    WRITE(*,*) "**************************************"
    WRITE(*,*) "Mem size: ", ARRAY_LEN*0.001*sizeof(real) ," KByte"
    WRITE(*,*) "Iterations: ", iters
    do k = 1, iters
        do i = 1, ARRAY_LEN
            call RANDOM_NUMBER(array(i))
        end do
        
        !!!!!!!! start timing here
        CALL perf_region_start(0, "TEST_BENCH"//achar(0))
        
        
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

        !!!!!!!! end timing here
        CALL perf_region_stop(0)

    end do
    

    PRINT *, 'array(', modulo(42,ARRAY_LEN) , ')', array(modulo(42,ARRAY_LEN))
    
    PRINT *, 'result(', modulo(42,ARRAY_LEN) , ')', result(modulo(42,ARRAY_LEN))
  
end SUBROUTINE TEST_BENCH