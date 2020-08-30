#-----------------------------------------------------------------------------#
# Custom User Constraints/Model Specifications
#-----------------------------------------------------------------------------#
    
from pyomo.core import *

#----------------------------------------------------------------------
# Roof technologies - user indicates criteria for roof top techs
#----------------------------------------------------------------------

def Roof_tech(data):
    """
    User-defined selection criteria for solar roof-top technologies (e.g. PV, ST)
    """  
    Roof_techset=[]
    for n,val in enumerate(data.solkWm2): # all techs with a given "Solar specific power" are considered to be roof-top techs
        if val>0:
            Roof_techset.append(n+1)
            
    return Roof_techset

def gen_custom(data, model):
    
    print("Generating custom constraints/model specifications...")
    
    #----------------------------------------------------------------------
    # Sets
    #----------------------------------------------------------------------  
    model.roof_tech = Set(initialize=Roof_tech(data), within=model.Tech) # roof-top technologies
    
    #----------------------------------------------------------------------
    # Parameters
    #----------------------------------------------------------------------
    model.maxSolarArea = Param(initialize=100000) # max roof-top area in each hub (m2); hard-coded custom constraint

    #----------------------------------------------------------------------
    # Constraints
    #----------------------------------------------------------------------
    
    # total roof area of all roof techs <= total roof area (per hub)
    def roofArea_rule(model,h):
        return (sum(model.CapTech[h,rt] / model.solkWm2[rt] for rt in model.roof_tech) <= model.maxSolarArea)
    model.roofArea = Constraint(model.hubs,rule=roofArea_rule)
