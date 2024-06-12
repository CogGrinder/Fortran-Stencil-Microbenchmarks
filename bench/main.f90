! #define DEBUG


! #define MAX_SIZE 1024*1024*128

! #define ARRAY_LEN  10
#define ARRAY_LEN 1024
! #define ITERS 1
#define ITERS 1024
#define FLEXIBLE_STENCIL 0

#ifdef array_len_OVERRIDE
    #define array_len array_len_OVERRIDE
#endif

PROGRAM main
    ! thank you to https://www.tutorialspoint.com/fortran/fortran_arrays.htm
    USE perf_regions_fortran
    use tools
    USE benchmark_names
    USE benchmark_implementations

#include "perf_regions_defines.h"
    implicit none

    ! integer :: iters
    integer(KIND=4) :: bench_id
    integer :: k,i,iters,array_len
    character(len=32) :: arg
    character(len=7) :: bench_str
    
    
    INTERFACE
        SUBROUTINE BENCH_SKELETON(iters,bench_id,bench_str, array_len)
            integer, intent(in) :: iters, array_len
            integer(KIND=4), intent(in) :: bench_id
            character(len=7), intent(in) :: bench_str
        end SUBROUTINE BENCH_SKELETON
        SUBROUTINE WARMUP_COMPUTATION(sten_len, array_len)
            integer, intent(in) :: sten_len, array_len
        end SUBROUTINE WARMUP_COMPUTATION
        SUBROUTINE COMPUTATION_FIXED_ARRAY(bench_id,bench_str, array_len)
            integer, intent(in) :: array_len
            integer(KIND=4), intent(in) :: bench_id
            character(len=7), intent(in) :: bench_str
        end SUBROUTINE COMPUTATION_FIXED_ARRAY
        SUBROUTINE COMPUTATION_ALLOCATABLE_ARRAY(bench_id,bench_str, array_len)
            integer, intent(in) :: array_len
            integer(KIND=4), intent(in) :: bench_id
            character(len=7), intent(in) :: bench_str
        end SUBROUTINE COMPUTATION_ALLOCATABLE_ARRAY
        SUBROUTINE COMPUTATION_2D_JI(bench_id,bench_str, array_len)
            integer, intent(in) :: array_len
            integer(KIND=4), intent(in) :: bench_id
            character(len=7), intent(in) :: bench_str
        end SUBROUTINE COMPUTATION_2D_JI
        SUBROUTINE COMPUTATION_2D_IJ(bench_id,bench_str, array_len)
            integer, intent(in) :: array_len
            integer(KIND=4), intent(in) :: bench_id
            character(len=7), intent(in) :: bench_str
        end SUBROUTINE COMPUTATION_2D_IJ
    end INTERFACE
    
    ! getting the variant of the benchmark from the command line
    ! see https://gcc.gnu.org/onlinedocs/gfortran/GET_005fCOMMAND_005fARGUMENT.html


    iters = ITERS
    array_len = ARRAY_LEN

    !!!!!!!! initialize timing here
CALL perf_regions_init()
    
    CALL WARMUP_COMPUTATION(3,array_len)

    ! DEBUG VERSION : HARD CODED CALLS TO BENCHMARKS
    
    bench_str = '1D_FIXD'
    WRITE(*,*) "Iterations: ", iters
    do k = 1, iters
        CALL perf_region_start(99, "ITERS"//achar(0))
        CALL COMPUTATION_FIXED_ARRAY(0, bench_str, array_len)
        CALL perf_region_stop(99) !FOOA
    end do
    bench_str = '1D_ALOC'
    WRITE(*,*) "Iterations: ", iters
    do k = 1, iters
        CALL COMPUTATION_ALLOCATABLE_ARRAY(2, bench_str, array_len)
    end do
    bench_str = 'MODULE'
    WRITE(*,*) "Iterations: ", iters
    do k = 1, iters
        CALL COMPUTATION_ALLOCATABLE_ARRAY_MODULE(3, bench_str, array_len)
    end do
    bench_str = '2D_JI'
    WRITE(*,*) "Iterations: ", iters
    do k = 1, iters
        CALL COMPUTATION_2D_JI(4, bench_str, array_len)
    end do
    bench_str = '2D_IJ'
    WRITE(*,*) "Iterations: ", iters
    do k = 1, iters
        CALL COMPUTATION_2D_IJ(5, bench_str, array_len)
    end do

    ! PREVIOUSLY : READ FROM COMMAND LINE ARGUMENTS
    ! i = 1
    ! do
    !     call get_command_argument(i,arg)
    !     ! condition to leave do loop
    !     if (len_trim(arg) == 0) then
    !         exit
    !     else if (index(arg, 'iters=') == 1) then
    !         write(*,*) arg
    !         CALL get_key_value(arg,iters)            
    !     else
    !         read(arg,*) bench_id
    
    !         WRITE(*,*) "**************************************"
    !         WRITE(*,*) "**************************************"

    !         write (*,*) 'Calling benchmark of id ', bench_id
            
    !         ! see https://pages.mtu.edu/~shene/COURSES/cs201/NOTES/chap03/select
    !         select case (bench_id)
    !             case (BENCH_FIXED_ARRAY)
    !                 bench_str = '1D_FIXD'
    !             case (BENCH_ALLOCATABLE_ARRAY)
    !                 bench_str = '1D_ALOC'
    !             case(BENCH_2D_JI)
    !                 bench_str = '2D_JI'
    !             case(BENCH_2D_IJ)
    !                 bench_str = '2D_IJ'
    !             case (BENCH_ALLOCATABLE_ARRAY_MODULE)
    !                 bench_str = 'MODULE'
    !             case DEFAULT
    !                 bench_str = 'ERROR'
    !                 write (*,*) 'Error: no such benchmark'
    !         end select
    !         if ( .not. bench_str .eq. 'ERROR') then
    !             CALL BENCH_SKELETON(iters, bench_id, bench_str, array_len)
    !         end if
    !     endif
    !     i = i + 1
    ! end do

    !!!!!!!! finalize timing here
CALL perf_regions_finalize()

END PROGRAM main



SUBROUTINE BENCH_SKELETON(iters,bench_id,bench_str, array_len)
USE perf_regions_fortran
USE benchmark_names
#include "perf_regions_defines.h"
    use benchmark_implementations
    
    integer, intent(in) :: iters
    integer(KIND=4), intent(in) :: bench_id
    character(len=7), intent(in) :: bench_str
    integer, intent(in) :: array_len


    write (*,*) 'Running bench ', bench_str, '...'
    WRITE(*,*) "**************************************"
    WRITE(*,*) "Mem size: ", array_len*0.001*sizeof(real) ," KByte"
    WRITE(*,*) "Iterations: ", iters
    do k = 1, iters
        CALL perf_region_start(99, "ITERS"//achar(0))
        select case (bench_id)
            case (BENCH_FIXED_ARRAY)
                CALL COMPUTATION_FIXED_ARRAY(bench_id, bench_str, array_len)
            case (BENCH_ALLOCATABLE_ARRAY)
                CALL COMPUTATION_ALLOCATABLE_ARRAY(bench_id, bench_str, array_len)
            case (BENCH_2D_JI)
                CALL COMPUTATION_2D_JI(bench_id, bench_str, array_len)
            case (BENCH_2D_IJ)
                CALL COMPUTATION_2D_IJ(bench_id, bench_str, array_len)
            case (BENCH_ALLOCATABLE_ARRAY_MODULE)
                CALL COMPUTATION_ALLOCATABLE_ARRAY_MODULE(bench_id, bench_str, array_len)
            case DEFAULT
                write (*,*) 'Error: no such benchmark'
        end select
        CALL perf_region_stop(99) !FOOA
    end do
  
end SUBROUTINE BENCH_SKELETON

SUBROUTINE WARMUP_COMPUTATION(sten_len, array_len)
    integer, intent(in) :: sten_len, array_len
    real, dimension(array_len) :: array
    real, dimension(array_len) :: result

    do i = 1, array_len
        call RANDOM_NUMBER(array(i))
    end do

    do i = 1 + sten_len/2, array_len - sten_len/2
        result(i + sten_len/2) = 0
        do j = 1,sten_len

            result(i) = result(i) + array(i-sten_len/2 -1 + j)
        end do

    end do
    ! we ignore edges in the computation which explains the shift in indexes

    ! normalize by sten_sum
    do i = 1, array_len
        result(i) = result(i)/sten_sum
    end do

end SUBROUTINE WARMUP_COMPUTATION

SUBROUTINE COMPUTATION_FIXED_ARRAY(bench_id,bench_str, array_len)
use perf_regions_fortran
use tools
#include "perf_regions_defines.h"
    
    ! stencil must be odd length
    integer, dimension(1:3) :: stencil
    integer(KIND=4), intent(in) :: bench_id
    character(len=7), intent(in) :: bench_str
    integer, intent(in) :: array_len
    real    :: sten_sum
    integer :: sten_len
    real(dp), dimension(array_len) :: array
    real(dp), dimension(array_len) :: result

    stencil = (/ 1, 0, 1/)

    CALL stencil_characteristics(stencil,sten_sum,sten_len)

    do i = 1, array_len
        call RANDOM_NUMBER(array(i))
    end do
        !!!!!!!! start timing here
CALL perf_region_start(bench_id, bench_str//achar(0))

        
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    do i = 1 + sten_len/2, array_len - sten_len/2
        result(i + sten_len/2) = 0
        do k = 1,sten_len
#ifdef DEBUG
        write(6, 1, advance="no") k, i-sten_len/2 -1 + k
#endif
            result(i) = result(i) + stencil(k) * array(i-sten_len/2 -1 + k)
        end do
        ! normalize by sten_sum
        result(i) = result(i)/sten_sum
    end do
    ! we ignore edges in the computation which explains the shift in indexes

    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    !!!!!!!! end timing here
CALL perf_region_stop(bench_id)

        

    CALL ANTI_OPTIMISATION_WRITE(array(modulo(42,array_len)))
    CALL ANTI_OPTIMISATION_WRITE(result(modulo(42,array_len)))

end SUBROUTINE COMPUTATION_FIXED_ARRAY

SUBROUTINE COMPUTATION_ALLOCATABLE_ARRAY(bench_id,bench_str, array_len)
    use tools
    use perf_regions_fortran
#include "perf_regions_defines.h"
    
    ! stencil must be odd length
    integer, dimension(-1:1) :: stencil
    integer(KIND=4), intent(in) :: bench_id
    character(len=7), intent(in) :: bench_str
    integer, intent(in) :: array_len
    real    :: sten_sum
    integer :: sten_len
    real(dp), allocatable :: array(:), result(:)
    allocate(array(array_len))
    allocate(result(array_len) , source=0.0_dp)

    stencil = (/ 1, 0, 1/)

    CALL stencil_characteristics(stencil,sten_sum,sten_len)

    do i = 1, array_len
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
    do i = 1 + sten_len/2, array_len - sten_len/2
        result(i + sten_len/2) = 0
        do k = -sten_len/2,sten_len/2
#ifdef DEBUG
        write(6, 1, advance="no") k, i + k
#endif
            result(i) = result(i) + stencil(k) * array(i + k)
        end do

        ! normalize by sten_sum
        result(i) = result(i)/sten_sum
    end do
    ! we ignore edges in the computation which explains the shift in indexes

    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !!!!!!!! end timing here
    CALL perf_region_stop(bench_id)

        

    CALL ANTI_OPTIMISATION_WRITE(array(modulo(42,array_len)))
    CALL ANTI_OPTIMISATION_WRITE(result(modulo(42,array_len)))

end SUBROUTINE COMPUTATION_ALLOCATABLE_ARRAY

SUBROUTINE COMPUTATION_2D_JI(bench_id,bench_str, array_len)
    use tools
    use perf_regions_fortran
    use benchmark_parameters
#include "perf_regions_defines.h"
    
    ! stencil must be odd length
    integer, dimension(-1:1,-1:1) :: stencil
    integer(KIND=4), intent(in) :: bench_id
    character(len=7), intent(in) :: bench_str
    integer, intent(in) :: array_len
    real    :: sten_sum
    integer :: sten_len
    ! 2D arrays
    real(dp), allocatable :: array(:,:), result(:,:)
    allocate(array(nx,ny))
    allocate(result(nx,ny) , source=0.0_dp)

    stencil = reshape((/ 0, 1, 0, &
&                        1, 1, 1, &
&                        0, 1, 0/), shape(stencil))
    ! must be written in transpose form to fit column-wise specifications

    CALL stencil_characteristics_2D(stencil,sten_sum,sten_len)
#ifdef DEBUG
    write(*,*) stencil, sten_sum, sten_len
#endif

    do j = 1, ny
        do i = 1, nx
            array(i,j) = (i-1)*ny + j
            result(i,j) = (i-1)*ny + j
            ! call RANDOM_NUMBER(array(i,j))
        end do
    end do
    
#ifdef DEBUG
    ! example for formatting :
    ! I5 for a 5-digit integer.
    ! F10.4 for a floating-point number with 10 total characters, including 4 digits after the decimal point.
    ! A for a character string.
    ! 100 format(I5, F10.4, A)
    2 format(I4, I2, I2, I2)
#endif
        !!!!!!!! start timing here
    CALL perf_region_start(bench_id, bench_str//achar(0))

        
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    do j = 1 + sten_len/2, ny - sten_len/2
        do i = 1 + sten_len/2, nx - sten_len/2
#if FLEXIBLE_STENCIL
            do k_2 = -sten_len/2 ,sten_len/2
                do k_1 = -sten_len/2 ,sten_len/2
# ifdef DEBUG
                    write(6, 2, advance="no") k_1, i + k_1, k_2, i + k_2
# endif
                    result(i,j) = result(i,j) + stencil(k_1,k_2) * array(i + k_1, j + k_2)
                    ! note : (k_1 - 1 - sten_len/2,k_2 - 1 - sten_len/2) is the centered index of the stencil
                end do
            end do
# ifdef DEBUG        
            write(*,*) " at index " , i,j
# endif
            ! normalize by sten_sum
            result(i,j) = result(i,j)/sten_sum
#else
            result(i,j) = array(i - 1, j - 1) &
            &           + array(i - 1, j + 1) &
            &           + array(i    , j    ) &
            &           + array(i + 1, j - 1) &
            &           + array(i + 1, j + 1)
            result(i,j) = result(i,j)/sten_sum
#endif
        end do
    end do
    ! we ignore edges in the computation which explains the shift in indexes

    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    !!!!!!!! end timing here
    CALL perf_region_stop(bench_id)

        

    CALL ANTI_OPTIMISATION_WRITE(array(modulo(42,nx),modulo(42,ny)))
    CALL ANTI_OPTIMISATION_WRITE(result(modulo(42,nx),modulo(42,ny)))

end SUBROUTINE COMPUTATION_2D_JI

SUBROUTINE COMPUTATION_2D_IJ(bench_id,bench_str, array_len)
    use tools
    use perf_regions_fortran
#include "perf_regions_defines.h"
    
    ! stencil must be odd length
    integer, dimension(-1:1,-1:1) :: stencil
    integer(KIND=4), intent(in) :: bench_id
    character(len=7), intent(in) :: bench_str
    integer, intent(in) :: array_len
    real    :: sten_sum
    integer :: sten_len
    ! 2D arrays
    real(dp), allocatable :: array(:,:), result(:,:)
    allocate(array(array_len,array_len))
    allocate(result(array_len,array_len) , source=0.0_dp)

    stencil = reshape((/ 0, 1, 0, &
&                        1, 1, 1, &
&                        0, 1, 0/), shape(stencil))
    ! must be written in transpose form to fit column-wise specifications

    CALL stencil_characteristics_2D(stencil,sten_sum,sten_len)
#ifdef DEBUG
    write(*,*) stencil, sten_sum, sten_len
#endif

    do i = 1, array_len
        do j = 1, array_len
            call RANDOM_NUMBER(array(i,j))
        end do
    end do
    
#ifdef DEBUG
    ! example for formatting :
    ! I5 for a 5-digit integer.
    ! F10.4 for a floating-point number with 10 total characters, including 4 digits after the decimal point.
    ! A for a character string.
    ! 100 format(I5, F10.4, A)
    2 format(I4, I2, I2, I2)
#endif
        !!!!!!!! start timing here
    CALL perf_region_start(bench_id, bench_str//achar(0))

        
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    do i = 1 + sten_len/2, array_len - sten_len/2
        do j = 1 + sten_len/2, array_len - sten_len/2
#if FLEXIBLE_STENCIL
            do k_2 = -sten_len/2 ,sten_len/2
                do k_1 = -sten_len/2 ,sten_len/2
# ifdef DEBUG
                    write(6, 2, advance="no") k_1, i + k_1, k_2, i + k_2
# endif
                    result(i,j) = result(i,j) + stencil(k_1,k_2) * array(i + k_1, j + k_2)
                    ! note : (k_1 - 1 - sten_len/2,k_2 - 1 - sten_len/2) is the centered index of the stencil
                end do
            end do
# ifdef DEBUG        
        write(*,*) " at index " , i,j
# endif
        ! normalize by sten_sum
        result(i,j) = result(i,j)/sten_sum
#else
            result(i,j) = array(i - 1, j - 1) &
            &           + array(i - 1, j + 1) &
            &           + array(i    , j    ) &
            &           + array(i + 1, j - 1) &
            &           + array(i + 1, j + 1)
            result(i,j) = result(i,j)/sten_sum
#endif
        end do
    end do
    ! we ignore edges in the computation which explains the shift in indexes

    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    !!!!!!!! end timing here
    CALL perf_region_stop(bench_id)

        

    CALL ANTI_OPTIMISATION_WRITE(array(modulo(42,array_len),modulo(42,array_len)))
    CALL ANTI_OPTIMISATION_WRITE(result(modulo(42,array_len),modulo(42,array_len)))

end SUBROUTINE COMPUTATION_2D_IJ