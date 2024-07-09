! #define MAX_SIZE 1024*1024*128

! default value macros
#define ARRAY_LEN 1024 * 16
#define ITERS 1024

! see benchmark_parameters.f90 for options
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! BEWARE : benchmark_size_mode isn't compile time fixed, it only has a default option, unlike bench_id
! TODO : make an option to fix at compile time / keep flexible for different compiler optimisations
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#include "src/benchmark_compilation_fixed_parameters.h"

! TODO : change from BENCH_ID paradigm
#if     ALLOC_MODE == ALLOC
# define BENCH_ID 6
#elif   ALLOC_MODE == STATIC
# define BENCH_ID 5
#elif   ALLOC_MODE == NONE
# define BENCH_ID 6
#else
# define BENCH_ID 0
#endif

#ifdef ARRAY_LEN_OVERRIDE
    #define ARRAY_LEN ARRAY_LEN_OVERRIDE
#endif

PROGRAM main
    ! thank you to https://www.tutorialspoint.com/fortran/fortran_arrays.htm
    USE perf_regions_fortran
    use tools
    USE benchmark_names
    USE benchmark_implementations
    USE benchmark_2D_CPU
    USE benchmark_2D_GPU
    USE benchmark_parameters

#include "perf_regions_defines.h"
    implicit none

    ! integer :: iters
    integer :: k,i,iters,array_len
! #if SIZE_AT_COMPILATION == 0
    integer :: benchmark_size_mode
! #endif
    character(len=32) :: arg
    character(len=7) :: bench_str
    character(len=32) :: kernel_name
    
    
    INTERFACE
        SUBROUTINE BENCH_SKELETON(iters,bench_str, array_len)
            integer, intent(in) :: iters, array_len
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


    ! default values
    iters = ITERS
    array_len = ARRAY_LEN
#if SIZE_AT_COMPILATION == 0
    benchmark_size_mode = BENCHMARK_SIZE_MODE
#endif

    CALL set_ni_nj(benchmark_size_mode,iters)
    CALL set_1D_size(benchmark_size_mode,array_len,iters)

    !!!!!!!! initialize timing here
CALL perf_regions_init()
    
    CALL WARMUP_COMPUTATION(3,array_len)

    i = 1
    do
        call get_command_argument(i,arg)
        ! condition to leave do loop
        if (len_trim(arg) == 0) then
            exit
        else if (index(arg, 'sizemode=') == 1) then
            write(*,*) arg
            CALL get_key_value(arg,benchmark_size_mode) 
            CALL set_ni_nj(benchmark_size_mode,iters)
            CALL set_1D_size(benchmark_size_mode,array_len,iters)
        else if (index(arg, 'iters=') == 1) then
            write(*,*) arg
            CALL get_key_value(arg,iters)
        endif
        i = i + 1
    end do

    !!!!!!!!!!!!!!!!!!!!!!!!!!! BENCH CALL !!!!!!!!!!!!!!!!!!!!!!!!!!!!

    WRITE(*,*) "**************************************"
    WRITE(*,*) "**************************************"

    write (*,*) 'Calling benchmark of id ', BENCH_ID
    select case (KERNEL_MODE)
        case (DEFAULT_KERNEL)
            kernel_name = 'default_kernel'
        case (X_KERNEL)
            kernel_name = 'x direction kernel'
        case (Y_KERNEL)
            kernel_name = 'y direction kernel'
        case (SIZE_5_KERNEL)
            kernel_name = 'size 5 kernel'
        case DEFAULT
            kernel_name = 'default_kernel'
    end select
    write (*,*) 'Using ', kernel_name
    
    ! see https://pages.mtu.edu/~shene/COURSES/cs201/NOTES/chap03/select
    select case (BENCH_ID)
        case (BENCH_FIXED_ARRAY)
            bench_str = '1D_FIXD'
        case (BENCH_ALLOCATABLE_ARRAY)
            bench_str = '1D_ALOC'
        case (BENCH_ALLOCATABLE_ARRAY_MODULE)
            bench_str = '1D_MODU'
            
        case(BENCH_2D_CPU_JI)
            bench_str = '2D_JI'
        case(BENCH_2D_CPU_IJ)
            bench_str = '2D_IJ'
        case (BENCH_2D_CPU_MODULE)
            bench_str = '2D_MODU'
        case (BENCH_2D_CPU_MODULE_STATIC)
            bench_str = '2D_FIXD'

        case (BENCH_2D_GPU_OMP_BASE)
            bench_str = 'GPU'

        case DEFAULT
            bench_str = 'ERROR'
            write (*,*) 'Error: no such benchmark'
    end select
    if ( .not. bench_str .eq. 'ERROR') then
        CALL BENCH_SKELETON(iters, bench_str, array_len)
    end if

    !!!!!!!! finalize timing here
CALL perf_regions_finalize()

END PROGRAM main



SUBROUTINE BENCH_SKELETON(iters, bench_str, array_len)
USE perf_regions_fortran
USE benchmark_names
USE benchmark_parameters
#include "perf_regions_defines.h"
    use benchmark_implementations
    use benchmark_2D_GPU
    use benchmark_2D_CPU
    
    integer, intent(in) :: iters
    character(len=7), intent(in) :: bench_str
    integer, intent(in) :: array_len


    write (*,*) 'Running bench ', bench_str, '...'
    WRITE(*,*) "**************************************"
    if (     BENCH_ID == BENCH_FIXED_ARRAY              &
        .or. BENCH_ID == BENCH_ALLOCATABLE_ARRAY        &
        .or. BENCH_ID == BENCH_ALLOCATABLE_ARRAY_MODULE) then
        WRITE(*,*) "Mem size: ", array_len*0.001 ," KByte"
    else
        nii = ni
        njj = nj
        ! write(*,*) "ni", nii
        ! write(*,*) "nj", njj
        WRITE(*,*) "Mem size: ", nii* &
                                njj*0.001 ," KByte"
    end if
    WRITE(*,*) "Iterations: ", iters
    do k = 1, iters
#ifdef DEBUG
        CALL perf_region_start(99, "DEBUG"//achar(0))
#endif
        select case (BENCH_ID)
            case (BENCH_FIXED_ARRAY)
                CALL COMPUTATION_FIXED_ARRAY(BENCH_ID, bench_str, array_len)
            case (BENCH_ALLOCATABLE_ARRAY)
                CALL COMPUTATION_ALLOCATABLE_ARRAY(BENCH_ID, bench_str, array_len)
            case (BENCH_ALLOCATABLE_ARRAY_MODULE)
                CALL COMPUTATION_ALLOCATABLE_ARRAY_MODULE(BENCH_ID, bench_str, array_len)

            case (BENCH_2D_CPU_JI)
                CALL COMPUTATION_2D_JI(BENCH_ID, bench_str, array_len)
            case (BENCH_2D_CPU_IJ)
                CALL COMPUTATION_2D_IJ(BENCH_ID, bench_str, array_len)
            case (BENCH_2D_CPU_MODULE)
                CALL COMPUTATION_2D_MODULE(BENCH_ID, bench_str, array_len)
            case (BENCH_2D_CPU_MODULE_STATIC)
                CALL COMPUTATION_2D_MODULE_FIXED(BENCH_ID, bench_str, array_len)

            case (BENCH_2D_GPU_OMP_BASE)
                CALL COMPUTATION_GPU_OMP_BASE(BENCH_ID, bench_str, array_len)
                
            case DEFAULT
                write (*,*) 'Error: no such benchmark'
        end select
#ifdef DEBUG
        CALL perf_region_stop(99) !DEBUG
#endif
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

    !!!!!!!! start timing here
    CALL perf_region_start(bench_id, bench_str//achar(0))
        
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
    CALL perf_region_stop(bench_id)

        

    CALL ANTI_OPTIMISATION_WRITE(array(modulo(42,array_len)))
    CALL ANTI_OPTIMISATION_WRITE(result(modulo(42,array_len)))

end SUBROUTINE COMPUTATION_ALLOCATABLE_ARRAY

SUBROUTINE COMPUTATION_2D_JI(bench_id,bench_str, array_len)
    use tools
    use perf_regions_fortran
    use benchmark_parameters
#include "perf_regions_defines.h"
    
    integer(KIND=4), intent(in) :: bench_id
    character(len=7), intent(in) :: bench_str
    integer, intent(in) :: array_len
    integer :: i,j
    integer :: sten_len = 3
    ! 2D arrays
    real(dp), allocatable :: array(:,:), result(:,:)
    allocate(array(ni,&
                    nj))
    allocate(result(ni,&
                    nj) , source=-1.0_dp)

    do j = 1, nj
        do i = 1, ni
            array(i,j) = (i-1)*nj + j
            ! call RANDOM_NUMBER(array(i,j))
        end do
    end do

        !!!!!!!! start timing here
    CALL perf_region_start(bench_id, bench_str//achar(0))

        
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    do j = 1 + 2, nj - 2
        do i = 1 + 2, ni - 2
#if KERNEL_MODE == NO_INCLUDE
            result(i,j) = 1.0_dp * array(i - 1, j - 1) &
                        + 2.0_dp * array(i - 1, j + 1) &
                        + 3.0_dp * array(i    , j    ) &
                        + 4.0_dp * array(i + 1, j - 1) &
                        + 5.0_dp * array(i + 1, j + 1)
            result(i,j) = result(i,j)/15.0_dp
#else
# if   KERNEL_MODE == DEFAULT_KERNEL
#  include "kernels/kernel_2D_default.h"
# elif KERNEL_MODE == X_KERNEL
#  include "kernels/kernel_2D_x.h"
# elif KERNEL_MODE == Y_KERNEL
#  include "kernels/kernel_2D_y.h"
# elif KERNEL_MODE == SIZE_5_KERNEL
#  include "kernels/kernel_2D_size_5.h"
# else
#  include "kernels/kernel_2D_default.h"
# endif /*KERNEL_MODE*/
#endif /*NO_INCLUDE*/
        end do
    end do
    ! we ignore edges in the computation which explains the shift in indexes

    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    !!!!!!!! end timing here
    CALL perf_region_stop(bench_id)

        

    CALL ANTI_OPTIMISATION_WRITE(array(modulo(42,ni),&
                                    modulo(42,nj)))
    CALL ANTI_OPTIMISATION_WRITE(result(modulo(42,ni),&
                                    modulo(42,nj)))

end SUBROUTINE COMPUTATION_2D_JI

SUBROUTINE COMPUTATION_2D_IJ(bench_id,bench_str, array_len)
    use tools
    use perf_regions_fortran
    use benchmark_parameters
#include "perf_regions_defines.h"
    
    integer(KIND=4), intent(in) :: bench_id
    character(len=7), intent(in) :: bench_str
    integer, intent(in) :: array_len
    integer :: i,j
    integer :: sten_len = 3
    ! 2D arrays
    real(dp), allocatable :: array(:,:), result(:,:)
    allocate(array(ni,&
                    nj))
    allocate(result(ni,&
                    nj) , source=-1.0_dp)

    do i = 1, ni
        do j = 1, nj
            array(i,j) = (i-1)*nj + j
            ! call RANDOM_NUMBER(array(i,j))
        end do
    end do
        !!!!!!!! start timing here
    CALL perf_region_start(bench_id, bench_str//achar(0))

        
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    do i = 1 + 2, ni - 2
        do j = 1 + 2, nj - 2
#if KERNEL_MODE == NO_INCLUDE
            result(i,j) = 1.0_dp * array(i - 1, j - 1) &
                        + 2.0_dp * array(i - 1, j + 1) &
                        + 3.0_dp * array(i    , j    ) &
                        + 4.0_dp * array(i + 1, j - 1) &
                        + 5.0_dp * array(i + 1, j + 1)
            result(i,j) = result(i,j)/15.0_dp
#else
# if   KERNEL_MODE == DEFAULT_KERNEL
#  include "kernels/kernel_2D_default.h"
# elif KERNEL_MODE == X_KERNEL
#  include "kernels/kernel_2D_x.h"
# elif KERNEL_MODE == Y_KERNEL
#  include "kernels/kernel_2D_y.h"
# elif KERNEL_MODE == SIZE_5_KERNEL
#  include "kernels/kernel_2D_size_5.h"
# else
#  include "kernels/kernel_2D_default.h"
# endif /*KERNEL_MODE*/
#endif /*NO_INCLUDE*/
        end do
    end do
    ! we ignore edges in the computation which explains the shift in indexes

    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    !!!!!!!! end timing here
    CALL perf_region_stop(bench_id)

        

    CALL ANTI_OPTIMISATION_WRITE(array(modulo(42,ni),&
                                    modulo(42,nj)))
    CALL ANTI_OPTIMISATION_WRITE(result(modulo(42,ni),&
                                    modulo(42,nj)))

end SUBROUTINE COMPUTATION_2D_IJ