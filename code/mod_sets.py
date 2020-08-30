#-----------------------------------------------------------------------------#
# Model Sets
#-----------------------------------------------------------------------------#

from pyomo.core import *

def gen_set(data, model):
    
    print("Generating model sets...")
    
    # Time sets
    model.Time = RangeSet(1, data.nTime) # hours
    model.SubTime = RangeSet(0, data.nTime, within=model.Time) # including time 0
    
    # ID assignments
    model.Tech = RangeSet(1,data.nTech) # set of technologies
    model.EC = RangeSet(1, data.nEC) # set of energy carriers
    model.Stg = RangeSet(1, data.nStg)  # set of storage technologies
    model.LinkID = RangeSet(1,data.NetworkData.shape[1]) # link ID for network connection between hub_i and hub_j for the given energy carrier

    # Solar sets
    model.SolEC = Set(initialize=data.solECID, within=model.EC) # solar energy carrier ID
    model.SolarTechs = Set(initialize=data.techSol, within=model.Tech) # solar techs
    
    # Tech sets
    model.TechFixIn = Set(initialize=data.techFixIn, within=model.Tech) # set of technologies with fixed input shares
    model.TechFixOut = Set(initialize=data.techFixOut, within=model.Tech) # set of technologies with fixed output shares
    model.TechFreeOut = Set(initialize=data.techFreeOut, within=model.Tech) # set of technologies without fixed output shares

    # Part-load tech sets
    model.PartLFree = Set(initialize = model.TechFreeOut & data.techPL, within=model.Tech)
    model.PartLFix = Set(initialize = model.TechFixOut & data.techPL, within=model.Tech)
    model.PartLTech = Set(initialize = data.techPL, within=model.Tech)
    
    # Import/export sets
    model.EImpSet = Set(initialize=data.impEC, within=model.EC) # set of import (supply) energy carriers
    model.EExpSet = Set(initialize=data.expEC, within=model.EC) # set of export energy carriers
    model.ENImpSet = Set(initialize=set(model.EC) - set(model.EImpSet), within=model.EC) # set of energy carriers NOT imported
    model.ENExpSet = Set(initialize=set(model.EC) - set(model.EExpSet), within=model.EC) # set of energy carriers NOT exported
    model.EImpHrSet = Set(initialize=data.impHrEC, within=model.EImpSet) # set of hourly import (supply) energy carriers
    model.EImpFxSet = Set(initialize=set(model.EImpSet) - set(model.EImpHrSet), within=model.EImpSet) # set of energy carriers NOT priced hourly (i.e., fixed price imports)
    model.EExpHrSet = Set(initialize=data.expHrEC, within=model.EExpSet) # set of hourly export energy carriers
    model.EExpFxSet = Set(initialize=set(model.EExpSet) - set(model.EExpHrSet), within=model.EExpSet) # set of energy carriers NOT priced hourly (i.e., fixed price exports)

    # Hub sets
    model.hubs=RangeSet(1,data.nHub) #0 is items /number of hubs
    model.hub_i=RangeSet(1,data.nHub, within=model.hubs) #used for networks e.q. Q(i,j)
    model.hub_j=RangeSet(1,data.nHub, within=model.hubs) #used for networks e.q. Q(i,j)
    
    