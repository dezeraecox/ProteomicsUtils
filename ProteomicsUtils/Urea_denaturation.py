"""
Generates plots of the TPE reactivity (according to Log2 Cys/NonCys) for all peptides corresponding to a given protein across samples e.g. denaturation curve or time intervals.
"""

import os, sys
from ProteomicsUtils.LoggerConfig import logger_config
from ProteomicsUtils import StatUtils, CalcUtils, FileHandling, DataWrangling, PlotUtils
import matplotlib.pyplot as plt

logger = logger_config(__name__)
logger.info("Import Successful")

def main(input_path, output_path, sample_name):
    """
    Master function to apply a list of functions to the input file, generating urea denaturation curve for each protein

    Parameters:
    input_path: string
        input path for the file to be processed
    output_path: string
        output path for which any output generated by functions will be saved
    sample_name: string
        sample name associated with the file to be processed.

    Returns:
    summary_table: DataFrame
        dataframe containing the summarised output of the functions
        applied in order
    """

    #av_summary = do_funcs(input_path, output_path, sample_name)
    logger.info('Input Path: {}'.format(input_path))

    logger.info(f'Preparing to process {sample_name}....')
    total_data = FileHandling.file_reader(input_path)
    quant_data, col_list = DataWrangling.quantified_data(total_data)
    two_unique_cys, cys_pep, non_cys_pep = DataWrangling.Unique_Cys_sorter(quant_data)
    #set index of summary dataframes to the protein accession
    cys_pep = cys_pep.set_index(["Master Protein Accessions"], drop=False)
    non_cys_pep = non_cys_pep.set_index(["Master Protein Accessions"], drop=False)

    non_cys_Av = CalcUtils.non_cys_AR(cys_pep, non_cys_pep)

    summary_table = CalcUtils.cys_div_noncys(cys_pep, non_cys_Av, col_list)

    #Saving all dataframes so far to excel results document
    data_frames = [total_data, quant_data, two_unique_cys, cys_pep, non_cys_pep, summary_table]
    sheetnames = ['Total Data', 'Quant Data', 'TwoUniqueCYS', 'CysPep', 'NonCysPep', 'Summary Table']
    FileHandling.df_to_excel(output_path, sheetnames, data_frames)

    #collect only columns of interest
    summary_table.reset_index(drop=True, inplace=True)
    ratio_col = [col for col in summary_table.columns if '_Cys/NonCys' in col]
    select_col = ['Master Protein Accessions', 'Annotated Sequence'] + ratio_col
    summary_data = summary_table[select_col]
    logger.debug(summary_data)
    #rename columns to simple names
    summary_data = summary_data.rename(columns = {'Master Protein Accessions':'ProteinID',   'Annotated Sequence':'Sequence'})
    #for peptides seen more than once in a sample, take average ratio to give only unique ratios for each peptide
    av_summary = CalcUtils.single_element_av(summary_data, 'Sequence')


    ##Filtering for proteins which have too many missing values, and generating plots.
    logger.info('Filtering for missing values...')
    #removing rows with >thresh Nans
    filtered_consensus = DataWrangling.filter_NaNs(av_summary, filter_type='total', threshold=0)
    #preparing variables and plotting scatter for each protein
    logger.info('Creating scatter plots...')
    urea_conc = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6]
    fig_dict = PlotUtils.multirow_scatter(filtered_consensus,
                                key='ProteinID',
                                col_head='Sequence',
                                x_vals=urea_conc,
                                x_label='Urea Conc',
                                y_label='Cys_NonCys')

    #to save all figures to pdf
    FileHandling.fig_to_pdf(fig_dict, output_path+'Thresholded_')
    logger.info('Save figs to pdf complete')
    #to show all figures as output,
    for protein, figure in fig_dict.items():
        plt.show(figure)

    Threshold_0 = filtered_consensus
    dfs = [Threshold_0]
    sheetnames = ['Total_0']
    FileHandling.df_to_excel(output_path=output_path+'Thresholded_', sheetnames = sheetnames, data_frames=dfs)

    return summary_data



if __name__ == "__main__":
    #setting defaults
    input_path = 'C:/Users/dezer_000/Desktop/Current Analysis/180501_Urea_Exp8_Analysis/180523_Test_new_module/170529_Dezerae_MultiConsensus_Peptides_2UP.xlsx'
    output_path = 'C:/Users/dezer_000/Desktop/Current Analysis/180501_Urea_Exp8_Analysis/180523_Test_new_module/'
    sample_name = 'Urea Denaturation (Exp 8)'
    main(input_path, output_path, sample_name)
