PROGRAM main
    ! USE OMP_lib

    ! thank you to https://www.tutorialspoint.com/fortran/fortran_arrays.htm

    real, dimension(5) :: array

    do i = 1, 5
        call RANDOM_NUMBER(array(i))
    end do
    
    do i = 1, 5
        PRINT *, 'array(', i, ')', thread_num
    end do
  
end PROGRAM main