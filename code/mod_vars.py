#-----------------------------------------------------------------------------#
# Model Variables
#-----------------------------------------------------------------------------#

from pyomo.core import *

def gen_var(data, model):
    
    print("Generating model variables...")

    # Technology-related variables
    model.CapTech = Var(model.hubs, model.Tech, domain=NonNegativeReals) # installed tech capacity
    model.Ein = Var(model.hubs, model.Time, model.Tech, model.EC, domain=NonNegativeReals) # input energy to tech
    model.Eout = Var(model.hubs, model.Time, model.Tech, model.EC, domain=NonNegativeReals) # output energy from tech
    model.Ypl_op = Var(model.hubs, model.Time, model.PartLTech, domain=Binary) # binary indicator for operation of part-load tech during time period
    
    # Import/export variables
    model.Eexp = Var(model.hubs, model.Time, model.EC, domain=NonNegativeReals) # export energy
    model.Eimp= Var(model.hubs, model.Time, model.EC, domain=NonNegativeReals) # import energy
    
    # Storage technology variables
    model.CapStg = Var(model.hubs, model.Stg, model.EC, domain=NonNegativeReals) # installed storage capacity
    model.FlowStg = Var(model.hubs, model.Time, model.Stg, model.EC, domain=Reals) # energy into storage
    model.SoC = Var(model.hubs, model.SubTime, model.Stg, model.EC, domain=NonNegativeReals) # state of charge of storage
    
    # Network variables
    model.CapNet = Var(model.LinkID, model.hub_i, model.hub_j, model.EC, domain=NonNegativeReals) # installed network link capacity
    model.NetE = Var(model.LinkID, model.hub_i, model.hub_j, model.EC, model.Time, domain=NonNegativeReals) # transfer of energy from hub i to hub j
    model.Yx_op = Var(model.LinkID, model.hub_i, model.hub_j, model.EC, model.Time, domain=Binary) # binary indicator for energy transfer (NetE) from hub i to hub j during time period

    # Cost variables
    model.TotalCost = Var(domain=Reals) # total cost
    model.InvCost = Var(domain=NonNegativeReals) # investment cost
    model.FuelCost = Var(domain=NonNegativeReals) # fuel cost
    model.VOMCost = Var(domain=NonNegativeReals) # variable operation and maintainance cost
    model.FOMCost = Var(domain=NonNegativeReals) # fixed operation and maintainance cost
    model.CO2Tax = Var(domain=NonNegativeReals) # carbon tax
    model.IncomeExp = Var(domain=NonNegativeReals) # income from exports
    
    # Carbon variables
    model.TotalCarbon = Var(domain=Reals) # total carbon
    model.TotalCarbon2 = Var(domain=Reals) # total carbon (needed due to Pyomo internal rules in order to minimize carbon)
    model.FuelCO2 = Var(domain=Reals) # energy carrier carbon emissions
    model.TechCO2 = Var(domain=Reals) # technology installation carbon emissions
    model.StgCO2 = Var(domain=Reals) # storage installation carbon emissions
    model.NetCO2 = Var(domain=Reals) # network installation carbon emissions