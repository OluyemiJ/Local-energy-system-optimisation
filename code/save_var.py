#-----------------------------------------------------------------------------#
# Save Results
#-----------------------------------------------------------------------------#

from pyomo.core import *

def model_saveVar(model, result_file):
    
    print("Saving results to text file...")

    with open(result_file, 'w') as f:
#        f.write ('{} {}\n'.format("objective ", value(model.TotalCost)))
        for v in model.component_objects(Var, active=True): # save all variables values to result_file
            varobject = getattr(model, str(v))
            for index in varobject:
                if index is not None:
                    line = ' '.join(str(t) for t in index)
                    f.write ('{} {} {}\n'.format(v, line, varobject[index].value))
                else:
                    f.write ('{} {} {}\n'.format(v, index, varobject[index].value))
