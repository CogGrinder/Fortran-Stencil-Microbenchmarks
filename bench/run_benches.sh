#! /bin/bash

# set BENCH_EXECUTABLE and PERF_REGIONS
export PERF_REGIONS="../perf_regions"
export BENCH_EXECUTABLE=main
# set verbosity here
export PERF_REGIONS_VERBOSITY=1

export PERF_REGIONS_MAX=256

export LD_LIBRARY_PATH="$PERF_REGIONS/build:$LD_LIBRARY_PATH"
export PERF_REGIONS_COUNTERS=""
export PERF_REGIONS_COUNTERS="PAPI_L1_TCM,PAPI_L2_TCM,PAPI_L3_TCM,WALLCLOCKTIME"

./$BENCH_EXECUTABLE
# TODO : add all new benchmarks to file.csv
# ./$BENCH_EXECUTABLE |  grep TEST_BENCH | paste -sd ',\t' >> file.csv
# ./$BENCH_EXECUTABLE 0 1 2 3
# ./$BENCH_EXECUTABLE 0 1 2 3 |  grep -A100 Section | paste >> file.csv
# cat file.csv



#### Generate variance data for PAPI_L3_TCM and a point of comparison of allocatable and fixed arrays
# for i in {1..10}
# do
#     echo "Running time ${i}..."
#     ./$BENCH_EXECUTABLE 0
#     ./$BENCH_EXECUTABLE 1
#     ./$BENCH_EXECUTABLE 1
#     ./$BENCH_EXECUTABLE 0
#     # ./$BENCH_EXECUTABLE 0 1
#     # ./$BENCH_EXECUTABLE 0 1 |  grep -A100 Section | paste >> BENCH_0_BENCH_1_variance.csv
# done
# cat BENCH_0_BENCH_1_variance.csv
# for i in {1..10}
# do
#     echo "Running time ${i}..."
#     ./$BENCH_EXECUTABLE iters=1024 0 iters=1024 1 |  grep -A100 Section | paste >> 1D_FIXD_1D_ALOC_variance.csv
# done
# cat 1D_FIXD_1D_ALOC_variance.csv

# ./$BENCH_EXECUTABLE iters=128 0
# ./$BENCH_EXECUTABLE iters=128 1

#### Bugged module access to perf_regions ####
# ./$BENCH_EXECUTABLE iters=128 4
