#include "include/compilation_fixed_parameters.h"

MODULE BENCHMARK_PARAMETERS

    !!!!!!! declare execution time loop bounds and array sizes when necessary !!!!!!
#if SIZE_AT_COMPILATION!=1
    !  1D size
    integer :: n1d
    !  2D size
    integer :: ni,nj
#endif

#if LOOP_BOUND_AT_COMPILATION!=1
    !  1D size
    integer :: loop_bound_n1d
    !  2D size
    integer :: loop_bound_ni,loop_bound_nj
#endif

    ! TODO: change to support loop bounds at compilation
    contains

    !!!!!!! set execution time loop bounds and array sizes when necessary !!!!!!
    SUBROUTINE set_2D_size_and_loop_bounds(niinput,njinput)
        integer, intent(in) :: niinput
        integer, intent(in) :: njinput
#if SIZE_AT_COMPILATION==1
        ! sizes set through preprocessing        
        write(*,*) "SIZE_AT_COMPILATION successfully set to 1, sizes set through preprocessing"
#else
        ni = niinput
        nj = njinput
#endif
#if LOOP_BOUND_AT_COMPILATION==1
        ! loop bounds set through preprocessing        
        write(*,*) "LOOP_BOUND_AT_COMPILATION successfully set to 1, loop bounds set through preprocessing"
#else
        loop_bound_ni = niinput
        loop_bound_nj = njinput
#endif
    END SUBROUTINE

    SUBROUTINE set_1D_size_and_loop_bounds(n1dinput)
        integer, intent(in) :: n1dinput
#if SIZE_AT_COMPILATION==1
        ! sizes set through preprocessing        
        write(*,*) "SIZE_AT_COMPILATION successfully set to 1, sizes set through preprocessing"
#else
        n1d = n1dinput
#endif
#if LOOP_BOUND_AT_COMPILATION==1
        ! loop bounds set through preprocessing        
        write(*,*) "LOOP_BOUND_AT_COMPILATION successfully set to 1, loop bounds set through preprocessing"
#else
        loop_boun_n1d = n1dinput
#endif /* LOOP_BOUND_AT_COMPILATION*/
    END SUBROUTINE

END MODULE BENCHMARK_PARAMETERS