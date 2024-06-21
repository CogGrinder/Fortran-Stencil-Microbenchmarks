! this value is a power of 2 between 1 and 32 - recommended is 32
#define BENCHMARK_ACCELERATION 8

MODULE benchmark_parameters
    ! here set your processor's L3 cache size in Mib
    integer, parameter :: l3_size_in_mib = 6

    ! nx is the i/row-size
    integer :: nx = 16 * 4
    ! ny is the j/column-size
    integer :: ny = 64 * 4
    
    contains
    ! uses the property 31*33*1024 = 32*31*992 = 32*33*1056 = 1047552 using gcd properties
    SUBROUTINE set_nx_ny(mode,iters)
        use benchmark_names
        integer, intent(in) :: mode
        integer, intent(out) :: iters
        select case (mode)
            case (SMALLER_THAN_L3)
                nx = 128 * l3_size_in_mib
                ny = 128
                ! here we adjust iters to use roughly as many computations as with 1024*1024
                iters = 31*33 * (1024**2 / 128**2)
                iters = iters / BENCHMARK_ACCELERATION
            case (SLIGHTLY_SMALLER_THAN_L3)
                nx = 1024 * l3_size_in_mib
                ny = 992
                ! iters chosen to compensate change in ny
                iters = 32*33 / BENCHMARK_ACCELERATION
            case (SLIGHTLY_BIGGER_THAN_L3)
                nx = 1024 * l3_size_in_mib
                ny = 1056
                ! iters chosen to compensate change in ny
                iters = 32*31 / BENCHMARK_ACCELERATION
            case (BIGGER_THAN_L3)
                nx = 1024 * 3 * l3_size_in_mib
                ny = 992
                iters = 32*33 / BENCHMARK_ACCELERATION
                ! here we adjust to get back to 1024*1056
                iters = iters / 3
            case DEFAULT
        end select
    END SUBROUTINE
    SUBROUTINE set_1D_size(mode,size,iters)
        use benchmark_names
        integer, intent(in) :: mode
        integer, intent(out) :: size, iters
        select case (mode)
            case (SMALLER_THAN_L3)
                size = 128 * 128 * l3_size_in_mib
                iters = (31*33 * (1024**2 / 128**2) / BENCHMARK_ACCELERATION)
            case (SLIGHTLY_SMALLER_THAN_L3)
                size = 1024 * 992 * l3_size_in_mib
                iters =  32*33 / BENCHMARK_ACCELERATION
            case (SLIGHTLY_BIGGER_THAN_L3)
                size = 1024 * 1056 * l3_size_in_mib
                iters =  32*31 / BENCHMARK_ACCELERATION
            case (BIGGER_THAN_L3)
                size = 1024 * 992 * 3 * l3_size_in_mib
                iters = (32*33 / BENCHMARK_ACCELERATION) / 3
            case DEFAULT
        end select
    END SUBROUTINE

END MODULE benchmark_parameters