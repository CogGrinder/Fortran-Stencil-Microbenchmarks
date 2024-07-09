! this value is a power of 2 between 1 and 32 - recommended is 32
#define BENCHMARK_ACCELERATION 32
#include "benchmark_compilation_fixed_parameters.h"

MODULE benchmark_parameters

    ! here set your processor's L3 cache size in Mib - useful for modes 100 to 103
    integer, parameter :: l3_size_in_mib = 6

#if SIZE_AT_COMPILATION==1
    contains
    SUBROUTINE set_2D_size(niinput,njinput)
        integer, intent(in) :: niinput
        integer, intent(in) :: njinput
        write(*,*) "SIZE_AT_COMPILATION successfully set to 1"
    END SUBROUTINE
    SUBROUTINE set_1D_size(n1dinput)
        integer, intent(in) :: n1dinput
        write(*,*) "SIZE_AT_COMPILATION successfully set to 1"
    END SUBROUTINE
#else
    !  1D size
    integer :: n1d
    !  2D size
    integer :: ni,nj
    contains
    SUBROUTINE set_2D_size(niinput,njinput)
        integer, intent(in) :: niinput
        integer, intent(in) :: njinput
        ni = niinput
        nj = njinput
    END SUBROUTINE
    SUBROUTINE set_1D_size(n1dinput)
        integer, intent(in) :: n1dinput
        n1d = n1dinput
    END SUBROUTINE
#endif /* end of SIZE_AT_COMPILATION*/
END MODULE benchmark_parameters