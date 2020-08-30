#-----------------------------------------------------------------------------#
# Model Constraints
#-----------------------------------------------------------------------------#

from pyomo.core import *
import numpy as np

from cnst_sys import *
from cnst_techGen import *
from cnst_techSpc import *
from cnst_net import *
from cnst_stg import *
from cnst_co2 import *
from cnst_cost import *

def gen_cnst(data, model):
    
    print("Generating model constraints...")
    
    const_sys(data, model) # general system constraints; defined in cnst_sys.py
    const_techGen(data, model) # general technology constraints; defined in cnst_techGen.py
    const_techSpec(data, model) # specific technology constraints; defined in cnst_techSpc.py
    const_net(model) # network constraints; defined in cnst_net.py
    const_stg(data, model) # storage constraints; defined in cnst_stg.py
    const_co2(data, model) # carbon constraints; defined in cnst_co2.py
    const_cost(model) # cost constraints; defined in cnst_cost.py
    