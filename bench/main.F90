! default value macros
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
        SUBROUTINE BENCH_SKELETON(iters,bench_str)
            integer, intent(in) :: iters
            character(len=7), intent(in) :: bench_str
        end SUBROUTINE BENCH_SKELETON
        SUBROUTINE WARMUP_COMPUTATION(iters)
            integer, intent(in) :: iters
        end SUBROUTINE WARMUP_COMPUTATION
        SUBROUTINE COMPUTATION_1D(bench_id,bench_str)
            integer(KIND=4), intent(in) :: bench_id
            character(len=7), intent(in) :: bench_str
        end SUBROUTINE COMPUTATION_1D
        SUBROUTINE COMPUTATION_2D_JI(bench_id,bench_str)
            integer(KIND=4), intent(in) :: bench_id
            character(len=7), intent(in) :: bench_str
        end SUBROUTINE COMPUTATION_2D_JI
        SUBROUTINE COMPUTATION_2D_IJ(bench_id,bench_str)
            integer(KIND=4), intent(in) :: bench_id
            character(len=7), intent(in) :: bench_str
        end SUBROUTINE COMPUTATION_2D_IJ
    end INTERFACE
    

    ! default values
    iters = DEFAULT_ITERS
    n1dinput = 128
    niinput = 128
    njinput = 128

    CALL set_2D_size(niinput,njinput)
    CALL set_1D_size(n1dinput)

    
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


    !!!!!!!! initialize timing here
#ifndef NO_PERF_REGIONS
    CALL perf_regions_init()
#endif

    if ( .not. bench_str .eq. 'ERROR') then
        ! TODO: debug this
        ! Do at least one warmup computation
        CALL WARMUP_COMPUTATION(max(iters/10, 1))
        CALL BENCH_SKELETON(iters, bench_str)
    end if

    !!!!!!!! finalize timing here
#ifndef NO_PERF_REGIONS
CALL perf_regions_finalize()
#endif

END PROGRAM main



SUBROUTINE BENCH_SKELETON(iters, bench_str)
USE perf_regions_fortran
USE BENCHMARK_PARAMETERS
#include "perf_regions_defines.h"
    USE BENCHMARK_1D
    USE BENCHMARK_2D_CPU
    USE BENCHMARK_2D_GPU
    
    integer, intent(in) :: iters
    character(len=7), intent(in) :: bench_str


    write (*,*) 'Running bench ', bench_str, '...'
    WRITE(*,*) "**************************************"
    WRITE(*,*) "Precision in bytes: ", dp, " bytes"
    if (     BENCH_ID == BENCH_1D              &
        .or. BENCH_ID == BENCH_1D_MODULE) then
        ! 1D size
            WRITE(*,*) "Mem size: ", n1d*0.000001*dp ," Mbyte"
        else
            ! 2D size
            WRITE(*,*) "Mem size: ", ni* &
                                    nj*0.000001*dp ," Mbyte"
    end if
    WRITE(*,*) "Iterations: ", iters
    do k = 1, iters
#ifdef DEBUG
#ifndef NO_PERF_REGIONS
        CALL perf_region_start(99, "DEBUG")
#endif
#endif
        select case (BENCH_ID)
            case (BENCH_1D)
                CALL COMPUTATION_1D(BENCH_ID, bench_str)
            case (BENCH_1D_MODULE)
                CALL COMPUTATION_1D_MODULE(BENCH_ID, bench_str)

            case (BENCH_2D_CPU_JI)
                CALL COMPUTATION_2D_JI(BENCH_ID, bench_str)
            case (BENCH_2D_CPU_IJ)
                CALL COMPUTATION_2D_IJ(BENCH_ID, bench_str)
            case (BENCH_2D_CPU_MODULE)
                CALL COMPUTATION_2D_MODULE(BENCH_ID, bench_str)
            case (BENCH_2D_GPU_OMP_BASE)
                CALL COMPUTATION_GPU_OMP_BASE(BENCH_ID, bench_str)
                
            case DEFAULT
                write (*,*) 'Error: no such benchmark'
        end select
#ifdef DEBUG
#ifndef NO_PERF_REGIONS
        CALL perf_region_stop(99) !DEBUG
#endif
#endif
    end do
  
end SUBROUTINE BENCH_SKELETON

SUBROUTINE WARMUP_COMPUTATION(iters)
    ! WARNING: TODO: make sure this is not leaking memory
    USE perf_regions_fortran
USE BENCHMARK_PARAMETERS
#include "perf_regions_defines.h"
    USE BENCHMARK_1D
    USE BENCHMARK_2D_CPU
    USE BENCHMARK_2D_GPU

    integer, intent(in) :: iters
    ! '-' is used as character for ignoring line in output
    character(len=7) :: warmup_str = '-WARMUP'
    integer :: warmup_id = 100
    
    
    WRITE(*,*) "--------------------------------------"
    write (*,*) 'Running ', warmup_str, '...'
    if (     BENCH_ID == BENCH_1D              &
        .or. BENCH_ID == BENCH_1D_MODULE) then
        ! 1D size
        WRITE(*,*) "Mem size: ", n1d*0.000001*dp ," Mbyte"
    else
        ! 2D size
        WRITE(*,*) "Mem size: ", ni* &
                                nj*0.000001*dp ," Mbyte"
    end if
    WRITE(*,*) "Iterations: ", iters
    do k = 1, iters
        select case (BENCH_ID)
            case (BENCH_1D)
                CALL COMPUTATION_1D(warmup_id, warmup_str)
            case (BENCH_1D_MODULE)
                CALL COMPUTATION_1D_MODULE(warmup_id, warmup_str)

            case (BENCH_2D_CPU_JI)
                CALL COMPUTATION_2D_JI(warmup_id, warmup_str)
            case (BENCH_2D_CPU_IJ)
                CALL COMPUTATION_2D_IJ(warmup_id, warmup_str)
            case (BENCH_2D_CPU_MODULE)
                CALL COMPUTATION_2D_MODULE(warmup_id, warmup_str)
            case (BENCH_2D_GPU_OMP_BASE)
                CALL COMPUTATION_GPU_OMP_BASE(warmup_id, warmup_str)
                
            case DEFAULT
                write (*,*) 'Error: no such benchmark'
        end select
    end do
    WRITE(*,*) "--------------------------------------"
end SUBROUTINE WARMUP_COMPUTATION

SUBROUTINE COMPUTATION_1D(bench_id,bench_str)
    USE TOOLS
    use perf_regions_fortran
    USE BENCHMARK_PARAMETERS
#include "perf_regions_defines.h"
    
    ! stencil must be odd length
    integer, dimension(-1:1) :: stencil
    integer(KIND=4), intent(in) :: bench_id
    character(len=7), intent(in) :: bench_str
    real    :: sten_sum
    integer :: sten_len

#if ALLOC_MODE == ALLOCATABLE
    real(dp), allocatable :: array(:), result(:)
    allocate(array(n1d))
    allocate(result(n1d) , source=0.0_dp)
#elif ALLOC_MODE == STATIC
    real(dp), dimension(n1d) :: array
    real(dp), dimension(n1d) :: result
#endif /*ALLOC_MODE*/

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

        

CALL ANTI_OPTIMISATION_WRITE(array(5),"array_tmp.txt")
CALL ANTI_OPTIMISATION_WRITE(result(5),"result_tmp.txt")

end SUBROUTINE COMPUTATION_1D

SUBROUTINE COMPUTATION_2D_JI(bench_id,bench_str)
    USE TOOLS
    use perf_regions_fortran
    USE BENCHMARK_PARAMETERS
#include "perf_regions_defines.h"
    
    integer(KIND=4), intent(in) :: bench_id
    character(len=7), intent(in) :: bench_str
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
    ! real(dp), dimension(ni,nj) :: array
    ! real(dp), dimension(ni,nj) :: result
    real(dp) array(ni,nj), result(ni,nj)
#endif /*ALLOC_MODE*/


    do j = 1, nj
        do i = 1, ni
            array(i,j) = (i-1)*nj + j
            ! call RANDOM_NUMBER(array(i,j))
        end do
    end do

        !!!!!!!! start timing here
#ifndef NO_PERF_REGIONS
    CALL perf_region_start(bench_id, bench_str)
#endif

        
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
#ifndef NO_PERF_REGIONS
    CALL perf_region_stop(bench_id)
#endif

        

    CALL ANTI_OPTIMISATION_WRITE(array(5,5),"array_tmp.txt")
    CALL ANTI_OPTIMISATION_WRITE(result(5,5),"result_tmp.txt")

end SUBROUTINE COMPUTATION_2D_JI

SUBROUTINE COMPUTATION_2D_IJ(bench_id,bench_str)
    USE TOOLS
    use perf_regions_fortran
    USE BENCHMARK_PARAMETERS
#include "perf_regions_defines.h"
    
    integer(KIND=4), intent(in) :: bench_id
    character(len=7), intent(in) :: bench_str
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
    ! real(dp), dimension(ni,nj) :: array
    ! real(dp), dimension(ni,nj) :: result
    real(dp) array(ni,nj), result(ni,nj)
#endif /*ALLOC_MODE*/

    do i = 1, ni
        do j = 1, nj
            array(i,j) = (i-1)*nj + j
            ! call RANDOM_NUMBER(array(i,j))
        end do
    end do
        !!!!!!!! start timing here
#ifndef NO_PERF_REGIONS
    CALL perf_region_start(bench_id, bench_str)
#endif

        
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
#ifndef NO_PERF_REGIONS
    CALL perf_region_stop(bench_id)
#endif

        

    CALL ANTI_OPTIMISATION_WRITE(array(5,5),"array_tmp.txt")
    CALL ANTI_OPTIMISATION_WRITE(result(5,5),"result_tmp.txt")

end SUBROUTINE COMPUTATION_2D_IJ