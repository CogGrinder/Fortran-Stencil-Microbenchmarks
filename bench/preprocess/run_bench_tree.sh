#!/bin/bash
cd bench_tree
directories_1=$(ls -d */)
echo $directories_1
echo
# sleep 0.5
for directory_1 in $directories_1
do
    cd $(basename $directory_1)
    directories_2=$(ls -d */)
    echo $directories_2
    echo
    # sleep 0.1
    for directory_2 in $directories_2
    do

        cd $(basename $directory_2)
        directories_3=$(ls -d */)
        echo $directories_3
        echo
        # sleep 2
        for directory_3 in $directories_3
        do
            cd $(basename $directory_3)
            # remove previous data
            rm -f out.csv
            ./run.sh
            # remove the anti-optimisation file
            # used for output of elements of the array being computed
            # to prevent compiler from removing computations from zero-closure
            # the choice of a file output is because it removes the verbosity from the terminal output
            rm tmp.txt
            cd ..
        done
        cd ..
    done
    cd ..
done