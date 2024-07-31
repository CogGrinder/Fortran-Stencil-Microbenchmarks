#include "include/compilation_fixed_parameters.h"

MODULE BENCHMARK_2D_CPU
    use perf_regions_fortran
    USE TOOLS
    implicit none
    
    contains
    
    
    ! to test 2D stencils with allocatable
SUBROUTINE COMPUTATION_2D_MODULE(bench_id,bench_str)
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

    do j = 1, loop_bound_nj
        do i = 1, loop_bound_ni
            array(i,j) = (i-1)*nj + j
            ! call RANDOM_NUMBER(array(i,j))
        end do
    end do
    
        !!!!!!!! start timing here
#ifndef NO_PERF_REGIONS
    CALL perf_region_start(bench_id, bench_str)
#endif

        
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    do j = 1 + 2, loop_bound_nj - 2
        do i = 1 + 2, loop_bound_ni - 2
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

#if ALLOC_MODE == ALLOCATABLE
    DEALLOCATE (array)
    DEALLOCATE (result)
#endif /*ALLOC_MODE*/

end SUBROUTINE COMPUTATION_2D_MODULE

end MODULE BENCHMARK_2D_CPU