import os, sys, re
import glob
import matplotlib.pyplot as plt
#Personal Modules
from ProteomicsUtils import StatUtils, CalcUtils, FileHandling, DataWrangling, PlotUtils
from ProteomicsUtils.LoggerConfig import logger_config


logger = logger_config(__name__)
logger.info("Import Successful")

def do_funcs():
    """
    Master function to apply a list of functions to the input file

    Parameters:
    input_path: string
        input path for the file to be processed
    output_path: string
        output path for which any output generated by functions will be saved
    sample_name: string
        sample name associated with the file to be processed

    Returns:
    figures : dictionary with each figure produced
    """
    pass

def main(input_path, output_path, sample_name):
    logger.info('Input path: {}'.format(input_path))
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    if os.path.isdir(input_path):
        figures = multifile_hist(input_path, output_path, sample_name)
    else:
        figures = PlotUtils.pep_abund_hist(input_path)
        FileHandling.fig_to_pdf(figures, output_path, fig_type=samplename+'PepAbundHist')
        logger.info(f"Figures saved to {output_path}")

    return figures


def multifile_hist(input_folder, output_path, sample_name):

    logger.info('Input Folder detected: {}'.format(input_folder))

    #find all files that contain Compiled in name
    compiled_files = glob.glob(input_folder+'/*Compiled.xlsx')
    #if there are no Compiled files, generate them
    if not compiled_files:
        FileHandling.PD_compiler(input_folder)
        #redefine compiled_files to include newly generated
        compiled_files = glob.glob(input_folder+'/*Compiled.xlsx')
    #iterate through all compiled_files, creating and saving figures
    figs = []
    figures = {}
    for file in compiled_files:
        logger.info(file)
        fig_dict = PlotUtils.pep_abund_hist(file)
        figs.append(fig_dict)
    #save figs to pdf
    for fig_dict in figs:
        figures.update(fig_dict)
    FileHandling.fig_to_pdf(figures, output_path, fig_type=sample_name+'PepAbundHist')
    logger.info(f"Figures saved to {output_path}")
    return figures


if __name__ == "__main__":
    #default parameters if no command line arguements given
    input_path = 'C:/Users/dezer_000/Desktop/Trial_data/'
    output_path = 'C:/Users/dezer_000/Desktop/Trial_data/Results'
    sample_name = 'Trial_data'
    main(input_path, output_path, sample_name)

##Figure out how to parse commandline arguements


##Need to figure out how to save title of the figure with pdfpages
#https://stackoverflow.com/questions/33414819/matplotlib-doesnt-save-suptitle
