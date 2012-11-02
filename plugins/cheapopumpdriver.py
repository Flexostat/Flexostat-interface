from time import sleep, time
import threading
#import wx
import sys

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
        self._state = 0
        with self.serpt.lock:
            self.serpt.write('pmv0;')
        self._actionComplete = time()+4
        
        
    
    def _pumpGetResponse(self):
        return None
        
    def withdraw(self, volume):
        """  Instruct the pump to withrdraw volume units.
        
        """
        volume = volume[0]
        self._state = self._state+volume;
        if self._state <0:
            self._state = 0
        if self._state > 1800:
            self._state = 1800
        cmd_str = 'pmv' + str(self._state) + ';'
        with self.serpt.lock:
            self.serpt.write(cmd_str)
        wait_time = 4*volume/1800
        if wait_time < 1:
            wait_time = 1
        self._actionComplete = time()+wait_time
            
    def dispense(self,volume):
        """  Instruct the pump to dispese volume units.
        
        """
        self.withdraw([-v for v in volume])
        
    def waitForPumping(self):
        """ Block until pumping is done
        
        """
        sleep_time = self._actionComplete - time()
        if sleep_time >0:
            sleep(sleep_time)
        

