!#define DEBUG

PROGRAM main
    ! thank you to https://www.tutorialspoint.com/fortran/fortran_arrays.htm

    real, dimension(10) :: array
    real, dimension(10) :: result
    integer, dimension(3) :: stencil
    integer :: stencil_sum, len
    stencil = (/ 1, 0, 1/)
    len = 3 ! must be odd
    stencil_sum = 2


    do i = 1, 10
        call RANDOM_NUMBER(array(i))
    end do
    
    ! example for formatting :
    ! I5 for a 5-digit integer.
    ! F10.4 for a floating-point number with 10 total characters, including 4 digits after the decimal point.
    ! A for a character string.
    ! 100 format(I5, F10.4, A)
    
#ifdef DEBUG
    1 format(I2, I2)
#endif

    do i = 1, 10-len+1
        result(i + len/2) = 0
        do j = 1,len
#ifdef DEBUG
            write(6, 1, advance="no") j, i-len/2 + j
#endif
            ! TODO : is there a += operator ?
            result(i + len/2) = result(i + len/2) + stencil(j) * array(i-len/2 + j)
        end do
#ifdef DEBUG        
        write(*,*) " at index " , i + len/2
#endif
    end do
    ! we ignore edges in the computation which explains the shift in indexes

    ! normalize by stencil_sum
    do i = 1, 10
        result(i) = result(i)/stencil_sum
    end do
    
    

    do i = 1, 10
        PRINT *, 'array(', i, ')', array(i)
    end do

    do i = 1, 10
        PRINT *, 'result(', i, ')', result(i)
    end do
  
end PROGRAM main