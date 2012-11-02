class State:
    def __init__(self):
        self.z = 0
    def __str__(self):
        return '%.4f' % self.z

def computeControl(self,od,z,chamber=0,time=0.0):
    if z == None:
        z = State()
    #calculate control
    setpoints = map(float,self.cparams['setpoint'].split())
    #for debug
#    print "setpoints: "+ str(setpoints)+ "this: " + str(setpoints[chamber])
    
    err_sig = 1000*(od-setpoints[chamber])
    z.z = z.z+err_sig*float(self.cparams['ki'])
    if z.z<0:
        z.z = 0
    if z.z>float(self.cparams['maxdilution']):
        z.z = float(self.cparams['maxdilution'])
    
    u = z.z+err_sig*float(self.cparams['kp'])
    if u < float(self.cparams['mindilution']):
        u = float(self.cparams['mindilution'])
    if u > float(self.cparams['maxdilution']):
        u = float(self.cparams['maxdilution'])
    u = int(u) # make sure u is an int
    
    return (u,z)
