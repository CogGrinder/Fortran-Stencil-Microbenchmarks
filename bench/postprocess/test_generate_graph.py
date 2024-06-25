import numpy as np
import matplotlib.pyplot as plt

import csv

DEBUG = False

with open('data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t', quotechar='|')
    
    labels = reader.__next__()[1:]
    data = [[] for i in range(len(labels)) ]
    benchnames = []
    for i, row in enumerate(reader):
        benchname = row[0].lstrip("bench_execution_")
        if not 'default' in benchname:
            benchnames.append(benchname)
            for j, number in enumerate(row[1:]):
                if not labels[j]=="WALLCLOCKTIME":
                    data[j].append(int(float(number)))
                    if (DEBUG):
                        print(int(float(number)),end="int ")
                else :
                    data[j].append(float(number))
                    if (DEBUG):
                        print(float(number),end="flo ")        
        if (DEBUG):
            print()

    if (DEBUG):
        print(benchnames)
    for i, label in enumerate(labels):
        if not label in ['SPOILED','COUNTER'] :
            plt.plot(data[i], label=labels[i])
    plt.yscale('log')
    plt.xticks(ticks=range(len(benchnames)),labels=benchnames, rotation=90)
    plt.legend()
    plt.tight_layout()
    plt.show()