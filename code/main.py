# run model here

from run_model import *
from pyomo.core import *
import os


cwd = os.getcwd()

# input excel file to set system details
input_path = os.path.join(cwd, 'code', 'system_config.xlsx')

# results files to be saved in which folder?
results_path = os.path.join(cwd, 'results', 'results.txt')

# folder where parameters are saved
parameters_path = os.path.join(cwd, 'parameter', 'parameters.txt')

# run model
run_en_model(input_path, results_path, parameters_path)

# visualise results
visualise(result_path)