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

#ifndef SIZE_MODE
# define SIZE_MODE 16 /* default SIZE_MODE in Mb */
#endif

#if         SIZE_MODE == SMALLER_THAN_L3
# define BENCHMARK_SIZE_MODE 100
#elif       SIZE_MODE == SLIGHTLY_SMALLER_THAN_L3
# define BENCHMARK_SIZE_MODE 101
#elif       SIZE_MODE == SLIGHTLY_BIGGER_THAN_L3
# define BENCHMARK_SIZE_MODE 102
#elif       SIZE_MODE == BIGGER_THAN_L3
# define BENCHMARK_SIZE_MODE 103
#elif       SIZE_MODE == NONE
# define BENCHMARK_SIZE_MODE 0
#else
# define BENCHMARK_SIZE_MODE (int(SIZE_MODE)) /* BENCHMARK_SIZE_MODE is SIZE_MODE except when overruled by L3-relative sizes */
#endif /*SIZE_MODE*/

#ifndef SIZE_AT_COMPILATION /* SIZE_AT_COMPILATION only supports SIZE_MODE from 1 to 99 ! TODO: support 3D and 1D */
# define SIZE_AT_COMPILATION 0 /* default is to not determine size at compilation */
#endif
#if SIZE_MODE==0 /* SIZE_AT_COMPILATION does not support SIZE_MODE 0 ie default */
# define SIZE_AT_COMPILATION 0
#endif
#if SIZE_AT_COMPILATION==1
! SIZE_AT_COMPILATION is 1
! use NI and NJ from -D flag
# define ni (NI)
# define nj (NJ)
#endif /*SIZE_AT_COMPILATION*/

! included benchmark_compilation_fixed_parameters.h file
#endif /*BENCH_PARAMS_H*/