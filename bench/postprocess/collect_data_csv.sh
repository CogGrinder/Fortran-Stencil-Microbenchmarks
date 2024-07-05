#!/bin/bash
VERBOSE=false
# defaultpath and tree_depth must be updated with each new added parameter
defaultpath=bench_defaultalloc/_defaultsize/_sizenotcompiled/_defaultkernel
tree_depth=4
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
        if $VERBOSE
        then
            echo "$line"
        fi
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
if $VERBOSE
    then
        echo $directories_1
        echo
    fi
for directory_1 in $directories_1
do
    cd $(basename $directory_1)
    directories_2=$(ls -d */)
    if $VERBOSE
        then
            echo $directories_2
            echo
        fi
    for directory_2 in $directories_2
    do
        cd $(basename $directory_2)
        directories_3=$(ls -d */)
        if $VERBOSE
            then
                echo $directories_3
                echo
            fi
        for directory_3 in $directories_3
        do
            cd $(basename $directory_3)
            directories_4=$(ls -d */)
            if $VERBOSE
                then
                    echo $directories_4
                    echo
                fi
            # sleep 2
            for directory_4 in $directories_4
            do
                cd $(basename $directory_4)
                # write to global output
                # cat out.csv | xargs echo >> $OUTPUT_FILE
                while IFS= read -r line; do
                    if [ "${line:0:7}" != "Section" ] && [ "${line:0:1}" != "-" ] && [ "${line:0:31}" != "Performance counters profiling:" ] && [ "${line:0:6}" != "Error:" ]
                    then
                        if $VERBOSE
                        then
                            echo "$line"
                        fi
                        # TODO : replace with json benchmark name or executable name
                        # UPDATE : add new directory here
                        echo -e "bench_tree/$(basename $directory_1)/$(basename $directory_2)/$(basename $directory_3)/$(basename $directory_4)/run.sh\t${line:8}" >> $OUTPUT_FILE
                    fi
                    # grep -o 'action'
                done < <( cat out.csv )
                cd ..
            done
            cd ..
        done
        cd ..
    done
    cd ..
done
echo done