from time import sleep, time
import threading
#import wx
import sys

debug = False

class cheapoPump:
    
    def __init__(self,cparams,logfiles,pparams,cport,c_lock):
        self.pump_lock = c_lock
        
        self.logfiles = logfiles
        self.pparams = pparams
        self.cparams = cparams #all controller parameters live here
        self.serpt = cport
        
        print "pump init"
        #fully in
        self._state = 0
        with self.pump_lock:
            cport.write('pmv0;')
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
        with self.pump_lock:
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
        

class Pump:
    
    def __init__(self,cparams,logfiles,pparams,cport,pport):
        self.pump_lock = threading.Lock()
        
        self.logfiles = logfiles
        self.pparams = pparams
        self.cparams = cparams #all controller parameters live here
        self.serpt = cport
        self.pport = pport
        
        if pport != None and (pport.isOpen()):
            self._initPump()
            
            
    def _initPump(self):
        print "pump init"
        with self.pump_lock:
            self.pport.flushInput()
            #disable alarms
            s = "AL 0\r"
            print ">> " + s
            self.pport.write(s)
            print "<< " + self._pumpGetResponse()
            #set diameter
            s = "DIA "+self.pparams['syringediameter']+"\r"
            print ">> " + s
            self.pport.write(s)
            print "<< " + self._pumpGetResponse()
            #set pump rate
            s = ("RAT "+self.pparams['syringerate']+
                 self.pparams['syringrateunit']+"\r")
            print ">> " + s
            self.pport.write(s)
            print "<< " + self._pumpGetResponse()
            #set volume units
            s = "VOL "+self.pparams['volumeunits']+"\r"
            print ">> " + s
            self.pport.write(s)
            print "<< " + self._pumpGetResponse()
    
    def _pumpGetResponse(self):
        if debug:
            with self.stdout_lock:
                sys.stdout.write("+++++++START PGR:")
            
        while self.pport.inWaiting() <=0:
            sleep(0.1)
        response = self.pport.read(self.pport.inWaiting())
        while response[-1] != '\x03':
            while self.pport.inWaiting() <=0:
                sleep(0.1)
            response = response + self.pport.read(self.pport.inWaiting())
            
        if debug:
            with self.stdout_lock:
                print response
            
        return response
        
    def withdraw(self, volume):
        pump = self.pport
        u = str(int(volume))
        with self.pump_lock:
            pump.write("DIR WDR\r")
            self._pumpGetResponse()
            pump.write("VOL"+u+"\r")
            self._pumpGetResponse()
            pump.write("RUN\r")
            self._pumpGetResponse()
    
    def dispense(self,volume):
        pump = self.pport
        u = str(int(volume))
        with self.pump_lock:
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

    
    
