import argparse
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import sys
import json
import datetime

import csv

DEBUG = False

# global labels
# global data
# global benchnames

ignored_counters = ['SPOILED', 'COUNTER']
#used for ignoring folder with default benchmarks
default_foldername = 'defaultalloc'

def import_data(normalise=True):
    """Function that imports csv data as numpy array and label lists

    Args:
        normalise (bool): Normalize all benchmark data
            relative to size and iterations
    """
    global labels
    global labels_no_superfluous
    global cache_miss_data
    global wallclocktime_data
    global cache_miss_data
    global benchpaths
    global benchnames
    global label_mask 
    f = open("../preprocess/all_benchmark_parameters.json", "r")
    param_dict = json.load(f)

    with open('data.csv', newline='') as csvfile:
        csvfile_reader = csv.reader(csvfile, delimiter='\t', quotechar='|')
        # import the first line of the csv as the data labels
        labels = csvfile_reader.__next__()[1:]
        # make a list of the labels we keep for graphing
        # TODO: see if it is better to make a mask ?? I don't think so
        labels_no_superfluous = labels.copy()
        for label in ignored_counters:
            labels_no_superfluous.remove(label)
        print(f"CSV LABELS: {labels}")
        print(f"KEPT LABELS: {labels_no_superfluous}")

        wallclocktime_data = []
        #initialise cache miss data array - we assume wallclocktime to be a label of the data in the "-1"
        # see line 126
        cache_miss_data = [[] for i in range(len(labels_no_superfluous) - 1) ]
        benchpaths = []
        benchnames = []
        for row in csvfile_reader:
            benchpath = row[0]
            benchname = benchpath
            benchname = benchname.lstrip("bench_tree/bench_").rstrip("/run.sh").replace("/","")
            # if DEBUG:
            #     print(benchname)
            if default_foldername not in benchname:
                benchpaths.append(benchpath)
                benchnames.append(benchname)
                j_included_label=0
                for j_row, number in enumerate(row[1:]):
                    if labels[j_row] not in ignored_counters:
                        imported_data = float(number)
                        if labels[j_row]=="WALLCLOCKTIME":
                            if (DEBUG):
                                print(imported_data,end="flo ")
                            # if normalise:
                            #     imported_data *= float("5e+8")
                        else :
                            imported_data = int(imported_data)
                            if (DEBUG):
                                print(imported_data,end="int ")
                        if normalise:
                            imported_data /= param_dict[row[0]]["iters"] * param_dict[row[0]]["ni"] * param_dict[row[0]]["nj"]
                        # save data in appropriate data
                        if labels[j_row]=="WALLCLOCKTIME":
                            wallclocktime_data.append(imported_data)
                        else:
                            if DEBUG:
                                print(f"cache_miss_data[j_included_label] - j_included_label={j_included_label}")
                            cache_miss_data[j_included_label].append(imported_data)
                            j_included_label+=1
                        
                            

        cache_miss_data = np.array(cache_miss_data)
        # label_mask = np.array([ len(benchnames) *[label in ['SPOILED', 'COUNTER']] for label in labels])
        # cache_miss_data = ma.masked_array(cache_miss_data, mask=label_mask)
        
        # JSON export
        filename = "data.json"
        f = open(filename, "w")
        json.dump(cache_miss_data.tolist(),f, indent=4)
        
def show_graph_2D(fileprefix="",is_wallclocktime_graph=False) :
        global labels
        global labels_no_superfluous
        global cache_miss_data
        global wallclocktime_data
        global benchnames
        global label_mask

        plt.figure(figsize=(40,20))

        # TODO: replace with access to JSON bench parameters
        benchnames_mask =  [
            [ "alloc"  in benchmark_name for benchmark_name in benchnames],
            [ "static" in benchmark_name for benchmark_name in benchnames]
            ]
        if DEBUG:
            print("\n\nMask for first data label")
            print(benchnames_mask[0])
        benchnames_mask = np.array(benchnames_mask)
        # courtesy of https://matplotlib.org/stable/gallery/lines_bars_and_markers/barchart.html#sphx-glr-gallery-lines-bars-and-markers-barchart-py
        # tickleft = np.arange(1,len(benchnames)+1)
        # tickleft_alloc =    np.arange(1,len(benchnames)-benchnames_mask[0][0].sum()+1)
        tickleft_alloc =    (1-benchnames_mask[0]).cumsum()
        # tickleft_static =   np.arange(1,len(benchnames)-benchnames_mask[1][0].sum()+1)
        tickleft_static =   (1-benchnames_mask[1]).cumsum()

        if is_wallclocktime_graph:
            if DEBUG:
                print("\nData:")
                print(wallclocktime_data)

            # data_alloc =    ma.masked_array(cache_miss_data, mask= np.bitwise_or(benchnames_mask[0],label_mask) )
            data_alloc =    ma.masked_array(wallclocktime_data, mask= benchnames_mask[0] )
            # data_static =   ma.masked_array(cache_miss_data, mask= np.bitwise_or(benchnames_mask[1],label_mask) )
            data_static =   ma.masked_array(wallclocktime_data, mask= benchnames_mask[1] )
            if DEBUG:
                print(data_alloc[0])
        else:
            benchnames_mask =  np.array([
                [ benchnames_mask[0].copy() for i in range(len(labels_no_superfluous)-1)],
                [ benchnames_mask[1].copy() for i in range(len(labels_no_superfluous)-1)]
                ])

            if DEBUG:
                print(benchnames_mask[0])

            if DEBUG:
                print("\nData:")
                print(cache_miss_data)

            # data_alloc =    ma.masked_array(cache_miss_data, mask= np.bitwise_or(benchnames_mask[0],label_mask) )
            data_alloc =    ma.masked_array(cache_miss_data, mask= benchnames_mask[0] )
            # data_static =   ma.masked_array(cache_miss_data, mask= np.bitwise_or(benchnames_mask[1],label_mask) )
            data_static =   ma.masked_array(cache_miss_data, mask= benchnames_mask[1] )
            
            if DEBUG:
                print(data_alloc[0])
                print(benchnames_mask[0].sum())

            # courtesy of https://matplotlib.org/stable/gallery/lines_bars_and_markers/barchart.html#sphx-glr-gallery-lines-bars-and-markers-barchart-py
            # tickleft = np.arange(1,len(benchnames)+1)
            # tickleft_alloc =    np.arange(1,len(benchnames)-benchnames_mask[0][0].sum()+1)
            tickleft_alloc =    (1-benchnames_mask[0][0]).cumsum()
            # tickleft_static =   np.arange(1,len(benchnames)-benchnames_mask[1][0].sum()+1)
            tickleft_static =   (1-benchnames_mask[1][0]).cumsum()
        sub_width = 1.0/(len(labels)-1)
        if is_wallclocktime_graph:
            offset = 0
            if DEBUG:
                print(data_alloc.shape)
                print(tickleft_alloc.shape)
            plt.bar(tickleft_alloc + offset,wallclocktime_data,width=sub_width, label="WALLCLOCKTIME", alpha=1)
            plt.bar(tickleft_static + offset,wallclocktime_data,width=sub_width/3, label="static variant", alpha=1, color='black')
        else:
            index = 0
            for label in labels_no_superfluous:
                if label != 'WALLCLOCKTIME':
                    offset = index * sub_width
                    if DEBUG:
                        print(data_alloc[index].shape)
                        print(tickleft_alloc.shape)
                    plt.bar(tickleft_alloc + offset,data_alloc[index],width=sub_width, label=label, alpha=1)
                    plt.bar(tickleft_static + offset,data_static[index],width=sub_width/3, label="static variants", alpha=1, color='black')
                    index += 1
        # plt.yscale('log')
        # plt.xticks(rotation=90)
        plt.xticks(ticks=tickleft_static +sub_width*(len(labels)-2 -1)/2.0,labels=benchnames, rotation=60, ha='right')
        plt.legend(bbox_to_anchor=(1.05, 1),
                         loc='upper left', borderaxespad=0.)
        plt.tight_layout()

        now = datetime.date.today()
        plt.savefig(fileprefix+"fig" + str(now) + ".pdf")
        plt.show() if str(input("Open figure in new window? (Y/n)\n"))=='Y' else None

def show_graph_3D_1() :
        global labels
        global cache_miss_data
        global benchnames
        fig = plt.figure(figsize=(8, 3))
        ax1 = fig.add_subplot(projection='3d')

        # _xx, _yy = np.meshgrid(benchnames, labels)
        _xx, _yy = np.meshgrid(np.arange(len(benchnames)), np.arange(len(labels)))
        x, y = _xx.ravel(), _yy.ravel()
        print(x)
        print(y)
        print(x.shape)
        bottom = np.zeros_like(x)
        width = 1
        depth = 1
        flattened_data = np.array([x for line in cache_miss_data for x in line])
        print(flattened_data.shape)
        ax1.bar3d(x, y, bottom, width, depth, flattened_data, shade=True)
        ax1.set_title('Shaded')
        # ax1.zscale('log')

        """
        for i, label in enumerate(labels):
            if not label in ['SPOILED','COUNTER'] :
                plt.bar(benchnames,data[i], label=labels[i])
        plt.yscale('log')
        """
        # plt.xticks(rotation=90)
        # plt.xticks(rotation=60, ha='right')
        plt.legend()
        plt.tight_layout()
        plt.show()

def polygon_under_graph(x, y):
    """
    Construct the vertex list which defines the polygon filling the space under
    the (x, y) line graph. This assumes x is in ascending order.
    """
    return [(x[0], 0.), *zip(x, y), (x[-1], 0.)]

def show_graph_3D_2() :
        global labels
        global cache_miss_data
        global benchnames

        # 3D accumulation courtesy of https://matplotlib.org/stable/gallery/mplot3d/polys3d.html
        ax = plt.figure().add_subplot(projection='3d')

        # x = np.linspace(0., 1.*(len(labels)-2), (len(labels)-2)*4)

        # 2D subgraph courtesy of https://matplotlib.org/stable/gallery/lines_bars_and_markers/barchart.html#sphx-glr-gallery-lines-bars-and-markers-barchart-py
        tickleft = np.arange(len(benchnames))
        sub_width = 1.0/(len(labels)-2)
        for j in range(2):
            index = 0
            for i, label in enumerate(labels):
                offset = index * sub_width
                if not label in ['SPOILED','COUNTER'] :
                    ax.bar(tickleft + offset,cache_miss_data[i],width=sub_width, label=label, alpha=1, zs=j+1, zdir='y')
                    index += 1
        # plt.yscale('log')
        # plt.xticks(rotation=90)
        # ax.xticks(ticks=tickleft+0.5,labels=benchnames, rotation=60, ha='right')
        ax.legend()
        # plt.tight_layout()
        plt.show()

def main():
    """Main function of graph generation - interprets input from argparse

    Use --help for details.
    """
    parser = argparse.ArgumentParser(description="Graph generator for benchmark results with options to choose data to compare with different groupings")
    args = parser.parse_args()
    if len(sys.argv)==1:
        print("No arguments provided.",file=sys.stderr)
        parser.print_help(sys.stderr)
        print("\nDefault execution:\n")

    normalise = True
    if len(sys.argv) >= 2:
        normalise = sys.argv[1]
    import_data(normalise)
    show_graph_2D(fileprefix="cache_misses")
    show_graph_2D(fileprefix="wallclocktime",is_wallclocktime_graph=True)
    print("\nDone.")


# courtesy of https://docs.python.org/fr/3/library/__main__.html
if __name__ == '__main__':
    sys.exit(main())