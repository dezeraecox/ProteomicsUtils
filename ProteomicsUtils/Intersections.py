import pandas as pd
import pyupset as pyu
import itertools
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from ProteomicsUtils import FileHandling
from ProteomicsUtils.LoggerConfig import logger_config


logger = logger_config(__name__)
logger.info("Import Successful")


#using permute itertools
def perm_generator(elements):
    combination_dict = {}
    for n in range(1,len(elements)+1):
        combination_dict[n]=itertools.combinations(elements, n)
    return combination_dict

def intersection_func(comb_dict, data_dict):
    intersect_dict = {}
    for key, value in comb_dict.items():
        for combination in value:
            comb_treats = []
            #iter_name = ' v '.join(str(element) for element in combination)
            for treatment in combination:
                comb_treats.append(set(data_dict[treatment].dropna().tolist()))
            intersect_dict[combination] = set.intersection(*comb_treats)
    return intersect_dict


def dataframe_totals_annotator(dataframe):
    #create row with column totals without NaNs
    for column in list(dataframe.columns.values):
        dataframe.loc['Total', column] = len(dataframe[column].dropna())

    return dataframe

def dataframe_treatment_in_column_annotator(dataframe, elements):

    #creat new rows for each element of intersection
    for element in elements:
        dataframe.loc[element] = ''

    #populate the rows with 1 if that element was included in the intersection
    for column_name in list(dataframe.columns.values):
        dataframe.loc['Degree', column_name] = len(column_name)
        for element in column_name:
            dataframe.loc[element, column_name] = 1

    return dataframe



def do_funcs(path_list, output_path):
    datadict = {}
    treatments_list = []

    #gather data from all files
    for path in path_list:
        dataframe = FileHandling.file_reader(path)
        treatIDs= list(dataframe.columns.values)
        #gather each column, and place in dictionary according to treatmentID
        for treatment in treatIDs:
            datadict[treatment] = dataframe[treatment]
        treatments_list.append(treatIDs)

    flattened_treatment_list = [y for x in treatments_list for y in x]
    logger.info(flattened_treatment_list)

    #generate all permutations of the treatmentIDs
    dictionary = perm_generator(flattened_treatment_list)
    #Complete the intersection on each combination of columns
    inter_dict = intersection_func(dictionary, datadict)

    #turn intersection dictionary into dataframe
    intersections = pd.DataFrame.from_dict(inter_dict, orient='index').transpose()

    #to annotate totals and column degrees
    intersections = dataframe_treatment_in_column_annotator(dataframe_totals_annotator(intersections), flattened_treatment_list)

    #save to excel
    FileHandling.df_to_excel(output_path+'_Intersection.xlsx', ['Intersections'], [intersections.reset_index()])

    return intersections

    #think about extending this to compare two different dfs, rather that from one dataframe

def heat_mapper(dataframe, colour):
    sns.set()
    max_value = np.max(dataframe.max())
    fig = sns.heatmap(dataframe, cmap = colour, vmin=0, vmax=max_value)
    return fig


if __name__ == '__main__':
    path_list = ['C:/Users/dezer_000/Documents/App_Dev_Projects/MS_set_intersection/test_data.xlsx', 'C:/Users/dezer_000/Documents/App_Dev_Projects/MS_set_intersection/test_data_duplicate.xlsx']
    output_path = 'C:/Users/dezer_000/Documents/App_Dev_Projects/MS_set_intersection/test_data_two'

    do_funcs(path_list, output_path)
