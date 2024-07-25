#!/bin/bash
#!usr/bin/bash
# if struggling to execute on windows subsystem for linux
# see https://askubuntu.com/questions/304999/not-able-to-execute-a-sh-file-bin-bashm-bad-interpreter

# see https://man7.org/linux/man-pages/man3/printf.3.html
# for printf options used here
# and https://tldp.org/HOWTO/Bash-Prompt-HOWTO/x361.html
# for return carriage special options

tree_depth=5

if [[ "$1" == "" ]]
then
echo -ne "Use flag \"--help\" for help.\r"
sleep 1
fi

if [[ "$1" == "-h" || "$1" == "--help" ]]
then
echo -e Set flag \"./run_bench_tree -v\" for verbose option, default is non verbose.
echo -e Set flag \"./run_bench_tree -vomp\" for verbose OpenMP option, default is non verbose.
fi

if [[ "$1" == "-v" || "$2" == "-v" ]]
then
VERBOSE=true
fi

: ${VERBOSE:=false}

PURPLE="\033[1;35m"
NO_COLOUR="\033[0m"

# function used for printing bench <number>
writeprogressbar() {
    printf "$(printf "%-8s" "$1")[$progressbar]($progresspercent%%)"
}

writeprogress() {
    progresspercent=$(printf "%3d" $((100 * ibench/nbench)))
    n=$(( 16 * ibench / nbench ))
    progressbar=$(printf -- '-%.0s' $(seq 0 $n))$(printf ' %.0s' $(seq $n 16))
    progressbar=${progressbar:1:16}
    export progresspercent
    export progressbar
    echo -ne "\r                                \r"
    if $VERBOSE
    then
    echo -en "$PURPLE bench $((ibench+1))\n"
    else
    echo -en "$PURPLE\033[1A$(printf "%-10s" "bench $((ibench+1))")\033[1B\033[10D"
    fi
    writeprogressbar launch
}

cd bench_tree
directories_1=$(ls -d -1q */)

nbench=$(find -mindepth $tree_depth -maxdepth $tree_depth -type d | wc -w)
echo -ne "\r                                \r"
echo Total amount of benchmarks: $nbench
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
    rm tmp.txt
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
                    # remove previous data
                    rm -f out.csv
                    writeprogress
                    printf "\r"
                    ./run.sh $1 $2
                    if $VERBOSE
                    then
                    echo -ne "\r                                \r"
                    fi
                    # remove the anti-optimisation file
                    # used for output of elements of the array being computed
                    # to prevent compiler from removing computations from zero-closure
                    # the choice of a file output is because it removes the verbosity from the terminal output
                    rm tmp.txt
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
if $VERBOSE
then
echo -en "$NO_COLOUR"
echo "done."
else
echo -en "$NO_COLOUR\033[1Adone.           \033[1B\033[16D"
fi