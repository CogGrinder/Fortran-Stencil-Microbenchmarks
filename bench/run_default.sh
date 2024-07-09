#! /bin/bash

# set BENCH_EXECUTABLE and PERF_REGIONS
export PERF_REGIONS="../perf_regions"
export BENCH_MAKE_DIR="."
export BENCH_EXECUTABLE="bin/bench_defaultalloc_defaultsize_sizenotcompiled_defaultkernel"

# set perf_regions variables here
export PERF_REGIONS_VERBOSITY=0
export PERF_REGIONS_MAX=256

export LD_LIBRARY_PATH="$PERF_REGIONS/build:$LD_LIBRARY_PATH"
export PERF_REGIONS_COUNTERS=""
export PERF_REGIONS_COUNTERS="PAPI_L1_TCM,PAPI_L2_TCM,PAPI_L3_TCM,WALLCLOCKTIME"
# Uncomment for non-PAPI:
# export PERF_REGIONS_COUNTERS="WALLCLOCKTIME"

export ALLOC_MODE=""
export SIZE_MODE=""
export SIZE_AT_COMPILATION="0"
export NI="4096"
export NJ="4096"
export KERNEL_MODE=""

make -C $BENCH_MAKE_DIR clean 
make -C $BENCH_MAKE_DIR print_main 
make -C $BENCH_MAKE_DIR bin/bench_defaultalloc_defaultsize_sizenotcompiled_defaultkernel

filename=out

echo "Running mode _defaultsize..."    
ls
# ./$BENCH_EXECUTABLE
# thank you to glenn jackman's answer on https://stackoverflow.com/questions/5853400/bash-read-output
while IFS= read -r line; do
    echo "$line"
    if [ "${line:0:1}" != " " ]
    then
        echo "$line" >> $filename.csv
    fi
    # grep -o 'action'
done < <( ./$BENCH_EXECUTABLE iters=16 ni=4096 nj=4096 )
# |  grep -A100 Section | paste >> $filename.csv
echo
# cat $filename.csv
