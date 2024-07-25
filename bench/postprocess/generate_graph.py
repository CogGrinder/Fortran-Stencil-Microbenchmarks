import argparse
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import sys
import json
import datetime

import os
import pathlib
import shutil

import csv
import pandas as pd

global VERBOSE
VERBOSE = False
global DEBUG
DEBUG = False

# used for selecting benchmarks classifying data
all_metadata_columns=["kernel_mode",
                      "hardware_option",
                      "alloc_option",
                      "is_module",
                      "size_option",
                      "is_compilation_time_size"]
metadata_types =\
    {
    "kernel_mode" : str,
    "hardware_option" : str,
    "alloc_option" : str,
    "is_module" : bool,
    "size_option" : float,
    "is_compilation_time_size" : bool
    }
all_data_values=['PAPI_L1_TCM',  'PAPI_L2_TCM',  'PAPI_L3_TCM',  'WALLCLOCKTIME']
# default benchmark, also known as baseline benchmark or control experiment
baseline_for_comparison =\
    {
    "kernel_mode" : "DEFAULT_KERNEL",
    "hardware_option" : "CPU",
    "alloc_option" : "ALLOCATABLE",
    "is_module" : True,
    "size_option" : None,
    "is_compilation_time_size" : True
    }

# used to ignore counters collected by perf_regions that have a debug purpose
ignored_counters = ['SPOILED', 'COUNTER']
# deprecated: used for ignoring folder with default benchmark
default_foldername = 'bench_default'

def import_data_pandas(json_metadata_path,
                       csv_benchdata_path,
                       all_metadata_columns=all_metadata_columns,
                       all_data_values=all_data_values,
                       normalise=True):
    """Function that imports csv data as pd.DataFrame
    Args:
        normalise (bool): Normalize all benchmark data
            relative to size and iterations
    """


    # import csv bench data
    datacsvf = open(csv_benchdata_path)
    print("Reading .csv with pd...")
    datacsvdf = pd.read_csv(datacsvf, delimiter='\t')
    datacsvdf.rename(mapper={'Section':'id'},axis=1,inplace=True)
    if DEBUG and VERBOSE:
        print(datacsvdf.index)
    datacsvdf.set_index(keys='id',drop=True,verify_integrity=True,inplace=True)
    if DEBUG and VERBOSE:
        print(datacsvdf.index)
    if VERBOSE or DEBUG:
        print(datacsvdf)
        print()


    # import json bench metadata
    benchparamjsonf = open(json_metadata_path, "r")
    print("Reading .json with pd...")
    param_metadata_dict = json.load(benchparamjsonf)
    benchparamjsonf.close()
    jsonmetadata_df = pd.json_normalize(param_metadata_dict,record_path="data")
    jsonmetadata_df.set_index(keys='id',drop=True,verify_integrity=True,inplace=True)
    # sorting
    jsonmetadata_df.sort_values(by=all_metadata_columns, inplace=True, ascending=True)
    if VERBOSE or DEBUG:
        print(jsonmetadata_df)
        print()

    if DEBUG:
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
    print("Joining both DataFrames...")
    joined_df = datacsvdf.join(jsonmetadata_df)
    index_list = list(joined_df.index)
    # removing default benchmark
    default_key = [i for i in index_list if 'bench_default' in i ]
    default_key=default_key[0]
    joined_df.drop(index=default_key,inplace=True)
    
    # len is the fastest, courtesy of https://stackoverflow.com/questions/15943769/how-do-i-get-the-row-count-of-a-pd-dataframe
    if VERBOSE or DEBUG:
        print(joined_df)
    print("Done importing.")
    print()

    if normalise:
        print("Normalising...")
        labels = all_data_values
        for label in labels:
            joined_df[label] = joined_df[label] / (joined_df["iters"] * joined_df["ni"] * joined_df["nj"])
        if VERBOSE:
            print(joined_df[labels])

    return joined_df

def find_non_unique_parameters(df: pd.DataFrame,
                             columns=all_metadata_columns):
    """Function that checks for parameters that have more than one value in DataFrame.

    Useful both for finding parameters with are interesting to graph (more than 1 value) or need to be specified, and parameters which are fixed already.

    Args:
        columns (list[str]): List of column labels to search
    Returns:
        np.array[bool] containing whether the label has only one value
    """
    return np.array([len(set(df[label].to_numpy()))>1 for label in columns])

def make_graphs(df: pd.DataFrame,
                interactive=False,
                directory=None,
                subplots_in_one_figure=False,
                all_data_values=all_data_values,
                all_metadata_columns=all_metadata_columns,
                graphed_column="size_option",
                secondary_graphed=None,
                baseline_for_comparison=baseline_for_comparison):
    """Function that makes graphs by using data and metadata from DataFrame and setting fixed units
    Args:
        normalise (bool): Normalize all benchmark data
            relative to size and iterations
    """

    ############ selecting data ############

    if interactive:
        # input column to graph
        int_graphed_column = int(input(f"Choose column to graph, {all_metadata_columns}\n").strip() or "0")
        graphed_column = all_metadata_columns[int_graphed_column]


    print(f"Computing {graphed_column}{'' if secondary_graphed is None else ' ('+secondary_graphed+' as rows)'} graphing...")
    column_selection = all_metadata_columns.copy()
    if VERBOSE:
        print(f"all columns:{column_selection}")
    column_selection.remove(graphed_column)
    # if their is a secondary graphed parameter, add here
    if secondary_graphed is not None:
        column_selection.remove(secondary_graphed)
    if VERBOSE:
        print(f"column selection:{column_selection}")

    # fixed_columns = [None for i in range(len(column_selection))]
    fixed_columns = []
    non_fixed_columns = all_metadata_columns.copy()
    values_kept = []

    # thank you to https://stackoverflow.com/questions/33042777/removing-duplicates-from-pd-dataframe-with-condition-for-retaining-original
    if VERBOSE:
        print(f"\nFiltering fields with more than one value...\n")
    for label in column_selection:
        set_of_label = list(set(df[label].to_numpy()))
        if len(set_of_label)>1:
            # set default choice:
            value_kept = baseline_for_comparison[label]
            # if default choice is not in DataFrame, get first choice
            if not baseline_for_comparison[label] in set_of_label:
                value_kept=set_of_label[0]
            # set interactively
            if interactive:
                print(f"Label \"{label}\" has duplicates. Choose one: {set_of_label}")
                # see https://stackoverflow.com/questions/22402548/how-to-define-default-value-if-empty-user-input-in-python
                # default input is 0 so one can press enter for default
                index_kept = int(input(f"Choose index\n").strip() or "0")
                value_kept = set_of_label[index_kept]
            if DEBUG:
                print(f"Kept value: {value_kept}")
            fixed_columns.append(label)
            non_fixed_columns.remove(label)
            values_kept.append(value_kept)
            # force the column's string column label to type 'category'  
            df[label] = df[label].astype('category')
            # put the kept value first in the ordered category for dropping duplicates later
            sorted_category = list(set(df[label].to_list()))
            sorted_category.remove(value_kept)
            sorted_category.insert(0,value_kept)
            df[label] = df[label].cat.set_categories(sorted_category, ordered=True)
        elif VERBOSE:
            print(f"Label \"{label}\" already has 1 or 0 values.")
    
    if DEBUG:
        print(f"fixed_columns: {fixed_columns}")
        print(f"non_fixed_columns: {non_fixed_columns}")
    if VERBOSE:
        print(f"Values kept: {values_kept}")

    # sort to put first selected category at the top of each label 
    df.sort_values(fixed_columns, inplace=True, ascending=True) 
    if DEBUG:
        print(f"Now sorted by custom categories") 
        if VERBOSE:
            print(df)
    # dropping duplicates keeps first
    graphing_df = df.drop_duplicates(non_fixed_columns,keep="first") 
    if DEBUG:
        print("Dropped duplicates") 
        print(graphing_df)
    

    ############ making table of graphs ############

    # pivot and transpose make our graph into a more readable format
    # with the index being a "MultiIndex" in the form of a tuple of parameters
    graphed_columns = [graphed_column]
    if not secondary_graphed is None:
        graphed_columns.insert(0,secondary_graphed)
    graphing_df = graphing_df.pivot(index=graphed_columns,
                                        columns=column_selection,
                                        values=all_data_values)
    graphing_df = graphing_df.transpose()

    # TODO: another option to try: >>> index = pd.MultiIndex.from_tuples(tuples)
    # >>> values = [[12, 2], [0, 4], [10, 20],
    # ...           [1, 4], [7, 1], [16, 36]]
    # >>> df = pd.DataFrame(values, columns=['max_speed', 'shield'], index=index)
    # >>> df
    
    if DEBUG:
        print(graphing_df)

    ############ generating graphs ############
    
    index_list = list(list(str(i) for i in tuple_i) for tuple_i in graphing_df.index)
    column_list = []
    n_rows = 1
    if secondary_graphed is None:
        if DEBUG:
            print(graphing_df.columns.array)  
        column_list = list(map(metadata_types[graphed_column],graphing_df.columns))
    else:
        multi_id = graphing_df.columns.to_numpy()
        primary_graphed_list = list(set([t[1] for t in multi_id]))
        secondary_graphed_list = list(set([t[0] for t in multi_id]))
        column_list = list(map(metadata_types[graphed_column],primary_graphed_list))
        n_rows = len(secondary_graphed_list)

    if DEBUG:
        print(f"columns: {graphing_df.columns}")
        print(f"column_list: {column_list}")
    n_graphs = len(graphing_df.index)
    
    # declaring matplotlib ax and fig, and ax_list
    ax = None
    fig,ax_list = plt.subplots(1,n_graphs)
    if not secondary_graphed is None:
        fig,ax_list = plt.subplots(n_rows,n_graphs)
    if not subplots_in_one_figure:
        dir = f"{'.' if directory==None else str(directory).rstrip('/')}/{graphed_column}"
        os.mkdir(dir)
    for j in range(n_rows):
        for i in range(n_graphs):
            if not subplots_in_one_figure:
                fig,ax = plt.subplots()
            else:
                if secondary_graphed is None:
                    ax = ax_list[i]          
                else:
                    ax = ax_list[j][i]
            if VERBOSE:
                print(f"Graphing {index_list[i]}...")
            
            graphed_data_i = graphing_df.iloc[i].array
            if not secondary_graphed is None:            
                j_slice = [t[0]==secondary_graphed_list[j] for t in multi_id]
                graphed_data_i=graphing_df.iloc[0].array[j_slice]
            if DEBUG:
                print(f"graphing_df.iloc[0].array: {graphing_df.iloc[0].array}")
                print(f"graphed_data_i: {graphed_data_i}")

            ax.bar(range(len(column_list)),graphed_data_i)

            title = str(index_list[i][0]) if subplots_in_one_figure else f"{graphed_column} with {str(index_list[i][0])}\nFixed options: {' '.join(index_list[i][1:])}"
            title_size = 10 if subplots_in_one_figure else 20
            ax.set_title(title, fontsize=title_size)
            ax.set_xticks(ticks=range(len(column_list)),labels=column_list, rotation=60, ha='right', size='xx-small')
            if not subplots_in_one_figure:
                fig.savefig(f"{dir}/{graphed_column}_{str(index_list[i][0])}.pdf")

    if subplots_in_one_figure:
        if not secondary_graphed is None:            
            # courtesy of https://stackoverflow.com/questions/25812255/row-and-column-headers-in-matplotlibs-subplots
            rows = [f'{secondary_graphed} = {{}}'.format(row) for row in secondary_graphed_list]
            for ax, row in zip(ax_list[:,0], rows):
                ax.set_ylabel(row, rotation=90, size='small')
        fig.suptitle(f"Graphs of {graphed_column}{'' if secondary_graphed is None else ' ('+secondary_graphed+' as rows)'}\nFixed options: {' '.join(index_list[i][1:])}")
        fig.tight_layout()
        fig.savefig(f"{str(directory).rstrip('/')}/{graphed_column}{'' if secondary_graphed is None else '-'+secondary_graphed}_{datetime.date.today()}.pdf")

def old_import_data_debug(normalise=True,
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
    # make a DataFile out of it - to parse the "data" list in the dictionary
    jsonmetadata_df = pd.json_normalize(param_metadata_dict,record_path="data")
    jsonmetadata_df.set_index(keys='id',drop=True,verify_integrity=True,inplace=True)
    if DEBUG:
        print(jsonmetadata_df)
        print(jsonmetadata_df.loc["bench_tree/bench_size5kernel/_alloc/_01.00Mb/_sizecompiled/run.sh"])

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
            benchname = benchname.lstrip("bench_tree/").rstrip("/run.sh").replace("/","")
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
                            imported_data /= jsonmetadata_df.loc[row[0],"iters"] * jsonmetadata_df.loc[row[0],"ni"] * jsonmetadata_df.loc[row[0],"nj"]
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
        
def old_show_graph_2D_debug(fileprefix="",is_wallclocktime_graph=False) :
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

def argument_parsing(parser: argparse.ArgumentParser):
    parser.add_argument('-M','--MODE', nargs='?', default='default',
                    help='Can be default, interactive or old.')
    
    parser.add_argument('-D', '--directory',  default=f"figs_{datetime.date.today()}",
                        help='Sets .pdf directory.')
    parser.add_argument('-G', '--graphed',
                        help=f'Sets a single metadata variable to graph - from {", ".join(all_metadata_columns)}.')
    parser.add_argument('-sG', '--secondary-graphed',
                        help=f'Sets a secondary metadata variable to graph - from {", ".join(all_metadata_columns)}, all.\
                              Option \'all\' is useful for comparing more data at once in all variants.\
                                  Restrictions: cannot be the same as --graphed. Ignored if -sp is not set.')

    # Optional flags
    parser.add_argument('-csv',  default="data.csv",
                        help='Sets bench data .csv path. Warning: depends on corresponding .json or may be unreadable.')
    parser.add_argument('-json',  default="../preprocess/all_benchmark_parameters.json",
                        help='Sets bench metadata .json path.')
    parser.add_argument('-sp', '--subplots', action='store_true',
                        help='Makes subplot graphs to see all types of data at once.')
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

    # check that not args.graphed and args.secondary_graphed are well defined.
    if not args.graphed is None and not args.graphed in all_metadata_columns :
        parser.error(f"{args.graphed} invalid metadata variable.")
    if not args.secondary_graphed is None and (not args.secondary_graphed in all_metadata_columns and args.secondary_graphed!='all') :
        parser.error(f"{args.secondary_graphed} neither valid metadata variable nor 'all'.")
    if not args.secondary_graphed is None and not args.graphed is None and\
        args.secondary_graphed==args.graphed:
        parser.error("Graphed variable and secondary graphed variable cannot be the same.")

    if not args.directory is None:
        if pathlib.Path(args.directory).is_dir() :
            if args.clean_before and args.MODE!="old":
                shutil.rmtree(args.directory)
                print(f"Cleaned {args.directory} directory")
                os.mkdir(args.directory)
        else:
            os.mkdir(args.directory)

    if args.MODE=="default":
        df = import_data_pandas(args.json,args.csv,normalise=True)
        columns = all_metadata_columns
        non_unique_parameters = find_non_unique_parameters(df,columns=columns)
        if DEBUG:
            print(non_unique_parameters)
        
        # index is used to select column
        if not args.graphed is None:
            igraphed=all_metadata_columns.index(args.graphed)
        if not args.secondary_graphed in [None,'all']:
            isecondary=all_metadata_columns.index(args.secondary_graphed)


        # if graphed variable is not specified
        if args.graphed is None:
            # iterate over non unique parameters to graph all of them
            for i in range(len(non_unique_parameters)):
                if non_unique_parameters[i]:
                    if args.secondary_graphed is None:
                        make_graphs(df, graphed_column=columns[i], interactive=False, subplots_in_one_figure=args.subplots, directory=args.directory)
                    elif args.secondary_graphed!='all' and i!=isecondary :
                        make_graphs(df, graphed_column=columns[i],
                                    secondary_graphed=columns[isecondary],
                                    interactive=False, subplots_in_one_figure=args.subplots, directory=args.directory)
        else:
                if non_unique_parameters[igraphed]:
                    if args.secondary_graphed is None:
                        make_graphs(df, graphed_column=columns[igraphed], interactive=False, subplots_in_one_figure=args.subplots, directory=args.directory)
                    elif args.secondary_graphed=='all' :
                        for j in range(len(non_unique_parameters)):
                            if non_unique_parameters[j]:
                                if j!=igraphed :
                                    make_graphs(df, graphed_column=columns[igraphed],
                                                secondary_graphed=columns[j],
                                                interactive=False, subplots_in_one_figure=args.subplots, directory=args.directory)
                    else:
                        make_graphs(df, graphed_column=columns[igraphed],
                                    secondary_graphed=columns[isecondary],
                                    interactive=False, subplots_in_one_figure=args.subplots, directory=args.directory)

                else:
                    parser.error(f"{args.graphed} cannot be graphed because it is uniquely represented.")

    elif args.MODE=="interactive":
        df = import_data_pandas(args.json,args.csv,normalise=True)
        make_graphs(df, interactive=True, directory=args.directory)

    elif args.MODE=="old":
        old_import_data_debug(normalise=True)
        old_show_graph_2D_debug(fileprefix="cache_misses")
        old_show_graph_2D_debug(fileprefix="wallclocktime",is_wallclocktime_graph=True)
    else:
        print("Mode undefined.")
    print("Done.")

# courtesy of https://docs.python.org/fr/3/library/__main__.html
if __name__ == '__main__':
    sys.exit(main())