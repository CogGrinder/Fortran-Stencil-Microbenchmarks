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

import warnings

global VERBOSE
VERBOSE = False
global DEBUG
DEBUG = False

# used for selecting benchmarks classifying data
all_metadata_columns=["kernel_mode",
                      "hardware",
                      "allocation",
                      "module",
                      "size",
                      "compile_size"]
metadata_types =\
    {
    "kernel_mode" : str,
    "hardware" : str,
    "allocation" : str,
    "module" : bool,
    "size" : float,
    "compile_size" : bool
    }
all_data_values=['PAPI_L1_TCM',  'PAPI_L2_TCM',  'PAPI_L3_TCM',  'WALLCLOCKTIME']
# default benchmark, also known as baseline benchmark or control experiment
baseline_for_comparison =\
    {
    "kernel_mode" : "DEFAULT_KERNEL",
    "hardware" : "CPU",
    "allocation" : "ALLOCATABLE",
    "module" : True,
    "size" : None,
    "compile_size" : True
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
    # WARNING: may cause errors. Chooses first in case of duplicate benchmarks.
    # jsonmetadata_df.drop_duplicates('id',inplace=True)
    # removing default benchmark
    default_key = [i for i in list(jsonmetadata_df.index) if 'bench_default/' in jsonmetadata_df.iloc[i]['id'] ]
    if DEBUG:
        print(f"default keys: {default_key}")
    # default_key=default_key[0]
    jsonmetadata_df.drop(index=default_key,inplace=True)
    
    jsonmetadata_df.set_index(keys='id',drop=True,verify_integrity=True,inplace=True)
    # sorting
    jsonmetadata_df.sort_values(by=list(jsonmetadata_df.columns), inplace=True, ascending=True)
    if VERBOSE or DEBUG:
        print(jsonmetadata_df)
        print()

    if DEBUG:
        #multiindex test
        multiindex = pd.MultiIndex.from_arrays(arrays=[
        jsonmetadata_df[metaparam].to_list() for metaparam in all_metadata_columns
        ])
        print(multiindex)
        print()

    ### join ###
    print("Joining both DataFrames...")
    joined_df = datacsvdf.join(jsonmetadata_df)
    index_list = list(joined_df.index)
    # removing default benchmark
    default_key = [i for i in index_list if 'bench_default/' in i ]
    if DEBUG:
        print(f"default keys: {default_key}")
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
    if VERBOSE:
        print([set(df[label].to_numpy()) for label in columns if len(set(df[label].to_numpy()))>1])
    return np.array([len(set(df[label].to_numpy()))>1 for label in columns])

def prompt_user_to_choose_from_array(choice_list:list,message="",default=None):
    # sets default if input is empty
    # see https://stackoverflow.com/questions/22402548/how-to-define-default-value-if-empty-user-input-in-python
    input_choice = input(message).strip() or default
    if input_choice in choice_list:
        final_choice = input_choice
    else: # if not in 
        try:
            choice_index = int(input_choice)
        except:
            print(f"{input_choice} invalid entry.")
            return prompt_user_to_choose_from_array(choice_list,message='Try again or press <Enter>:',default=default)
        try:
            final_choice = choice_list[choice_index]
        except:
            print("Index out of bounds.")
            return prompt_user_to_choose_from_array(choice_list,message='Try again or press <Enter>:',default=default)
    
    if (final_choice==None):
        raise TypeError("Undefined choice.")
    else:
        return final_choice
    

def make_graphs(df: pd.DataFrame,
                interactive=False,
                directory=None,
                subplots_in_one_figure=False,
                all_data_values=all_data_values,
                all_metadata_columns=all_metadata_columns,
                variable_to_graph="size",
                secondary_graphed=None,
                baseline_for_comparison=baseline_for_comparison):
    """Function that makes graphs by using data and metadata from DataFrame and setting fixed units
    Args:
        normalise (bool): Normalize all benchmark data
            relative to size and iterations
    """

    ############ selecting data ############

    ### selecting graphing variable ###
    # default is set by function call
    
    if interactive:
        valid_variables_to_graph=np.array(all_metadata_columns)[find_non_unique_parameters(df)]
        # input column to graph
        variable_to_graph = prompt_user_to_choose_from_array(
            message=f"\n{valid_variables_to_graph} are valid variables to graph as non-uniquely valued.\
                \nChoose variable to graph using index or name:",
            choice_list=valid_variables_to_graph,
            default=variable_to_graph)
        print(f"\nChose {variable_to_graph}.")
    

    print(f"Computing {variable_to_graph}{'' if secondary_graphed is None else ' ('+secondary_graphed+' as rows)'} graphing...")
    
    column_selection = all_metadata_columns.copy()
    
    if VERBOSE:
        print(f"all columns:{column_selection}")
    column_selection.remove(variable_to_graph)
    # if their is a secondary graphed parameter, add here
    if secondary_graphed is not None:
        column_selection.remove(secondary_graphed)
    if VERBOSE:
        print(f"column selection:{column_selection}")

    # fixed_columns = [None for i in range(len(column_selection))]
    fixed_columns = []
    non_fixed_columns = all_metadata_columns.copy()
    values_kept = []

    if DEBUG:
        # removes unnecessary data for debugging
        df = df.copy()
        df.drop([col for col in list(df.columns) if not col in all_metadata_columns and not col in all_data_values],axis=1,inplace=True)
        print(df)

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
                value_kept = prompt_user_to_choose_from_array(
                    choice_list=set_of_label,
                    message=f"Label \"{label}\" has duplicates. Choices are {set_of_label}.\
                        \nChoose index or name or press <Enter> for default:",
                    default=value_kept
                )
            if DEBUG:
                print(f"{label} kept value: {value_kept}")
            fixed_columns.append(label)
            non_fixed_columns.remove(label)
            values_kept.append(value_kept)
            # force the column's string column label to type 'category'  
            df[label] = df[label].astype('category')
            # put the kept value first in the ordered category for dropping duplicates later
            sorted_category = list(set(df[label].to_list()))
            sorted_category.remove(value_kept)
            sorted_category.insert(0,value_kept)
            if DEBUG:
                print(sorted_category)
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
        print(df)
    # dropping duplicates keeps first
    graphing_df = df.drop_duplicates(non_fixed_columns,keep="first") 
    if DEBUG:
        print("Dropped duplicates") 
        print(graphing_df)

    warned=False
    # check for fixed columns with leftover "ugly duckling" data
    for i, label in enumerate(fixed_columns):
        set_of_label = list(set(graphing_df[label].to_numpy()))
        if len(set_of_label)>1:
            # https://docs.python.org/3/tutorial/errors.html
            # raise ValueError(f"Metavariable '{label}' failed filtering: values {set_of_label}")
            warnings.warn(f"\nMetavariable '{label}' failed filtering duplicates. Values: {set_of_label}.\
                          \n\nLikely explanation is a benchmark has not executed properly or was reexectuted halfway.",
                          category=RuntimeWarning)
            warned=True
            is_ugly_duckling = graphing_df[label]!=values_kept[i]
            set_of_label.remove(values_kept[i])
            print(f"Attempting to remove unfiltered data : {set_of_label}.\
                  \nMay remove most of data in case of a systematic error.")
            graphing_df = graphing_df.drop(index=graphing_df.index.array[is_ugly_duckling],
                             axis=1)
    if warned and (VERBOSE or DEBUG):
        print("Data after cleaning up filtering:")
        print(graphing_df)

    # other solution: use pd.DataFrame.to_json and then pd.json_normalize
    

    ############ making table of graphs ############

    # pivot and transpose make our graph into a more readable format
    # with the index being a "MultiIndex" in the form of a tuple of parameters
    graphed_columns = [variable_to_graph]
    if not secondary_graphed is None:
        graphed_columns.insert(0,secondary_graphed)
    graphing_df = graphing_df.pivot(index=graphed_columns,
                                        columns=column_selection,
                                        values=all_data_values)
    if DEBUG:
        print(graphing_df)
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
        column_list = list(map(metadata_types[variable_to_graph],graphing_df.columns))
    else:
        multi_id = graphing_df.columns.to_numpy()
        primary_graphed_list = list(set([t[1] for t in multi_id]))
        secondary_graphed_list = list(set([t[0] for t in multi_id]))
        column_list = list(map(metadata_types[variable_to_graph],primary_graphed_list))
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
        dir = f"{'.' if directory==None else str(directory).rstrip('/')}/{variable_to_graph}"
        if not pathlib.Path(dir).is_dir() :
            os.mkdir(dir)
        # else:
        #     warnings.warn(f"{dir} exists. May be overwriting files.",category=RuntimeWarning)
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
                graphed_data_i=graphing_df.iloc[i].array[j_slice]
            if DEBUG:
                print(f"graphing_df.iloc[0].array: {graphing_df.iloc[i].array}")
                print(f"graphed_data_i: {graphed_data_i}")

            ax.bar(range(len(graphed_data_i)),graphed_data_i)

            title = str(index_list[i][0]) if subplots_in_one_figure else f"Graph of {variable_to_graph} using {str(index_list[i][0])} data\nFixed options: {' '.join(index_list[i][1:])}"
            title_size = 10 if subplots_in_one_figure else 12
            ax.set_title(title, fontsize=title_size)
            ax.set_xticks(ticks=range(len(column_list)),labels=column_list, rotation=60, ha='right', size='xx-small')
            if not subplots_in_one_figure:
                filename=f"{dir}/{variable_to_graph}_{str(index_list[i][0])}.pdf"
                fig.savefig(filename)
                plt.close()
                if interactive:
                    print(filename)

    if subplots_in_one_figure:
        if not secondary_graphed is None:            
            # courtesy of https://stackoverflow.com/questions/25812255/row-and-column-headers-in-matplotlibs-subplots
            rows = [f'{secondary_graphed} = {{}}'.format(row) for row in secondary_graphed_list]
            for ax, row in zip(ax_list[:,0], rows):
                ax.set_ylabel(row, rotation=90, size='small')
        fig.suptitle(f"Graphs of {variable_to_graph}{'' if secondary_graphed is None else ' ('+secondary_graphed+' as rows)'}\nFixed options: {' '.join(index_list[i][1:])}")
        fig.tight_layout()
        filename = f"{str(directory).rstrip('/')}/{variable_to_graph}{'' if secondary_graphed is None else '-'+secondary_graphed}_{datetime.date.today()}.pdf"
        fig.savefig(filename)
        plt.close()
        if interactive:
            print(filename)

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
    parser.add_argument('-sp', '--subplots', action='store_true',
                        help=f'Highly recommended. Makes subplot graphs instead of individual graphs. Enables showing {", ".join(all_data_values)} data on the same graph.')
    parser.add_argument('-M','--MODE', metavar='name', nargs='?', default='default',
                    help='Can be default, interactive or old.\nInteractive lets you choose your selected benchmark variant to test against.')
    
    parser.add_argument('-D', '--directory', metavar='path',  default=f"figs_{datetime.date.today()}",
                        help='Sets .pdf directory.')
    parser.add_argument('-G', '--graphed', metavar='name',
                        help=f'Sets a single metadata variable to graph - from {", ".join(all_metadata_columns)}.')
    
    # thank you to https://stackoverflow.com/questions/27411268/arguments-that-are-dependent-on-other-arguments-with-argparse
    parser_subplots_specific = parser.add_argument_group(title='subplots specific options')
    parser_subplots_specific.add_argument('-sG', '--secondary-graphed', metavar='name',
                        help=f'Ignored if -sp is not set. Sets a secondary metadata variable to graph - from {", ".join(all_metadata_columns)}, all.\
                              Option \'all\' is useful for comparing more data at once in all variants.\
                                  Restrictions: cannot be the same as --graphed.')

    # Optional flags
    parser.add_argument('-csv', metavar='path',  default="data.csv",
                        help='Sets bench data .csv path. Warning: depends on corresponding metadata .json or data may be unreadable.')
    parser.add_argument('-json', metavar='path',  default="../preprocess/all_benchmark_parameters.json",
                        help='Sets bench metadata .json path.')
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
            print(f"non_unique_parameters:{np.array(all_metadata_columns)[non_unique_parameters]}")
        
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
                        make_graphs(df, variable_to_graph=columns[i], interactive=False, subplots_in_one_figure=args.subplots, directory=args.directory)
                    elif args.secondary_graphed!='all' and i!=isecondary :
                        make_graphs(df, variable_to_graph=columns[i],
                                    secondary_graphed=columns[isecondary],
                                    interactive=False, subplots_in_one_figure=args.subplots, directory=args.directory)
                    else:
                        pass # TODO: if args.secondary_graphed=='all'
        else:
                if non_unique_parameters[igraphed]:
                    if args.secondary_graphed is None or (args.secondary_graphed=='all' and not args.subplots) :
                        make_graphs(df, variable_to_graph=columns[igraphed], interactive=False, subplots_in_one_figure=args.subplots, directory=args.directory)
                    elif args.secondary_graphed=='all' :
                        for j in range(len(non_unique_parameters)):
                            if non_unique_parameters[j] and columns[j]!='size': # ignore size because it makes unreadable subplots
                                if j!=igraphed :
                                    make_graphs(df, variable_to_graph=columns[igraphed],
                                                secondary_graphed=columns[j],
                                                interactive=False, subplots_in_one_figure=args.subplots, directory=args.directory)
                    else:
                        make_graphs(df, variable_to_graph=columns[igraphed],
                                    secondary_graphed=columns[isecondary],
                                    interactive=False, subplots_in_one_figure=args.subplots, directory=args.directory)

                else:
                    warnings.warn(f"{args.graphed} cannot be graphed because it is uniquely represented.\nCheck if data contains failed benchmarks.",category=RuntimeWarning)
                    return -1

    elif args.MODE=="interactive":
        df = import_data_pandas(args.json,args.csv,normalise=True)
        valid_variables_to_graph=np.array(all_metadata_columns)[find_non_unique_parameters(df)]
        default_variable = valid_variables_to_graph[0]
        make_graphs(df, interactive=True, directory=args.directory, variable_to_graph=default_variable)

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