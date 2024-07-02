import sys
import os
import pathlib
import shlex
import shutil
import json
from typing import Union

allocation_suffixes = { "ALLOC"                 : "_alloc",
                        "STATIC"                : "_static",
                        ""                      : "_defaultalloc"}
size_suffixes =       { "SMALLER_THAN_L3"           : "_smallerl3",
                        "SLIGHTLY_SMALLER_THAN_L3"  : "_ssmallerl3",
                        "SLIGHTLY_BIGGER_THAN_L3"   : "_sbiggerl3",
                        "BIGGER_THAN_L3"            : "_biggerl3",
                        ""                          : "_defaultsize"}
# dictionary containing number related to size identifier
# thank you Abhijit at https://stackoverflow.com/questions/36459969/how-to-convert-a-list-to-a-dictionary-with-indexes-as-values
size_mode_number = {k: v+100 for v, k in enumerate(size_suffixes.keys())}

tree_depth = 2


def codegen_bench_tree_branch(alloc_option: str, size_option: Union[int, str]):
    """ TODO: Comment function
    """
    if alloc_option in allocation_suffixes.keys()\
        and (size_option in size_suffixes.keys() or int(size_option) in range(0,100)) :

        alloc_directory = f"bench_tree/bench_execution{allocation_suffixes[alloc_option]}"
        if not pathlib.Path(alloc_directory).is_dir() :
            os.mkdir(alloc_directory)
        
        size_suffix = "_"+str(size_option).zfill(2)+"Mb" if (size_option!="" and int(size_option) in range(0,100)) else size_suffixes[size_option]
        size_directory  = alloc_directory+f"/{size_suffix}"
        if not pathlib.Path(size_directory).is_dir() :
            os.mkdir(size_directory)
        
        # the last depth directory is the full directory
        fulldirectory = size_directory
        print(fulldirectory)

        filename = f"{fulldirectory}/run.sh"
        f = open(filename, "w")
        os.chmod(filename,0b111111111)
        

        # see https://realpython.com/python-f-strings/
        f.write(f"""#! /bin/bash

# set BENCH_EXECUTABLE and PERF_REGIONS
export PERF_REGIONS="../{"../"*(tree_depth+2)}perf_regions"
export BENCH_MAKE_DIR="{"../"*(tree_depth+2)}"
export BENCH_EXECUTABLE="{"../"*(tree_depth+2)}bin/bench{allocation_suffixes[alloc_option]}{size_suffix}"

# set perf_regions variables here
export PERF_REGIONS_VERBOSITY=0
export PERF_REGIONS_MAX=256

export LD_LIBRARY_PATH="$PERF_REGIONS/build:$LD_LIBRARY_PATH"
export PERF_REGIONS_COUNTERS=""
export PERF_REGIONS_COUNTERS="PAPI_L1_TCM,PAPI_L2_TCM,PAPI_L3_TCM,WALLCLOCKTIME"

export ALLOC_MODE="{alloc_option}"
export SIZE_MODE="{size_option}"

make -C $BENCH_MAKE_DIR bin/bench{allocation_suffixes[alloc_option]}{size_suffix}

filename=out

# for sizemode in 0 1 2 3
# do
    echo "Running mode {size_suffix}..."    
    # ./$BENCH_EXECUTABLE
    # thank you to glenn jackman's answer on https://stackoverflow.com/questions/5853400/bash-read-output
    while IFS= read -r line; do
        echo "$line"
        if [ "${{line:0:1}}" != " " ]
        then
            echo "$line" >> $filename.csv
        fi
        # grep -o 'action'
    done < <( ./$BENCH_EXECUTABLE )
    # |  grep -A100 Section | paste >> $filename.csv
# done
echo
# cat $filename.csv
""")
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
    # file_test()
    # thank you to https://www.knowledgehut.com/blog/programming/sys-argv-python-examples#how-to-use-sys.argv-in-python?
    param = ""
    param2 = ""
    if len(sys.argv) >= 2:
        param = sys.argv[1]
    if len(sys.argv) >= 3:
        param2 = sys.argv[2]
    
    if not pathlib.Path("bench_tree").is_dir() :
        os.mkdir("bench_tree")
    
    if param == "clean":
        print("Cleaning benchmark script tree... Y/n ?")
        if (str(input()) == "Y") :
            shutil.rmtree("bench_tree")
            print("Cleaned")
        else :
            print("Aborted")
    elif param == "all":
        # shutil.rmtree("bench_tree")
        print(f"Creating all benchmark scripts...")
        codegen_bench_tree_branch("","")
        all_parameters = {}
        for alloc_option in allocation_suffixes.keys() :
            for size_option in range(1,17) :
                # TODO: all_parameters[param_id] = {"size_otion": size_option, alloc_otion: ...}
                codegen_bench_tree_branch(alloc_option,size_option)
    elif param == "all_l3":
        # shutil.rmtree("bench_tree")
        print(f"Creating all benchmark scripts...")
        for alloc_option in allocation_suffixes.keys() :
            for size_option in size_suffixes.keys() :
                codegen_bench_tree_branch(alloc_option,size_option)
    else :
        print(f"Creating {phrase} benchmark script...")
        codegen_bench_tree_branch(param,param2)
    json.dump(all_parameters)
    return 0

# courtesy of https://docs.python.org/fr/3/library/__main__.html
if __name__ == '__main__':
    sys.exit(main())