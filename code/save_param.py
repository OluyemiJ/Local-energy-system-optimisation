#-----------------------------------------------------------------------------#
# Save Parameters
#-----------------------------------------------------------------------------#

from pyomo.core import *

def model_saveParam(model, param_file):
    
    print("Saving model parameter values to text file...")
    
    with open(param_file, 'w') as f:
        for p in model.component_objects(Param, active=True): # save all parameters values to param_file
            paramobject = getattr(model, str(p))
            for index in paramobject:
                if type(index) is tuple:
                    line = ' '.join(str(t) for t in index)
                    f.write ('{} {} {}\n'.format(p, line, paramobject[index]))
                elif index is None:
                    f.write ('{} {}\n'.format(p, paramobject.value))
                else:
                    f.write ('{} {} {}\n'.format(p, index, paramobject[index]))