import pandas as pd
import pyupset as pyu
import itertools
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from ProteomicsUtils import FileHandling
from ProteomicsUtils.LoggerConfig import logger_config

pd.set_option('display.max_rows', 999)

logger = logger_config(__name__)
logger.info("Import Successful")


def pairwise_array_maker(element_list):
    pairwise = pd.DataFrame()
    for element in element_list:
        pairwise.loc[element, element] = None
    return pairwise


def proportion_calculator(dataframe, array_maker):
    #create pairwise array, which will contain total unique proteins
    pairwise_df = array_maker(dataframe.columns.values)
    #copy pairwise to intersection_df, which will contain the intersections
    intersect_df = pairwise_df.copy()
    #to append the total unique proteins for each pairwaise comparison by iterating through each column, index pairwise
    for element1 in dataframe.columns.values:
        for element2 in dataframe.columns.values:
            element1_data = dataframe[element1].dropna()
            element2_data = dataframe[element2].dropna()
            total_unique = len(set(element1_data.append(element2_data)))
            #ssave total unique to pairwise df
            pairwise_df.loc[element1, element2] = total_unique
            #calculate intersections
            intersect_df.loc[element1, element2] = len(set(element1_data).intersection(set(element2_data)))
    #calculate proportion by intersection divided by total unique
    proportion_df = (intersect_df/pairwise_df)*100
    proportion_df = proportion_df.round(decimals=2)

    return pairwise_df, intersect_df, proportion_df


def heat_mapper(dataframe, colour, max_value=None):
    sns.set()
    #find max value that is not 100 to avoid colouring the centre cross over
    for x in range (0, dataframe.shape[0]):
        dataframe.iloc[x,x] = None
    if not max_value:
        max_value = np.max(list(dataframe.max()))
    fig, ax = plt.subplots()
    sns.heatmap(dataframe, cmap = colour, vmin=0, vmax=max_value, ax=ax)
    plt.tight_layout()
    plt.autoscale()
    return fig


def do_funcs_onefile(input_path, output_path, colour='Blues', max=None, sheetname=None):

    #gather dataframe
    dataframe = pd.read_excel(input_path, sheet_name=sheetname)

    #calculate unique, intersection and proportion_overlap for each pair
    total_unique, intersection, proportion_overlap = proportion_calculator(dataframe, pairwise_array_maker)

    #generate heatmap
    fig = heat_mapper(proportion_overlap, colour=colour, max_value=max)
    #save heatmap to pdf, svg
    FileHandling.fig_to_pdf(figs=[fig], output_path=output_path)
    FileHandling.fig_to_svg(fig_names=['Pairwise Heatmap'], fig_list=[fig], output_path=output_path)

    #plt.show(fig)

    #save all dataframes to excel
    sheetnames = ['Total Unique Data', 'Pairwise Intersection', 'Pairwise Proportions']
    data_frames = [total_unique, intersection, proportion_overlap]
    FileHandling.df_to_excel(output_path, sheetnames, data_frames)

    return proportion_overlap



#think about extending this to compare two different dfs, rather that from one dataframe


if __name__ == '__main__':
    path = 'C:/Users/dezer_000/Desktop/Current Analysis/180503_Stress_Compilation/All_Protein_Compilation.xlsx'
    output_path = 'C:/Users/dezer_000/Desktop/Current Analysis/180503_Stress_Compilation/All_Protein_Compilation_Pairwise.xlsx'
    do_funcs_onefile(path, output_path)
