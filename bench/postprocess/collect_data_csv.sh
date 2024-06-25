#!/bin/bash
OUTPUT_FILE=../../../../postprocess/data.csv
default=bench_execution_defaultalloc_defaultsize
defaultpath=bench_execution_defaultalloc/_defaultsize
tree_depth=2

cd ../preprocess/bench_tree
directories_1=$(find -mindepth 1 -maxdepth 1 -type d)
echo $directories_1
echo

cd $defaultpath
while IFS= read -r line; do
    if [ "${line:0:7}" == "Section" ]
    then
        echo "$line"
        # TODO : replace with json benchmark name or executable name
        echo -e "$line" >> $OUTPUT_FILE
    fi
    # grep -o 'action'
done < <( cat out.csv )
for i in $(seq 1 $tree_depth)
do
    cd ..
done


for directory_1 in $directories_1
do
    cd $(basename $directory_1)
    directories_2=$(find -mindepth 1 -maxdepth 1 -type d)
    echo $directories_2
    echo
    for directory_2 in $directories_2
    do
        cd $(basename $directory_2)
        # write to global output
        # cat out.csv | xargs echo >> $OUTPUT_FILE
        while IFS= read -r line; do
            if [ "${line:0:7}" != "Section" ] && [ "${line:0:1}" != "-" ] && [ "${line:0:31}" != "Performance counters profiling:" ]
            then
                echo "$line"
                # TODO : replace with json benchmark name or executable name
                echo -e "$(basename $directory_1)$(basename $directory_2)\t${line:9}" >> $OUTPUT_FILE
            fi
            # grep -o 'action'
        done < <( cat out.csv )
        cd ..
    done
    cd ..
done