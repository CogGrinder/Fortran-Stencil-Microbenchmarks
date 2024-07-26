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

# UPDATE: when implementing new parameter, increment TREE_DEPTH
# this parameter is used for setting relative directories, with repeated "../" prefixes
TREE_DEPTH = 6

# global variables set later by user
global ACCURACY
global VERBOSE
global DEBUG
global IS_NVFORTRAN_COMPILER
# defaults
ACCURACY = 1
VERBOSE = False
DEBUG = False
IS_NVFORTRAN_COMPILER = False

# L3_SIZE (float or int): set your L3 cache size here. Used for setting sizes relative to L3 cache.
L3_SIZE = 16

###### metadata for developers #######
# all_metadata_variables (dict) : names of parameters. Used for filtering arguments when executing in 'single' mode.
# UPDATE: add new parameter here
metadata_names = ["kernel_mode",
                      "hardware",
                      "allocation",
                      "module",
                      "size",
                      "compile_size"]

# metadata_types (dict) : types of parameters. Currently not used, may be used to simplify maintainability.
# UPDATE: add new parameter type here
metadata_types =\
    {
    "kernel_mode" : str,
    "hardware_option" : str,
    "alloc_option" : str,
    "is_module" : bool,
    "size_option" : float,
    "is_compilation_time_size" : bool
    }

# metadata_defaults (dict) : values of parameters. Used for replacing missing parameters when omitted.
# UPDATE: add new parameter default here
metadata_defaults =\
    {
    "kernel_mode" : "DEFAULT_KERNEL",
    "hardware" : "CPU",
    "allocation" : "ALLOCATABLE",
    "module" : True,
    "size" : 16.0,
    "compile_size" : True
    }

# suffixes (dict of dict) : used for naming folders, naming binaries and iterating over all possible values for each parameter.
# "" is used to specify default folder name.
# Please be aware this is set as "_default" currently to simplify csv fetching.
# NB: booleans need boolean keys
# UPDATE: add new parameter options and their prefixes here

suffixes = {}

suffixes['hardware'] = { "CPU"                   : "_cpu",
                        "GPU"                   : "_gpu",
                        ""                      : "_default"}

suffixes['allocation'] = { "ALLOCATABLE"           : "_allocatable",
                        "STATIC"                : "_static",
                        ""                      : "_default"}

suffixes['module'] =  { False                       : "_nomodule",
                        True                    : "_module",
                        ""                      : "_default"}

suffixes['size'] =    { "SMALLER_THAN_L3"           : "_smallerl3",
                        "SLIGHTLY_SMALLER_THAN_L3"  : "_ssmallerl3",
                        "SLIGHTLY_BIGGER_THAN_L3"   : "_sbiggerl3",
                        "BIGGER_THAN_L3"            : "_biggerl3",
                        ""                          : "_default"}

suffixes['compile_size'] = { False     : "_sizenotcompiled",
                        True                    : "_sizecompiled",
                        ""                      : "_default"}

suffixes['kernel_mode'] = { "X_KERNEL"              : "_xkernel",
                        "Y_KERNEL"              : "_ykernel",
                        "SIZE_5_KERNEL"         : "_size5kernel",
                        "DEFAULT_KERNEL"        : "_defaultkernel",
                        ""                      : "_default"}
# location of source files
src = pathlib.Path("../src/")
mainfile = pathlib.Path("../main.F90")
# if DEBUG :
#     # testing mainfile
#     mainfile = pathlib.Path("../main.test.F90")
makefile = pathlib.Path("../Makefile")


def generate_2d_array_size(size_in_mb: float, bitsize_per_float=8):
    """Calculate array dimensions to obtain a total memory cost

    Args:
        size_in_mb (float): size in Mb to obtain
        bitsize_per_float (int, optional): specify floating point bit precision
    """
    # default is 16
    if size_in_mb == 0:
        size_in_mb = 16
    memory_spaces = 1024*1024*(size_in_mb)*8.0/bitsize_per_float
    ni = math.sqrt(memory_spaces)
    nj = memory_spaces / ni
    return math.floor(ni),math.floor(nj)

def codegen_bench_tree_branch(
        allocation =    metadata_defaults["allocation"],
        kernel_mode =   metadata_defaults["kernel_mode"],
        size =          metadata_defaults["size"],
        hardware =      metadata_defaults["hardware"],
        module =        metadata_defaults["module"],
        compile_size =  metadata_defaults["compile_size"]):
    """Function for generating script that compiles and execute benchmark

    Codegen generates a branch in a folder tree of root 'bench_tree'
    based on all parameters passed, making folders where needed
    using naming conventions defined from suffix dictionaries

    Args:
        allocation (str): String that represents the type of allocation used in bench
        size (Union[int, str]): Integer or string that represents the size of the arrays
            if non-zero int, corresponds to size in Mb;
            if zero, falls back to default;
            if str, is related to L3 size. TODO : autodetect L3 size
        compile_size (bool, optional): Decides whether array size is baked in
            by passing it to compiler directly.
            Size is calculated either in python script and passed
            through preprocessing or calculated in a module at the
            setup step in the execution. Defaults to False.
        kernel_mode (str, optional): String that represents which stencil computation
            kernel is used. Defaults to "".
    """    
    ni=0
    nj=0
    if size in suffixes['size'].keys() or int(size) == 0:
        iters = math.ceil(ACCURACY*16)
    else:
        # max is used to insure there is at least 1 iteration
        iters = max(1,int(ACCURACY*100//size))

    ###### generating directory ######
    # directory is represented as an str
    directory = "bench_tree"

    # first depth is kernel_mode_suffix
    directory += f"/bench{suffixes['kernel_mode'][kernel_mode]}"
    if not pathlib.Path(directory).is_dir() :
        os.mkdir(directory)

    # CPU/GPU
    directory += f"/{suffixes['hardware'][hardware]}"
    if not pathlib.Path(directory).is_dir() :
        os.mkdir(directory)

    # adding allocation_type
    directory += f"/{suffixes['allocation'][allocation]}"
    if not pathlib.Path(directory).is_dir() :
        os.mkdir(directory)
    
    # adding module
    directory += f"/{suffixes['module'][module]}"
    if not pathlib.Path(directory).is_dir() :
        os.mkdir(directory)
    
    # size_suffix in the _01Mb format or _{option suffix} format
    size_suffix = suffixes['size'][size] if (size in suffixes['size'].keys())\
            else "_"+"%05.2f"%size+"Mb"
    directory += f"/{size_suffix}"
    if not pathlib.Path(directory).is_dir() :
        os.mkdir(directory)
    
    # adding compilation_size_suffix
    directory += f"/{suffixes['compile_size'][compile_size]}"
    if not pathlib.Path(directory).is_dir() :
        os.mkdir(directory)


    # the last depth joined directory is the full directory
    fulldirectory = directory
    # bench binary name is the concatenation of all
    benchname = (directory.removeprefix("bench_tree/")).replace("/","")
    if (VERBOSE):
        print(f"benchname:{benchname} directory:{fulldirectory}")

    ######### compile_size and kernel_mode #########
    # if we compile array sizes then we need to copy all source files and compile them with special preprocessing
    # see in the f.write() conditionals to change the make directory and BENCH_EXECUTABLE bin directory
    is_copy_bench_files = compile_size or kernel_mode!=""
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
    # here compute the bench parameters for using at compile time if compile_size
    if type(size)==int or type(size)==float:
        ni, nj = generate_2d_array_size(size)
    else:
        percentage_of_l3 = 100
        match size:
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
# verbose options:
# general VERBOSE
if [[ "$1" == "-v" || "$2" == "-v" ]]
then
VERBOSE=true
fi
: ${{VERBOSE:=false}}
# OpenMP VERBOSE
if [[ "$1" == "-vomp" || "$2" == "-vomp" ]]
then
export VERBOSE_OMP="1"
fi

PURPLE="\\033[1;35m"
LIGHT_RED="\\033[1;31m"
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

# NB: booleans are encoded as 0 or 1 in scripts
export MAIN="{benchname}"
export HARDWARE="{hardware}"
export KERNEL_MODE="{kernel_mode}"
export ALLOC_MODE="{allocation}"
export MODULE_MODE="{int(module) if type(module)==bool else ''}"
export SIZE_MODE="{size}"
export SIZE_AT_COMPILATION="{int(compile_size) if type(compile_size)==bool else ''}"
export NI="{ni if compile_size else ""}"
export NJ="{nj if compile_size else ""}"

# pretty output for progress bar
if $VERBOSE
then :
else
printf "\\r"
writeprogressbar compile
fi
if $VERBOSE
then
while IFS= read line; do
    printf "\\r                                \\r"
    printf "$line\\n"
    printf "\\r                                \\r"
    writeprogressbar compile
    printf "\\r"
done < <( make -C $BENCH_MAKE_DIR main {"F90=nvfortran" if IS_NVFORTRAN_COMPILER else ""} 2>&1 | tee compile_output.log )
# courtesy of https://stackoverflow.com/questions/418896/how-to-redirect-output-to-a-file-and-stdout
# 2>&1 captures both stdout and stderr, and tee writes it to a log file while passing it to the while loop
else
    # make -C $BENCH_MAKE_DIR main {"F90=nvfortran" if IS_NVFORTRAN_COMPILER else ""} > compile_output.log
    # better catching of stderr https://stackoverflow.com/questions/11087499/bash-how-do-you-capture-stderr-to-a-variable
    ERROR_OUTPUT="$(make -C $BENCH_MAKE_DIR main {"F90=nvfortran" if IS_NVFORTRAN_COMPILER else ""} 2>&1 > compile_output.log)"
    
    n_lines_error=$(echo "$ERROR_OUTPUT" | wc -l)
    if (( n_lines_error > 1 ));then
    echo n_lines_error: $n_lines_error
    printf "%s" "$ERROR_OUTPUT"
    printf "$NO_COLOUR\n"
    fi
fi
printf "\\r"

filename=out

if $VERBOSE
then
printf "\\r                                \\r"
echo "Running mode {benchname}...     "
writeprogressbar execute
else
printf "\\r                                \\r"
writeprogressbar execute
fi
# thank you to glenn jackman's answer on https://stackoverflow.com/questions/5853400/bash-read-output
while IFS= read -r line; do
    if $VERBOSE
    then
    printf "\\r                                \\r"
    printf "$line\\n"
    writeprogressbar execute
    fi
    # MULE lines are those without a " " space prefix
    if [ "${{line:0:1}}" != " " ]
    then
        echo "$line" >> $filename.csv
    fi
done < <( {"" if not "GPU" in hardware else "OMP_TARGET_OFFLOAD=mandatory "}./$BENCH_EXECUTABLE iters={iters} {"" if compile_size else f"ni={ni} nj={nj}"} )
printf "\\r"
writeprogressbar done
printf "\\r"
# |  grep -A100 Section | paste >> $filename.csv
# cat $filename.csv
""")
    f.close()
    return filename, iters, ni, nj

def get_parsed_parameter(parser_namespace: argparse.Namespace, param_name: str, default_dic=metadata_defaults):
    return getattr(parser_namespace, param_name, default_dic[param_name])

def iterator(parsed: argparse.Namespace, param_name: str):
    global DEBUG
    parameter = getattr(parsed, param_name)
    if param_name=='size':
        # size range
        if DEBUG:
            print("size: " + str(parsed.size))
            print("size_range: " + str(parsed.size_range))
            print("size_range type: " + str(type(parsed.size_range)))
        # if parsed.size is None
        l=[metadata_defaults['size']]
        # parsed.size takes precedence over parsed.size_range
        if parsed.size is not None:
            if parsed.size in suffixes['size'].keys():
                l = [parsed.size]
            else :
                l = [float(parsed.size)]
        elif len(parsed.size_range)==1:
            l = range(1,math.ceil(float(parsed.size_range[0])))
        elif len(parsed.size_range)==2:
            l = range(math.floor(float(parsed.size_range[0])),math.ceil(float(parsed.size_range[1])))
        else:
            l = list(map(float,parsed.size_range))
        return l
    elif parameter is None:
        l = list(suffixes[param_name].keys())
        if "" in l:
            l.remove("")
        return l
    else:
        return [parameter]

def argument_parsing(parser: argparse.ArgumentParser):
    parser.add_argument('-M','--MODE', metavar='name', nargs='?', default='all',
                    help='Can be all, all_l3, single or clean. "all" generates all possible combinations with set range of sizes.')
    parser.add_argument('-A', '--ACCURACY', metavar='float', type=float,
                        help='An optional parameter that makes the benchmark more accurate if above 1 and accelerates it if below 1')

    # thank you to https://stackoverflow.com/questions/27411268/arguments-that-are-dependent-on-other-arguments-with-argparse
    parser_mode_specific = parser.add_argument_group(title='mode specific options',
                                   description='Flags for modes "single" and "all".\n\
                                   Setting an option here will fix its value in the enumeration of combinations of "all".',)
    
    # Arguments for single mode
    parser_mode_specific.add_argument('--kernel-mode', metavar='name', nargs='?',
                    help=f'A kernel_mode in {", ".join(list(suffixes["kernel_mode"].keys())).rstrip(", ")}')
    parser_mode_specific.add_argument('--hardware', metavar='name', nargs='?',
                    help=f'A hardware in {", ".join(list(suffixes["hardware"].keys())).rstrip(", ")}')
    parser_mode_specific.add_argument('--allocation', metavar='name', nargs='?',
                    help=f'An allocation in {", ".join(list(suffixes["allocation"].keys())).rstrip(", ")}')
    parser_mode_specific.add_argument('--module', metavar='python boolean', nargs='?', type=bool,
                help=f'Sets if the function is in a module. Either True of False.')
    parser_mode_specific.add_argument('--size', metavar='name', nargs='?',
                    help=f'A size in {", ".join(list(suffixes["size"].keys()))} or between 0 and 99.\
                        Has precedence over --range and sets single size in mode "all".')
    parser_mode_specific.add_argument('--size-range', metavar='float', nargs='+', default=[1,17],
                        help='Used in mode "all". Represents the scope of sizes in Mb to study.\
                              If --size is used, flag is ignored and scope of sizes is only one size.\
                              If length is 2, acts as lower and upper bound.\
                              If length is 1, acts as upper bound with lower bound 1.\
                              If length is greater than 2, it is the list of sizes in Mb.')
    parser_mode_specific.add_argument('--compile-size', metavar='python boolean', nargs='?', type=bool,
                help=f'Sets if the array size is set at compilation time. Either True of False.')
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

    ### metadata ###
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
    if args.nvfortran:
        IS_NVFORTRAN_COMPILER=True
    if args.verbose:
        VERBOSE=True
    
    if DEBUG:
        print(args)

    # checking for parser errors
    if args.kernel_mode is not None:
        if not args.kernel_mode in iterator(args,"kernel_mode"):
            parser.error(f"{args.kernel_mode} invalid value for kernel_mode")
    if args.hardware is not None:
        if not args.hardware in iterator(args,"hardware"):
            parser.error(f"{args.hardware} invalid value for hardware")
    if args.allocation is not None:
        if not args.allocation in iterator(args,"allocation"):
            parser.error(f"{args.allocation} invalid value for allocation")
    if args.size is not None:
        if args.size in suffixes['size'].keys():
            pass
        elif 0.1<=float(args.size):
            args.size = float(args.size)
        else:
            parser.error(f"{args.size} invalid value for size")

    if args.ACCURACY is not None:
            if args.ACCURACY <= 0:
                parser.error(f"Accuracy flag set to {args.ACCURACY}: cannot be non-positive")
            else:
                ACCURACY = args.ACCURACY

    
    if VERBOSE:
        print("verbose output on")
        print(args.allocation)
        print(args.size)
        print("size_range: " + str(iterator(args,"size")))
        print(args.compile_size)
        print("ACCURACY="+str(ACCURACY))

    ###### executing command ######
    ### preparing folders and parameters dictionary ###
    if args.MODE != "clean":
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
    if args.MODE == "all":
        print(f"Creating all benchmark scripts...")
        codegen_bench_tree_branch(**{k:"" for k in metadata_names})
        for kernel in iterator(args,"kernel_mode") :
            for hardware in iterator(args,"hardware") :
                for alloc in iterator(args,"allocation") :
                    for module in iterator(args,"module") :
                        for size in iterator(args,"size") :
                            for compile_size in iterator(args,"compile_size") :
                                filename, iters, ni, nj  = codegen_bench_tree_branch(
                                    kernel_mode=kernel,
                                    hardware=hardware,
                                    allocation=alloc,
                                    module=module,
                                    size=size,
                                    compile_size=compile_size,
                                    )
                                json_dict_all_parameters["data"].append(
                                    {"id":filename,
                                    "kernel_mode": kernel,
                                    "hardware" : hardware,
                                    "allocation": alloc,
                                    "module": module,
                                    "size": size,
                                    "compile_size": compile_size,
                                    "ni": ni,
                                    "nj": nj,
                                    "iters": iters})
    elif args.MODE in ["debug","all_old"]:
        print(f"Debug: Creating all benchmark scripts...")
        codegen_bench_tree_branch(**{k:"" for k in metadata_names})
        for kernel in iterator(args,"kernel_mode") :
            # for hardware in iterator(args,"hardware") :
                for alloc in iterator(args,"allocation") :
                    for module in iterator(args,"module") :
                        for size in iterator(args,"size") :
                            for compile_size in iterator(args,"compile_size") :
                                filename, iters, ni, nj  = codegen_bench_tree_branch(
                                    kernel_mode=kernel,
                                    # hardware=hardware,
                                    allocation=alloc,
                                    module=module,
                                    size=size,
                                    compile_size=compile_size,
                                    )
                                json_dict_all_parameters["data"].append(
                                    {"id":filename,
                                    "kernel_mode": kernel,
                                    # "hardware" : hardware,
                                    "allocation": alloc,
                                    "module": module,
                                    "size": size,
                                    "compile_size": compile_size,
                                    "ni": ni,
                                    "nj": nj,
                                    "iters": iters})
    elif args.MODE == "all_l3":
        all_l3_relative_sizes = list(suffixes['size'].keys())
        all_l3_relative_sizes.remove("")
        # TODO : pass L3 size as compilation/execution time parameter - using grep and command
        print(f"Creating all L3-relative benchmark scripts...")
        for alloc in iterator(args,"allocation") :
            for size in all_l3_relative_sizes :
                for compile_size in [False,True] :
                    filename, iters, ni, nj = codegen_bench_tree_branch(alloc,size,\
                                                compile_size=compile_size)
                    json_dict_all_parameters["data"].append({"id":filename,
                                                "size": size,
                                                "ni": ni,
                                                "nj": nj,
                                                "allocation": alloc,
                                                "iters": iters,
                                                "compile_size": compile_size})
    elif args.MODE == "single" :
        description = 'default' if (args.allocation is None and args.size is None and args.compile_size is None and args.kernel_mode is None)\
            else str(args.allocation) + str(args.size) + "compile_size: " + str(args.compile_size) + str(args.kernel_mode)
        print(f"Creating {description} benchmark script...")
        # argparse unpacking https://stackoverflow.com/questions/7336181/python-pass-arguments-to-different-methods-from-argparse
        # use args.vars()
        argsdict=vars(args)
        # subset of dictionary:
        # https://stackoverflow.com/questions/3953371/get-a-sub-set-of-a-python-dictionary
        single_mode_vars = {k:(argsdict[k] if not argsdict[k] is None else "") for k in metadata_names if k in argsdict}
        print(single_mode_vars)
        filename,iters,_,_ =\
            codegen_bench_tree_branch(**single_mode_vars)
        json_dict_all_parameters["data"].append({"id":filename,
                                                "size": args.size,
                                                "allocation": args.allocation,
                                                "iters": iters,
                                                "compile_size": args.compile_size,
                                                "kernel_mode_option": args.kernel_mode})
    elif args.MODE != "clean" :
        print("Invalid command.",file=sys.stderr)
        parser.print_help(sys.stderr)
        sys.exit(1)

    ### JSON dump of all parameters used ###
    if args.MODE != "clean":
        f = open(json_filename, "w")
        json.dump(json_dict_all_parameters,f,sort_keys=True, indent=4)
        f.close()
        print("done.")
    
    ### clean mode ###
    if args.MODE == "clean":
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