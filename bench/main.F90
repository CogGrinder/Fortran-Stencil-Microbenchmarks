! default value macros
#define DEFAULT_ARRAY_LEN 1024 * 16
#define DEFAULT_ITERS 128

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! see following file for macro definitions
#include "src/include/compilation_fixed_parameters.h"

! selector for which function to call for computation
#if HARDWARE == GPU
# if DIM == 1
#  error Not implemented

# elif DIM == 2
#  if     MODULE_MODE == 1
#   define BENCH_ID BENCH_2D_GPU_OMP_BASE
! TODO: add non-module version of GPU bench
#  elif   MODULE_MODE == 0
#   error Non-module version not implemented
#  endif /*MODULE_MODE*/
# else
#  error Dimension not implemented
# endif /*DIM*/
#else /*HARDWARE*/

# if DIM == 1
#  if     MODULE_MODE == 1
#   define BENCH_ID BENCH_1D_MODULE
#  elif   MODULE_MODE == 0
#   define BENCH_ID BENCH_1D
#  endif

# elif DIM == 2
#  if     MODULE_MODE == 1
#   define BENCH_ID BENCH_2D_CPU_MODULE
#  elif   MODULE_MODE == 0
#   define BENCH_ID BENCH_2D_CPU_JI
#  endif /*MODULE_MODE*/
# else
#  error Dimension not implemented
# endif /*DIM*/
#endif /*HARDWARE*/

PROGRAM main
    ! thank you to https://www.tutorialspoint.com/fortran/fortran_arrays.htm
    USE perf_regions_fortran
    USE TOOLS
    USE BENCHMARK_1D
    USE BENCHMARK_2D_CPU
    USE BENCHMARK_2D_GPU
    USE BENCHMARK_PARAMETERS

#include "perf_regions_defines.h"
    implicit none

    ! integer :: iters
    integer :: k,i,iters,niinput,njinput,n1dinput
    character(len=32) :: arg
    character(len=7) :: bench_str
    character(len=32) :: kernel_name, alloc_name
    character(len=128) :: binary_name
    
    
    INTERFACE
        SUBROUTINE BENCH_SKELETON(iters,bench_str, array_len)
            integer, intent(in) :: iters, array_len
            character(len=7), intent(in) :: bench_str
        end SUBROUTINE BENCH_SKELETON
        SUBROUTINE WARMUP_COMPUTATION(sten_len, array_len)
            integer, intent(in) :: sten_len, array_len
        end SUBROUTINE WARMUP_COMPUTATION
        SUBROUTINE COMPUTATION_1D(bench_id,bench_str, array_len)
            integer, intent(in) :: array_len
            integer(KIND=4), intent(in) :: bench_id
            character(len=7), intent(in) :: bench_str
        end SUBROUTINE COMPUTATION_1D
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
    

    ! default values
    iters = DEFAULT_ITERS
    n1dinput = DEFAULT_ARRAY_LEN
    niinput = 128
    njinput = 128

    CALL set_2D_size(niinput,njinput)
    CALL set_1D_size(n1dinput)

    !!!!!!!! initialize timing here
CALL perf_regions_init()
    
    CALL WARMUP_COMPUTATION(3,n1dinput)

    i = 1
    ! see https://gcc.gnu.org/onlinedocs/gfortran/GET_005fCOMMAND_005fARGUMENT.html
    do
        call get_command_argument(i,arg)
        ! condition to leave do loop
        if (len_trim(arg) == 0) then
            exit
        else if (index(arg, 'ni=') == 1) then
            write(*,*) arg
            CALL get_key_value(arg,niinput)
        else if (index(arg, 'nj=') == 1) then
            write(*,*) arg
            CALL get_key_value(arg,njinput)
        else if (index(arg, 'n1d=') == 1) then
            write(*,*) arg
            CALL get_key_value(arg,n1dinput)
        else if (index(arg, 'iters=') == 1) then
            write(*,*) arg
            CALL get_key_value(arg,iters)
        endif
        i = i + 1
    end do

    CALL set_2D_size(niinput,njinput)
    CALL set_1D_size(n1dinput)

    !!!!!!!!!!!!!!!!!!!!!!!!!!! BENCH DESCRIPTION !!!!!!!!!!!!!!!!!!!!!!!!!!!!
    
    CALL get_command_argument(0,binary_name)
    WRITE(*,*) "**************************************"
    WRITE(*,*) "**************************************"
    write (*,*) 'Calling benchmark of id :'
    write (*,*) binary_name
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
            kernel_name = 'non specified kernel'
    end select
    select case (ALLOC_MODE)
        case (ALLOCATABLE)
            alloc_name = 'allocatable'
        case (STATIC)
            alloc_name = 'static'
        case DEFAULT
            alloc_name = 'default'
    end select
    write (*,*) 'Kernel type: ', kernel_name
    write (*,*) 'Allocation type: ', alloc_name
    
    ! bench_str (str): used for describing function call to perf_regions
    ! see https://pages.mtu.edu/~shene/COURSES/cs201/NOTES/chap03/select
    select case (BENCH_ID)
        case (BENCH_1D)
            bench_str = '1D'
        case (BENCH_1D_MODULE)
            bench_str = '1D_MODU'
            
        case(BENCH_2D_CPU_JI)
            bench_str = '2D_JI'
        case(BENCH_2D_CPU_IJ)
            bench_str = '2D_IJ'
        case (BENCH_2D_CPU_MODULE)
            bench_str = '2D_MODU'

        case (BENCH_2D_GPU_OMP_BASE)
            bench_str = 'GPU'

        case DEFAULT
            bench_str = 'ERROR'
            write (*,*) 'Error: no such benchmark'
    end select

    if ( .not. bench_str .eq. 'ERROR') then
        CALL BENCH_SKELETON(iters, bench_str, n1dinput)
    end if

    !!!!!!!! finalize timing here
CALL perf_regions_finalize()

END PROGRAM main



SUBROUTINE BENCH_SKELETON(iters, bench_str, array_len)
USE perf_regions_fortran
USE BENCHMARK_PARAMETERS
#include "perf_regions_defines.h"
    USE BENCHMARK_1D
    USE BENCHMARK_2D_CPU
    USE BENCHMARK_2D_GPU
    
    integer, intent(in) :: iters
    character(len=7), intent(in) :: bench_str
    integer, intent(in) :: array_len


    write (*,*) 'Running bench ', bench_str, '...'
    WRITE(*,*) "**************************************"
    WRITE(*,*) "Precision in bytes: ", dp, " bytes"
    if (     BENCH_ID == BENCH_1D              &
        .or. BENCH_ID == BENCH_1D_MODULE) then
        WRITE(*,*) "Mem size: ", array_len*0.001 ," Kbyte"
    else
        WRITE(*,*) "Mem size: ", ni* &
                                nj*0.001 ," Kbyte"
    end if
    WRITE(*,*) "Iterations: ", iters
    do k = 1, iters
#ifdef DEBUG
        CALL perf_region_start(99, "DEBUG"//achar(0))
#endif
        select case (BENCH_ID)
            case (BENCH_1D)
                CALL COMPUTATION_1D(BENCH_ID, bench_str, array_len)
            case (BENCH_1D_MODULE)
                CALL COMPUTATION_1D_MODULE(BENCH_ID, bench_str, array_len)

            case (BENCH_2D_CPU_JI)
                CALL COMPUTATION_2D_JI(BENCH_ID, bench_str, array_len)
            case (BENCH_2D_CPU_IJ)
                CALL COMPUTATION_2D_IJ(BENCH_ID, bench_str, array_len)
            case (BENCH_2D_CPU_MODULE)
                CALL COMPUTATION_2D_MODULE(BENCH_ID, bench_str, array_len)
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

SUBROUTINE COMPUTATION_1D(bench_id,bench_str, array_len)
    USE TOOLS
    use perf_regions_fortran
#include "perf_regions_defines.h"
    
    ! stencil must be odd length
    integer, dimension(-1:1) :: stencil
    integer(KIND=4), intent(in) :: bench_id
    character(len=7), intent(in) :: bench_str
    integer, intent(in) :: array_len
    real    :: sten_sum
    integer :: sten_len

#if ALLOC_MODE == ALLOCATABLE
    real(dp), allocatable :: array(:), result(:)
    allocate(array(array_len))
    allocate(result(array_len) , source=0.0_dp)
#elif ALLOC_MODE == STATIC
    real(dp), dimension(array_len) :: array
    real(dp), dimension(array_len) :: result
#endif /*ALLOC_MODE*/

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

end SUBROUTINE COMPUTATION_1D

SUBROUTINE COMPUTATION_2D_JI(bench_id,bench_str, array_len)
    USE TOOLS
    use perf_regions_fortran
    USE BENCHMARK_PARAMETERS
#include "perf_regions_defines.h"
    
    integer(KIND=4), intent(in) :: bench_id
    character(len=7), intent(in) :: bench_str
    integer, intent(in) :: array_len
    integer :: i,j
    integer :: sten_len = 3
    ! 2D arrays
#if ALLOC_MODE == ALLOCATABLE
    real(dp), allocatable :: array(:,:), result(:,:)
    allocate(array(ni,&
                    nj))
    allocate(result(ni,&
                    nj) , source=-1.0_dp)
#elif ALLOC_MODE == STATIC
    real(dp), dimension(array_len,array_len) :: array
    real(dp), dimension(array_len,array_len) :: result
#endif /*ALLOC_MODE*/


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
# include "kernels/select_kernel_2D.h"
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
    USE TOOLS
    use perf_regions_fortran
    USE BENCHMARK_PARAMETERS
#include "perf_regions_defines.h"
    
    integer(KIND=4), intent(in) :: bench_id
    character(len=7), intent(in) :: bench_str
    integer, intent(in) :: array_len
    integer :: i,j
    integer :: sten_len = 3
    ! 2D arrays
#if ALLOC_MODE == ALLOCATABLE
    real(dp), allocatable :: array(:,:), result(:,:)
    allocate(array(ni,&
                    nj))
    allocate(result(ni,&
                    nj) , source=-1.0_dp)
#elif ALLOC_MODE == STATIC
    real(dp), dimension(array_len,array_len) :: array
    real(dp), dimension(array_len,array_len) :: result
#endif /*ALLOC_MODE*/

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
# include "kernels/select_kernel_2D.h"
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