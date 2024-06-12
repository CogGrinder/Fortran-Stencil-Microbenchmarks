! #define DEBUG
! #define DEBUG_PERF

MODULE benchmark_2D_GPU
    use benchmark_names
    use perf_regions_fortran
    use tools
    implicit none
    
    contains
    
    
    ! to test 2D stencils on an OpenMP offloaded GPU
    SUBROUTINE COMPUTATION_GPU_OMP_BASE(bench_id,bench_str,array_len)
        use tools
        use perf_regions_fortran
        use benchmark_parameters
#include "perf_regions_defines.h"
        
        ! stencil must be odd length
        integer, dimension(-1:1,-1:1) :: stencil
        integer(KIND=4), intent(in) :: bench_id
        character(len=7), intent(in) :: bench_str
        integer, intent(in) :: array_len
        integer i,j
        integer :: sten_len = 3
        ! 2D arrays
        real(dp), allocatable :: array(:,:), result(:,:)
        allocate(array(nx,ny))
        allocate(result(nx,ny) , source=-1.0_dp)
    
        do j = 1, ny
            do i = 1, nx
                array(i,j) = (i-1)*ny + j
                ! call RANDOM_NUMBER(array(i,j))
            end do
        end do
        
            !!!!!!!! start timing here
        CALL perf_region_start(bench_id, bench_str//achar(0))
    
            
        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        do j = 1 + sten_len/2, ny - sten_len/2
            do i = 1 + sten_len/2, nx - sten_len/2
                result(i,j) = array(i - 1, j - 1) &
                &           + array(i - 1, j + 1) &
                &           + array(i    , j    ) &
                &           + array(i + 1, j - 1) &
                &           + array(i + 1, j + 1)
                result(i,j) = result(i,j)/5
            end do
        end do
        ! we ignore edges in the computation which explains the shift in indexes
    
        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    
        !!!!!!!! end timing here
        CALL perf_region_stop(bench_id)
    
            
    
        CALL ANTI_OPTIMISATION_WRITE(array(modulo(42,nx),modulo(42,ny)))
        CALL ANTI_OPTIMISATION_WRITE(result(modulo(42,nx),modulo(42,ny)))

end SUBROUTINE COMPUTATION_GPU_OMP_BASE

end MODULE benchmark_2D_GPU