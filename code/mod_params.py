#-----------------------------------------------------------------------------#
# Model Parameters
#-----------------------------------------------------------------------------#

from pyomo.core import *

def gen_param(data, model):
    
    print("Generating model parameters...")
    
    # Technology parameters
    model.eff = Param(model.TechFreeOut, initialize = data.EffInit()) # efficiencies for technologies without fixed output shares
    model.effFixOut = Param(model.TechFixOut, model.EC, initialize = data.EffFixOutInit()) # efficiencies for technologies with fixed output shares
    model.shrFixIn = Param(model.TechFixIn, model.EC, initialize = data.InFixInit()) # fixed input shares
    model.partLoad = Param(model.Tech, initialize=data.pldict) # minimum load
    model.lifeTechs = Param(model.Tech, initialize = data.GenDict(data.nTech,data.lifeTech)) # tech lifetime (not used)
    model.maxCapTechs = Param(model.hubs, model.Tech, initialize=data.TechLimitInit(data.maxCapTech)) # max installed tech capacity
    model.minCapTechs = Param(model.hubs, model.Tech, initialize=data.TechLimitInit(data.minCapTech)) # min installed tech capacity
    model.maxOutTechs = Param(model.hubs, model.Tech, initialize=data.TechLimitInit(data.maxOutTech)) # max total energy output of tech
    model.minOutTechs = Param(model.hubs, model.Tech, initialize=data.TechLimitInit(data.minOutTech)) # min total energy output of tech
    model.techCO2 = Param(model.Tech, initialize=data.GenDict(data.nTech,data.co2Tech)) # carbon factor for tech installation
    model.YtCapCost = Param(model.Tech, initialize = data.TechCapInit(model)) # tech pre-installed capacities; indicator to apply costs based on capacity (investment); model does not apply these costs to a pre-installed capacity; this function also assigns pre-installed capacities to the cap variable
    model.solkWm2 = Param(model.Tech, initialize = data.GenDict(data.nTech,data.solkWm2)) # specific power for solar techs
    model.invTech = Param(model.Tech, initialize= data.GenDict(data.nTech,data.invTech)) # tech investment cost
    model.omvTech = Param(model.Tech, initialize= data.GenDict(data.nTech,data.omvTech)) # tech variable O&M cost
    model.omfTech = Param(model.Tech, initialize= data.GenDict(data.nTech,data.omfTech)) # tech fixed O&M cost
    model.CRFtech = Param(model.Tech, domain=NonNegativeReals, initialize=data.CRF(data.lifeTech)) # tech captial recovery factor
    model.maxCFA = Param(model.Tech, initialize=data.GenDict(data.nTech,data.maxCFA)) # max annual capacity factor
    model.minCFA = Param(model.Tech, initialize=data.GenDict(data.nTech,data.minCFA)) # max annual capacity factor
#    model.CRFtech = Param(model.Tech, domain=NonNegativeReals, initialize=data.TechCRF()) # tech captial recovery factor
    
    # Storage parameters
    model.maxStorCh = Param(model.Stg, initialize= data.GenDict(data.nStg,data.chMax)) # storage max charging rate
    model.maxStorDisch = Param(model.Stg, initialize = data.GenDict(data.nStg,data.dchMax)) # storage max discharging rate
    model.standbyLoss = Param(model.Stg, initialize = data.GenDict(data.nStg,data.stndby)) # storage standby loss
    model.chargingEff = Param(model.Stg, initialize = data.GenDict(data.nStg,data.chEff)) # storage charging efficiency
    model.dischargingEff = Param(model.Stg, initialize = data.GenDict(data.nStg,data.dchEff)) # storage discharging efficiency
    model.minSoC = Param(model.Stg, initialize = data.GenDict(data.nStg,data.minSoC)) # storage min state of charge
    model.invStg = Param(model.Stg, initialize = data.GenDict(data.nStg,data.invCostStg)) # storage investement cost
    model.lifeStg = Param(model.Stg, initialize = data.GenDict(data.nStg,data.lifeStg)) # storage lifetime (this param not used directly)
    model.omfStg = Param(model.Stg, initialize = data.GenDict(data.nStg,data.omfCostStg)) # storage O&M fixed cost
    model.stgCO2 = Param(model.Stg, initialize = data.GenDict(data.nStg,data.co2Stg)) # carbon factor for storage installation
    model.CRFstg = Param(model.Stg, domain=NonNegativeReals, initialize=data.CRF(data.lifeStg)) # storage captial recovery factor
#    model.CRFstg = Param(model.Stg, domain=NonNegativeReals, initialize=data.StgCRF()) # storage captial recovery factor
#    maxS_dict, minS_dict = data.StgMaxMinCapInit()
#    model.maxCapStg = Param(model.hubs, model.Stg, model.EC, initialize = maxS_dict) # max installed storage capacity
#    model.minCapStg = Param(model.hubs, model.Stg, model.EC, initialize = minS_dict) # min installed storage capacity
    model.maxCapStg = Param(model.Stg, initialize = data.maxCapStg) # max installed storage capacity
    model.minCapStg = Param(model.Stg, initialize = data.minCapStg) # min installed storage capacity
    model.YsCapCost = Param(model.Stg, initialize = data.StgCapInit(model)) # storage pre-installed capacities initialization and flag setting

    # Network parameters
    YNx_dict, YNx_capcost_dict, len_dict, loss_dict, invNet_dict, omfNet_dict, omvNet_dict, maxcNet_dict, mincNet_dict, co2Net_dict, lifeNet_dict =  data.NetworkInit(model) # must be called after model.CapNet declaration (function initializes model.CapNet installed capacities)
    model.netLength = Param(model.LinkID, initialize = len_dict) # network length
    model.netLoss = Param(model.LinkID, initialize = loss_dict) # network loss
    model.invNet = Param(model.LinkID, initialize = invNet_dict) # network investment cost
    model.omfNet = Param(model.LinkID, initialize = omfNet_dict) # network fixed O&M cost
    model.omvNet = Param(model.LinkID, initialize = omvNet_dict) # network variable O&M cost
    model.CRFnet = Param(model.LinkID, domain=NonNegativeReals, initialize=data.CRF(data.lifeNet)) # network captial recovery factor
#    model.CRFnet = Param(model.LinkID, domain=NonNegativeReals, initialize=data.NetCRF()) # network captial recovery factor
    model.netMax = Param(model.LinkID, model.hub_i, model.hub_j, model.EC, initialize = maxcNet_dict) # max installed network
    model.netMin = Param(model.LinkID, model.hub_i, model.hub_j, model.EC, initialize = mincNet_dict) # min installed network
    model.netCO2 = Param(model.LinkID, initialize = co2Net_dict) # carbon factor for network  installation
    model.lifeNet = Param(model.LinkID, initialize = lifeNet_dict) # network link lifetime (this param not used directly)
    model.Yx = Param(model.LinkID, model.hub_i, model.hub_j, model.EC, initialize = YNx_dict) # network link indicator for flow from hub i to j
    model.YxCapCost = Param(model.LinkID, model.hub_i, model.hub_j, model.EC, initialize = YNx_capcost_dict) # indicator to apply costs (investment and fixed) based on capacity; model does not apply these costs to a pre-installed capacity, or from hub j to i where costs from hub i to j are already accounted for
    
    # Import/export parameters
    model.impCostFx = Param(model.EImpSet, initialize=data.impCostFx.to_dict()) # EC import cost
    model.impCostHr = Param(model.EImpHrSet, model.Time, initialize=data.GenDict2D(data.impHr)) # EC hourly import cost
    model.expPriceFx = Param(model.EExpSet, initialize=data.expPriceFx.to_dict())  # EC export price
    model.expPriceHr = Param(model.EExpHrSet, model.Time, initialize=data.GenDict2D(data.expHr)) # EC hourly import cost
    model.co2Tax = Param(model.EImpSet, initialize=data.impCO2Tax.to_dict()) # carbon tax 
    model.maxImp = Param(model.EImpSet, initialize=data.impMax.to_dict()) # max import supply
    model.ecCO2 = Param(model.EImpSet, initialize=data.impCO2.to_dict()) # carbon factors for ECs
    
    # Other global parameters
    model.interestRate = Param(within=NonNegativeReals, initialize=data.interest) # interest rate (this param not used directly)
    model.bigM = Param(within=NonNegativeReals, initialize=data.bigm) # acts as an upper limit for Eout from part load technologies and network link exchanges
    model.maxCarbon = Param(initialize=data.maxcarbon) # max total carbon
    model.loads = Param(model.hubs, model.Time, model.EC, default=0, initialize=data.loads) # demands
    model.solarEm = Param(model.Time, initialize=data.GenDict(data.nTime,data.solIrr)) # insolation