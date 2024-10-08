#!/bin/bash
#!usr/bin/bash
# if struggling to execute on windows subsystem for linux
# see https://askubuntu.com/questions/304999/not-able-to-execute-a-sh-file-bin-bashm-bad-interpreter

# see https://man7.org/linux/man-pages/man3/printf.3.html
# for printf options used here
# and https://tldp.org/HOWTO/Bash-Prompt-HOWTO/x361.html
# for return carriage special options

# UPDATE : tree_depth and debug_fullpath() must be updated with each new added parameter
tree_depth=7
base_directory=$(pwd)
debug_fullpath() {
printf "$base_directory/bench_tree/$(basename $directory_1)/$(basename $directory_2)/$(basename $directory_3)/$(basename $directory_4)/$(basename $directory_5)/$(basename $directory_6)/$(basename $directory_7)/run.sh"
}
# special color ouput
RED='\033[0;31m'
PURPLE="\033[1;35m"
NO_COLOUR="\033[0m"

### execution flags ###
if [[ "$1" == "" || "$1" == "-h" ]]
then
echo -ne "Use flag \"--help\" for help.\r"
sleep 1
fi
if [[ "$1" == "--help" || "$2" == "--help" || "$3" == "--help" || "$4" == "--help" ]]
then
echo -e Set flag \"./run_bench_tree -v\" for verbose option, default is non verbose.
echo -e Set flag \"./run_bench_tree -vout\" for showing output of the benchmark.
echo -e Set flag \"./run_bench_tree -vcompile\" for showing compilation of the benchmark.
echo -e Set flag \"./run_bench_tree -vomp\" for verbose OpenMP option, default is non verbose.
echo -e Set flag \"./run_bench_tree -vompgpu\" for verbose OpenMP option for GPU benchmark only, default is non verbose.
fi

if [[ "$1" == "-v" || "$2" == "-v" || "$3" == "-v" || "$4" == "-v" ]]
then
VERBOSE=true
fi
: ${VERBOSE:=false}

# clear progress bar line in terminal
clear_line() {
    if $VERBOSE
    then
    echo -ne "\r                                \r"
    fi
}

# function used for progress bar
writeprogressbar() {
    printf "$(printf "%-8s" "$1")[$progressbar]($progresspercent%%)"
}

# function for printing bench number
# will print details of previous benchmark when there is an error
writeprogress() {
    progresspercent=$(printf "%3d" $((100 * ibench/nbench)))
    n=$(( 16 * ibench / nbench ))
    progressbar=$(printf -- '-%.0s' $(seq 0 $n))$(printf ' %.0s' $(seq $n 16))
    progressbar=${progressbar:1:16}
    export progresspercent
    export progressbar
    clear_line
    if $VERBOSE
    then
    echo -en "$PURPLE bench $((ibench))\n"
    else
        # check if benchmark was successful
        if [[ "$run_exit_status" != "0" ]] && [[ "$run_exit_status" != "" ]]; then
            printf "$RED%s$NO_COLOUR %s\n" "Benchmark failed:" "$failed_bench_path"
            echo
        fi
        echo -en "$PURPLE\033[1A$(printf "%-32s" "bench $((ibench))")\033[1B\033[32D"
    fi
    writeprogressbar launch
}

cd bench_tree
directories_1=$(ls -d -1q */)

nbench=$(find -mindepth $tree_depth -maxdepth $tree_depth -type d | wc -w)
echo -ne "\r                                \r"
echo Total amount of benchmarks: $nbench
echo
echo
if $VERBOSE
then
    echo $directories_1
    echo
fi

recursive_run()
{
    let depth=$1
    if (( "$depth" <= "1"))
    then
    cd $(basename $2)
    # remove previous data
    rm -f out.csv
    writeprogress
    ./run.sh $VERBOSE
    # remove the anti-optimisation file
    # used for output of elements of the array being computed
    # to prevent compiler from removing computations from zero-closure
    # the choice of a file output is because it removes the verbosity from the terminal output
    rm -f array_tmp.txt
    rm -f result_tmp.txt
    cd ..
    ((ibench+=1))
    else
        # dynamic names: https://stackoverflow.com/questions/16553089/dynamic-variable-names-in-bash
        for directory in $directories
        do  
            cd $(basename $directory)
            recursive_run $(( depth - 1 )) $directory
            cd ..
        done
    fi

}

ibench=0
# sleep 1

# recursive_run $tree_depth

for directory_1 in $directories_1
do
    cd $(basename $directory_1)
    directories_2=$(ls -d -1q */)
    if $VERBOSE
    then
    echo $directories_2
    echo
    fi
    # sleep 0.1
    for directory_2 in $directories_2
    do

        cd $(basename $directory_2)
        directories_3=$(ls -d -1q */)
        if $VERBOSE
        then
        echo $directories_3
        echo
        fi
        # sleep 2
        for directory_3 in $directories_3
        do
            cd $(basename $directory_3)
            directories_4=$(ls -d -1q */)
            if $VERBOSE
            then
            echo $directories_4
            echo
            fi
            # sleep 2
            for directory_4 in $directories_4
            do
                cd $(basename $directory_4)
                directories_5=$(ls -d -1q */)
                if $VERBOSE
                then
                echo $directories_5
                echo
                fi
                # sleep 2
                for directory_5 in $directories_5
                do
                    cd $(basename $directory_5)
                    directories_6=$(ls -d -1q */)
                    if $VERBOSE
                    then
                    echo $directories_6
                    echo
                    fi
                    # sleep 2
                    for directory_6 in $directories_6
                    do
                        cd $(basename $directory_6)
                        directories_7=$(ls -d -1q */)
                        if $VERBOSE
                        then
                        echo $directories_7
                        echo
                        fi
                        # sleep 2
                        for directory_7 in $directories_7
                        do
                            cd $(basename $directory_7)
                            # remove previous data
                            rm -f out.csv
                            writeprogress
                            printf "\r"
                            bash -b run.sh $1 $2 $3 $4
                            # check if benchmark was successful
                            run_exit_status=$?
                            if [[ "$run_exit_status" != "0" ]] && [[ "$run_exit_status" != "" ]]; then
                            failed_bench_path=$(debug_fullpath)
                            fi
                            clear_line
                            # remove the anti-optimisation file
                            # used for output of elements of the array being computed
                            # to prevent compiler from removing computations from zero-closure
                            # the choice of a file output is because it removes the verbosity from the terminal output
                            rm -f tmp.txt
                            cd ..
                            ((ibench+=1))
                        done
                        cd ..
                    done
                    cd ..
                done
                cd ..
            done
            cd ..
        done
        cd ..
    done
    cd ..
done
if $VERBOSE
then
echo -en "$NO_COLOUR"
printf "%-32s" "Done running tree."
else
    echo -ne "$NO_COLOUR$(printf "%-32s" "")\033[32D"
    # check if last benchmark was successful
    if [[ "$run_exit_status" != "0" ]] && [[ "$run_exit_status" != "" ]]; then
        printf "$RED%s$NO_COLOUR %s\n" "Benchmark failed:" "$failed_bench_path"
        echo
    fi
    if [[ "$1" == "-vomp" || "$2" == "-vomp" || "$1" == "-vompgpu" || "$2" == "-vompgpu" ]]; then
    echo -ne "$NO_COLOUR\033[1A$(printf "%-32s" "")\033[1B\033[32D"
    printf "%-32s\n" "Done running tree."
    else
    echo -ne "$NO_COLOUR\033[1A$(printf "%-32s" "Done running tree.")\033[1B\033[32D"
    echo -e "\r                                \r"
    fi
fi