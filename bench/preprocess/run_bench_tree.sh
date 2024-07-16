#!/bin/bash
# if struggling to execute on windows subsystem for linux
# see https://askubuntu.com/questions/304999/not-able-to-execute-a-sh-file-bin-bashm-bad-interpreter
#!usr/bin/bash
cd bench_tree
directories_1=$(ls -d -1q */)
echo $directories_1

nbench=$(find -mindepth 4 -maxdepth 4 -type d | wc -w)
echo @?
ibench=0
# sleep 1
for directory_1 in $directories_1
do
    cd $(basename $directory_1)
    directories_2=$(ls -d -1q */)
    echo $directories_2
    echo
    # sleep 0.1
    for directory_2 in $directories_2
    do

        cd $(basename $directory_2)
        directories_3=$(ls -d -1q */)
        echo $directories_3
        echo
        # sleep 2
        for directory_3 in $directories_3
        do
            cd $(basename $directory_3)
            directories_4=$(ls -d -1q */)
            echo $directories_4
            echo
            # sleep 2
            for directory_4 in $directories_4
            do
                cd $(basename $directory_4)
                # remove previous data
                rm -f out.csv
                progressbar=$(printf "%3d" $((100 * ibench/nbench)))
                echo -ne "                                \r"
                echo "benchmark $(printf "%3d" $ibench)             ($progressbar%)"
                echo -ne "benchmark $(printf "%3d" $ibench)             ($progressbar%)\r"
                export progressbar
                ./run.sh
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