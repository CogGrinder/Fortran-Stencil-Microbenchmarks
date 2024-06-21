#! /bin/bash

# set BENCH_EXECUTABLE and PERF_REGIONS
export PERF_REGIONS="../../perf_regions"
export BENCH_MAKE_DIR="../"
export BENCH_EXECUTABLE=../bin/bench_alloc

# set perf_regions variables here
export PERF_REGIONS_VERBOSITY=0
export PERF_REGIONS_MAX=256

export LD_LIBRARY_PATH="$PERF_REGIONS/build:$LD_LIBRARY_PATH"
export PERF_REGIONS_COUNTERS=""
export PERF_REGIONS_COUNTERS="PAPI_L1_TCM,PAPI_L2_TCM,PAPI_L3_TCM,WALLCLOCKTIME"

make -C $BENCH_MAKE_DIR ALLOC_MODE=ALLOC

filename=array_alloc

description=( SMALLER_THAN_L3 SLIGHTLY_SMALLER_THAN_L3 SLIGHTLY_BIGGER_THAN_L3 BIGGER_THAN_L3 )

for sizemode in 0 1 2 3
do
    echo "Running mode ${description[sizemode]}..."
    echo -e "MODE\t${description[sizemode]}" >> $filename.csv
    
    # ./$BENCH_EXECUTABLE sizemode=${sizemode} 3 4 5 6
    # thank you to glenn jackman's answer on https://stackoverflow.com/questions/5853400/bash-read-output
    while IFS= read -r line; do
        echo "$line"
        if [ "${line:0:1}" != " " ]
        then
            echo "$line" >> $filename.csv
        fi
        # grep -o 'action'
    done < <( ./$BENCH_EXECUTABLE sizemode=${sizemode} 3 4 5 6 )
    # |  grep -A100 Section | paste >> $filename.csv
done
echo
cat $filename.csv