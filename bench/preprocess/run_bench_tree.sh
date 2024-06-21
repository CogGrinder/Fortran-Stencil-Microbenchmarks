#!/bin/bash
ls
cd bench_tree
ls
directories=$(find -mindepth 1 -type d)
echo $directories

for directory in $directories
do
    cd $(basename $directory)
    ls
    ./run.sh
    # remove the anti-optimisation file
    rm output.txt
    cd ..
done