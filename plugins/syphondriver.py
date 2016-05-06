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

        self.chamber = 1
        self.last_open = 0
        
        print "pump init"
        self._actionComplete = time()+4
        
        
    
    def _pumpGetResponse(self):
        return None
    
    def withdraw(self, volume):
        """  Instruct the pump to withrdraw volume units.
            
            volume should be a numpy array of dimension 1
        """
        return
            
    def dispense(self,volume):
        """  Instruct the pump to dispese volume units.
        
            volume should be a numpy array of dimension 1
        """
        with self.serpt.lock:
            if self.pparams['pulsebugworkaround'].lower() == 'true':
                command_str ='pul'+str(int(self.chamber*(2**10)+volume[0]))+";"
            else:
                command_str ='pul'+str(int(self.chamber*(1000)+volume[0]))+";"
            self.serpt.write(command_str)
        self._actionComplete = time() +0.02*volume[0] + 1
        
    def waitForPumping(self):
        """ Block until pumping is done
        
        """
        while self._actionComplete>time():
            sleep_time = self._actionComplete - time()
            if sleep_time < 0:
                sleep_time = 0.1
            if sleep_time > 4:
                sleep_time = 4
            sleep(sleep_time)
       

    def select(self,chamber):
        self.chamber = chamber
        
