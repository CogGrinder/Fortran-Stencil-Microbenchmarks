!#define DEBUG



#define MAX_SIZE 1024*1024*128

#define ARRAY_LEN 1024

#ifdef ARRAY_LEN_OVERRIDE
    #define ARRAY_LEN ARRAY_LEN_OVERRIDE
#endif

PROGRAM main
    ! thank you to https://www.tutorialspoint.com/fortran/fortran_arrays.htm

    USE perf_regions_fortran
    use tools
    USE benchmark_names

#include "perf_regions_defines.h"

    integer :: iters
    integer :: bench_id
    character(len=32) :: arg
    character(len=7) :: bench_str


    INTERFACE
        SUBROUTINE BENCH_SKELETON(iters,bench_id,bench_str)
            integer, intent(in) :: iters, bench_id
            character(len=7), intent(in) :: bench_str
        end SUBROUTINE BENCH_SKELETON
    end INTERFACE
    
    ! getting the variant of the benchmark from the command line
    ! see https://gcc.gnu.org/onlinedocs/gfortran/GET_005fCOMMAND_005fARGUMENT.html


    iters = 1024
    ! stencil = (/ 1, 0, 1/)


    !!!!!!!! initialize timing here
    CALL perf_regions_init()

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
                CALL BENCH_SKELETON(iters, bench_id, bench_str)
            case (TEST_BENCH_1)
                bench_str = 'BENCH_1'
                CALL BENCH_SKELETON(iters, bench_id, bench_str)
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
    use benchmark_implementations
    
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