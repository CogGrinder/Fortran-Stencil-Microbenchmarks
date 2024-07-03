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
#endif

#ifndef SIZE_AT_COMPILATION /* SIZE_AT_COMPILATION only supports SIZE_MODE from 1 to 99 ! TODO: support 3D and 1D */
# define SIZE_AT_COMPILATION 0 /* default is to not determine size at compilation */
#endif
#if SIZE_MODE==0 /* SIZE_AT_COMPILATION does not support SIZE_MODE 0 ie default */
# define SIZE_AT_COMPILATION 0
#endif
#if SIZE_AT_COMPILATION==1
! SIZE_AT_COMPILATION is 1

# define NX(BENCHMARK_SIZE_MODE) int(sqrt(real(1024*1024*(BENCHMARK_SIZE_MODE))))
# define NY(BENCHMARK_SIZE_MODE,var2) 1024*1024*(BENCHMARK_SIZE_MODE) / (var2)
# define nx NX(BENCHMARK_SIZE_MODE)
# define ny NY(BENCHMARK_SIZE_MODE,NX(BENCHMARK_SIZE_MODE))
#endif
! included .h file