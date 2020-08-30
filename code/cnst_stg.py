#-----------------------------------------------------------------------------#
# Storage Constraints
#-----------------------------------------------------------------------------#

from pyomo.core import *

def const_stg(data, model):
    
    print("- Storage constraints")
    
    def storageBalance_rule(model, h, m, stg, e):
        return (model.SoC[h,m,stg,e] == ((1-model.standbyLoss[stg]) * model.SoC[h,(m-1),stg,e] + model.FlowStg[h,m,stg,e])) 
    model.storageBalance = Constraint(model.hubs, model.Time, model.Stg, model.EC, rule=storageBalance_rule) #storage continuinity variable
    
    # storage state of charge (SoC) should be the same at the start and end time period
    def storageStartEnd_rule(model, h, stg, e):
        return (model.SoC[h,0,stg,e] == model.SoC[h,data.nTime,stg,e])
    model.storageStartEnd = Constraint(model.hubs, model.Stg, model.EC, rule=storageStartEnd_rule)
    
    # storage max charging
    def storageChargeRate_rule(model, h, m, stg, e):
        return (model.FlowStg[h,m,stg,e] <= model.maxStorCh[stg] * model.CapStg[h,stg,e])
    model.storageChargeRate = Constraint(model.hubs, model.Time, model.Stg, model.EC, rule=storageChargeRate_rule) #maximum charging
    
    # storage max discharging
    def storageDischRate_rule(model, h, m, stg, e):
        return (model.FlowStg[h,m,stg,e] >= -1 * model.maxStorDisch[stg] * model.CapStg[h,stg,e])
    model.storageDischRate = Constraint(model.hubs,model.Time, model.Stg, model.EC, rule=storageDischRate_rule) #maximum discharging
    
    # storage minimum SoC
    def storageMinState_rule(model, h, m, stg, e):
        return (model.SoC[h,m,stg,e] >= model.CapStg[h,stg,e]*model.minSoC[stg])
    model.storageMinState = Constraint(model.hubs, model.Time, model.Stg, model.EC, rule=storageMinState_rule) #minimum SoC allowed
    
    # SoC <= installed capacity
    def storageCap_rule(model, h, m, stg, e):
        return (model.SoC[h,m,stg,e] <= model.CapStg[h,stg,e])
    model.storageCap = Constraint(model.hubs,model.Time, model.Stg, model.EC, rule=storageCap_rule) #smaller than storage cap
    
    # maximum storage capacity constraint
    def storageMaxCap_rule(model, h, stg, e):
        return (model.CapStg[h,stg,e] <= model.maxCapStg[stg])
    model.storageMaxCap = Constraint(model.hubs, model.Stg, model.EC, rule=storageMaxCap_rule)
    
    # minimum storage capacity constraint
    def storageMinCap_rule(model, h, stg, e):
        return (model.CapStg[h,stg,e] >= model.minCapStg[stg])
    model.storageMinCap = Constraint(model.hubs, model.Stg, model.EC, rule=storageMinCap_rule)
