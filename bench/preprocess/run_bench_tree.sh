#!/bin/bash
cd bench_tree
directories_1=$(find -mindepth 1 -maxdepth 1 -type d)
echo $directories_1
echo
# sleep 0.5

for directory_1 in $directories_1
do
    cd $(basename $directory_1)
    directories_2=$(find -mindepth 1 -maxdepth 1 -type d)
    echo $directories_2
    echo
    # sleep 0.1
    for directory_2 in $directories_2
    do
        cd $(basename $directory_2)
        # remove previous data
        rm -f out.csv
        ./run.sh
        # remove the anti-optimisation file
        rm output.txt
        cd ..
    done
    cd ..
done