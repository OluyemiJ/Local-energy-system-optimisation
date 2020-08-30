#-----------------------------------------------------------------------------#
# Carbon Constraints
#-----------------------------------------------------------------------------#

from pyomo.core import *
import numpy as np

def const_co2(data, model):
    
    print("- Carbon constraints")
    
    # total CO2
    def totalCarbon_rule(model):
        return(model.TotalCarbon == model.FuelCO2 + model.TechCO2 + model.StgCO2 + model.NetCO2)
    model.totalCarbon = Constraint(rule=totalCarbon_rule)    
    
    # max CO2
    def carbonConst_rule(model):
        return (model.TotalCarbon <= model.maxCarbon)
    
    if np.isnan(data.maxcarbon) == False: # if max carbon is not nan (i.e., is given)
        model.carbonConst = Constraint(rule=carbonConst_rule)  
    
    # CO2 from energy carriers
    def fuelCO2_rule(model):
        return(model.FuelCO2 == sum(model.ecCO2[ei] * model.Eimp[h,m,ei] for h in model.hubs for m in model.Time for ei in model.EImpSet))
    model.fuelCO2Const = Constraint(rule=fuelCO2_rule)
    
    # CO2 from tech installation
    def techCO2_rule(model):
        return(model.TechCO2 == sum(model.techCO2[t] * model.CapTech[h,t] * model.YtCapCost[t] for h in model.hubs for t in model.Tech))
    model.techCO2Const = Constraint(rule=techCO2_rule)
    
    # CO2 from storage installation
    def stgCO2_rule(model):
        return(model.StgCO2 == sum(model.stgCO2[s] * model.CapStg[h,s,e] * model.YsCapCost[s] for h in model.hubs for s in model.Stg for e in model.EC))
    model.stgCO2Const = Constraint(rule=stgCO2_rule)
    
    # CO2 from network installation
    def netCO2_rule(model):
        return(model.NetCO2 == sum(model.netCO2[l] * model.CapNet[l,hi,hj,e] *model.netLength[l] * model.YxCapCost[l,hi,hj,e] for l in model.LinkID for hi in model.hub_i for hj in model.hub_j for e in model.EC))
    model.netCO2Const = Constraint(rule=netCO2_rule)
    
    # Pyomo-specific way to specify total carbon variable
    def totalCarbon2_rule(model):
        return(model.TotalCarbon2 == model.TotalCarbon)
    model.totalCarbon2 = Constraint(rule=totalCarbon2_rule)
