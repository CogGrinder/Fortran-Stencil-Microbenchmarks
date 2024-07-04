import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import sys
import json

import csv

DEBUG = False

# global labels
# global data
# global benchnames

def import_data(normalise: bool):
    global labels
    global data
    global data_masked
    global benchnames
    f = open("../preprocess/all_benchmark_parameters.json", "r")
    param_dict = json.load(f)

    with open('data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t', quotechar='|')
        
        labels = reader.__next__()[1:]
        data = [[] for i in range(len(labels)) ]
        benchnames = []
        for row in reader:
            benchname = row[0]
            benchname = benchname.lstrip("bench_tree/bench_execution_")
            benchname = benchname.rstrip("/run.sh")
            benchname = benchname.replace("/","")
            print(benchname)
            if not 'default' in benchname:
                benchnames.append(benchname)
                for j, number in enumerate(row[1:]):
                    imported_data = float(number)
                    if labels[j]=="WALLCLOCKTIME":
                        if (DEBUG):
                            print(imported_data,end="flo ")        
                    else :
                        imported_data = int(imported_data)
                        if (DEBUG):
                            print(imported_data,end="int ")
                    if normalise:
                        # print(param_dict[benchname]["iters"])
                        # print(param_dict[benchname]["size_option"])
                        imported_data /= param_dict[row[0]]["iters"] * param_dict[row[0]]["nx"] * param_dict[row[0]]["ny"]
                    data[j].append(imported_data)
                            

        data = np.array(data)
        global label_mask 
        label_mask = np.array([ len(benchnames) *[label in ['SPOILED', 'COUNTER']] for label in labels])
        # print(label_mask)
        data_masked = ma.masked_array(data, mask=label_mask)


        # labels.remove('SPOILED')
        # labels.remove('COUNTER')

        if (DEBUG):
            print(benchnames)
        show_graph_2D()
        # show_graph_3D_2()
        
def show_graph_2D() :
        global labels
        global data
        global data_masked
        global benchnames
        global label_mask

        benchnames_mask =  [
            [ "alloc"  in benchmark_name for benchmark_name in benchnames],
            [ "static" in benchmark_name for benchmark_name in benchnames]
            ]
        # print(benchnames_mask[0])
        
        benchnames_mask =  np.array([
            [ benchnames_mask[0].copy() for i in range(len(labels))],
            [ benchnames_mask[1].copy() for i in range(len(labels))]
            ])

        # print(benchnames_mask[0])
        print(data_masked[0])

        data_alloc =    ma.masked_array(data, mask= np.bitwise_or(benchnames_mask[0],label_mask) )
        data_static =   ma.masked_array(data, mask= np.bitwise_or(benchnames_mask[1],label_mask) )
        print(data_alloc[0])

        print(benchnames_mask[0].sum())

        # courtesy of https://matplotlib.org/stable/gallery/lines_bars_and_markers/barchart.html#sphx-glr-gallery-lines-bars-and-markers-barchart-py
        # tickleft = np.arange(1,len(benchnames)+1)
        # tickleft_alloc =    np.arange(1,len(benchnames)-benchnames_mask[0][0].sum()+1)
        tickleft_alloc =    (1-benchnames_mask[0][0]).cumsum()
        # tickleft_static =   np.arange(1,len(benchnames)-benchnames_mask[1][0].sum()+1)
        tickleft_static =   (1-benchnames_mask[1][0]).cumsum()
        sub_width = 1.0/(len(labels)-1)
        index = 0
        for i, label in enumerate(labels):
            offset = index * sub_width
            if not label in ['SPOILED','COUNTER'] :
                print(data_alloc[i].shape)
                print(tickleft_alloc.shape)
                plt.bar(tickleft_alloc + offset,data_alloc[i],width=sub_width, label=label, alpha=1)
                plt.bar(tickleft_static + offset,data_static[i],width=sub_width/3, label="static variants", alpha=1, color='grey')
                index += 1
        # plt.yscale('log')
        # plt.xticks(rotation=90)
        plt.xticks(ticks=tickleft_static +sub_width*(len(labels)-2 -1)/2.0,labels=benchnames, rotation=60, ha='right')
        plt.legend(bbox_to_anchor=(1.05, 1),
                         loc='upper left', borderaxespad=0.)
        plt.tight_layout()
        plt.show()

def show_graph_3D_1() :
        global labels
        global data
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
        flattened_data = np.array([x for line in data for x in line])
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
        global data
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
                    ax.bar(tickleft + offset,data[i],width=sub_width, label=label, alpha=1, zs=j+1, zdir='y')
                    index += 1
        # plt.yscale('log')
        # plt.xticks(rotation=90)
        # ax.xticks(ticks=tickleft+0.5,labels=benchnames, rotation=60, ha='right')
        ax.legend()
        # plt.tight_layout()
        plt.show()

def main():
    normalise = True
    if len(sys.argv) >= 2:
        normalise = sys.argv[1]
    import_data(normalise)

# courtesy of https://docs.python.org/fr/3/library/__main__.html
if __name__ == '__main__':
    sys.exit(main())