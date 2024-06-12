! credit to https://curc.readthedocs.io/en/latest/programming/OpenMP-Fortran.html
! note : upper case and lower case commands seem to be up to taste, like in SQL

#define LENGTH 1024*32
! #define LENGTH 256

PROGRAM omp
    USE OMP_lib
    integer :: main_thread, thread_num, sum, target_devices
    ! allocatable seems to be necessary for CUDA target pragma
    integer, allocatable :: A(:), B(:), C(:)
    allocate(A(LENGTH))
    allocate(B(LENGTH))
    allocate(C(LENGTH))
    
    main_thread = 0
  
    !$omp parallel firstprivate(A,B,C) private(thread_num) firstprivate(main_thread)
    thread_num = omp_get_thread_num()
    PRINT *, 'Hello World ! thread n°', thread_num
  
    ! note : can use .eq. for ==
    if (thread_num == main_thread) then
      PRINT *, 'Number of threads : ', omp_get_num_threads()

      PRINT *, 'Number of target devices : ', omp_get_num_devices()
      ! example from "Programming Your GPU with OpenMP" byt T.Deakin and T.G.Mattson page 62
      ! dependencies :
      ! https://developer.nvidia.com/cuda-downloads


      ! modified
      write (*,*) "entering target..."
      !$omp loop bind(thread) private(A,B,C)
      do k = 1, LENGTH
        do i = 1, LENGTH
          ! write (*,*) "entered target loop..."
          
          C(i) = A(i) + B(i)
        end do
      end do
      sum = 0
      do i = 1, LENGTH
        sum = sum + C(i)
      end do
      write (*,*) "C sum :", sum
      !!$omp end target
    end if
  !$omp end parallel

  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  ! examples from https://docs.nvidia.com/hpc-sdk/compilers/hpc-compilers-user-guide/index.html#openmp-use
  write(*,*) "!$omp target teams loop "
  !$omp target teams loop 
  do n1loc_blk = 1, n1loc_blksize
    do igp = 1, ngpown 
      do ig_blk = 1, ig_blksize 
        do ig = ig_blk, ncouls, ig_blksize
          do n1_loc = n1loc_blk, ntband_dist, n1loc_blksize
            !expensive computation codes           
          enddo 
        enddo 
      enddo 
    enddo 
  enddo
  write(*,*) "!$omp target teams loop collapse(3)"
  write(*,*) "with !$omp loop bind(parallel) collapse(2)"
  !$omp target teams loop collapse(3)
  do n1loc_blk = 1, n1loc_blksize
    do igp = 1, ngpown 
      do ig_blk = 1, ig_blksize 
        !$omp loop bind(parallel) collapse(2)
        do ig = ig_blk, ncouls, ig_blksize
          do n1_loc = n1loc_blk, ntband_dist, n1loc_blksize
            !expensive computation codes           
          enddo 
        enddo 
      enddo 
    enddo 
  enddo
  write(*,*) "!$omp target teams loop collapse(3)"
  write(*,*) "with !$omp loop bind(thread) collapse(2)"
  !$omp target teams loop collapse(3)
  do n1loc_blk = 1, n1loc_blksize
    do igp = 1, ngpown 
      do ig_blk = 1, ig_blksize 
        !$omp loop bind(thread) collapse(2)
        do ig = ig_blk, ncouls, ig_blksize
          do n1_loc = n1loc_blk, ntband_dist, n1loc_blksize
            ! expensive computation codes           
          enddo 
        enddo 
      enddo 
    enddo 
  enddo

end PROGRAM omp