import argparse
import sys
import os
import shutil
from shutil import copytree as copy_tree
import pathlib
import shlex
import shutil
import json
from typing import Union
import math

import random
import subprocess, sys

def get_folders(path: str):
    folders = []
    # see https://docs.python.org/3/library/os.html#os.scandir
    with os.scandir(path) as scan:
        folders = [ entry for entry in scan if not entry.name.startswith('.') and entry.is_dir()]
    return folders

def random_subset(folder_list):
    length = len(folder_list)
    n_samples = 0
    if 0 < length <= 2:
        n_samples = 1
    else:
        n_samples = int(length//3)
    return random.sample(folder_list,n_samples)

# random_subset(get_folders(dir))

# command = """

# thank you to https://stackoverflow.com/questions/9322796/keep-a-subprocess-alive-and-keep-giving-it-commands-python

command = "cd ../preprocess/bench_tree"
dir = "../preprocess/bench_tree"
tree=""
for directory_1 in random_subset(get_folders(dir)):
    tree+=directory_1.name + "\n"
    command += "\ncd " + directory_1.name
    
    for directory_2 in random_subset(get_folders(dir+f"/{directory_1.name}")):
        tree+=" "*4+directory_2.name + "\n"
        command += "\ncd " + directory_2.name
        for directory_3 in random_subset(get_folders(dir+f"/{directory_1.name}/{directory_2.name}")):
            tree+=" "*8+directory_3.name + "\n"
            command += "\ncd " + directory_3.name
            for directory_4 in random_subset(get_folders(dir+f"/{directory_1.name}/{directory_2.name}/{directory_3.name}")):
                tree+=" "*12+directory_4.name + "\n"
                command +=f"""
cd {directory_4.name}
# remove previous data
rm -f out.csv
./run.sh
# remove the anti-optimisation file
# used for output of elements of the array being computed
# to prevent compiler from removing computations from zero-closure
# the choice of a file output is because it removes the verbosity from the terminal output
rm tmp.txt
cd ..
"""
print(tree)
subprocess.run(command, shell = True, executable="/bin/bash")
print(tree)