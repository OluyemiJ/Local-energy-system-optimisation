#-----------------------------------------------------------------------------#
# Run Model
#-----------------------------------------------------------------------------#

from input_data import *
from mod_sets import *
from mod_vars import *
from mod_params import *
from mod_const import *
from mod_custom import *
from mod_obj import *
from run_solve import *
from save_var import *
from save_param import *

def run_model(input_path, param_file, result_file):

    inp_data=InputData(input_path) # read-in input data; class defined in input_data.py
    mod = ConcreteModel() # create model instance
    
    ## define model
    gen_set(inp_data, mod) # model sets; defined in mod_sets.py
    gen_var(inp_data, mod) # model variables; defined in mod_vars.py
    gen_param(inp_data, mod) # model parameters; defined in mod_params.py
    gen_cnst(inp_data, mod) # model constraints; defined in mod_const.py
    gen_custom(inp_data, mod) # user-defined model specifications; defined in mod_custom.py
    gen_obj(inp_data, mod) # model objective; defined in mod_obj.py
    
    ## save model parameters to file
    model_saveParam(mod, param_file) # save modeling results; defined in save_var.py
    
    ## run model
    model_solve(mod) # solve model; defined in run_solve.py
    model_saveVar(mod, result_file) # save modeling results; defined in save_var.py
    
    