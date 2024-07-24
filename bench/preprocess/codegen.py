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
# for debugging
import time
import subprocess

global ACCURACY
ACCURACY = 1

global VERBOSE
VERBOSE = False
global DEBUG
DEBUG = False
L3_SIZE = 16
global IS_NVFORTRAN_COMPILER
IS_NVFORTRAN_COMPILER = False

# UPDATE: when implementing new parameter, increment TREE_DEPTH
# this parameter is used for setting relative directories, with repeated "../" prefixes
TREE_DEPTH = 5

allocation_suffixes = { "ALLOCATABLE"           : "_allocatable",
                        "STATIC"                : "_static",
                        ""                      : "_defaultalloc"}
module_suffixes = { False                       : "_nomodule",
                        True                    : "_module",
                        ""                      : "_defaultmodule"}
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
                        ""                      : "_default"}

# dictionary containing number related to size identifier
# thank you Abhijit at https://stackoverflow.com/questions/36459969/how-to-convert-a-list-to-a-dictionary-with-indexes-as-values
size_mode_number = {k: v+100 for v, k in enumerate(size_suffixes.keys())}

src = pathlib.Path("../src/")
mainfile = pathlib.Path("../main.F90")
if DEBUG and VERBOSE:
    mainfile = pathlib.Path("../main.test.F90")
makefile = pathlib.Path("../Makefile")


def generate_2d_array_size(size_in_mb):
    # default is 16
    if size_in_mb == 0:
        size_in_mb = 16
    ni = int(math.sqrt(1024*1024*(size_in_mb)))
    nj = math.floor(1024*1024*(size_in_mb) // ni)
    return ni,nj

def codegen_bench_tree_branch(alloc_option: str,
                              size_option: Union[int, str],
                              hardware_option="GPU",
                              iters=42,
                              is_module=True,
                              is_compilation_time_size=False,
                              kernel_mode=""):
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
    if size_option in size_suffixes.keys() or int(size_option) == 0:
        iters = math.ceil(ACCURACY*32)
    else:
        # max is used to insure there is at least 1 iteration
        iters = max(1,int(ACCURACY*100//size_option))

    ###### generating directory ######
    # directory is represented as an str
    directory = "bench_tree"

    # first depth is kernel_mode_suffix
    directory += f"/bench{kernel_mode_suffixes[kernel_mode]}"
    if not pathlib.Path(directory).is_dir() :
        os.mkdir(directory)

    # adding allocation_type TODO : make the second depth CPU/GPU once that is functional
    directory += f"/{allocation_suffixes[alloc_option]}"
    if not pathlib.Path(directory).is_dir() :
        os.mkdir(directory)
    
    # adding is_module
    directory += f"/{module_suffixes[is_module]}"
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
        tic = 0
        if DEBUG:
            tic = time.perf_counter()
        args = shlex.split(f"cp -r {src.resolve()} {str(fulldirectory_absolute)+'/src'}")
        subprocess.run(args=args,executable="cp")
        # shutil.copytree(src.resolve(),str(fulldirectory_absolute)+"/src",dirs_exist_ok=True)
        if DEBUG:
            toc = time.perf_counter()
            if (toc-tic)>0.5:
                print(f"Copied source in {toc-tic:0.4f}s")
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
VERBOSE=$1
: ${{VERBOSE:=false}}
PURPLE="\\033[1;35m"
NO_COLOUR="\\033[0m"
                
writeprogressbar() {{
    printf "$PURPLE%-8s[$progressbar]($progresspercent%%)$NO_COLOUR" $1
}}

# set BENCH_EXECUTABLE
export PERF_REGIONS="{"" if is_copy_bench_files else "../"*(TREE_DEPTH+2)}src/perf_regions"
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
export MODULE_MODE="{int(is_module)}"
export SIZE_MODE="{size_option}"
export SIZE_AT_COMPILATION="{int(is_compilation_time_size)}"
export NI="{ni if is_compilation_time_size else ""}"
export NJ="{nj if is_compilation_time_size else ""}"
export KERNEL_MODE="{kernel_mode}"

# normal make
# make -C $BENCH_MAKE_DIR main {"F90=nvfortran" if IS_NVFORTRAN_COMPILER else ""}

# pretty output for progress bar
if $VERBOSE
then :
else
printf "\\r"
writeprogressbar compile
# printf "\\r"
fi
while IFS= read -r line; do
    if $VERBOSE
    then
    echo -ne "                                \\r"
    echo "$line"
    writeprogressbar compile
    echo -ne "\\r"
    fi
    # echo -ne "compile [$progressbar]($progresspercent%)\\r"
    # grep -o 'action'
done < <( make -C $BENCH_MAKE_DIR main {"F90=nvfortran" if IS_NVFORTRAN_COMPILER else ""} )
printf "\\r"

filename=out

if $VERBOSE
then
echo -ne "\\r                                \\r"
echo "Running mode {benchname}...     "
writeprogressbar execute
else
echo -ne "\\r                                \\r"
writeprogressbar execute
fi

# thank you to glenn jackman"s answer on https://stackoverflow.com/questions/5853400/bash-read-output
while IFS= read -r line; do
    if $VERBOSE
    then
    echo -ne "\\r                                \\r"
    echo "$line"
    writeprogressbar execute
    fi
    # echo -ne "execute [$progressbar]($progresspercent%)\\r"
    # MULE lines are those without a " " space prefix
    if [ "${{line:0:1}}" != " " ]
    then
        echo "$line" >> $filename.csv
    fi
    # grep -o 'action'
done < <( ./$BENCH_EXECUTABLE iters={iters} {"" if is_compilation_time_size else f"ni={ni} nj={nj}"} )
printf "\\r"
writeprogressbar done
printf "\\r"
# |  grep -A100 Section | paste >> $filename.csv
# cat $filename.csv
""")
    f.close()
    return filename, iters, ni, nj

def argument_parsing(parser: argparse.ArgumentParser):
    parser.add_argument('-M','--MODE', nargs='?', default='all',
                    help='Can be all, all_l3, single or clean. "all" generates all possible combinations with set range of sizes.')
    parser.add_argument('-A', '--ACCURACY', metavar='multiplier', type=float,
                        help='An optional parameter that makes the benchmark more accurate if above 1 and accelerates it if below 1')

    # thank you to https://stackoverflow.com/questions/27411268/arguments-that-are-dependent-on-other-arguments-with-argparse
    parser_mode_specific = parser.add_argument_group(title='mode specific options',
                                   description='Flags for modes "single" and "all".\n\
                                   Setting an option here will fix its value in the enumeration of combinations of "all".',)
    
    # Arguments for single mode
    parser_mode_specific.add_argument('--kernel-mode', nargs='?',
                    help=f'A kernel_mode_option in {", ".join(list(kernel_mode_suffixes.keys())).rstrip(", ")}')
    parser_mode_specific.add_argument('--alloc', nargs='?',
                    help=f'An alloc_option in {", ".join(list(allocation_suffixes.keys())).rstrip(", ")}')
    parser_mode_specific.add_argument('--size', nargs='?',
                    help=f'A size_option in {", ".join(list(size_suffixes.keys()))} or between 0 and 99.\
                        Has precedence over --range and sets single size in mode "all".')
    parser_mode_specific.add_argument('--compile-size', nargs='?', type=bool,
                help=f'Sets if the array size is set at compilation time. Either True of False.')
    parser_mode_specific.add_argument('--module', nargs='?', type=bool,
                help=f'Sets if the function is in a module. Either True of False.')
    parser_mode_specific.add_argument('--size-range', metavar="size", nargs='+', default=[1,17],
                        help='Used in mode "all". Represents the scope of sizes in Mb to study. If --size is used, flag is ignored and scope is set to single size.\
                              If length is 2, acts as lower and upper bound.\
                              If length is 1, acts as upper bound with lower bound 1.\
                              If length is greater than 2, it is the list of sizes in Mb.')
    # Optional arguments
    parser.add_argument('-nv', '--nvfortran', action='store_true',
                        help='Uses nvfortran compiler and enables GPU benchmarking.')
    parser.add_argument('-c', '--clean-before', action='store_true',
                        help='Cleans existing directory before creating')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Displays more output')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Displays debug output')
    return parser.parse_args()

def main():
    """Main function of code generation - interprets input from argparse

    Use --help for details.
    """
    global ACCURACY
    global VERBOSE
    global DEBUG
    global IS_NVFORTRAN_COMPILER
    
    # courtesy of https://stackoverflow.com/questions/20063/whats-the-best-way-to-parse-command-line-arguments
    ### argument parser ###
    parser = argparse.ArgumentParser(description="Code generator for benchmarking with various options in a tree structure")
    args = argument_parsing(parser)
    
    ### defaults ###
    mode = 'single'
    alloc_option = ""
    is_module = ""
    size_option = ""
    is_compilation_time_size = ""
    kernel_mode_option = ""
    iterator_of_selected_sizes = range(1,16+1)

    ### program data ###
    all_alloc_options = list(allocation_suffixes.keys())
    all_alloc_options.remove("")
    all_module = [False, True]
    all_kernel_mode_options = list(kernel_mode_suffixes.keys())
    all_kernel_mode_options.remove("")
    all_compilation_time_size = [False, True]

    # dictionary used for exporting bench parameters as .JSON file
    # courtesy of https://help.objectiflune.com/en/pres-connect-rest-api-cookbook/2019.2/Content/Cookbook/Technical_Overview/JSON_Structures/Specific_Structures/JSON_Record_Data_List.htm
    # if -c cleaning option is not used it is imported
    # because existing benchmarks have their parameters stored
    json_filename = "all_benchmark_parameters.json"
    json_dict_all_parameters = {"data":[]}

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
    if args.kernel_mode is not None:
        if args.kernel_mode in all_kernel_mode_options:
            kernel_mode_option = args.kernel_mode
            if mode!="single":
                all_kernel_mode_options = [args.kernel_mode]
        else:
            parser.error(f"{args.kernel_mode} invalid value for kernel_mode")
    if args.module is not None:
        is_module = args.module
        if mode!="single":
            all_module = [args.module]
    if args.alloc is not None:
        if args.alloc in all_alloc_options:
            alloc_option = args.alloc
            if mode!="single":
                all_alloc_options = [args.alloc]
        else:
            parser.error(f"{args.alloc} invalid value for alloc_option")
    if args.size is not None:
        if args.size in size_suffixes.keys() or int(args.size) in range(0,100):
            size_option = args.size
        else:
            parser.error(f"{args.size} invalid value for size")
    if args.compile_size is not None:
        is_compilation_time_size = args.compile_size
        if mode!="single":
            all_compilation_time_size = [args.compile_size]

    # range selector    
    if DEBUG:
        print("size_range: " + str(args.size_range))
        print("size_range type: " + str(type(args.size_range)))
    if args.size is not None:
        if args.size in size_suffixes.keys():
            iterator_of_selected_sizes = [args.size]
        else :
            iterator_of_selected_sizes = [float(args.size)]
    elif len(args.size_range)==1:
        iterator_of_selected_sizes = range(1,math.ceil(float(args.size_range[0])))
    elif len(args.size_range)==2:
        iterator_of_selected_sizes = range(math.floor(float(args.size_range[0])),math.ceil(float(args.size_range[1])))
    else:
        iterator_of_selected_sizes = list(map(float,args.size_range))
    if args.ACCURACY is not None:
        if args.ACCURACY <= 0:
            parser.error(f"Accuracy flag set to {args.ACCURACY}: cannot be non-positive")
        else:
            ACCURACY = args.ACCURACY
    if args.nvfortran:
        IS_NVFORTRAN_COMPILER=True
    if args.verbose:
        VERBOSE=True
    if VERBOSE:
        print("verbose output on")
        print(alloc_option)
        print(size_option)
        print("size_range: " + str(iterator_of_selected_sizes))
        print(is_compilation_time_size)
        print("ACCURACY="+str(ACCURACY))

    ###### executing command ######
    ### preparing folders and parameters dictionary ###
    if mode != "clean":
        if not args.clean_before:
            if pathlib.Path(json_filename).is_file() :
                f = open("../preprocess/all_benchmark_parameters.json", "r")
                print("Importing existing .JSON dictionary of benchmark parameters.")
                json_dict_all_parameters = json.load(f)
                f.close()
        if pathlib.Path("bench_tree").is_dir() :
            if args.clean_before:
                if pathlib.Path(json_filename).is_file():
                    os.remove(json_filename)
                    print(f"Cleaned {json_filename}")
                shutil.rmtree("bench_tree")
                print("Cleaned bench_tree")
                os.mkdir("bench_tree")
            else:
                print("Warning: bench_tree directory exists. May not function as expected when writing files.")
                print("You may use option -c to erase existing directory before creating new files or use parameter clean.")
        else:
            os.mkdir("bench_tree")
    # for debugging new implementations
    if mode in ["debug","all_old"]:
        print(f"Debug: Creating all benchmark scripts...")
        codegen_bench_tree_branch("","")
        
        for alloc_option in all_alloc_options :
            for size_option in iterator_of_selected_sizes :
                for is_compilation_time_size in all_compilation_time_size :
                    for kernel_mode in all_kernel_mode_options:
                        filename, iters, ni, nj  = codegen_bench_tree_branch(alloc_option,size_option,\
                                                    is_compilation_time_size=is_compilation_time_size,kernel_mode=kernel_mode)
                        json_dict_all_parameters["data"].append({"id":filename,
                                                    "kernel_mode": kernel_mode,
                                                    "size_option": size_option,
                                                    "ni": ni,
                                                    "nj": nj,
                                                    "alloc_option": alloc_option,
                                                    "iters": iters,
                                                    "is_compilation_time_size": is_compilation_time_size})
    elif mode in ["all","all_compilation_time"]:
        # shutil.rmtree("bench_tree")
        print(f"Creating all benchmark scripts...")
        codegen_bench_tree_branch("","")
        all_module
        for kernel_mode in all_kernel_mode_options:
            for alloc_option in all_alloc_options :
                for is_module in all_module :
                    for size_option in iterator_of_selected_sizes :
                        for is_compilation_time_size in all_compilation_time_size :
                            filename, iters, ni, nj  = codegen_bench_tree_branch(
                                alloc_option,
                                size_option,
                                is_module=is_module,
                                is_compilation_time_size=is_compilation_time_size,
                                kernel_mode=kernel_mode)
                            json_dict_all_parameters["data"].append(
                                {"id":filename,
                                "kernel_mode": kernel_mode,
                                "size_option": size_option,
                                "is_module": is_module,
                                "ni": ni,
                                "nj": nj,
                                "alloc_option": alloc_option,
                                "iters": iters,
                                "is_compilation_time_size": is_compilation_time_size})
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
                    json_dict_all_parameters["data"].append({"id":filename,
                                                "size_option": size_option,
                                                "ni": ni,
                                                "nj": nj,
                                                "alloc_option": alloc_option,
                                                "iters": iters,
                                                "is_compilation_time_size": is_compilation_time_size})
    elif mode == "single" :
        description = 'default' if (alloc_option=='' and size_option=='' and is_compilation_time_size=='' and kernel_mode_option=='')\
            else str(alloc_option) + str(size_option) + "is_compilation_time_size: " + str(is_compilation_time_size) + str(kernel_mode_option)
        print(f"Creating {description} benchmark script...")
        filename,iters,_,_ = codegen_bench_tree_branch(alloc_option,size_option,is_compilation_time_size,kernel_mode=kernel_mode_option)
        json_dict_all_parameters["data"].append({"id":filename,
                                                "size_option": size_option,
                                                "alloc_option": alloc_option,
                                                "iters": iters,
                                                "is_compilation_time_size": is_compilation_time_size,
                                                "kernel_mode_option": kernel_mode_option})
    elif mode != "clean" :
        print("Invalid command.",file=sys.stderr)
        parser.print_help(sys.stderr)
        sys.exit(1)

    ### JSON dump of all parameters used ###
    if mode != "clean":
        f = open(json_filename, "w")
        json.dump(json_dict_all_parameters,f,sort_keys=True, indent=4)
        f.close()
        print("done.")
    
    ### clean mode ###
    if mode == "clean":
        print("Cleaning benchmark script tree and .JSON metadata...\nY/n ?")
        if (str(input()) == "Y") :
            os.remove(json_filename)
            print(f"Cleaned {json_filename}")
            shutil.rmtree("bench_tree")
            print("Cleaned bench_tree")
        else :
            print("Aborted")

    return 0

# courtesy of https://docs.python.org/fr/3/library/__main__.html
if __name__ == '__main__':
    sys.exit(main())