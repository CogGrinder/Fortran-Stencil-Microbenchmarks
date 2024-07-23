#include "benchmark_compilation_fixed_parameters.h"
! #define DEBUG
! #define DEBUG_PERF

MODULE BENCHMARK_2D_GPU
    USE BENCHMARK_NAMES
    use perf_regions_fortran
    USE TOOLS
    implicit none
    
    contains
    
    
! to test 2D stencils on an OpenMP offloaded GPU
SUBROUTINE COMPUTATION_GPU_OMP_BASE(bench_id,bench_str,array_len)
    USE TOOLS
    use perf_regions_fortran
    USE BENCHMARK_PARAMETERS
#include "perf_regions_defines.h"
    
    integer(KIND=4), intent(in) :: bench_id
    character(len=7), intent(in) :: bench_str
    integer, intent(in) :: array_len

#ifndef NO_GPU /*used for ignoring this module when compiling without nvfortran*/

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

#else
    write(*,*) "GPU BENCHMARK NOT COMPILED"
#endif /*NO_GPU*/

end SUBROUTINE COMPUTATION_GPU_OMP_BASE

end MODULE BENCHMARK_2D_GPU