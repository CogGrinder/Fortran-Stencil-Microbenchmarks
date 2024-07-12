import argparse # see https://docs.python.org/3/library/argparse.html
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

global ACCURACY
ACCURACY = 1

global VERBOSE
VERBOSE = False
global DEBUG
DEBUG = False
L3_SIZE = 16

# this parameter is used for readable implementation of relative directories, with "../" prefixes
TREE_DEPTH = 4

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

kernel_mode_suffixes ={ "X_KERNEL"              : "_xkernel",
                        "Y_KERNEL"              : "_ykernel",
                        "SIZE_5_KERNEL"         : "_size5kernel",
                        "DEFAULT_KERNEL"        : "_defaultkernel",
                        ""                      : "_defaultkernel"}

# dictionary containing number related to size identifier
# thank you Abhijit at https://stackoverflow.com/questions/36459969/how-to-convert-a-list-to-a-dictionary-with-indexes-as-values
size_mode_number = {k: v+100 for v, k in enumerate(size_suffixes.keys())}

src = pathlib.Path("../src/")
mainfile = pathlib.Path("../main.f90")
# if DEBUG:
#     mainfile = pathlib.Path("../main.test.f90")
makefile = pathlib.Path("../Makefile")


def generate_2d_array_size(size_in_mb):
    # default is 16
    if size_in_mb == 0:
        size_in_mb = 16
    ni = int(math.sqrt(1024*1024*(size_in_mb)))
    nj = math.floor(1024*1024*(size_in_mb) // ni)
    return ni,nj

def codegen_bench_tree_branch(alloc_option: str, size_option: Union[int, str],iters=42, is_compilation_time_size=False, kernel_mode=""):
    """Function for generating script that compiles and execute benchmark

    Codegen generates a branch in a folder tree of root 'bench_tree'
    based on all parameters passed, making folders where needed
    using naming conventions defined from suffix dictionaries

    Args:
        alloc_option (str): String that represents the type of allocation used in bench
        size_option (Union[int, str]): Integer or string that represents the size of the arrays
            if non-zero int, corresponds to size in Mb;
            if zero, falls back to default;
            if str, is related to L3 size. TODO : autodetect L3 size
        iters (int, optional): Number of iterations - higher is more precise
            can be left void for adaptive relative to array size. Defaults to 42.
        is_compilation_time_size (bool, optional): Decides wether array size is baked in
            by passing it to compiler directly.
            Size is calculated either in python script and passed
            through preprocessing or calculated in a module at the
            setup step in the execution. Defaults to False.
        kernel_mode (str, optional): String that represents which stencil computation
            kernel is used. Defaults to "".
    """    
    ni=0
    nj=0
    iters=42
    if size_option in size_suffixes.keys() or int(size_option) == 0:
        iters = math.ceil(ACCURACY*32)
    else:
        # max is used to insure there is at least 1 iteration
        iters = max(1,int(ACCURACY*100//size_option))

    if alloc_option in allocation_suffixes.keys()\
        and (size_option in size_suffixes.keys() or int(size_option) in range(0,100)) :

        # directory is represented as an str
        directory = "bench_tree"

        # first depth is allocation_type TODO : make it kernel_mode and then CPU/GPU once that is functional
        directory += f"/bench{allocation_suffixes[alloc_option]}"
        if not pathlib.Path(directory).is_dir() :
            os.mkdir(directory)
        
        # size_suffix in the _01Mb format or _{option suffix} format
        # size_suffix = "_"+str(size_option).zfill(2)+"Mb"\
        #     if (size_option!="" and int(size_option) in range(0,100))\
        #     else size_suffixes[size_option]
        size_suffix = size_suffixes[size_option] if (size_option in size_suffixes.keys())\
              else "_"+"%05.2f"%size_option+"Mb"
            
        directory += f"/{size_suffix}"
        if not pathlib.Path(directory).is_dir() :
            os.mkdir(directory)
        
        # adding compilation_size_suffix
        directory += f"/{is_compilation_time_size_suffixes[is_compilation_time_size]}"
        if not pathlib.Path(directory).is_dir() :
            os.mkdir(directory)

        # adding kernel_mode_suffix
        directory += f"/{kernel_mode_suffixes[kernel_mode]}"
        if not pathlib.Path(directory).is_dir() :
            os.mkdir(directory)

        # the last depth joined directory is the full directory
        fulldirectory = directory
        # bench binary name is the concatenation of all
        benchname = (directory.removeprefix("bench_tree/")).replace("/","")
        if (VERBOSE):
            print(f"benchname:{benchname} directory:{fulldirectory}")

        ######### is_compilation_time_size and kernel_mode #########
        # if we compile array sizes then we need to copy all source files and compile them with special preprocessing
        # see in the f.write() conditionals to change the make directory and BENCH_EXECUTABLE bin directory
        is_copy_bench_files = is_compilation_time_size or kernel_mode!=""
        if  is_copy_bench_files:
            fulldirectory_absolute = pathlib.Path(fulldirectory).resolve()
            if DEBUG and VERBOSE:
                print(fulldirectory_absolute)
            shutil.copytree(src.resolve(),str(fulldirectory_absolute)+"/src",dirs_exist_ok=True)
            shutil.copy2(mainfile.resolve(),fulldirectory_absolute)
            shutil.copy2(makefile.resolve(),fulldirectory_absolute)


        filename = f"{fulldirectory}/run.sh"
        f = open(filename, "w")
        os.chmod(filename,0b111111111)
        
        ####### pre-compilation bench parameters #######
        # here compute the bench parameters for using at compile time if is_compilation_time_size
        if type(size_option)==int or type(size_option)==float:
            ni, nj = generate_2d_array_size(size_option)
        else:
            percentage_of_l3 = 100
            match size_option:
                case "SMALLER_THAN_L3":
                    percentage_of_l3 = 15.625
                case "SLIGHTLY_SMALLER_THAN_L3":
                    percentage_of_l3 = 96.875
                case "SLIGHTLY_BIGGER_THAN_L3":
                    percentage_of_l3 = 103.125
                case "BIGGER_THAN_L3":
                    percentage_of_l3 = 300.0
                case _:
                    pass
            ni, nj = generate_2d_array_size(L3_SIZE*percentage_of_l3/100.0)

        # see https://realpython.com/python-f-strings/
        f.write(f"""#! /bin/bash

# set BENCH_EXECUTABLE and PERF_REGIONS
export PERF_REGIONS="../{"../"*(TREE_DEPTH+2)}perf_regions"
export BENCH_MAKE_DIR="{"." if is_copy_bench_files else "../"*(TREE_DEPTH+2)}"
export BENCH_EXECUTABLE="{"" if is_copy_bench_files else "../"*(TREE_DEPTH+2)}bin/{benchname}"

# set perf_regions variables here
export PERF_REGIONS_VERBOSITY=0
export PERF_REGIONS_MAX=256

export LD_LIBRARY_PATH="$PERF_REGIONS/build:$LD_LIBRARY_PATH"
export PERF_REGIONS_COUNTERS=""
export PERF_REGIONS_COUNTERS="PAPI_L1_TCM,PAPI_L2_TCM,PAPI_L3_TCM,WALLCLOCKTIME"
# Uncomment for non-PAPI:
# export PERF_REGIONS_COUNTERS="WALLCLOCKTIME"

export MAIN="{benchname}"
export ALLOC_MODE="{alloc_option}"
export SIZE_MODE="{size_option}"
export SIZE_AT_COMPILATION="{int(is_compilation_time_size)}"
export NI="{ni if is_compilation_time_size else ""}"
export NJ="{nj if is_compilation_time_size else ""}"
export KERNEL_MODE="{kernel_mode}"

make -C $BENCH_MAKE_DIR main {"_PERF_REGIONS_FOLDER=../"+ "../"*(TREE_DEPTH+2)+"perf_regions" if is_copy_bench_files else ""}

filename=out

echo "Running mode {benchname}..."    
ls
# ./$BENCH_EXECUTABLE
# thank you to glenn jackman's answer on https://stackoverflow.com/questions/5853400/bash-read-output
while IFS= read -r line; do
    echo "$line"
    # MULE lines are those without a " " space prefix
    if [ "${{line:0:1}}" != " " ]
    then
        echo "$line" >> $filename.csv
    fi
    # grep -o 'action'
done < <( ./$BENCH_EXECUTABLE iters={iters} {"" if is_compilation_time_size else f"ni={ni} nj={nj}"} )
# |  grep -A100 Section | paste >> $filename.csv
echo
# cat $filename.csv
""")
        f.close()
        return filename, iters, ni, nj
    else:
        raise ValueError("Parameter wrong - read script for more information")


def main():
    """Main function of code generation - interprets input from argparse

    Use --help for details.
    """
    global ACCURACY
    global VERBOSE
    global DEBUG
    # courtesy of https://stackoverflow.com/questions/20063/whats-the-best-way-to-parse-command-line-arguments
    parser = argparse.ArgumentParser(description="Code generator for benchmarking with various options in a tree structure")

    phrase = shlex.join(sys.argv[1:])
    # file_test()
    # thank you to https://www.knowledgehut.com/blog/programming/sys-argv-python-examples#how-to-use-sys.argv-in-python?
    mode = 'single'
    alloc_option = ""
    size_option = ""
    is_compilation_time_size = ""
    iterator_of_selected_sizes = range(1,16+1)

    all_alloc_options = list(allocation_suffixes.keys())
    all_alloc_options.remove("")
    all_kernel_modes = list(kernel_mode_suffixes.keys())
    all_kernel_modes.remove("")
    all_parameters = {}
    
    parser.add_argument('-M','--MODE', nargs='?', default='all',
                    help='Can be all, all_l3, single or clean. "all" generates all possible combinations with set range of sizes.')
    parser.add_argument('-A', '--ACCURACY', metavar='multiplier', type=float,
                        help='An optional parameter that makes the benchmark more accurate if above 1 and accelerates it if below 1')

    # thank you to https://stackoverflow.com/questions/27411268/arguments-that-are-dependent-on-other-arguments-with-argparse
    parser_mode_specific = parser.add_argument_group(title='mode specific options',
                                   description='Flags for modes "single" and "all".',)
    
    # Arguments for single mode
    parser_mode_specific.add_argument('--alloc', nargs='?',
                    help=f'An alloc_option in {", ".join(list(allocation_suffixes.keys())).rstrip(", ")}')
    parser_mode_specific.add_argument('--size', nargs='?',
                    help=f'A size_option in {", ".join(list(size_suffixes.keys()))} or between 0 and 99')
    parser_mode_specific.add_argument('--compile-size', nargs='?', type=bool,
                help=f'A compilation time size option within {" ".join(list(map(str,is_compilation_time_size_suffixes.keys())))}')
    parser_mode_specific.add_argument('--range', metavar="size", nargs='+', default=[1,17],
                        help='Used in mode "all". Represents the scope of sizes in Mb to study. If length is 2, acts as lower and upper bound. If length is\
                             1, acts as upper bound with lower bound 1, if is number only selects that number, else it is the list of sizes in Mb.')
    # Optional arguments
    parser.add_argument('-c', '--clean-before', action='store_true',
                        help='Cleans existing directory before creating')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Displays more output')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Displays debug output')
    
    args = parser.parse_args()
    

    ### checking parameter values ###
    # courtesy of https://stackoverflow.com/questions/4042452/display-help-message-with-python-argparse-when-script-is-called-without-any-argu
    if len(sys.argv)==1:
        print("No arguments provided.",file=sys.stderr)
        parser.print_help(sys.stderr)
        sys.exit(1)
    if args.debug:
        DEBUG=True
    if DEBUG:
        print(args)

    # setting command
    if args.MODE is not None:
        mode = args.MODE
    # setting options
    if args.alloc is not None:
        alloc_option = args.alloc
    if args.size is not None:
        size_option = args.size
    if args.compile_size is not None:
        is_compilation_time_size = args.compile_size
    if args.range is not None:
        if DEBUG:
            print("range: " + str(args.range))
            print("range type: " + str(type(args.range)))
        if type(args.range) in [float, int]:
            iterator_of_selected_sizes = [args.range]
        elif len(args.range)==1:
            iterator_of_selected_sizes = range(1,math.ceil(float(args.range[0])))
        elif len(args.range)==2:
            iterator_of_selected_sizes = range(math.floor(float(args.range[0])),math.ceil(float(args.range[1])))
        else:
            iterator_of_selected_sizes = list(map(float,args.range))
    if args.ACCURACY is not None:
        if args.ACCURACY <= 0:
            parser.error(f"Accuracy flag set to {args.ACCURACY}: cannot be non-positive")
        else:
            ACCURACY = args.ACCURACY
    
    if args.verbose:
        VERBOSE=True
    if VERBOSE:
        print("verbose output on")
        print(alloc_option)
        print(size_option)
        print("range: " + str(iterator_of_selected_sizes))
        print(is_compilation_time_size)
        print("ACCURACY="+str(ACCURACY))

    ### executing command ###
    if mode != "clean":
        if pathlib.Path("bench_tree").is_dir() :
            if args.clean_before:
                shutil.rmtree("bench_tree")
                print("Cleaned tree")
                os.mkdir("bench_tree")
            else:
                print("Warning: bench_tree directory exists. May not function as expected when writing files.")
                print("You may use option -c to erase existing directory before creating new files or use parameter clean.")
        else:
            os.mkdir("bench_tree")
    
    if mode == "clean":
        print("Cleaning benchmark script tree... Y/n ?")
        if (str(input()) == "Y") :
            shutil.rmtree("bench_tree")
            print("Cleaned")
        else :
            print("Aborted")
    elif mode in ["all_old","all_no_compilation_time"]:
        print(f"Creating all benchmark scripts...")
        codegen_bench_tree_branch("","")
        
        for alloc_option in all_alloc_options :
            for size_option in iterator_of_selected_sizes :
                filename,iters,_,_ = codegen_bench_tree_branch(alloc_option,size_option)
                all_parameters[filename] = {"size_option": size_option,
                                            "alloc_option": alloc_option,
                                            "iters": iters,
                                            "is_compilation_time_size": False}
    elif mode in ["all","all_compilation_time"]:
        # shutil.rmtree("bench_tree")
        print(f"Creating all benchmark scripts...")
        codegen_bench_tree_branch("","")
        for alloc_option in all_alloc_options :
            for size_option in iterator_of_selected_sizes :
                for is_compilation_time_size in [False,True] :
                    for kernel_mode in all_kernel_modes:
                        filename, iters, ni, nj  = codegen_bench_tree_branch(alloc_option,size_option,\
                                                    is_compilation_time_size=is_compilation_time_size,kernel_mode=kernel_mode)
                        all_parameters[filename] = {"kernel_mode": kernel_mode,
                                                    "size_option": size_option,
                                                    "ni": ni,
                                                    "nj": nj,
                                                    "alloc_option": alloc_option,
                                                    "iters": iters,
                                                    "is_compilation_time_size": is_compilation_time_size}
    elif mode == "all_l3":
        # shutil.rmtree("bench_tree")
        all_l3_relative_size_options = list(size_suffixes.keys())
        all_l3_relative_size_options.remove("")
        # TODO : pass L3 size as compilation/execution time parameter - using grep and command
        print(f"Creating all L3-relative benchmark scripts...")
        for alloc_option in all_alloc_options :
            for size_option in all_l3_relative_size_options :
                for is_compilation_time_size in [False,True] :
                    filename, iters, ni, nj = codegen_bench_tree_branch(alloc_option,size_option,\
                                                is_compilation_time_size=is_compilation_time_size)
                    all_parameters[filename] = {"size_option": size_option,
                                                "ni": ni,
                                                "nj": nj,
                                                "alloc_option": alloc_option,
                                                "iters": iters,
                                                "is_compilation_time_size": is_compilation_time_size}
    elif mode == "single" :
        description = 'default' if (alloc_option=='' and size_option=='' and is_compilation_time_size=='')\
            else str(alloc_option) + str(size_option) + "is_compilation_time_size: " + str(is_compilation_time_size)
        print(f"Creating {description} benchmark script...")
        filename,iters,_,_ = codegen_bench_tree_branch(alloc_option,size_option,is_compilation_time_size)
        all_parameters[filename] = {"size_option": size_option,
                                                "alloc_option": alloc_option,
                                                "iters": iters,
                                                "is_compilation_time_size": is_compilation_time_size}
    else :
        print("Invalid command.",file=sys.stderr)
        parser.print_help(sys.stderr)
        sys.exit(1)

    # JSON dump of all parameters used
    filename = "all_benchmark_parameters.json"
    f = open(filename, "w")
    json.dump(all_parameters,f,sort_keys=True, indent=4)
    print("done.")
    return 0

# courtesy of https://docs.python.org/fr/3/library/__main__.html
if __name__ == '__main__':
    sys.exit(main())