! #define DEBUG



#define MAX_SIZE 1024*1024*128

#define ARRAY_LEN  10
! 1024*128
#define ITERS 1

#ifdef ARRAY_LEN_OVERRIDE
    #define ARRAY_LEN ARRAY_LEN_OVERRIDE
#endif

PROGRAM main
    ! thank you to https://www.tutorialspoint.com/fortran/fortran_arrays.htm

    USE perf_regions_fortran
    use tools
    USE benchmark_names

#include "perf_regions_defines.h"

    ! integer :: iters
    integer :: bench_id
    character(len=32) :: arg
    character(len=7) :: bench_str


    INTERFACE
        SUBROUTINE BENCH_SKELETON(iters,bench_id,bench_str)
            integer, intent(in) :: iters, bench_id
            character(len=7), intent(in) :: bench_str
        end SUBROUTINE BENCH_SKELETON
        SUBROUTINE ANTI_OPTIMISATION_WRITE(written)
            real, intent(in) :: written
        end SUBROUTINE ANTI_OPTIMISATION_WRITE
        SUBROUTINE WARMUP_COMPUTATION(sten_len)
            integer, intent(in) :: sten_len
        end SUBROUTINE WARMUP_COMPUTATION
        SUBROUTINE TEST_COMPUTATION_0(bench_id,bench_str)
            integer, intent(in) :: bench_id
            character(len=7), intent(in) :: bench_str
        end SUBROUTINE TEST_COMPUTATION_0
        SUBROUTINE TEST_COMPUTATION_1()
        end SUBROUTINE TEST_COMPUTATION_1
    end INTERFACE
    
    ! getting the variant of the benchmark from the command line
    ! see https://gcc.gnu.org/onlinedocs/gfortran/GET_005fCOMMAND_005fARGUMENT.html


    ! iters = 1024
    ! stencil = (/ 1, 0, 1/)


    !!!!!!!! initialize timing here
    CALL perf_regions_init()
    
    CALL WARMUP_COMPUTATION(3)

    i = 1
    do
        call get_command_argument(i,arg)
        if (len_trim(arg) == 0) then
            exit
        else
            read(arg,*) bench_id
        endif

        write (*,*) 'Calling benchmark of id ', bench_id
        
        ! see https://pages.mtu.edu/~shene/COURSES/cs201/NOTES/chap03/select
        select case (bench_id)
            case (TEST_BENCH_0)
                bench_str = 'BENCH_0'
                CALL BENCH_SKELETON(ITERS, bench_id, bench_str)
            case (TEST_BENCH_1)
                bench_str = 'BENCH_1'
                CALL BENCH_SKELETON(ITERS, bench_id, bench_str)
            case DEFAULT
                write (*,*) 'Error: no such benchmark'
        end select
        i = i + 1
    end do
    !!!!!!!! finalize timing here
    CALL perf_regions_finalize()

END PROGRAM main



SUBROUTINE BENCH_SKELETON(iters,bench_id,bench_str)
    USE perf_regions_fortran
    USE benchmark_names
    ! use benchmark_implementations
    
    integer, intent(in) :: iters, bench_id
    character(len=7), intent(in) :: bench_str
    integer :: sten_sum, sten_len

    write (*,*) 'Running bench ', bench_str, '...'
    WRITE(*,*) "**************************************"
    WRITE(*,*) "Mem size: ", ARRAY_LEN*0.001*sizeof(real) ," KByte"
    WRITE(*,*) "Iterations: ", iters
    do k = 1, iters
        select case (bench_id)
            case (TEST_BENCH_0)
                CALL TEST_COMPUTATION_0(bench_id, bench_str)
            case (TEST_BENCH_1)
                CALL TEST_COMPUTATION_0(bench_id, bench_str)
            case DEFAULT
                write (*,*) 'Error: no such benchmark'
        end select
    end do
  
end SUBROUTINE BENCH_SKELETON

SUBROUTINE WARMUP_COMPUTATION(sten_len)
    integer, intent(in) :: sten_len
    real, dimension(ARRAY_LEN) :: array
    real, dimension(ARRAY_LEN) :: result

    do i = 1, ARRAY_LEN
        call RANDOM_NUMBER(array(i))
    end do

    do i = 1 + sten_len/2, ARRAY_LEN - sten_len/2
        result(i + sten_len/2) = 0
        do j = 1,sten_len

            ! TODO : is there a += operator ?
            result(i) = result(i) + array(i-sten_len/2 -1 + j)
        end do

    end do
    ! we ignore edges in the computation which explains the shift in indexes

    ! normalize by sten_sum
    do i = 1, ARRAY_LEN
        result(i) = result(i)/sten_sum
    end do

end SUBROUTINE WARMUP_COMPUTATION

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
        !!!!!!!! start timing here
    CALL perf_region_start(bench_id, bench_str//achar(0))

        
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    do i = 1 + sten_len/2, ARRAY_LEN - sten_len/2
        result(i + sten_len/2) = 0
        do j = 1,sten_len
#ifdef DEBUG
        write(6, 1, advance="no") j, i-sten_len/2 -1 + j
#endif
            ! TODO : is there a += operator ?
            result(i) = result(i) + stencil(j) * array(i-sten_len/2 -1 + j)
        end do
#ifdef DEBUG        
    write(*,*) " at index " , i
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

        

    CALL ANTI_OPTIMISATION_WRITE(array(modulo(42,ARRAY_LEN)))
    CALL ANTI_OPTIMISATION_WRITE(result(modulo(42,ARRAY_LEN)))

end SUBROUTINE
SUBROUTINE TEST_COMPUTATION_1()
end SUBROUTINE

SUBROUTINE ANTI_OPTIMISATION_WRITE(written)
    implicit none
    real, intent(in) :: written
    integer :: descriptor
    character(len=42) :: filename

    filename = 'output.txt'
    descriptor = 42

    open(unit=descriptor, file=filename, status='unknown')
    write(descriptor,*) written
    close(descriptor)

end SUBROUTINE ANTI_OPTIMISATION_WRITE