#-----------------------------------------------------------------------------#
# Run Solver
#-----------------------------------------------------------------------------#

from pyomo.core import *
from pyomo.opt import SolverFactory, SolverManagerFactory

def model_solve(model):

    opt = SolverFactory("glpk") #select solver
    #opt.options["mipgap"]=0.05 #different options to use for solver (parameter name can be different depending on solver)
    #opt.options["FeasibilityTol"]=1e-05
    #opt.options['outlev']  = 1  # tell gurobi to be verbose with output
    #opt.options['iisfind'] = 1  # tell gurobi to find an iis table for the infeasible model
    solver_manager = SolverManagerFactory("serial")
    #results = solver_manager.solve(instance, opt=opt, tee=True,timelimit=None, mipgap=0.1)
    
    print("Preprocessing...")
    model.preprocess()
    
    print("Running solver...")
    results = solver_manager.solve(model, opt=opt, tee=True,timelimit=None) # gurobi syntax