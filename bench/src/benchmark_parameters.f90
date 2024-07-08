! this value is a power of 2 between 1 and 32 - recommended is 32
#define BENCHMARK_ACCELERATION 32
#include "benchmark_compilation_fixed_parameters.h"

MODULE benchmark_parameters

    ! here set your processor's L3 cache size in Mib - useful for modes 100 to 103
    integer, parameter :: l3_size_in_mib = 6

#if SIZE_AT_COMPILATION==1
    contains
    SUBROUTINE set_ni_nj(mode,iters)
        integer, intent(in) :: mode
        integer, intent(in) :: iters
        write(*,*) "SIZE_AT_COMPILATION successfully set to 1"
    END SUBROUTINE
    SUBROUTINE set_1D_size(mode,size,iters)
        integer, intent(in) :: mode
        integer, intent(in) :: size
        integer, intent(in) :: iters
        write(*,*) "SIZE_AT_COMPILATION successfully set to 1"
    END SUBROUTINE
#else
    ! ni is the i/row-size
    integer :: ni = 128
    ! nj is the j/column-size
    integer :: nj = 128
    
    contains
    ! uses the property 31*33*1024 = 32*31*992 = 32*33*1056 = 1047552 using gcd properties
    SUBROUTINE set_ni_nj(mode,iters)
        use benchmark_names
        integer, intent(in) :: mode
        integer, intent(inout) :: iters
        select case (mode)
            case (1:99)
                ! ni = 1024 * mode 
                ! nj = 1024
                ni = int(sqrt(real(1024*1024*mode)))
                nj = 1024*1024*mode / ni
                ! TODO : address the problem of approximation or record the approximation value in output
                write(*,*) ni, nj
                ! write(*,FMT='(A,F2.2,A)') "Approximation by ", ( 1.0*ni*nj/1024*1024*mode -1 ), "%"
                iters = 1024 / BENCHMARK_ACCELERATION
            
            case (smaller_than_l3)
                ni = 128 * l3_size_in_mib
                nj = 128
                ! here we adjust iters to use roughly as many computations as with 1024*1024
                iters = 31*33 * (1024**2 / 128**2)
                iters = iters / BENCHMARK_ACCELERATION
            case (slightly_smaller_than_l3)
                ni = 1024 * l3_size_in_mib
                nj = 992
                ! iters chosen to compensate change in nj
                iters = 32*33 / BENCHMARK_ACCELERATION
            case (slightly_bigger_than_l3)
                ni = 1024 * l3_size_in_mib
                nj = 1056
                ! iters chosen to compensate change in nj
                iters = 32*31 / BENCHMARK_ACCELERATION
            case (bigger_than_l3)
                ni = 1024 * 3 * l3_size_in_mib
                nj = 992
                iters = 32*33 / BENCHMARK_ACCELERATION
                ! here we adjust to get back to 1024*1056
                iters = iters / 3
            case DEFAULT
                write(*,FMT='(A,I3,A,I4,A,I4)') "Error: unrecognized 2D array size mode ", mode, &
                " defaulting to ", ni, " by ", nj
        end select
    END SUBROUTINE
    SUBROUTINE set_1D_size(mode,size,iters)
        use benchmark_names
        integer, intent(in) :: mode
        integer, intent(inout) :: size, iters
        select case (mode)
            case (1:99)
                ! ni = 1024 * mode 
                ! nj = 1024
                ni = int(sqrt(real(1024*1024*mode)))
                nj = 1024*1024*mode / ni
                size = ni * nj
                ! TODO : address the problem of approximation or record the approximation value in output
                write(*,*) size
                ! write(*,FMT='(A,F2.2,A)') "Approximation by ", ( 1.0*ni*nj/1024*1024*mode -1 ), "%"
                iters = 1024 / BENCHMARK_ACCELERATION
            
            case (smaller_than_l3)
                size = 128 * 128 * l3_size_in_mib
                iters = (31*33 * (1024**2 / 128**2) / BENCHMARK_ACCELERATION)
            case (slightly_smaller_than_l3)
                size = 1024 * 992 * l3_size_in_mib
                iters =  32*33 / BENCHMARK_ACCELERATION
            case (slightly_bigger_than_l3)
                size = 1024 * 1056 * l3_size_in_mib
                iters =  32*31 / BENCHMARK_ACCELERATION
            case (bigger_than_l3)
                size = 1024 * 992 * 3 * l3_size_in_mib
                iters = (32*33 / BENCHMARK_ACCELERATION) / 3
            case DEFAULT
                write(*,FMT='(A,I3,A)') "Error: unrecognized 1D array size mode ", mode, &
                " defaulting to macro value"
        end select
    END SUBROUTINE
#endif /* end of SIZE_AT_COMPILATION*/
END MODULE benchmark_parameters