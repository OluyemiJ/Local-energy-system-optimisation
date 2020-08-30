#-----------------------------------------------------------------------------#
# Run Model - Main
#-----------------------------------------------------------------------------#

from run_mod import *

# input data file location
input_path=r'/Users/oluyemijegede/DSProjects/local_energy_system_optimisation/code/experiment1.xlsx'

# results saved to text file location
result_file = '/Users/oluyemijegede/DSProjects/local_energy_system_optimisation/code/results/results.txt'

# model parameters saved to text file location
param_file = '/Users/oluyemijegede/DSProjects/local_energy_system_optimisation/code/parameters/params.txt'

# execute model
run_model(input_path, param_file, result_file) # defined in run_mod.py
