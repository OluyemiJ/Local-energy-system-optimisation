#-----------------------------------------------------------------------------#
# Specific Technology Constraints 
#-----------------------------------------------------------------------------#
    
from pyomo.core import *

def const_techSpec(data, model):
    
    print("- Specific technology constraints")
    
    #-----------------------------------------------------------------------------#
    # Part-load tech constraints 
    #-----------------------------------------------------------------------------#

    ## lower bound for part load techs
    
    # - for technologies without fixed output shares:
    def partLoadFreeL_rule(model, h, m, plt):
        return (model.partLoad[plt] * model.CapTech[h, plt] <= sum(model.Eout[h,m,plt,e] for e in model.EC) + model.bigM * (1 - model.Ypl_op[h, m, plt]))
    
    model.partLoadFreeL = Constraint(model.hubs, model.Time, model.PartLFree, rule=partLoadFreeL_rule)
    
    # - for technologies with fixed output shares:
    model.partLoadFixL= ConstraintList()
    for plt in set(model.PartLFix):
        for h in set(model.hubs):
            for m in set(model.Time):
                model.partLoadFixL.add(model.partLoad[plt] * model.CapTech[h, plt] <= model.Eout[h,m,plt,data.outEC[plt][0]] + model.bigM * (1 - model.Ypl_op[h, m, plt])) # constraint applies to first output EC only (remaining output ECs determined according to given fixed shares)
    
    ## upper bound for part load techs
    
    def partLoadU_rule(model, h, m, plt):    
        return (sum(model.Eout[h,m,plt,e] for e in model.EC) <= model.bigM * model.Ypl_op[h,m,plt])
    
    model.partLoadU = Constraint(model.hubs, model.Time, model.PartLTech, rule=partLoadU_rule)
    
    #-----------------------------------------------------------------------------#
    # Solar constraints 
    #-----------------------------------------------------------------------------#
    
    # solar energy input to solar tech
    def solarInput_rule(model, h, m, st, se):
        return (model.Ein[h,m,st,se] == model.solarEm[m] * model.CapTech[h,st] / model.solkWm2[st])
    
    model.solarInput = Constraint(model.hubs, model.Time, model.SolarTechs, model.SolEC, rule=solarInput_rule) 
