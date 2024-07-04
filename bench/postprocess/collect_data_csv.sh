#!/bin/bash
# default=bench_execution_defaultalloc_defaultsize
# defaultpath and tree_depth must be updated with each new added parameter
defaultpath=bench_execution_defaultalloc/_defaultsize/_sizenotcompiled
tree_depth=3
OUTPUT_FILE=../../postprocess/data.csv
for i in $(seq 1 $tree_depth)
do
    OUTPUT_FILE=../$OUTPUT_FILE
done

rm -f $(basename $OUTPUT_FILE)

cd ../preprocess/bench_tree

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

directories_1=$(ls -d */)
echo $directories_1
echo
for directory_1 in $directories_1
do
    cd $(basename $directory_1)
    directories_2=$(ls -d */)
    echo $directories_2
    echo
    for directory_2 in $directories_2
    do
        cd $(basename $directory_2)
        directories_3=$(ls -d */)
        echo $directories_3
        echo
        for directory_3 in $directories_3
        do
            cd $(basename $directory_3)
            # write to global output
            # cat out.csv | xargs echo >> $OUTPUT_FILE
            while IFS= read -r line; do
                if [ "${line:0:7}" != "Section" ] && [ "${line:0:1}" != "-" ] && [ "${line:0:31}" != "Performance counters profiling:" ]
                then
                    echo "$line"
                    # TODO : replace with json benchmark name or executable name
                    echo -e "bench_tree/$(basename $directory_1)/$(basename $directory_2)/$(basename $directory_3)/run.sh\t${line:8}" >> $OUTPUT_FILE
                fi
                # grep -o 'action'
            done < <( cat out.csv )
            cd ..
        done
        cd ..
    done
    cd ..
done