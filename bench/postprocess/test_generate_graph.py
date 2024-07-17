import argparse
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import sys
import json
import datetime

import csv
import pandas

DEBUG = True

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
    benchparamjsonf = open("../preprocess/all_benchmark_parameters.json", "r")
    param_metadata_dict = json.load(benchparamjsonf)
    benchparamjsonf.close()

    # if DEBUG:
    datacsvf = open('data.csv')
    print("Reading with pandas...")
    datacsvdf = pandas.read_csv(datacsvf, delimiter='\t')
    datacsvdf.rename(mapper={'Section':'id'},axis=1,inplace=True)
    # print(debugcsv)
    print(datacsvdf.index)
    datacsvdf.set_index(keys='id',drop=True,verify_integrity=True,inplace=True)
    print(datacsvdf.index)
    print(datacsvdf)
    # l1cache = debugcsv.pivot(index='Section',columns=,values='PAPI_L1_TCM')
    # print(l1cache)
    l1cache=datacsvdf["PAPI_L1_TCM"]
    print(l1cache)

    jsonmetadata_df = pandas.json_normalize(param_metadata_dict,record_path="data")
    jsonmetadata_df.set_index(keys='id',drop=True,verify_integrity=True,inplace=True)
    print(jsonmetadata_df)
    multiindex = pandas.MultiIndex.from_arrays(arrays=[
    jsonmetadata_df["kernel_mode"].to_list(),
    jsonmetadata_df["alloc_option"].to_list(),
    jsonmetadata_df["is_compilation_time_size"].to_list(),
    jsonmetadata_df["size_option"].to_list()
    ])
    print(multiindex)
    print()
    # join
    joineddf = datacsvdf.join(jsonmetadata_df)
    index_list = list(joineddf.index)
    default_key = [i for i in index_list if 'bench_default' in i ]
    default_key=default_key[0]
    print(default_key)
    joineddf.drop(index=default_key,inplace=True)
    print(joineddf)
    all_values=['PAPI_L1_TCM',  'PAPI_L2_TCM',  'PAPI_L3_TCM',  'WALLCLOCKTIME']
    all_columns=["size_option","alloc_option","is_compilation_time_size","kernel_mode"]
    
    # example:
    size_optiondf = joineddf.pivot(index=['size_option'], columns=["alloc_option","is_compilation_time_size","kernel_mode"], values=['PAPI_L1_TCM',  'PAPI_L2_TCM',  'PAPI_L3_TCM',  'SPOILED',  'WALLCLOCKTIME',  'COUNTER'])
    print(size_optiondf)
    print(size_optiondf.index)
    size_optiondf = size_optiondf.transpose()
    size_optiondf.drop(['SPOILED', 'COUNTER'],inplace=True)
    print(size_optiondf)
    
    index_list = list(list(str(i) for i in tuple_i) for tuple_i in size_optiondf.index)
    column_list = list(map(int,size_optiondf.columns))
    print(index_list)
    print(column_list)

    # len is the fastest, courtesy of https://stackoverflow.com/questions/15943769/how-do-i-get-the-row-count-of-a-pandas-dataframe
    n_rows = len(size_optiondf.index)
    for i in range(n_rows):
        print(size_optiondf.iloc[i])
        fig,ax = plt.subplots()
        print(ax)
        print(index_list[i])
        ax.bar(column_list,size_optiondf.iloc[i].array)
        ax.set_title(f"size_option with {str(index_list[i][0])}\nFixed options: {' '.join(index_list[i][1:])}")
        ax.set_xticks(ticks=column_list,labels=['1Mb','2Mb'], rotation=60, ha='right')
        print(ax)
        fig.legend()
        fig.savefig(f"size_option_{str(index_list[i][0])}.pdf")
    exit(-1)

    # print(size_optiondf[].head())

    # thank you https://stackoverflow.com/questions/18992086/save-a-pandas-series-histogram-plot-to-file
    # and https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html
    ax = (size_optiondf).hist(legend=True)  # s is an instance of Series
    print(ax)
    for sublist in ax:
        for subax in sublist:
            fig = subax.get_figure()
            fig.savefig(subax.title.get_text()+'size_option.pdf')

    with open('data.csv', newline='') as csvfile:
        csvfile_reader = csv.reader(csvfile, delimiter='\t', quotechar='|')
        # import the first line of the csv as the data labels
        labels = csvfile_reader.__next__()[1:]
        # make a list of the labels we keep for graphing
        # TODO: see if it is better to make a mask ?? I don't think so
        labels_no_superfluous = labels.copy()
        for label in ignored_counters:
            if label in labels_no_superfluous:
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
                            imported_data /= param_metadata_dict[row[0]]["iters"] * param_metadata_dict[row[0]]["ni"] * param_metadata_dict[row[0]]["nj"]
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
        benchparamjsonf = open(filename, "w")
        json.dump(cache_miss_data.tolist(),benchparamjsonf, indent=4)
        
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