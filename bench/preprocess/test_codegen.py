import sys
import os
import shlex

mode_suffixes = {   "ALLOC" : "_alloc",
                    "STATIC" : "_static",
                    "" : ""}

def create_bench_run(param):
    if param in ["","ALLOC","STATIC"] :

        f = open("test_codegen_run.sh", "w")
        os.chmod("test_codegen_run.sh",0b111111111)
        # see https://realpython.com/python-f-strings/
        f.write(f"""#! /bin/bash

# set BENCH_EXECUTABLE and PERF_REGIONS
export PERF_REGIONS="../../perf_regions"
export BENCH_MAKE_DIR="../"
export BENCH_EXECUTABLE=../bin/bench{mode_suffixes[param]}

# set perf_regions variables here
export PERF_REGIONS_VERBOSITY=0
export PERF_REGIONS_MAX=256

export LD_LIBRARY_PATH="$PERF_REGIONS/build:$LD_LIBRARY_PATH"
export PERF_REGIONS_COUNTERS=""
export PERF_REGIONS_COUNTERS="PAPI_L1_TCM,PAPI_L2_TCM,PAPI_L3_TCM,WALLCLOCKTIME"

export ALLOC_MODE="{param}"

make -C $BENCH_MAKE_DIR

filename=array_alloc

description=( SMALLER_THAN_L3 SLIGHTLY_SMALLER_THAN_L3 SLIGHTLY_BIGGER_THAN_L3 BIGGER_THAN_L3 )

for sizemode in 0 1 2 3
do
    echo "Running mode ${{description[sizemode]}}..."
    echo -e "MODE\\t${{description[sizemode]}}" >> $filename.csv
    
    # ./$BENCH_EXECUTABLE sizemode=${{sizemode}} 3 4 5 6
    # thank you to glenn jackman's answer on https://stackoverflow.com/questions/5853400/bash-read-output
    while IFS= read -r line; do
        echo "$line"
        if [ "${{line:0:1}}" != " " ]
        then
            echo "$line" >> $filename.csv
        fi
        # grep -o 'action'
    done < <( ./$BENCH_EXECUTABLE sizemode=${{sizemode}} 3 4 5 6 )
    # |  grep -A100 Section | paste >> $filename.csv
done
echo
cat $filename.csv""")
        f.close()
    else:
        raise ValueError("Parameter wrong - read script for more information")

    return

def file_test():
    f = open("test_codegen_run.sh", "r")
    print(f.read())
    return

def main():
    phrase = shlex.join(sys.argv[1:])
    print(f"Creating {phrase} benchmark script...")
    # file_test()
    # thank you to https://www.knowledgehut.com/blog/programming/sys-argv-python-examples#how-to-use-sys.argv-in-python?
    param = ""
    if len(sys.argv) > 1:
        param = sys.argv[1]

    create_bench_run(param)
    return 0

# courtesy of https://docs.python.org/fr/3/library/__main__.html
if __name__ == '__main__':
    sys.exit(main())