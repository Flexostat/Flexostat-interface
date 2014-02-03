from numpy import array, ones
from mytimer import mytimer
from math import log10
from time import time, sleep

import json
import threading
import wx
import sys
import serial
import traceback
import types

debug = False


class Controller(object):
    def __init__(self, cparams, logfiles, pparams, cport, pport):
        """Initialize the controller.
        
        Args:
            cparams: configuration parameters.
            logfiles: names of files to log to.
            pparams: pump parameters.
            cport: controller serial port.
            pport: pump serial port.
        """
        pumpdriver_package = 'plugins.%s' % pparams['pumpdriver']
        control_function_package = 'plugins.%s' % cparams['controlfun']
        
        # Import pumpdriver
        pumpdriver = __import__(pumpdriver_package, globals(), locals(),
                                ['Pump'], -1)
                                
        # Fetch the control computation, make it a method of self.
        _temp = __import__(control_function_package, globals(), locals(),
                           ['computeControl'], -1)
        self.computeControl = types.MethodType(_temp.computeControl, self)
        
        #self.ser_lock = cport.lock
        self.stdout_lock = threading.RLock()
        
        # Calibration scaling the OD measurement to some reference value.
        # i.e. scaling to values reported by a spec.
        # TODO: This should be configurable.
        self.odcal = 1  
        
        # Make the pump driver as appropriate.
        self.pump = pumpdriver.Pump(cparams, logfiles, pparams, cport, pport)
        
        # Data from config.ini
        self.logfiles = logfiles
        self.pparams = pparams
        self.cparams = cparams # all controller parameters live here
        self.blank_filename = self.logfiles['blanklog']
        
        # Serial ports
        self.serpt = cport
        self.pport = pport
        
        # This lock is for the following tx/rx raw values.
        # TODO: should the controller know the number of chambers
        # in advance of measuring?
        self.OD_datalock = threading.RLock()
        self.tx_blank = []
        self.rx_blank = []
        self.rx_val = []
        self.tx_val = []
        self.z = []
        
        with self.serpt.lock:
            self.serpt.write("clo;")
            #self.serpt.flush()

        # Construct the timer threads that perform repeated actions.
        # TODO: make serial check period configurable.
        self.start_time = None  # Set on call to start()
        control_period = int(cparams['period'])
        self.cont_timer = mytimer(control_period, self.controlLoop)        
        self.ser_timer = mytimer(2, self.serialCheck)
        
    def start(self):
        """Starts the controller.
        
        So you can construct one without starting all the threads...
        """
        assert self.start_time is None, 'Already started!'
        self.start_time = time()
        self.cont_timer.start()
        self.ser_timer.start()
    
    def quit(self):
        """Quit the controller."""
        assert self.start_time is not None, 'Can\'t quit something you\'ve not started.'
        self.cont_timer.stop()
        self.ser_timer.stop()
        
    def serialCheck(self):
        """Reads data from the serial port.
        
        Called in a thread every N seconds.
        """
        # Serial port better be initialized
        assert self.serpt, 'ServoStat control serial port not initialized!'
        
        # No need for lock:
        # This runs in the only thread that READS self.serpt
        while self.serpt.inWaiting() > 0:
            line = self.serpt.readline().strip()
            self.parseline(line)
    
    def parseOD(self, line):
        """Helper that parses OD data from a line off the serial port.
        
        Args:
            line: the received line.
        
        Raises:
            ValueError if the line could not be parsed.
        """
        data = map(int, line.split())
        
        # Data line format: tx1 rx1 tx2 rx2 
        # TODO: can keep the logfiles open in append mode, no?
        f = open(self.logfiles['odlog'], 'a')
        time_str = str(int(round(time())))
        str_data = map(str, data)
        output_s = '%s %s' % (time_str, ' '.join(str_data))
        f.write(output_s + '\n')
        f.close()

        with self.stdout_lock:
            print output_s

        # Store the reported data locally.
        # Should this be threadsafe?????
        # Yes. It should be.
        with self.OD_datalock:
            self.tx_val = data[0::2]
            self.rx_val = data[1::2]
        
    def parseline(self, line):
        """Parses a line from the serial port.
        
        Args:
            line: the received line.
        """
        # Reporting something back other than OD
        if line[0].isalpha():
            if line[0] == 's':
                with self.stdout_lock:
                    print 'setpont: ' + line
            else:
                try:
                    wx.MessageBox(line, 'Command Response')
                except:
                    with self.stdout_lock:
                        print 'Command Response: ' + line
            return
        
        # First character is not alphabetical - reporting OD.
        try:
            self.parseOD(line)
        except ValueError:
            with self.stdout_lock:
                print 'bad line:', line
            return
            
    def computeOD(self, btx, brx, tx, rx):
        """Compute the OD from blank values and signal values.
        
        Args:
            btx: blank transmitted light value.
            brx: blank reflected light value.
            tx: current transmitted light value.
            rx: current reflected light value.
        
        Returns:
            Calculated optical density for the current values.
        """
        # If either value is 0 then return 0. Since the proper behavior in an 
        # error is to do nothing.
        # NOTE: later versions of this code should probably return None or
        #       throw an exception since the error should probably be handled
        #       by code higher up in the call stack.
        if tx == 0 or rx == 0:
            return 0
        
        blank = float(brx) / float(btx)
        measurement = float(rx) / float(tx)
        od = log10(blank/measurement) * self.odcal
        return od
        
    def controlLoop(self):
    	"""Main loop of control.
    	
    	The plan
          * get OD
          *   if blanks are empty, then store a blank
          * compute control value
          * do dilution (control valves and pumps)
    	"""
        
        with self.OD_datalock:
            tx = self.tx_val
            rx = self.rx_val
        
        if len(rx) == 0 or len(tx) == 0:
            # Have no measurements yet
            return
        
        # TODO: do we need to lock writing blanks?
        if len(self.tx_blank) == 0 or len(self.rx_blank) == 0:
            try:
                # TODO: Make this parsing a helper.
                bf = open(self.blank_filename, 'r')
                blank_values = map(int, bf.readline().split())
                self.tx_blank = blank_values[0::2]
                self.rx_blank = blank_values[1::2]
            except:
                # No blank.dat file. Use the most recent measurement.
                self.rx_blank = rx
                self.tx_blank = tx
                
                with open(self.blank_filename, 'w') as bf:
					# Interleave tx and rx  
					flat_blank = [str(j) for i in zip(self.tx_blank, self.rx_blank)
								  for j in i];
					bfstring = ' '.join(flat_blank)
					bf.write('%s\n' % bfstring)
                
            # Setup z when blanking
            self.z = [None] * len(self.rx_blank)  
                 
        # Compute control
        # TODO: number of chambers should be configurable, no?
        ods = map(self.computeOD, self.tx_blank,
                  self.rx_blank, tx, rx)
        cont = map(self.computeControl, ods, self.z, range(8),
                   [time()-self.start_time]*len(self.z))
        
        #u = [q[0] for q in cont]
        #self.z = [q[1] for q in cont]
        # Separate u lists from z
        contT = zip(*cont) #transpose cont values [([u1,u2],z),([u1,u2],z),...]
        u = array(contT[0]).transpose() #u=array([[u1,u1,u1,...],[u2,u2,u2,...]])
        self.z = contT[1]
        
        
        # Set excluded chambers to dilute at 11 units/chamber
        try:
            exf = open('exclude.txt','r')
            exvals = map(int,exf.readline().split())
            exf.close()
            for ee in exvals:
                u[:,ee-1] = u[:,ee-1]+11
        except:
        	pass
        	            
        # Log events
        print 'Logging data.'
        time_secs = int(round(time()))
        dlog = {'timestamp': time_secs,
        		'ods': [round(od, 4) for od in ods],
        		'u': u.tolist(),
        		'z': [str(z) for z in self.z]}
        log_str = json.dumps(dlog)

        with open(self.logfiles['fulllog'], 'a') as f:
        	f.write('%s\n' % log_str)
        
        with self.stdout_lock:
            print log_str
        
        # Handle dispensing.
        try:
            with self.serpt.lock:
                self.serpt.write("sel0;") #select media source
#                self.serpt.flush()
            print 'sel 0'
            sleep(0.5)
                
            # TODO: parameterize antibacklash, now 100
            self.pump.withdraw(u.sum(axis=1) + 100)
            self.pump.waitForPumping()
            self.pump.dispense(ones((u.shape[0], 1)) * 100)
            self.pump.waitForPumping()
            chamber_num = 1
            
            # dispvals gets a tuple of dispense volumes for chamber_num
            for dispvals in u.transpose():
                selstr = "sel%s;" % chamber_num
                #if we're moving from PV1 to PV2 then close first
                #to prevent leaks into tube 5
                #(ie to prevent multiple valves from being oupen at once)
                if chamber_num == 5:
                    with self.serpt.lock:
                        self.serpt.write("clo;")
#                        self.serpt.flush()
                    sleep(2);
                with self.serpt.lock:
                    self.serpt.write(selstr) #select chamber
#                    self.serpt.flush()
                print selstr #for debug
                sleep(1.0)  #give PV time to move, SPV needs ~100ms, servo 1s
                                
                self.pump.dispense(dispvals)
                self.pump.waitForPumping()
                
                chamber_num = chamber_num + 1
            
            with self.serpt.lock:
                self.serpt.write("clo;")
#                self.serpt.flush()
            print 'clo;'
                
        except AttributeError, e:
            with self.stdout_lock:
                print 'no pump', e
            traceback.print_exc(file=sys.stdout)
        
        pass

    
