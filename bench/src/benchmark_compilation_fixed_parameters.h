#ifndef BENCH_PARAMS_H
#define BENCH_PARAMS_H

!!!!!! preprocessor option names
#define NONE 0 /* acts as default */

! bench names
#define BENCH_1D 0
#define BENCH_1D_MODULE 1

#define BENCH_2D_CPU_JI 3
#define BENCH_2D_CPU_IJ 4
#define BENCH_2D_CPU_MODULE_STATIC 5
#define BENCH_2D_CPU_MODULE 6
    
#define BENCH_2D_GPU_OMP_BASE 7


! hardware type
#define CPU 1
#define GPU 2

! allocation type
#define ALLOCATABLE 1
#define STATIC 2
#define DEFAULT_ALLOC ALLOCATABLE /* default is allocatable */
#ifndef ALLOC_MODE
# define ALLOC_MODE DEFAULT_ALLOC
#endif

! 2D kernels
#define DEFAULT_KERNEL 0
#define X_KERNEL 1
#define Y_KERNEL 2
#define SIZE_5_KERNEL 5
#define NO_INCLUDE -1

#ifndef KERNEL_MODE
! no KERNEL_MODE, preprocessing incomplete
#endif

#ifndef SIZE_AT_COMPILATION /* SIZE_AT_COMPILATION only supports SIZE_MODE from 1 to 99 ! TODO: support 3D and 1D */
# define SIZE_AT_COMPILATION 0 /* default is to not determine size at compilation */
#endif
#if SIZE_AT_COMPILATION==1
! SIZE_AT_COMPILATION is 1
! use NI and NJ from -D flag
# define ni (NI)
# define nj (NJ)
#endif /*SIZE_AT_COMPILATION*/

#endif /*BENCH_PARAMS_H*/