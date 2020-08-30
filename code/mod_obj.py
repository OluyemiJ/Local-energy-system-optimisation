#-----------------------------------------------------------------------------#
# Objective Function
#-----------------------------------------------------------------------------#

from pyomo.core import *

def gen_obj(data, model):
    
    print("Defining objective...")
   
    def objcost_rule(model):
        return (model.TotalCost)
    
    def objcarbon_rule(model):
        return (model.TotalCarbon2)
    
    # select objective function: minimize cost or carbon
    if data.minobj == "Cost":
        model.Total_Cost = Objective(rule=objcost_rule, sense=minimize) # cost minimization objective
    elif data.minobj == "Carbon":
        model.Total_Carbon = Objective(rule=objcarbon_rule, sense=minimize) # carbon minimization objective