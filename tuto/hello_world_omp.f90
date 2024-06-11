! credit to https://curc.readthedocs.io/en/latest/programming/OpenMP-Fortran.html
! note : upper case and lower case commands seem to be up to taste, like in SQL

#define LENGTH 1024*256

PROGRAM omp
    USE OMP_lib
    integer :: main_thread, thread_num, sum, target_devices
    integer, dimension(LENGTH) :: A, B, C
    main_thread = 0
  
    !$omp parallel private(thread_num) firstprivate(main_thread)
    thread_num = omp_get_thread_num()
    PRINT *, 'Hello World ! thread n°', thread_num
  
    ! note : can use .eq. for ==
    if (thread_num == main_thread) then
      PRINT *, 'Number of threads : ', omp_get_num_threads()

      PRINT *, 'Number of target devices : ', omp_get_num_devices()
      ! example from "Programming Your GPU with OpenMP" byt T.Deakin and T.G.Mattson page 62
      ! dependencies :
      ! https://developer.nvidia.com/cuda-downloads
      ! gcc-offload-nvptx
      ! warning : nvcc version or cuda toolkit
      ! dont use nvidia-cuda-toolkit seems to be too old
      ! find /usr -type d -name cuda


      !$omp target firstprivate(A,B,C)
      do k = 1, LENGTH
        do i = 1, LENGTH
          C(i) = A(i) + B(i)
        end do
      end do
      
      ! sum = 0
      ! do i = 1, LENGTH
      !   sum = sum + C(i)
      ! end do
      write (*,*) "C LENGTH=", C(LENGTH)
      !$omp end target
    end if
    !$omp end parallel
end PROGRAM omp