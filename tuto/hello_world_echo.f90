program test
    integer :: i, bench_id
    ! testing arguments
    ! see https://gcc.gnu.org/onlinedocs/gfortran/GET_005fCOMMAND_005fARGUMENT.html
    character(len=32) :: arg
    character(len=32) :: str1 = "Hello"
    character(len=32) :: str2
    
    
    str2 = str1
    str2(1:1) = 'W'
    write(*,*) str1, str2

    ! print *, "Hello, World!"
    write(*,*) 'Hello, World!'
    ! testing integer division : result is constant integer 1
    write(*,*) '3/2 is ', 3/2 

    i = 1
    do
        call get_command_argument(i,arg)
        if (len_trim(arg) == 0) then
            exit
        else
            read(arg,*) bench_id
        endif

        write (*,*) trim(arg), bench_id
        i = i + 1
    end do
end program test