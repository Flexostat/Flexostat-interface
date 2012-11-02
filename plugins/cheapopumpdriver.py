from time import sleep, time
import threading
#import wx
import sys
from numpy import array

debug = False
class Pump:
    """ The Pump driver
    
    """
    
    def __init__(self,cparams,logfiles,pparams,cport,pport):
        """
        cparams: a dictionary containing all controller parametrs from
            config.ini
        logfiles: deprecated
        pparams: a dictionary containing all pump parameters from config.ini
        cport: an open serial port object for controlling the controller board,
            which may or may not have the pump attached depending on the
            hardware.
        pport: an open serial port object for controlling the pump.  may go
            unused (eg cheapo pump)
        
        NOTE: cport and pport also have thread locks associated with them
            (named .lock).  they should only be used with their lock.
        """
        self.logfiles = logfiles
        self.pparams = pparams
        self.cparams = cparams #all controller parameters live here
        self.serpt = cport
        
        print "pump init"
        #fully in
        self._state = array([0,0])
        with self.serpt.lock:
            self.serpt.write('pmv0;')
            self.serpt.flush()
            self.serpt.write('pmb0;')
            self.serpt.flush()
        self._actionComplete = time()+4
        
        
    
    def _pumpGetResponse(self):
        return None
    
    def _chkStateBounds(self):
        for ind in range(0,len(self._state)):
            if self._state[ind] < 0:
                self._state[ind] = 0
            if self._state[ind] > 1600:
                self._state[ind] = 1600
        
    def withdraw(self, volume):
        """  Instruct the pump to withrdraw volume units.
            
            volume should be a numpy array of dimension 1
        """
        
        if volume.size <=2:
            cmds = ['pma','pmb']
        else:
            return
        #for old board compatability
        if volume.size == 1:
            cmds[0] = 'pmv'
        for ind in range(0,volume.size):
            self._state[ind] += volume[ind]
            self._chkStateBounds()
            cmd_str = cmds[ind] +str(self._state[ind]) + ';'
            with self.serpt.lock:
                self.serpt.write(cmd_str)
            wait_time = max(4*volume[ind]/1600.,1)
            self._actionComplete = time()+wait_time
            
            
            
    def dispense(self,volume):
        """  Instruct the pump to dispese volume units.
        
            volume should be a numpy array of dimension 1
        """
        self.withdraw(-volume)
        
    def waitForPumping(self):
        """ Block until pumping is done
        
        """
        while self._actionComplete>time():
            sleep_time = self._actionComplete - time()
            sleep(sleep_time)
       

