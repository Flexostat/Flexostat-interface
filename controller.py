from mytimer import mytimer
#import pumpdriver
from time import time, sleep
from math import log10
import threading
#import wx
import sys
import serial
import traceback
import types

debug = False


class Controller:
    
    def __init__(self,cparams,logfiles,pparams,cport,pport):
        pumpdriver = __import__('plugins.'+pparams['pumpdriver'],globals(),
                                locals(),['Pump'],-1)
        _temp = __import__('plugins.'+cparams['controlfun'],globals(),locals,
                           ['computeControl'],-1)
        self.computeControl = types.MethodType(_temp.computeControl,self)
        self.ser_lock = cport.lock
        self.stdout_lock = threading.RLock()
        
        self.pump = pumpdriver.Pump(cparams,logfiles,pparams,cport,pport)
        self.odcal = 1
        
        self.logfiles = logfiles
        self.pparams = pparams
        self.cparams = cparams #all controller parameters live here
        self.serpt = cport
        self.pport = pport
        self.tx_blank = []
        self.rx_blank = []
        self.rx_val = []
        self.tx_val = []
        self.z = []
        with self.ser_lock:
            self.serpt.write("clo;")
            self.serpt.flush()
        
        #start the control-loop timer.
        self.cont_timer = mytimer(cparams['period'],self.controlLoop)
        self.cont_timer.start()
        
        #start the serial polling timer
        self.ser_timer = mytimer(2, self.serialCheck)
        self.ser_timer.start()
        
    def quit(self):
        self.cont_timer.stop()
        self.ser_timer.stop()
        
    def serialCheck(self):
        #if the serpt is uninitialized then do nothing.
        try:
#no need for lock.  only thread that READS serpt
#            with self.ser_lock:
            while (self.serpt.inWaiting() > 0):
                line = self.serpt.readline().strip()
                self.parseline(line)
        except AttributeError:
            pass
        
    def parseline(self,line):
        
        #reporting something back other than OD
        if line[0].isalpha():
            
            if line[0]=='s':
                with self.stdout_lock:
                    print 'setpont: ' + line
#                self.f.m_textCtrl_sp.ChangeValue(line.lstrip('s'))
            else:
                try:
                    wx.MessageBox(line, 'Command Response')
                except:
                    with self.stdout_lock:
                        print 'Command Response: ' + line
            
        else:   
            data = map(int,line.split())
            #data line format: tx1 rx1 tx2 rx2 
            
            f = open(self.logfiles['odlog'],"a")
            s = str(int(round(time())))
            for d in data:
                s += " " + str(d)
            f.write(s+'\n')
            f.close()
            with self.stdout_lock:
                print s
            #should this be threadsafe?????
            # yes.  it should be.
            self.tx_val = data[0::2]
            self.rx_val = data[1::2]
            
    def computeOD(self,btx,brx,tx,rx):
        #calulate OD
        blank = float(brx)/float(btx)
        measurement = (float(rx)/float(tx))
        od = log10(blank/measurement)*self.odcal
        return od
        
    def controlLoop(self):
        #the plan
        #get OD
        #if blanks == 0 then use this as blank
        #compute control value
        #do dilution (control valves and pumps)
        if len(self.rx_val) == 0 or len(self.tx_val) == 0:
            return
        if len(self.tx_blank) == 0 or len(self.rx_blank) == 0:
            try:
                bf = open('blank.dat','r')
                blank_values = map(int,bf.readline().split())
                self.tx_blank = blank_values[0::2]
                self.rx_blank = blank_values[1::2]
            except:
                self.rx_blank = self.rx_val
                self.tx_blank = self.tx_val
                bf = open('blank.dat','w')
                #intrleave tx and rx  
                flat_blank = [j for i in zip(self.tx_blank,self.rx_blank)
                              for j in i];
                bfstring = "";
                for j in flat_blank:
                    bfstring += str(j) + " "
                bf.write(bfstring + "\n")
                 
        #compute control
        ods = map(self.computeOD,self.tx_blank,self.rx_blank,
                            self.tx_val,self.rx_val)
        cont = map(self.computeControl,ods, self.z)
        
        u = [q[0] for q in cont]
        self.z = [q[1] for q in cont]

        
        exf = open('exclude.txt','r')
        exvals = map(int,exf.readline().split())
        for exx in exvals:
            u[exx-1] = 11
        exf.close()
        
        #log events
        #TODO: let z be a generic object and have instead log " blah %s"%z
        f = open(self.logfiles['fulllog'],"a")
        s = str(int(round(time())))+" " \
            + str(map(round,ods,[4]*len(ods)))+" " \
            + str(map(round,self.z,[4]*len(self.z)))+" "+str(u)
        f.write(s+'\n')
        f.close()
        
        with self.stdout_lock:
            print s
        
        try:
            with self.ser_lock:
                self.serpt.write("sel0;") #select media source
                self.serpt.flush()
            print 'sel 0'
            sleep(0.5)
                
            self.pump.withdraw(sum(u)+50)
            self.pump.waitForPumping()
            self.pump.dispense(50)
            self.pump.waitForPumping()
            chamber_num = 1
            
            for dispval in u:
                selstr = "sel" + str(chamber_num) + ";"
                #if we're moving from PV1 to PV2 then close first
                #to prevent leaks into tube 5
                if chamber_num == 5:
                    with self.ser_lock:
                        self.serpt.write("clo;");
                    sleep(2);
                with self.ser_lock:
                    self.serpt.write(selstr) #select chamber
                    self.serpt.flush()
                sleep(2.0)  #for some reason one PV is very slow.  
                print selstr #for debug
                
                self.pump.dispense(dispval)
                self.pump.waitForPumping()
                
                chamber_num = chamber_num + 1
            
            with self.ser_lock:
                self.serpt.write("clo;")
                self.serpt.flush()
            print 'clo'
                
        except AttributeError:
            with self.stdout_lock:
                print 'no pump'
            traceback.print_exc(file=sys.stdout)
        
        pass

    
