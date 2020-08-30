#-----------------------------------------------------------------------------#
# Cost Constraints
#-----------------------------------------------------------------------------#

from pyomo.core import *

def const_cost(model):
    
    print("- Cost constraints")
    
    # total cost
    def totalCost_rule(model):
        return(model.TotalCost == model.InvCost + model.FuelCost + model.VOMCost + model.FOMCost + model.CO2Tax - model.IncomeExp)
    model.totalCost = Constraint(rule=totalCost_rule)    
    
    # investment cost
    def invCost_rule(model):
        return(model.InvCost == (sum(model.CRFtech[t] * (model.invTech[t] * model.CapTech[h,t] * model.YtCapCost[t]) for h in model.hubs for t in model.Tech)
                                + sum(model.CRFstg[stg] * model.invStg[stg] * model.CapStg[h,stg,e] * model.YsCapCost[stg] for h in model.hubs for stg in model.Stg for e in model.EC)
                                + sum(model.CRFnet[l]*model.invNet[l]*model.netLength[l]*model.CapNet[l,hi,hj,e]*model.YxCapCost[l,hi,hj,e] for l in model.LinkID for hi in model.hub_i for hj in model.hub_j for e in model.EC)))
    model.invCost = Constraint(rule=invCost_rule)
    
    # energy carrier cost
    def fuelCost_rule(model):
        return(model.FuelCost == (sum(model.impCostFx[ei] * model.Eimp[h, m, ei] for h in model.hubs for m in model.Time for ei in model.EImpFxSet)
                                + sum(model.impCostHr[ei,m] * model.Eimp[h, m, ei] for h in model.hubs for m in model.Time for ei in model.EImpHrSet)))
    model.fuelCost = Constraint(rule=fuelCost_rule) 
    
    # variable O&M cost
    def vomCost_rule(model):
        return(model.VOMCost == (sum(model.Eout[h,m,t,e] * model.omvTech[t]
                                for h in model.hubs for m in model.Time for t in model.Tech for e in model.EC)
                                + sum(model.NetE[l,hi,hj,e,m]*(1-model.netLoss[l]*model.netLength[l])*model.omvNet[l]
                                for l in model.LinkID for hi in model.hub_i for hj in model.hub_j for e in model.EC for m in model.Time)))
    model.vomCost = Constraint(rule=vomCost_rule)
    
    # fixed O&M cost
    def fomCost_rule(model):
        return(model.FOMCost == (sum(model.CapTech[h,t]*model.omfTech[t] for h in model.hubs for t in model.Tech)
                                + sum(model.CapNet[l,hi,hj,e]*model.omfNet[l]
                                for l in model.LinkID for hi in model.hub_i for hj in model.hub_j for e in model.EC)
                                + sum(model.CapStg[h,s,e]*model.omfStg[s] for h in model.hubs for s in model.Stg for e in model.EC)))
    model.fomCost = Constraint(rule=fomCost_rule)
    
    # carbon tax
    def co2Tax_rule(model):
        return(model.CO2Tax == (sum(model.co2Tax[ei] * model.ecCO2[ei] * model.Eimp[h, m, ei] for h in model.hubs for m in model.Time for ei in model.EImpSet)))
    model.co2TaxConst = Constraint(rule=co2Tax_rule)
    
    # revenue from exports
    def incomeExp_rule(model):
        return(model.IncomeExp == (sum(model.expPriceFx[ex] * model.Eexp[h,m,ex] for h in model.hubs for m in model.Time for ex in model.EExpFxSet)
                                    + sum(model.expPriceHr[ex,m] * model.Eexp[h,m,ex] for h in model.hubs for m in model.Time for ex in model.EExpHrSet)))
    model.incomeExp = Constraint(rule=incomeExp_rule)
    

