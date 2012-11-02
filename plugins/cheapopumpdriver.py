from time import sleep, time
import threading
#import wx
import sys

debug = False
#formally named cheapoPump
class Pump:
    
    def __init__(self,cparams,logfiles,pparams,cport,pport):
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
        self.withdraw(-volume)
        
    def waitForPumping(self):
        sleep_time = self._actionComplete - time()
        if sleep_time >0:
            sleep(sleep_time)
        

