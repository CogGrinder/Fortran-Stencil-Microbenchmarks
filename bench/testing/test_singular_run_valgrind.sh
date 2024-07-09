#! /bin/bash

# set BENCH_EXECUTABLE and PERF_REGIONS
export PERF_REGIONS="../../perf_regions"
export BENCH_MAKE_DIR="../"
export BENCH_EXECUTABLE="../bin/bench_defaultalloc_defaultsize_sizenotcompiled_defaultkernel"

# set perf_regions variables here
export PERF_REGIONS_VERBOSITY=0
export PERF_REGIONS_MAX=256

export LD_LIBRARY_PATH="$PERF_REGIONS/build:$LD_LIBRARY_PATH"
export PERF_REGIONS_COUNTERS=""
export PERF_REGIONS_COUNTERS="PAPI_L1_TCM,PAPI_L2_TCM,PAPI_L3_TCM,WALLCLOCKTIME"
# Uncomment for non-PAPI:
# export PERF_REGIONS_COUNTERS="WALLCLOCKTIME"

echo "Running valgrind checher..."    
valgrind --trace-children=yes --show-error-list=yes ./$BENCH_EXECUTABLE iters=16