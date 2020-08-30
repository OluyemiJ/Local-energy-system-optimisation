#-----------------------------------------------------------------------------#
# Network Constraints
#-----------------------------------------------------------------------------#

from pyomo.core import *

def const_net(model):
    
    print("- Network constraints")
    
    # network energy transfer limited by capacity
    def netQ_rule(model, l, hi, hj, e, m):
        return (model.NetE[l,hi,hj,e,m] <= model.Yx[l,hi,hj,e] * model.CapNet[l,hi,hj,e])
    
    model.netQ_const = Constraint(model.LinkID, model.hub_i, model.hub_j, model.EC, model.Time, rule=netQ_rule)
    
    # set Yx_op = 1 if flow exists
    def YxOp_rule(model, l, hi, hj, e, m):
        return (model.NetE[l,hi,hj,e,m] <= (model.Yx_op[l,hi,hj,e,m] * model.bigM) )
    
    model.YxOprule1_const = Constraint(model.LinkID, model.hub_i, model.hub_j, model.EC, model.Time, rule=YxOp_rule)
    
    # ensure single directional flow at every time period (either flow from i to j or j to i, but not both in the same time period)
    def netflow_rule(model, l, hi, hj, e, m):
        return (model.Yx_op[l,hi,hj,e,m] + model.Yx_op[l,hj,hi,e,m] <= 1)
    
    model.netflow_const = Constraint(model.LinkID, model.hub_i, model.hub_j, model.EC, model.Time, rule=netflow_rule)
    
    # capacity from i to j is equal to capacity from j to i
    def netCapEq_rule(model, l, hi, hj, e):
        return (model.CapNet[l,hi,hj,e] == model.CapNet[l,hj,hi,e])
    
    model.netCapEq_const = Constraint(model.LinkID, model.hub_i, model.hub_j, model.EC, rule=netCapEq_rule)
    
    # network maximum capacity bound
    def netMaxCap_rule(model, l, hi, hj, e):
        return (model.CapNet[l,hi,hj,e] <= model.netMax[l,hi,hj,e])
    
    model.netMaxCap_const = Constraint(model.LinkID, model.hub_i, model.hub_j, model.EC, rule=netMaxCap_rule)
    
    # network minimum capacity bound
    def netMinCap_rule(model, l, hi, hj, e):
        return (model.CapNet[l,hi,hj,e] >= model.netMin[l,hi,hj,e])
    
    model.netMinCap_const = Constraint(model.LinkID, model.hub_i, model.hub_j, model.EC, rule=netMinCap_rule)