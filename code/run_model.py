#run model is here
from pyomo.core import *
from read_prepare_data import *
from model_sets import *
from model_variables import *
from model_constraints import *
from model_objective import *
from save_variables import *
from save_parameter import *


def run_en_model(input_path, result_path, parameters_path):

    data = prepare_data(input_path) #read and prepare the data for use
    en_model = ConcreteModel() #declare a model instance

    # use the data prepared above to make a model
    sets (data, en_model) # model sets in model_sets.py
    variables (data, en_model) # set up vaibales in model_variables.py
    parameters (data, en_model) # setup parameters in model_parameters.py
    constraints (data, en_model) # setup constraints in model_constraints.py
    objectives (data, en_model) # setup model objectives

    # solve model and save results
    save_params(en_model, parameters_path)
    solve_model(en_model)
    save_result(en_model, result_path)