#! /bin/bash

# set BENCH_EXECUTABLE and PERF_REGIONS
export PERF_REGIONS="../perf_regions"
export BENCH_EXECUTABLE="main"

export LD_LIBRARY_PATH="$PERF_REGIONS/build:$LD_LIBRARY_PATH"
export PERF_REGIONS_COUNTERS=""
export PERF_REGIONS_COUNTERS="PAPI_L1_TCM,PAPI_L2_TCM,PAPI_L3_TCM,WALLCLOCKTIME"

# ./$BENCH_EXECUTABLE
# TODO : add all new benchmarks to file.csv
# ./$BENCH_EXECUTABLE |  grep TEST_BENCH | paste -sd ',\t' >> file.csv
./$BENCH_EXECUTABLE 0 1 2 3
# ./$BENCH_EXECUTABLE 0 1 2 3 |  grep -A100 Section | paste >> file.csv
cat file.csv
