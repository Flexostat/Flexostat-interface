        
def computeControl(self,od,z,time=0.0):
    if z == None:
        z = 0
    #calculate control
    err_sig = 1000*(od-self.cparams['setpoint'])
    z = z+err_sig*self.cparams['ki']
    if z<0:
        z = 0
    if z>self.cparams['maxdilution']:
        z = self.cparams['maxdilution']
    
    u = z+err_sig*self.cparams['kp']
    if u < self.cparams['mindilution']:
        u = self.cparams['mindilution']
    if u > self.cparams['maxdilution']:
        u = self.cparams['maxdilution']
    u = int(u) # make sure u is an int
    
    return (u,z)