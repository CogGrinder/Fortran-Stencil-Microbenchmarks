#include "benchmark_compilation_fixed_parameters.h"
! #define DEBUG
! #define DEBUG_PERF

MODULE BENCHMARK_2D_CPU
    USE BENCHMARK_NAMES
    use perf_regions_fortran
    USE TOOLS
    implicit none
    
    contains
    
    
    ! to test 2D stencils with allocatable
SUBROUTINE COMPUTATION_2D_MODULE(bench_id,bench_str,array_len)
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

end SUBROUTINE COMPUTATION_2D_MODULE

    ! to test 2D stencils on an OpenMP offloaded GPU
SUBROUTINE COMPUTATION_2D_MODULE_FIXED(bench_id,bench_str,array_len)
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

end SUBROUTINE COMPUTATION_2D_MODULE_FIXED

end MODULE BENCHMARK_2D_CPU