#-----------------------------------------------------------------------------#
# General System Constraints
#-----------------------------------------------------------------------------#

from pyomo.core import *
import numpy as np

def const_sys(data, model):
    
    print("- System constraints")
    
    #-----------------------------------------------------------------------------#
    # Energy balance
    #-----------------------------------------------------------------------------#
    
#    def energyBalance_rule(model, h,  m, e): #energy balance when multiple hubs are present
#        return (model.loads[h,m,e] + model.Eexp[h,m,e] == (model.Eimp[h, m, e] + sum(model.OutStg[h,m,s,e] - model.InStg[h,m,s,e] for s in model.Stg) +
#                                                            sum(model.Eout[h,m,t,e] - model.Ein[h,m,t,e] for t in model.Tech) 
#                                                                    + sum(model.NetE[l,j,h,e,m]*(1-model.netLoss[l]*model.netLength[l])- model.NetE[l,h,j,e,m] for l in model.LinkID for j in model.hubs ))) 
#    
#    model.energyBalance = Constraint(model.hubs, model.Time, model.EC, rule=energyBalance_rule)
    
    def energyBalance_rule(model, h,  m, e): #energy balance when multiple hubs are present
        return (model.loads[h,m,e] + model.Eexp[h,m,e] == (model.Eimp[h, m, e] - sum(model.FlowStg[h,m,s,e] for s in model.Stg) +
                                                            sum(model.Eout[h,m,t,e] - model.Ein[h,m,t,e] for t in model.Tech) 
                                                                    + sum(model.NetE[l,j,h,e,m]*(1-model.netLoss[l]*model.netLength[l])- model.NetE[l,h,j,e,m] for l in model.LinkID for j in model.hubs ))) 
    
    model.energyBalance = Constraint(model.hubs, model.Time, model.EC, rule=energyBalance_rule)
    
    #-----------------------------------------------------------------------------#
    # Import/export constraints
    #-----------------------------------------------------------------------------#
    
    # maximum import supply
    def maxEimp_rule(model, e):
        return(sum(model.Eimp[h,m,e] for h in model.hubs for m in model.Time) <= model.maxImp[e])
    model.maxEimpConst = Constraint(model.EImpSet, rule=maxEimp_rule)
    
    # set non-export and non-import ECs to zero
    def Eexp_rule(model, h, m, e):
        return (model.Eexp[h,m,e] == 0)
    model.ExpConst = Constraint(model.hubs, model.Time, model.ENExpSet, rule=Eexp_rule) # set non-export ECs to zero
    
    def Eimp_rule(model, h, m, e):
        return (model.Eimp[h,m,e] == 0)
    model.ImpConst = Constraint(model.hubs, model.Time, model.ENImpSet, rule=Eimp_rule) # set non-import ECs to zero
