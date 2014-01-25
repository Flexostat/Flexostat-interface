from time import sleep, time
import threading
#import wx
import sys


class Pump(object):
    debug = False
    
    def __init__(self, cparams, logfiles, pparams, unused_cport, pport):
        self.logfiles = logfiles
        self.pparams = pparams
        self.cparams = cparams # All controller parameters live here
        self.pport = pport
        
        if pport is not None and pport.isOpen():
            self._initPump()
            
    def _initPump(self):
        print "pump init"
        with self.pport.lock:
            self.pport.flushInput()
            # Disable alarms
            s = "AL 0\r"
            print ">>", s
            self.pport.write(s)
            print "<<", self._pumpGetResponse()
            
            # Set diameter
            diameter = self.pparams['syringediameter']
            s = "DIA %s\r" % diameter
            print ">>", s
            self.pport.write(s)
            print "<< ", self._pumpGetResponse()
            
            # Set pump rate
            syringe_rate = self.pparams['syringerate']
            rate_unit = self.pparams['syringrateunit']
            s = "RAT %s %s\r" % (syringe_rate, rate_unit)
            print ">> " + s
            self.pport.write(s)
            print "<< " + self._pumpGetResponse()
            
            # Set volume units
            volume_units = self.pparams['volumeunits']
            s = "VOL %s\r" % volume_units
            print ">> " + s
            self.pport.write(s)
            print "<< " + self._pumpGetResponse()
    
    def _pumpGetResponse(self):        
        if self.debug:
            print "+++++++START PGR:"
            
        while self.pport.inWaiting() <= 0:
            sleep(0.1)
        response = self.pport.read(self.pport.inWaiting())
        while response[-1] != '\x03':
            while self.pport.inWaiting() <=0:
                sleep(0.1)
            response = response + self.pport.read(self.pport.inWaiting())
            
        if self.debug:
            print response
            
        return response
        
    def withdraw(self, volume):
        pump = self.pport
        u = str(int(volume))
        with self.pport.lock:
            pump.write("DIR WDR\r")
            self._pumpGetResponse()
            pump.write("VOL %s\r" % u)
            self._pumpGetResponse()
            pump.write("RUN\r")
            self._pumpGetResponse()
    
    def dispense(self, volume):
        pump = self.pport
        u = str(int(volume))
        with self.pport.lock:
            pump.write("DIR INF\r")
            self._pumpGetResponse()
            pump.write("VOL"+u+"\r")
            self._pumpGetResponse()
            pump.write("RUN\r")
            self._pumpGetResponse()
            
    def waitForPumping(self):
        pump = self.pport
        while True:
            pump.write("\r")
            s = self._pumpGetResponse()
            if s[3] == 'S':
                break;
            sleep(0.5)

    
    
