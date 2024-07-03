import sys
import os
import shutil
from shutil import copytree as copy_tree
import pathlib
import shlex
import shutil
import json
from typing import Union

DEBUG = False

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
src = pathlib.Path("../src/")
mainfile = pathlib.Path("../main.f90")
if DEBUG:
    mainfile = pathlib.Path("../main.test.f90")
makefile = pathlib.Path("../Makefile")


def codegen_bench_tree_branch(alloc_option: str, size_option: Union[int, str], iters=42, compilation_time_size=False):
    """ TODO: Comment function
    """
    if alloc_option in allocation_suffixes.keys()\
        and (size_option in size_suffixes.keys() or int(size_option) in range(0,100)) :

        alloc_directory = f"bench_tree/bench_execution{allocation_suffixes[alloc_option]}"
        if not pathlib.Path(alloc_directory).is_dir() :
            os.mkdir(alloc_directory)
        
        # size_suffix in the _01Mb format or _{option suffix} format
        size_suffix = "_"+str(size_option).zfill(2)+"Mb"\
            if (size_option!="" and int(size_option) in range(0,100))\
            else size_suffixes[size_option]
        size_directory  = alloc_directory+f"/{size_suffix}"
        if not pathlib.Path(size_directory).is_dir() :
            os.mkdir(size_directory)
        
        # the last depth directory is the full directory
        fulldirectory = size_directory
        print(fulldirectory)

        ######### compilation_time_size #########
        if compilation_time_size :
            fulldirectory_absolute = pathlib.Path(fulldirectory).resolve()
            print(fulldirectory_absolute)
            shutil.copytree(src.resolve(),str(fulldirectory_absolute)+"/src",dirs_exist_ok=True)
            shutil.copy2(mainfile.resolve(),fulldirectory_absolute)
            shutil.copy2(makefile.resolve(),fulldirectory_absolute)


        filename = f"{fulldirectory}/run.sh"
        f = open(filename, "w")
        os.chmod(filename,0b111111111)
        

        # see https://realpython.com/python-f-strings/
        f.write(f"""#! /bin/bash

# set BENCH_EXECUTABLE and PERF_REGIONS
export PERF_REGIONS="../{"../"*(tree_depth+2)}perf_regions"
export BENCH_MAKE_DIR="{"." if compilation_time_size else "../"*(tree_depth+2)}"
export BENCH_EXECUTABLE="{"" if compilation_time_size else "../"*(tree_depth+2)}bin/bench{allocation_suffixes[alloc_option]}{size_suffix}"

# set perf_regions variables here
export PERF_REGIONS_VERBOSITY=0
export PERF_REGIONS_MAX=256

export LD_LIBRARY_PATH="$PERF_REGIONS/build:$LD_LIBRARY_PATH"
export PERF_REGIONS_COUNTERS=""
export PERF_REGIONS_COUNTERS="PAPI_L1_TCM,PAPI_L2_TCM,PAPI_L3_TCM,WALLCLOCKTIME"

export ALLOC_MODE="{alloc_option}"
export SIZE_MODE="{size_option}"
export SIZE_AT_COMPILATION="{int(compilation_time_size)}"

make -C $BENCH_MAKE_DIR bin/bench{allocation_suffixes[alloc_option]}{size_suffix} {"_PERF_REGIONS_FOLDER=../"+ "../"*(tree_depth+2)+"perf_regions" if compilation_time_size else ""}

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
    param = ""
    param2 = ""
    all_parameters = {}
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
    elif param in ["all_old","all_no_compilation_time"]:
        # shutil.rmtree("bench_tree")
        print(f"Creating all benchmark scripts...")
        codegen_bench_tree_branch("","")
        for alloc_option in allocation_suffixes.keys() :
            for size_option in range(1,17) :
                filename = codegen_bench_tree_branch(alloc_option,size_option)
                all_parameters[filename] = {"size_option": size_option, "alloc_option": alloc_option, "iters": 42}
    elif param in ["all","all_compilation_time"]:
        # shutil.rmtree("bench_tree")
        print(f"Creating all benchmark scripts...")
        codegen_bench_tree_branch("","")
        for alloc_option in allocation_suffixes.keys() :
            for size_option in range(1,4) :
                filename = codegen_bench_tree_branch(alloc_option,size_option,compilation_time_size=True)
                all_parameters[filename] = {"size_option": size_option, "alloc_option": alloc_option, "iters": 42, "compilation_time_size": True}
    elif param == "all_l3":
        # shutil.rmtree("bench_tree")
        print(f"Creating all benchmark scripts...")
        for alloc_option in allocation_suffixes.keys() :
            for size_option in size_suffixes.keys() :
                codegen_bench_tree_branch(alloc_option,size_option)
    else :
        print(f"Creating {phrase} benchmark script...")
        codegen_bench_tree_branch(param,param2)
    filename = "all_benchmark_parameters.json"
    f = open(filename, "w")
    json.dump(all_parameters,f,sort_keys=True, indent=4)
    return 0

# courtesy of https://docs.python.org/fr/3/library/__main__.html
if __name__ == '__main__':
    sys.exit(main())