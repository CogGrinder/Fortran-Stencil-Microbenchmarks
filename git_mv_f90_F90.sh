#!/bin/bash
# see https://www.gnu.org/software/sed/manual/sed.html#sed-script-overview
echo $1
cd $1
f90_files=$(ls *.f90)
for file in $f90_files
do
    echo $file
    #change .f90 to .F90 and basename to lowercase
    file_refactor=$(echo $file | sed -r "s/(.*)[.]([^.]*)\$/\L\1.\U\2/")
    echo $file_refactor
    git mv $file $file_refactor
done
cd ..