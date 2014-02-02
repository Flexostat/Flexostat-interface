from numpy import array
from random import randint

#
#
#  Example mixture controller with random output.  
#
#
#

class State(object):
    """ The state variable for the control funcion
    
    This does not need to adhear to any proper interface although a
    readable __str__() method is highly recommended to allow for debugging.
    """
    def __init__(self):
        self.z = 0
        
    def __str__(self):
        return '%.4f' % self.z

def computeControl(self,od,z,chamber=0,time=0.0):
    """  Controller function
    
    self: self referrs to the main controller object that conains
    all state such as the parameters file.  computeControl should never write
    to any members of self
    od: current od of the camber
    chamber: the chamber number indexed from zero
    time: the current time since start up.
    
    Returns: a tuple (list of dilution values for this chamber, state object)
    
    """
    u = [randint(10,150), randint(10,150)]
    
        
    return (array(u),z)
