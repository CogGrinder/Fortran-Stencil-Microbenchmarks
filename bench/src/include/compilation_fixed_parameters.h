#ifndef COMPILATION_FIXED_PARAMETERS_H
#define COMPILATION_FIXED_PARAMETERS_H

! define "PREPROCESSOR_DEBUG" to show values received by preprocessor
#ifdef PREPROCESSOR_DEBUG
# warning Not compilable with "PREPROCESSOR_DEBUG" active
dim DIM
module MODULE_MODE
allocation ALLOC_MODE
compilation SIZE_AT_COMPILATION
kernel_mode KERNEL_MODE
#endif

! replace execution time parameters by compile time ones
#ifndef SIZE_AT_COMPILATION
# define SIZE_AT_COMPILATION 0 /* default is to not determine size at compilation */
#endif
#if SIZE_AT_COMPILATION==1
! use NI and NJ determined at compile time
# define n1d (NI * NJ)
# define ni NI
# define nj NJ
! TODO: support 3D and 1D
#endif /*SIZE_AT_COMPILATION*/

!!!!!! preprocessor option names !!!!!!
#define NONE 0 /* acts as default */

! dim - range from 1 to 2, 3 not yet implemented
#ifndef DIM
#define DIM 2
#endif

! bench names
#define BENCH_1D 0
#define BENCH_1D_MODULE 1

#define BENCH_2D_CPU_JI 3
#define BENCH_2D_CPU_IJ 4
#define BENCH_2D_CPU_MODULE 6
    
#define BENCH_2D_GPU_OMP_BASE 7


! hardware type
#define CPU 1
#define GPU 2

#ifndef HARDWARE
#define HARDWARE CPU
#endif

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
# define KERNEL_MODE DEFAULT_KERNEL
#endif

#endif /*COMPILATION_FIXED_PARAMETERS_H*/