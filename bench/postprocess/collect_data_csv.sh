#!/bin/bash
if [[ "$1" == "" ]]
then
echo -e "Use flag \"--help\" for help."
fi

if [[ "$1" == "-h" || "$1" == "--help" ]]
then
echo -e Set flag \"./run_bench_tree -nv\" for non verbose option, default is verbose.
echo Verbose gives you a preview of the file as it is written.
echo -e Set flag \"./run_bench_tree -d\" for debug option, default is non debug.
echo Shows you folder to explore while exploring benchmark tree.
exit
fi

# used to preview output file as it is written
# TODO: refactor as verbose
if [[ "$1" == "-nv" || "$2" == "-nv" ]]
then
PREVIEW=false
fi

: ${PREVIEW:=true}
# used to show folders while exploring benchmark tree
# TODO: refactor as debug
if [[ "$1" == "-d" || "$2" == "-d" ]]
then
VERBOSE=true
fi

: ${VERBOSE:=false}

RED='\033[0;31m'
NO_COLOUR='\033[0m'

# always contains default benchmark
defaultfolder=bench_default/
# UPDATE : tree_depth and fullpath() must be updated with each new added parameter
tree_depth=6
fullpath() {
printf "bench_tree/$(basename $directory_1)/$(basename $directory_2)/$(basename $directory_3)/$(basename $directory_4)/$(basename $directory_5)/$(basename $directory_6)/run.sh"
}

# output file is found at tree_depth + 2 upwards at postprocess/data.csv
OUTPUT_FILE=$(printf '../%.0s' $(seq 1 $((tree_depth+2))) )postprocess/data.csv
rm -f $(basename $OUTPUT_FILE)

# go to preprocess to fetch data
cd ../preprocess/bench_tree/

# going down default folder in tree_depth amount of layers
# checking if file exists
if [ ! -d $defaultfolder ]; then
    echo -e "${RED}Default bench not found.${NO_COLOUR} Enter columns labels in csv manually."
else

if $VERBOSE
then echo -n $defaultfolder
fi
cd $defaultfolder
for i in $(seq 1 $((tree_depth-1)) )
do
    defaultfolder=$(ls -d */)
    if $VERBOSE
    then echo -n $defaultfolder
    fi
    cd $defaultfolder
done
if $VERBOSE
then echo
fi
# getting header labels from default bench output .csv
while IFS= read -r line; do
    # in .csv, perf_regions labels start with "Section"
    if [ "${line:0:7}" == "Section" ]
    then
        if $PREVIEW
        then
            echo "$line"
        fi
        # replacing perf_regions naming with json benchmark name ie full path to run.sh
        echo -e "$line" >> $OUTPUT_FILE
    fi
    # grep -o 'action'
done < <( cat out.csv )
for i in $(seq 1 $tree_depth)
do
    cd ..
done

fi # if bench_default does / does not exist

if $VERBOSE
then
    echo -e "\nExploring directories..."
fi

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
                directories_5=$(ls -d */)
                if $VERBOSE
                    then
                        echo $directories_5
                        echo
                    fi
                # sleep 2
                for directory_5 in $directories_5
                do
                    cd $(basename $directory_5)
                    directories_6=$(ls -d */)
                    if $VERBOSE
                        then
                            echo $directories_6
                            echo
                        fi
                    # sleep 2
                    for directory_6 in $directories_6
                    do
                        cd $(basename $directory_6)
                        # write to global output
                        # cat out.csv | xargs echo >> $OUTPUT_FILE
                        if [ ! -f out.csv ]; then
                            if $PREVIEW; then
                            echo -e "$(fullpath)\\t${RED}out.csv not found.${NO_COLOUR}"
                            fi
                        else
                        while IFS= read -r line; do
                            if [ "${line:0:7}" != "Section" ] && [ "${line:0:1}" != "-" ] && [ "${line:0:31}" != "Performance counters profiling:" ] && [ "${line:0:6}" != "Error:" ]
                            then
                                # replacing perf_regions naming with json benchmark name ie full path to run.sh
                                outputline=$(fullpath)\\t${line:8}
                                if $PREVIEW
                                then
                                    echo -e "$outputline"
                                fi
                                echo -e "$outputline" >> $OUTPUT_FILE
                            fi
                            # grep -o 'action'
                        done < <( cat out.csv )
                        fi # if out.csv does / does not exist
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
echo Done collecting.