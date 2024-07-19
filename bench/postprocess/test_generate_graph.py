import argparse
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import sys
import json
import datetime

import os
import pathlib

import csv
import pandas as pd

global VERBOSE
VERBOSE = False
global DEBUG
DEBUG = False

# global labels
# global data
# global benchnames

ignored_counters = ['SPOILED', 'COUNTER']
#used for ignoring folder with default benchmarks
default_foldername = 'defaultalloc'

def import_data_pandas(json_metadata_path="../preprocess/all_benchmark_parameters.json",
                       csv_benchdata_path="data.csv",
                       normalise=True):
    """Function that imports csv data as pd.DataFrame
    Args:
        normalise (bool): Normalize all benchmark data
            relative to size and iterations
    """


    # import csv bench data
    datacsvf = open(csv_benchdata_path)
    print("Reading with pd...")
    datacsvdf = pd.read_csv(datacsvf, delimiter='\t')
    datacsvdf.rename(mapper={'Section':'id'},axis=1,inplace=True)
    print(datacsvdf.index)
    datacsvdf.set_index(keys='id',drop=True,verify_integrity=True,inplace=True)
    print(datacsvdf.index)
    print(datacsvdf)

    # import json bench metadata
    benchparamjsonf = open(json_metadata_path, "r")
    param_metadata_dict = json.load(benchparamjsonf)
    benchparamjsonf.close()
    jsonmetadata_df = pd.json_normalize(param_metadata_dict,record_path="data")
    jsonmetadata_df.set_index(keys='id',drop=True,verify_integrity=True,inplace=True)
    print(jsonmetadata_df)

    #multiindex test
    multiindex = pd.MultiIndex.from_arrays(arrays=[
    jsonmetadata_df["kernel_mode"].to_list(),
    jsonmetadata_df["alloc_option"].to_list(),
    jsonmetadata_df["is_compilation_time_size"].to_list(),
    jsonmetadata_df["size_option"].to_list()
    ])
    print(multiindex)
    print()

    ### join ###
    print("JOIN")
    joined_df = datacsvdf.join(jsonmetadata_df)
    index_list = list(joined_df.index)
    # removing default benchmark
    default_key = [i for i in index_list if 'bench_default' in i ]
    default_key=default_key[0]
    joined_df.drop(index=default_key,inplace=True)
    
    # len is the fastest, courtesy of https://stackoverflow.com/questions/15943769/how-do-i-get-the-row-count-of-a-pd-dataframe
    print(joined_df)

    return joined_df

def make_graphs(df: pd.DataFrame,
                interactive=False,
                directory=None,
                all_data_values=['PAPI_L1_TCM',  'PAPI_L2_TCM',  'PAPI_L3_TCM',  'SPOILED',  'WALLCLOCKTIME',  'COUNTER'],
                all_metadata_columns=["size_option","alloc_option","is_compilation_time_size","kernel_mode"],
                graphed_column="size_option",
                default_fixed=       {"size_option":None,
                                      "alloc_option":"ALLOC",
                                      "is_compilation_time_size":True,
                                      "kernel_mode":"DEFAULT_KERNEL"}):
    """Function that makes graphs by using data and metadata from DataFrame and setting fixed units
    Args:
        normalise (bool): Normalize all benchmark data
            relative to size and iterations
    """

    if interactive:
        # input column to graph
        int_graphed_column = int(input(f"Choose column to graph, {all_metadata_columns}\n").strip() or "0")
        graphed_column = all_metadata_columns[int_graphed_column]


    print(f"\nComputing table with {graphed_column}...\n")
    column_selection = all_metadata_columns.copy()
    print(f"all columns:{column_selection}")
    column_selection.remove(graphed_column)
    print(f"column selection:{column_selection}")

    # fixed_columns = [None for i in range(len(column_selection))]
    fixed_columns = []
    non_fixed_columns = all_metadata_columns.copy()

    # thank you to https://stackoverflow.com/questions/33042777/removing-duplicates-from-pd-dataframe-with-condition-for-retaining-original
    print(f"Searching fields with more than one value...")
    for label in column_selection:
        set_of_label = list(set(df[label].to_numpy()))
        if len(set_of_label)>1:
            # set default choice:
            str_value = default_fixed[label]
            # if default choice is not in DataFrame, get first choice
            if not default_fixed[label] in set_of_label:
                str_value=set_of_label[0]
            # set interactively
            if interactive:
                print(f"label \"{label}\" has duplicates. Choose one: {set_of_label}")
                # see https://stackoverflow.com/questions/22402548/how-to-define-default-value-if-empty-user-input-in-python
                # default input is 0 so one can press enter for default
                int_value = int(input(f"Choose index\n").strip() or "0")
                str_value = set_of_label[int_value]
            print(str_value)
            fixed_columns.append(label)
            non_fixed_columns.remove(label)
            # TODO
            # force the column's string column label to type 'category'  
            df[label] = df[label].astype('category')
            # define the valid categories:
            custom_sorted_category_list_from_label = list(set(df[label].to_list()))
            custom_sorted_category_list_from_label.remove(str_value)
            custom_sorted_category_list_from_label.insert(0,str_value)
            print(custom_sorted_category_list_from_label)
            df[label] = df[label].cat.set_categories(custom_sorted_category_list_from_label, ordered=True)
        else:
            print(f"label \"{label}\" already has 1 or 0 values")
    
    if DEBUG:
        print(f"fixed_columns: {fixed_columns}")
        print(f"non_fixed_columns: {non_fixed_columns}")

    # sort to put first selected category at the top of each label 
    df.sort_values(fixed_columns, inplace=True, ascending=True) 
    if DEBUG:
        print(f"Now sorted by custom categories") 
        print(df)
    # dropping duplicates keeps first
    size_optiondf = df.drop_duplicates(non_fixed_columns,keep="first") 
    print("Keep the highest value category given duplicate integer group") 
    print(size_optiondf)


    #other option to try: >>> index = pd.MultiIndex.from_tuples(tuples)
    # >>> values = [[12, 2], [0, 4], [10, 20],
    # ...           [1, 4], [7, 1], [16, 36]]
    # >>> df = pd.DataFrame(values, columns=['max_speed', 'shield'], index=index)
    # >>> df

    size_optiondf = size_optiondf.pivot(index=[graphed_column],
                                        columns=column_selection,
                                        values=all_data_values)
    size_optiondf = size_optiondf.transpose()
    size_optiondf.drop(['SPOILED', 'COUNTER'],inplace=True)
    print(size_optiondf)
    
    index_list = list(list(str(i) for i in tuple_i) for tuple_i in size_optiondf.index)
    column_list = list(map(str,size_optiondf.columns))
    print(f"column_list:{column_list}")

    dir = "./" if directory==None else str(directory).rstrip("/") + "/"

    n_rows_selection = len(size_optiondf.index)
    for i in range(n_rows_selection):
        print(size_optiondf.iloc[i])
        fig,ax = plt.subplots()
        print(ax)
        print(index_list[i])
        ax.bar(column_list,size_optiondf.iloc[i].array)
        ax.set_title(f"{graphed_column} with {str(index_list[i][0])}\nFixed options: {' '.join(index_list[i][1:])}")
        ax.set_xticks(ticks=column_list,labels=list(set(df[graphed_column].to_list())), rotation=60, ha='right')
        print(ax)
        fig.savefig(f"{dir}{graphed_column}_{str(index_list[i][0])}.pdf")
    exit(-1)

def import_data_old(normalise=True,
                    json_metadata_path="../preprocess/all_benchmark_parameters.json"):
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

    # import json bench metadata
    benchparamjsonf = open(json_metadata_path, "r")
    param_metadata_dict = json.load(benchparamjsonf)
    benchparamjsonf.close()

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

def argument_parsing(parser: argparse.ArgumentParser):
    parser.add_argument('-M','--MODE', nargs='?', default='default',
                    help='Can be default, interactive or old.')
    
    parser.add_argument('-D', '--directory',
                        help='Sets .pdf directory.')

    # Optional arguments
    # TODO:
    parser.add_argument('-c', '--clean-before', action='store_true',
                        help='Cleans existing files before generating.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Displays more output')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Displays debug output')
    return parser.parse_args()

def main():
    """Main function of graph generation - interprets input from argparse

    Use --help for details.
    """
    global VERBOSE
    global DEBUG
    parser = argparse.ArgumentParser(description="Graph generator for benchmark results with options to choose data to compare with different groupings")
    args = argument_parsing(parser)
    
    if len(sys.argv)==1:
        print("No arguments provided.",file=sys.stderr)
        parser.print_help(sys.stderr)
        sys.exit(1)
    if args.debug:
        DEBUG=True

    if DEBUG:
        print(args)

    if args.verbose:
        VERBOSE=True

    if not args.directory is None:
        if not pathlib.Path(args.directory).is_dir() :
                os.mkdir(args.directory)

    if args.MODE=="default":
        df = import_data_pandas(normalise=True)
        make_graphs(df, interactive=False, directory=args.directory)
    elif args.MODE=="interactive":
        df = import_data_pandas(normalise=True)
        make_graphs(df, interactive=True, directory=args.directory)

    elif args.MODE=="old":
        import_data_old(normalise=True)
        show_graph_2D(fileprefix="cache_misses")
        show_graph_2D(fileprefix="wallclocktime",is_wallclocktime_graph=True)
    else:
        print("Mode undefined.")
    print("\nDone.")

# courtesy of https://docs.python.org/fr/3/library/__main__.html
if __name__ == '__main__':
    sys.exit(main())