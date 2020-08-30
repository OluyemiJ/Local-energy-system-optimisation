#-----------------------------------------------------------------------------#
# Technology Constraints (General)
#-----------------------------------------------------------------------------#
    
from pyomo.core import *

## hourly capacity factor constraints
def const_CFHr(data, model):

    model.maxCFHrConst = ConstraintList()
    model.minCFHrConst = ConstraintList()
    
    for i in range(data.cfHr.shape[1]): # for each column (i.e., technology)
        cfhrT = data.cfHr.iloc[:,i] # extract hourly CF data for tech
        cfhrT = cfhrT.dropna(axis=0) # remove nan values
        t = data.cfHr.columns[i] # tech ID
        
        # extract hubs
        hublist = data.hubTech[t-1] # hubs which tech is assigned to
        if isinstance(hublist,float): # if only a single hub was given and it is read as float, convert to int
            hublist = int(hublist)
        hublist = str(hublist).split(',') # convert to string (int case); if more thane one hub is given, splits hubs into a list using ',' as a delimiter
        
        for j in range(cfhrT.shape[0]): # for each hour where a CF is given for tech
            m = cfhrT.index[j] # time
            try:
                if data.cfHrEq.iloc[i] == "max":
                    for k,h in enumerate(hublist): # for each hub
                        if t in set(model.TechFreeOut): # if TechFreeOut
                            model.maxCFHrConst.add(sum(model.Eout[int(h),m,t,e] for e in model.EC) <= cfhrT.loc[m]*model.CapTech[int(h),t])
                        elif t in set(model.TechFixOut): # if TechFixOut
                            model.maxCFHrConst.add(model.Eout[int(h),m,t,data.outEC[t][0]] <= cfhrT.loc[m]*model.CapTech[int(h),t]) # constraint applies to first output EC only
                elif data.cfHrEq.iloc[i] == "min":
                    for k,h in enumerate(hublist): # for each hub
                        if t in set(model.TechFreeOut): # if TechFreeOut
                            model.minCFHrConst.add(sum(model.Eout[int(h),m,t,e] for e in model.EC) >= cfhrT.loc[m]*model.CapTech[int(h),t])
                        elif t in set(model.TechFixOut): # if TechFixOut
                            model.minCFHrConst.add(model.Eout[int(h),m,t,data.outEC[t][0]] >= cfhrT.loc[m]*model.CapTech[int(h),t]) # constraint applies to first output EC only
                else:
                    raise ValueError()
            except ValueError:
                print('Capacity factor not specified as "max" or "min"; check hourly capacity factor input spreadsheet.')
                raise # reraise last exception

## general technology constraints
def const_techGen(data, model):
    
    print("- General technology constraints")
        
    # output energy (Eout) for technologies without a fixed output share (model.TechFreeOut)
    def EoutFree_rule(model, h, m, t):
        return (sum(model.Eout[h,m,t,e] for e in model.EC) == sum(model.Ein[h,m,t,e] for e in model.EC)*model.eff[t])
    model.eoutFree = Constraint(model.hubs, model.Time, model.TechFreeOut, rule=EoutFree_rule)
    
    # output energy (Eout) for technologies with a fixed output share (model.TechFixOut)
    def EoutFix_rule(model, h, m, t, e):
        return (model.Eout[h,m,t,e] == sum(model.Ein[h,m,t,ec] for ec in model.EC)*model.effFixOut[t,e])
    model.eoutFix = Constraint(model.hubs, model.Time, model.TechFixOut, model.EC, rule=EoutFix_rule)
    
    # output energy (Eout) for technologies with a fixed output share (model.TechFixOut)
    def EinFix_rule(model, h, m, t, e):
        return (model.Ein[h,m,t,e] == sum(model.Ein[h,m,t,ec] for ec in model.EC)*model.shrFixIn[t,e])
    model.einFix = Constraint(model.hubs, model.Time, model.TechFixIn, model.EC, rule=EinFix_rule)
    
    ## set Eout and Ein == 0 for ECs that do not exist for each technology
    #stin = [] # for tracking only
    for t in range(1,data.nTech+1):
        necin = set(model.EC) - set(data.inEC[t])
        if t not in model.TechFixIn:
            for e in necin:
                for h in range(1,data.nHub+1):
                    for m in range(1,data.nTime+1):
                        model.Ein[h,m,t,e].fix(0)
    #                    stin.append([h,m,t,e])
        
        if t not in model.TechFixOut:
            necout = set(model.EC) - set(data.outEC[t])
            for e in necout:
                for h in range(1,data.nHub+1):
                    for m in range(1,data.nTime+1):
                         model.Eout[h,m,t,e].fix(0)
    
    ## technology output cannot be higher than installed capacity 
    # - for technologies without fixed output shares:
    def capConstFree_rule(model, h, m, t):
        return (sum(model.Eout[h,m,t,e] for e in model.EC) <= model.CapTech[h,t])
    model.capConstFree = Constraint(model.hubs, model.Time, model.TechFreeOut, rule=capConstFree_rule)
    
    # - for technologies with fixed output shares:
    model.capConstFix= ConstraintList()
    for t in set(model.TechFixOut):
        for h in set(model.hubs):
            for m in set(model.Time):
                model.capConstFix.add(model.Eout[h,m,t,data.outEC[t][0]] <= model.CapTech[h,t]) # constraint applies to first output EC only (remaining output ECs determined according to given fixed shares)
    
    # installed capacity must be less than maximum capacity (max cap defaults to infinity if not specified)
    def maxCapacity_rule(model, h, t):
        return (model.CapTech[h,t] <= model.maxCapTechs[h,t])
    model.maxCapacity = Constraint(model.hubs, model.Tech, rule=maxCapacity_rule)
    
    # installed capacity must be greater than minimum capacity (min cap defaults to zero if not specified)
    def minCapacity_rule(model, h, t):
        return (model.CapTech[h,t] >= model.minCapTechs[h,t])
    model.minCapacity = Constraint(model.hubs, model.Tech, rule=minCapacity_rule)
    
    ## total technology output cannot be higher than maximum output
    # - for technologies without fixed output shares:
    def maxOutConstFree_rule(model, h, t):
        return (sum(model.Eout[h,m,t,e] for m in model.Time for e in model.EC) <= model.maxOutTechs[h,t])
    model.maxOutConstFree = Constraint(model.hubs, model.TechFreeOut, rule=maxOutConstFree_rule)
    
    # - for technologies with fixed output shares:
    model.maxOutConstFix= ConstraintList()
    for t in set(model.TechFixOut):
        for h in set(model.hubs):
            model.maxOutConstFix.add(sum(model.Eout[h,m,t,data.outEC[t][0]] for m in model.Time) <= model.maxOutTechs[h,t]) # constraint applies to first output EC only (remaining output ECs determined according to given fixed shares)
    
    ## total technology output cannot be less than minimum output
    # - for technologies without fixed output shares:
    def minOutConstFree_rule(model, h, t):
        return (sum(model.Eout[h,m,t,ec] for m in model.Time for ec in model.EC) >= model.minOutTechs[h,t])
    model.minOutConstFree = Constraint(model.hubs, model.TechFreeOut, rule=minOutConstFree_rule)
    
    # - for technologies with fixed output shares:
    model.minOutConstFix= ConstraintList()
    for t in set(model.TechFixOut):
        for h in set(model.hubs):
            model.minOutConstFix.add(sum(model.Eout[h,m,t,data.outEC[t][0]] for m in model.Time) >= model.minOutTechs[h,t]) # constraint applies to first output EC only (remaining output ECs determined according to given fixed shares)
    
    ## maximum capacity factor constraints - over time horizon
    # - for technologies without fixed output shares:
    def maxCFAFree_rule(model, h, t):
        return (sum(model.Eout[h,m,t,ec] for m in model.Time for ec in model.EC) <= model.maxCFA[t]*model.CapTech[h,t]*data.nTime)
    model.maxCFAFreeConst = Constraint(model.hubs, model.TechFreeOut, rule=maxCFAFree_rule)
    
    # - for technologies with fixed output shares:
    model.maxCFAFixConst= ConstraintList()
    for t in set(model.TechFixOut):
        for h in set(model.hubs):
            model.maxCFAFixConst.add(sum(model.Eout[h,m,t,data.outEC[t][0]] for m in model.Time) <= model.maxCFA[t]*model.CapTech[h,t]*data.nTime) # constraint applies to first output EC only

    ## minimum capacity factor constraints - over time horizon
    # - for technologies without fixed output shares:
    def minCFAFree_rule(model, h, t):
        return (sum(model.Eout[h,m,t,ec] for m in model.Time for ec in model.EC) >= model.minCFA[t]*model.CapTech[h,t]*data.nTime)
    model.minCFAFreeConst = Constraint(model.hubs, model.TechFreeOut, rule=minCFAFree_rule)
    
    # - for technologies with fixed output shares:
    model.minCFAFixConst= ConstraintList()
    for t in set(model.TechFixOut):
        for h in set(model.hubs):
            model.minCFAFixConst.add(sum(model.Eout[h,m,t,data.outEC[t][0]] for m in model.Time) >= model.minCFA[t]*model.CapTech[h,t]*data.nTime) # constraint applies to first output EC only

    ## hourly capacity factor constraints
    const_CFHr(data, model)    