! credit to https://curc.readthedocs.io/en/latest/programming/OpenMP-Fortran.html
! note : upper case and lower case commands seem to be up to taste, like in SQL
PROGRAM omp
    USE OMP_lib
    integer :: main_thread, thread_num
    main_thread = 0
  
    !$omp parallel private(thread_num) firstprivate(main_thread)
    thread_num = omp_get_thread_num()
    PRINT *, 'Hello World ! thread n°', thread_num
  
    ! note : can use .eq. for ==
    if (thread_num == main_thread) then
      PRINT *, 'Number of threads : ', omp_get_num_threads()
    endif
    !$omp end parallel
end PROGRAM omp