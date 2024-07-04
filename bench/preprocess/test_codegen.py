import sys
import os
import shutil
from shutil import copytree as copy_tree
import pathlib
import shlex
import shutil
import json
from typing import Union
import math

DEBUG = False

# this parameter is used for readable implementation of relative directories, with "../" prefixes
TREE_DEPTH = 3

allocation_suffixes = { "ALLOC"                 : "_alloc",
                        "STATIC"                : "_static",
                        ""                      : "_defaultalloc"}
size_suffixes =       { "SMALLER_THAN_L3"           : "_smallerl3",
                        "SLIGHTLY_SMALLER_THAN_L3"  : "_ssmallerl3",
                        "SLIGHTLY_BIGGER_THAN_L3"   : "_sbiggerl3",
                        "BIGGER_THAN_L3"            : "_biggerl3",
                        ""                          : "_defaultsize"}

is_compilation_time_size_suffixes = { False     : "_sizenotcompiled",
                        True                    : "_sizecompiled",
                        ""                      : "_defaultcompilation"}

# dictionary containing number related to size identifier
# thank you Abhijit at https://stackoverflow.com/questions/36459969/how-to-convert-a-list-to-a-dictionary-with-indexes-as-values
size_mode_number = {k: v+100 for v, k in enumerate(size_suffixes.keys())}

src = pathlib.Path("../src/")
mainfile = pathlib.Path("../main.f90")
if DEBUG:
    mainfile = pathlib.Path("../main.test.f90")
makefile = pathlib.Path("../Makefile")


def codegen_bench_tree_branch(alloc_option: str, size_option: Union[int, str], iters=42, is_compilation_time_size=False):
    """ TODO: Comment function
    """
    if alloc_option in allocation_suffixes.keys()\
        and (size_option in size_suffixes.keys() or int(size_option) in range(0,100)) :

        # first depth is allocation_type TODO : make it CPU/GPU once that is functional
        directory = f"bench_tree/bench_execution{allocation_suffixes[alloc_option]}"
        if not pathlib.Path(directory).is_dir() :
            os.mkdir(directory)
        
        # size_suffix in the _01Mb format or _{option suffix} format
        size_suffix = "_"+str(size_option).zfill(2)+"Mb"\
            if (size_option!="" and int(size_option) in range(0,100))\
            else size_suffixes[size_option]
        directory += f"/{size_suffix}"
        if not pathlib.Path(directory).is_dir() :
            os.mkdir(directory)
        
        # adding compilation_size_suffix
        directory += f"/{is_compilation_time_size_suffixes[is_compilation_time_size]}"
        if not pathlib.Path(directory).is_dir() :
            os.mkdir(directory)

        # the last depth directory is the full directory
        fulldirectory = directory
        print(fulldirectory)

        ######### is_compilation_time_size #########
        # if we compile array sizes then we need to copy all source files and compile them with special preprocessing
        # see in the f.write() conditionals to change the make directory and BENCH_EXECUTABLE bin directory
        if is_compilation_time_size :
            fulldirectory_absolute = pathlib.Path(fulldirectory).resolve()
            print(fulldirectory_absolute)
            shutil.copytree(src.resolve(),str(fulldirectory_absolute)+"/src",dirs_exist_ok=True)
            shutil.copy2(mainfile.resolve(),fulldirectory_absolute)
            shutil.copy2(makefile.resolve(),fulldirectory_absolute)


        filename = f"{fulldirectory}/run.sh"
        f = open(filename, "w")
        os.chmod(filename,0b111111111)
        
        ####### pre-compilation bench parameters #######
        # here compute the bench parameters for using at compile time if is_compilation_time_size
        if type(size_option)==int:
            nx = int(math.sqrt(1024*1024*(size_option)))
            ny = 1024*1024*(size_option) // nx
            # TODO : compute number of iters here

        # see https://realpython.com/python-f-strings/
        f.write(f"""#! /bin/bash

# set BENCH_EXECUTABLE and PERF_REGIONS
export PERF_REGIONS="../{"../"*(TREE_DEPTH+2)}perf_regions"
export BENCH_MAKE_DIR="{"." if is_compilation_time_size else "../"*(TREE_DEPTH+2)}"
export BENCH_EXECUTABLE="{"" if is_compilation_time_size else "../"*(TREE_DEPTH+2)}bin/bench{allocation_suffixes[alloc_option]}{size_suffix}{is_compilation_time_size_suffixes[is_compilation_time_size]}"

# set perf_regions variables here
export PERF_REGIONS_VERBOSITY=0
export PERF_REGIONS_MAX=256

export LD_LIBRARY_PATH="$PERF_REGIONS/build:$LD_LIBRARY_PATH"
export PERF_REGIONS_COUNTERS=""
export PERF_REGIONS_COUNTERS="PAPI_L1_TCM,PAPI_L2_TCM,PAPI_L3_TCM,WALLCLOCKTIME"

export ALLOC_MODE="{alloc_option}"
export SIZE_MODE="{size_option}"
export SIZE_AT_COMPILATION="{int(is_compilation_time_size)}"
export NX="{nx if type(size_option)==int else ""}"
export NY="{ny if type(size_option)==int else ""}"

make -C $BENCH_MAKE_DIR bin/bench{allocation_suffixes[alloc_option]}{size_suffix}{is_compilation_time_size_suffixes[is_compilation_time_size]} {"_PERF_REGIONS_FOLDER=../"+ "../"*(TREE_DEPTH+2)+"perf_regions" if is_compilation_time_size else ""}

filename=out

echo "Running mode {size_suffix}..."    
ls
# ./$BENCH_EXECUTABLE
# thank you to glenn jackman's answer on https://stackoverflow.com/questions/5853400/bash-read-output
while IFS= read -r line; do
    echo "$line"
    if [ "${{line:0:1}}" != " " ]
    then
        echo "$line" >> $filename.csv
    fi
    # grep -o 'action'
done < <( ./$BENCH_EXECUTABLE iters={iters} )
# |  grep -A100 Section | paste >> $filename.csv
echo
# cat $filename.csv
""")
        f.close()
        return filename
    else:
        raise ValueError("Parameter wrong - read script for more information")


def file_test():
    f = open("test_codegen_run.sh", "r")
    print(f.read())
    return

def main():
    phrase = shlex.join(sys.argv[1:])
    # file_test()
    # thank you to https://www.knowledgehut.com/blog/programming/sys-argv-python-examples#how-to-use-sys.argv-in-python?
    param1 = ""
    param2 = ""
    param3 = ""
    all_alloc_options = list(allocation_suffixes.keys())
    all_alloc_options.remove("")
    all_parameters = {}
    if len(sys.argv) >= 2:
        param1 = sys.argv[1]
    if len(sys.argv) >= 3:
        param2 = sys.argv[2]
    if len(sys.argv) >= 4:
        param2 = sys.argv[3]
    
    if not pathlib.Path("bench_tree").is_dir() :
        os.mkdir("bench_tree")
    
    if param1 == "clean":
        print("Cleaning benchmark script tree... Y/n ?")
        if (str(input()) == "Y") :
            shutil.rmtree("bench_tree")
            print("Cleaned")
        else :
            print("Aborted")
    elif param1 in ["all_old","all_no_compilation_time"]:
        # shutil.rmtree("bench_tree")
        print(f"Creating all benchmark scripts...")
        codegen_bench_tree_branch("","")
        
        for alloc_option in all_alloc_options :
            for size_option in range(1,17) :
                filename = codegen_bench_tree_branch(alloc_option,size_option)
                all_parameters[filename] = {"size_option": size_option,
                                            "alloc_option": alloc_option,
                                            "iters": 42,
                                            "is_compilation_time_size": False}
    elif param1 in ["all","all_compilation_time"]:
        # shutil.rmtree("bench_tree")
        print(f"Creating all benchmark scripts...")
        codegen_bench_tree_branch("","")
        for alloc_option in all_alloc_options :
            for size_option in range(1,17) :
                for is_compilation_time_size in [False,True] :
                    filename = codegen_bench_tree_branch(alloc_option,size_option,\
                                                is_compilation_time_size=is_compilation_time_size)
                    all_parameters[filename] = {"size_option": size_option,
                                                "alloc_option": alloc_option,
                                                "iters": 42,
                                                "is_compilation_time_size": is_compilation_time_size}
    elif param1 == "all_l3":
        # shutil.rmtree("bench_tree")
        print(f"Creating all benchmark scripts...")
        for alloc_option in all_alloc_options :
            for size_option in size_suffixes.keys() :
                for is_compilation_time_size in [False,True] :
                    codegen_bench_tree_branch(alloc_option,size_option,is_compilation_time_size=is_compilation_time_size)
    else :
        print(f"Creating {phrase} benchmark script...")
        codegen_bench_tree_branch(param1,param2)
    filename = "all_benchmark_parameters.json"
    f = open(filename, "w")
    json.dump(all_parameters,f,sort_keys=True, indent=4)
    return 0

# courtesy of https://docs.python.org/fr/3/library/__main__.html
if __name__ == '__main__':
    sys.exit(main())