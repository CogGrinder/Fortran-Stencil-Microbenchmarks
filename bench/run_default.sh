#! /bin/bash

# set BENCH_EXECUTABLE and PERF_REGIONS
export PERF_REGIONS="src/perf_regions"
export BENCH_MAKE_DIR="."
export BENCH_EXECUTABLE="bin/bench_default"

# set perf_regions variables here
export PERF_REGIONS_VERBOSITY=0
export PERF_REGIONS_MAX=256

export LD_LIBRARY_PATH="$PERF_REGIONS/build:$LD_LIBRARY_PATH"
export PERF_REGIONS_COUNTERS=""
export PERF_REGIONS_COUNTERS="PAPI_L1_TCM,PAPI_L2_TCM,PAPI_L3_TCM,WALLCLOCKTIME"
# Uncomment for non-PAPI:
# export PERF_REGIONS_COUNTERS="WALLCLOCKTIME"

export ALLOC_MODE=DEFAULT_ALLOC
export MODULE_MODE="1"
export SIZE_AT_COMPILATION="0"
export NI="4096"
export NJ="4096"
export KERNEL_MODE=""

make -C $BENCH_MAKE_DIR clean 
make -C $BENCH_MAKE_DIR print_main 
make -C $BENCH_MAKE_DIR main $1
# make -C $BENCH_MAKE_DIR main
# make -C $BENCH_MAKE_DIR main F90=nvfortran


filename=out

echo "Running mode _defaultsize..."    
ls
# thank you to glenn jackman's answer on https://stackoverflow.com/questions/5853400/bash-read-output
while IFS= read -r line; do
    echo "$line"
    if [ "${line:0:1}" != " " ]
    then
        echo "$line" >> $filename.csv
    fi
done < <( ./$BENCH_EXECUTABLE iters=64 ni=4096 nj=4096 )