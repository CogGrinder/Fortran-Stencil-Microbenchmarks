#ifndef BENCH_PARAMS_H
#define BENCH_PARAMS_H

#define NONE 0
#define ALLOC 1
#define STATIC 2

#define SMALLER_THAN_L3 100
#define SLIGHTLY_SMALLER_THAN_L3 101
#define SLIGHTLY_BIGGER_THAN_L3 102
#define BIGGER_THAN_L3 103

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

! included benchmark_compilation_fixed_parameters.h file
#endif /*BENCH_PARAMS_H*/